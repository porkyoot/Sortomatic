from peewee import *
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..utils.logger import logger

# We use a Proxy to delay the actual DB connection until we run 'init_db'
db = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = db

class FileIndex(BaseModel):
    path = CharField(unique=True, index=True, max_length=1024)
    filename = CharField(index=True)
    extension = CharField(null=True)
    size_bytes = IntegerField()
    modified_at = DateTimeField()
    
    # New Field: 'file' or 'bundle' (for atomic folders)
    entry_type = CharField(default='file', index=True) 
    
    # Analysis
    category = CharField(default=None, index=True)
    mime_type = CharField(null=True)  # Result of 'file' command check
    
    # Hashing
    fast_hash = CharField(null=True, index=True) # e.g. MD5 partial
    full_hash = CharField(null=True, index=True) # e.g. SHA-256
    perceptual_hash = CharField(null=True)       # For images
    
    is_duplicate = BooleanField(default=False)
    group_id = CharField(null=True, index=True)  # To group duplicates together
    
    # For the "War Room" (Review phase)
    action_pending = CharField(null=True) # e.g., 'KEEP', 'IGNORE', 'MERGE'

def init_db(db_path: str = "data/sortomatic.db"):
    """
    Initializes the SQLite connection with high-performance settings.
    """
    # WAL mode allows simultaneous reading and writing (crucial for concurrency)
    database = SqliteDatabase(db_path, pragmas={
        'journal_mode': 'wal',
        'cache_size': -1024 * 64,  # 64MB cache
        'synchronous': 0           # Risky but fast for local tools
    })
    
    # Bind the proxy to the real database
    db.initialize(database)
    logger.debug(f"Database initialized at {db_path} (WAL mode)")
    
    # Create tables if they don't exist
    db.connect()
    db.create_tables([FileIndex])
    
    return database

def close_db():
    """
    Closes the database connection.
    """
    try:
        if not db.is_closed():
            db.close()
            logger.debug("Database connection closed.")
    except AttributeError:
        # Proxy was never initialized
        pass