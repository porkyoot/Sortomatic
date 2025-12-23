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
    """
    The central inventory. 
    One row = One physical file on disk.
    """
    path = CharField(unique=True, index=True, max_length=1024)
    filename = CharField(index=True)
    extension = CharField(null=True, index=True)
    size_bytes = IntegerField()
    modified_at = DateTimeField()
    
    # Analysis Data
    category = CharField(default=None, index=True)
    content_hash = CharField(null=True, index=True) # MD5/SHA256
    is_duplicate = BooleanField(default=False)
    is_atomic = BooleanField(default=False)
    
    # For the "War Room" (Review phase)
    action_pending = CharField(null=True) # e.g., 'DELETE', 'MOVE'

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
    if not db.is_closed():
        db.close()
        logger.debug("Database connection closed.")