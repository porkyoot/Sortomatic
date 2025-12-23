import os
from pathlib import Path
from typing import Generator, Tuple
from .config import settings

def smart_walk(root: Path) -> Generator[Tuple[str, str], None, None]:
    """
    Yields tuples of (path, type).
    type is 'file' or 'bundle'.
    """
    # Convert list to set for O(1) lookup
    atomic_markers = set(settings.atomic_markers)
    
    for dirpath, dirnames, filenames in os.walk(root):
        # 1. Check for Atomic Markers (BEFORE filtering ignore_patterns)
        # We check the raw dirnames/filenames from the OS
        full_contents = set(dirnames) | set(filenames)
        if not full_contents.isdisjoint(atomic_markers):
            # FOUND ATOMIC FOLDER (e.g., a Git Repo)
            # Yield the folder itself as a 'bundle'
            yield (dirpath, 'bundle')
            
            # CRITICAL: Modify dirnames in-place to PREVENT recursion
            dirnames[:] = [] 
            continue

        # 2. Respect Ignore Patterns for normal recursion
        dirnames[:] = [d for d in dirnames if d not in settings.ignore_patterns]
            
        # 3. Normal File Processing
        for f in filenames:
            yield (os.path.join(dirpath, f), 'file')