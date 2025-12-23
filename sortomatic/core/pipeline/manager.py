import os
from datetime import datetime
from pathlib import Path
from ..database import FileIndex, db
from ..scanner import smart_walk
from .passes import categorization, hashing
from .executor import get_executor

class PipelineManager:
    def __init__(self, db_path: str, max_workers: int = 4):
        self.db_path = db_path
        self.workers = max_workers

    # --- Granular Passes ---

    def _index_pass(self, item: tuple):
        """Pass 1: Just FS Metadata"""
        path_str, entry_type = item
        try:
            stat = os.stat(path_str)
        except OSError:
            return None
            
        ctx = {
            'path': path_str,
            'filename': os.path.basename(path_str),
            'entry_type': entry_type,
            'size_bytes': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime),
            # Explicitly nullify others for clarity, though default is null/None
            'category': 'Project/Bundle' if entry_type == 'bundle' else None,
            'mime_type': None,
            'fast_hash': None,
            'full_hash': None,
            'perceptual_hash': None
        }
        return ctx

    def _categorize_pass(self, item: FileIndex):
        """Pass 2: Categorize from DB Model"""
        ctx = {
            'path': item.path,
            'filename': item.filename,
            'size_bytes': item.size_bytes,
            'category': None,
            'mime_type': None
        }
        
        # Run detection
        ctx = categorization.detect_type(ctx)
        
        # Return dict of ONLY updated fields for bulk_update
        return {
            'id': item.id,
            'category': ctx.get('category'),
            'mime_type': ctx.get('mime_type'),
            'extension': ctx.get('extension') # detect_type may refine this
        }

    def _hash_pass(self, item: FileIndex):
        """Pass 3: Hash from DB Model"""
        ctx = {
            'path': item.path,
            'size_bytes': item.size_bytes,
            'category': item.category, # Needed for perceptual hash check
            'fast_hash': None,
            'full_hash': None,
            'perceptual_hash': None
        }
        
        ctx = hashing.compute_hashes(ctx)
        
        return {
            'id': item.id,
            'fast_hash': ctx.get('fast_hash'),
            'full_hash': ctx.get('full_hash'),
            'perceptual_hash': ctx.get('perceptual_hash')
        }

    def _full_pass(self, item: tuple):
        """All-in-one pass for fresh scans"""
        ctx = self._index_pass(item)
        if not ctx: return None
        
        if ctx['entry_type'] == 'bundle':
            return ctx
            
        ctx = categorization.detect_type(ctx)
        ctx = hashing.compute_hashes(ctx)
        return ctx

    # --- Runners ---

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
        """Engine for FileSystem -> DB"""
        buffer = []
        total = 0
        executor = get_executor()
        
        # Submit jobs
        future_results = executor.map(worker_func, smart_walk(Path(root_path)))
        
        for result in future_results:
            if result:
                buffer.append(result)
                total += 1
                if progress_callback: progress_callback()
            
            if len(buffer) >= 1000:
                self._flush_insert(buffer)
                buffer = []
        
        if buffer: self._flush_insert(buffer)
        return total

    def _run_db_pipeline(self, query, worker_func, progress_callback):
        """Engine for DB -> CPU -> DB Update"""
        buffer = []
        total = 0
        executor = get_executor()
        
        # We must iterator over the query. 
        # CAUTION: Fetching all IDs first or using server-side cursor is safer for large DBs
        # For simplicity, we assume iterator() is sufficient (Peewee uses cursor)
        
        # Map requires an iterator
        future_results = executor.map(worker_func, query.iterator())
        
        for result in future_results:
            if result:
                buffer.append(result)
                total += 1
                if progress_callback: progress_callback()
                
            if len(buffer) >= 1000:
                self._flush_update(buffer)
                buffer = []
                
        if buffer: self._flush_update(buffer)
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