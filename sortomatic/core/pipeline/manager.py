import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from ..database import FileIndex, db
from ..scanner import smart_walk
from ..types import ScanContext, UpdateContext
from .passes import categorization, hashing
from .executor import get_executor

class PipelineManager:
    """Pipeline manager that processes files through indexing, categorization, and hashing passes.
    
    Note: Uses global database state initialized via database.init_db().
    """
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def _index_pass(self, item: tuple) -> Optional[ScanContext]:
        """Extract filesystem metadata."""
        path_str, entry_type = item
        try:
            stat = os.stat(path_str)
        except OSError:
            return None
            
        return ScanContext(
            path=path_str,
            filename=os.path.basename(path_str),
            entry_type=entry_type,
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            category='Project/Bundle' if entry_type == 'bundle' else None,
            mime_type=None,
            fast_hash=None,
            full_hash=None,
            perceptual_hash=None
        )

    def _categorize_pass(self, item: FileIndex) -> Dict[str, any]:
        """Categorize file from database model."""
        ctx = ScanContext(
            path=item.path,
            filename=item.filename,
            size_bytes=item.size_bytes,
            category=None,
            mime_type=None
        )
        
        ctx = categorization.detect_type(ctx)
        
        return {
            'id': item.id,
            'category': ctx.get('category'),
            'mime_type': ctx.get('mime_type'),
            'extension': ctx.get('extension')
        }

    def _hash_pass(self, item: FileIndex) -> Dict[str, any]:
        """Compute file hashes."""
        ctx = ScanContext(
            path=item.path,
            size_bytes=item.size_bytes,
            category=item.category,
            fast_hash=None,
            full_hash=None,
            perceptual_hash=None
        )
        
        ctx = hashing.compute_hashes(ctx)
        
        return {
            'id': item.id,
            'fast_hash': ctx.get('fast_hash'),
            'full_hash': ctx.get('full_hash'),
            'perceptual_hash': ctx.get('perceptual_hash')
        }

    def _full_pass(self, item: tuple) -> Optional[ScanContext]:
        """Run all passes in sequence for single item."""
        ctx = self._index_pass(item)
        if not ctx:
            return None
        
        if ctx.get('entry_type') == 'bundle':
            return ctx
            
        ctx = categorization.detect_type(ctx)
        ctx = hashing.compute_hashes(ctx)
        return ctx



    def run_index(self, root_path: str, progress_callback=None):
        return self._run_fs_pipeline(root_path, self._index_pass, progress_callback)
        
    def run_categorize(self, progress_callback=None):
        # Fetch unsorted items
        query = FileIndex.select().where(FileIndex.category.is_null())
        return self._run_db_pipeline(query, self._categorize_pass, progress_callback)
        
    def run_hash(self, progress_callback=None):
        # Fetch unhashed items (ignoring bundles)
        query = FileIndex.select().where(
            (FileIndex.full_hash.is_null()) & 
            (FileIndex.entry_type == 'file')
        )
        return self._run_db_pipeline(query, self._hash_pass, progress_callback)

    def run_all(self, root_path: str, progress_callback=None):
        return self._run_fs_pipeline(root_path, self._full_pass, progress_callback)

    # --- Pipeline Engines ---

    def _run_fs_pipeline(self, root_path, worker_func, progress_callback):
        """Process files from filesystem to database."""
        import concurrent.futures
        from itertools import islice
        
        buffer = []
        total = 0
        total_bytes = 0
        executor = get_executor()
        walker = smart_walk(Path(root_path))
        chunk_size = 10000
        
        while True:
            chunk = list(islice(walker, chunk_size))
            if not chunk:
                break
            
            futures = [executor.submit(worker_func, item) for item in chunk]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        buffer.append(result)
                        total += 1
                        total_bytes += result.get('size_bytes', 0)
                        if progress_callback:
                            progress_callback()
                    
                    if len(buffer) >= 1000:
                        self._flush_insert(buffer)
                        buffer = []
                except Exception as e:
                    from ...utils.logger import logger
                    logger.debug(f"Worker failed processing file: {e}", exc_info=True)
        
        if buffer:
            self._flush_insert(buffer)
        return {'count': total, 'bytes': total_bytes}

    def _run_db_pipeline(self, query, worker_func, progress_callback):
        """Process items from database with updates."""
        buffer = []
        total = 0
        executor = get_executor()
        future_results = executor.map(worker_func, query.iterator())
        
        for result in future_results:
            if result:
                buffer.append(result)
                total += 1
                if progress_callback:
                    progress_callback()
                
            if len(buffer) >= 1000:
                self._flush_update(buffer)
                buffer = []
                
        if buffer:
            self._flush_update(buffer)
        return total

    def _flush_insert(self, data):
        with db.atomic():
            FileIndex.insert_many(data).on_conflict_ignore().execute()
            
    def _flush_update(self, data):
        if not data: return
        
        # Peewee bulk_update requires Model instances, not dicts
        model_instances = [FileIndex(**item) for item in data]
        
        # Get fields from the first item, exclude 'id' (which is the PK)
        fields = list(data[0].keys())
        if 'id' in fields:
            fields.remove('id')
            
        with db.atomic():
            FileIndex.bulk_update(model_instances, fields=fields, batch_size=100)