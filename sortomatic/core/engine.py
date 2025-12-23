import os
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

# Relative imports assuming this is in sortomatic/core/
from .database import FileIndex, db as peewee_proxy
from .config import settings
from ..l8n import Strings
from ..utils.logger import logger, console

class ScanEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.batch_size = 10000  # Insert 10k files at a time to save RAM

    def run(self, root_path: str):
        """
        The main entry point. Orchestrates the scan.
        """
        root = Path(root_path).resolve()
        
        if not root.exists():
            logger.error(Strings.PATH_NOT_FOUND.format(path=root))
            return

        # 1. Count Phase (Optional, but makes the progress bar accurate)
        total_files = self._count_files_fast(root)
        
        # 2. Ingestion Phase
        self._ingest_files(root, total_files)

    def _count_files_fast(self, root: Path) -> int:
        """
        Counts files while respecting the same ignore patterns as the main scan.
        """
        count = 0
        with console.status(Strings.CRAWLING_MSG.format(name=root.name), spinner="dots"):
            for dirpath, dirnames, filenames in os.walk(root):
                # CRITICAL: Modify dirnames in-place to skip ignored folders recursively
                dirnames[:] = [d for d in dirnames if d not in settings.ignore_patterns]
                count += len(filenames)
        return count

    def _ingest_files(self, root: Path, total_files: int):
        """
        Walks the FS and inserts into DB using Raw SQL for maximum speed.
        """
        # inserting 100k+ rows in a loop.
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode = WAL") 
            conn.execute("PRAGMA synchronous = OFF") # Safe enough for initial scan
            
            buffer: List[Tuple] = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task(Strings.INDEXING_MSG.format(name=root.name), total=total_files)
                
                # The High-Speed Walker
                for dirpath, dirnames, filenames in os.walk(root):
                    # In-place modification of dirnames to skip ignored folders
                    dirnames[:] = [d for d in dirnames if d not in settings.ignore_patterns]
                    
                    for f in filenames:
                        full_path = os.path.join(dirpath, f)
                        try:
                            # minimal stat call
                            stat = os.stat(full_path)
                            
                            # Determine category instantly
                            ext = os.path.splitext(f)[1]
                            category = settings.get_category(ext)
                            
                            # Prepared tuple for SQL
                            buffer.append((
                                full_path,                  # path
                                f,                          # filename
                                ext.lower(),                # extension
                                stat.st_size,               # size_bytes
                                datetime.fromtimestamp(stat.st_mtime), # modified_at
                                category,                   # category
                                False                       # is_duplicate
                            ))
                            
                            progress.advance(task)
                            
                            # Flush batch if full
                            if len(buffer) >= self.batch_size:
                                self._flush_buffer(conn, buffer)
                                buffer.clear()
                                
                        except OSError:
                            # Permission errors, broken links, etc.
                            continue

                # Final flush
                if buffer:
                    self._flush_buffer(conn, buffer)
            
            logger.success(Strings.SCAN_COMPLETE.format(total_files=total_files))
        finally:
            conn.close()

    def _flush_buffer(self, conn: sqlite3.Connection, buffer: List[Tuple]):
        """
        Performs the raw SQL bulk insert.
        """
        sql = """
            INSERT OR IGNORE INTO fileindex 
            (path, filename, extension, size_bytes, modified_at, category, is_duplicate) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        conn.executemany(sql, buffer)
        conn.commit()