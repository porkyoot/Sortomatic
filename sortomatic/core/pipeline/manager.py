import os
import concurrent.futures
import atexit
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from ..database import FileIndex, db
from ..config import settings
from ..scanner import smart_walk
from ..types import ScanContext
from .passes import categorization, hashing

# Global executor instance for the pipeline
_executor = None

def get_executor():
    """Returns the global thread pool executor, initializing it if needed."""
    global _executor
    if _executor is None:
        _executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=settings.max_workers,
            thread_name_prefix="sortomatic_worker"
        )
    return _executor

def _shutdown_executor(wait=False):
    """Shuts down the executor, optionally cancelling pending tasks."""
    global _executor
    if _executor is not None:
        # cancel_futures=True is available in Python 3.9+ 
        # It's much faster for stopping large batches of tasks.
        _executor.shutdown(wait=wait, cancel_futures=True)
        _executor = None

# We use a lambda to ensure the default atexit call doesn't block forever
atexit.register(lambda: _shutdown_executor(wait=False))

class PipelineManager:
    """Pipeline manager that processes files through indexing, categorization, and hashing passes.
    
    Note: Uses global database state initialized via database.init_db().
    """
    def __init__(self):
        pass

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
        """Process files from filesystem to database using a sliding window."""
        import concurrent.futures
        
        buffer = []
        total = 0
        total_bytes = 0
        executor = get_executor()
        walker = smart_walk(Path(root_path))
        
        max_queued = settings.batch_size
        futures = set()
        
        def fill_pool():
            nonlocal total_bytes
            while len(futures) < max_queued:
                try:
                    item = next(walker)
                    futures.add(executor.submit(worker_func, item))
                except StopIteration:
                    return False
            return True

        has_more = fill_pool()
        
        while futures:
            done, futures = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                try:
                    result = future.result()
                    if result:
                        buffer.append(result)
                        total += 1
                        total_bytes += result.get('size_bytes', 0)
                        if progress_callback:
                            progress_callback()
                    
                    if len(buffer) >= (max_queued // 10):
                        self._flush_insert(buffer)
                        buffer = []
                except Exception as e:
                    from ...utils.logger import logger
                    logger.debug(f"FS Worker failed: {e}", exc_info=True)
            
            if has_more:
                has_more = fill_pool()
        
        if buffer:
            self._flush_insert(buffer)
        return {'count': total, 'bytes': total_bytes}

    def _run_db_pipeline(self, query, worker_func, progress_callback):
        """Process items from database using a sliding window."""
        import concurrent.futures
        
        buffer = []
        total = 0
        executor = get_executor()
        chunk_size = settings.batch_size
        
        query_iterator = query.iterator()
        futures = set()
        
        def fill_pool():
            while len(futures) < chunk_size:
                try:
                    item = next(query_iterator)
                    futures.add(executor.submit(worker_func, item))
                except StopIteration:
                    return False
            return True

        has_more = fill_pool()
        
        while futures:
            done, futures = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                try:
                    result = future.result()
                    if result:
                        buffer.append(result)
                        total += 1
                        if progress_callback:
                            progress_callback()
                        
                    if len(buffer) >= (chunk_size // 10):
                        self._flush_update(buffer)
                        buffer = []
                except Exception as e:
                    from ...utils.logger import logger
                    logger.debug(f"DB Worker failed: {e}", exc_info=True)
            
            if has_more:
                has_more = fill_pool()
                    
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