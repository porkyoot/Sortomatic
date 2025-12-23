"""Type definitions for the scanning pipeline."""
from typing import TypedDict, Optional
from datetime import datetime


class FileMetadata(TypedDict, total=False):
    """Base file metadata from filesystem."""
    path: str
    filename: str
    entry_type: str
    size_bytes: int
    modified_at: datetime


class CategoryData(TypedDict, total=False):
    """Category detection results."""
    category: Optional[str]
    mime_type: Optional[str]
    extension: Optional[str]


class HashData(TypedDict, total=False):
    """Hash computation results."""
    fast_hash: Optional[str]
    full_hash: Optional[str]
    perceptual_hash: Optional[str]


class ScanContext(FileMetadata, CategoryData, HashData):
    """Complete scan context combining all pipeline data."""
    pass


class UpdateContext(TypedDict):
    """Context for database updates with ID."""
    id: int
