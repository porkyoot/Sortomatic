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

    def process_item(self, item: tuple):
        """
        The Worker Function. Runs the pipeline passes on a single item.
        """
        path_str, entry_type = item
        
        # Base Context
        try:
            stat = os.stat(path_str)
        except OSError:
            return None # File vanished or locked

        ctx = {
            'path': path_str,
            'filename': os.path.basename(path_str),
            'entry_type': entry_type,
            'size_bytes': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime)
        }

        # If it's a Bundle (Atomic Folder), skip content analysis passes
        if entry_type == 'bundle':
            ctx['category'] = 'Project/Bundle'
            return ctx

        # --- RUN PASSES ---
        # 1. Categorize
        ctx = categorization.detect_type(ctx)
        
        # 2. Hash (CPU Heavy)
        ctx = hashing.compute_hashes(ctx)
        
        return ctx

    def run(self, root_path: str, progress_callback=None):
        """
        Orchestrate the concurrent scan.
        """
        root = Path(root_path)
        buffer = []
        
        total = 0
        executor = get_executor()
        from ...utils.logger import logger
        logger.debug(f"Using {executor._max_workers} threads for analysis")
        
        # Submit jobs lazily from the generator
        future_results = executor.map(self.process_item, smart_walk(root))
        
        for result in future_results:
            if result:
                buffer.append(result)
                total += 1
                if progress_callback: progress_callback()
            
            # Bulk Insert Batching
            if len(buffer) >= 1000:
                self._flush(buffer)
                buffer = []
                
        if buffer: self._flush(buffer)
        return total

    def _flush(self, data):
        # Use Peewee's atomic bulk insert for speed
        with db.atomic():
            FileIndex.insert_many(data).on_conflict_ignore().execute()