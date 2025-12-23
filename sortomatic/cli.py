import typer
import os
import sys
import atexit
from pathlib import Path
from typing import Optional
from .core import database
from .core.config import settings
from .core.pipeline.manager import PipelineManager
from .l8n import Strings
from .utils.logger import setup_logger, logger, console

app = typer.Typer(help=Strings.APP_HELP)


# Configuration
DATA_DIR = Path(".sortomatic")
DB_PATH = DATA_DIR / "sortomatic.db"

# --- THE GLOBAL SAFETY NET ---
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Catch all uncaught exceptions, log them as FATAL, and exit gracefully.
    """
    # Handle KeyboardInterrupt (Ctrl+C) gracefully
    if issubclass(exc_type, KeyboardInterrupt):
        database.close_db()
        logger.info(f"\n{Strings.USER_ABORT}")
        sys.exit(0)

    # Log as FATAL with the full traceback saved in the logger
    # Rich will render this traceback beautifully because we set rich_tracebacks=True
    logger.fatal(f"Uncaught exception: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
    
    database.close_db()
    # Optional: Exit with a non-zero code to indicate failure to scripts
    sys.exit(1)

# Register the hook
sys.excepthook = handle_exception
atexit.register(database.close_db)
# -----------------------------

def ensure_environment():
    """Make sure data directories exist."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show DEBUG logs"),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    """
    Global entry point callback.
    """
    if threads:
        settings.max_workers = threads
        
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(log_level)

@app.command(help=Strings.SCAN_DOC)
def scan(
    path: str = typer.Argument(..., help=Strings.SCAN_PATH_HELP),
    reset: bool = typer.Option(False, "--reset", help=Strings.SCAN_RESET_HELP),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    """
    Index a directory into the database.
    """
    if threads:
        settings.max_workers = threads
        
    ensure_environment()
    
    # Initialize the Peewee ORM (creates tables)
    database.init_db(str(DB_PATH))
    
    if reset:
        typer.confirm(Strings.WIPE_CONFIRM, abort=True)
        # Drop and recreate to handle schema changes
        database.db.drop_tables([database.FileIndex])
        database.db.create_tables([database.FileIndex])
        logger.warning(Strings.WIPE_SUCCESS)

    logger.info(f"Starting scan: {path}")

    # Run the Pipeline
    manager = PipelineManager(str(DB_PATH), max_workers=settings.max_workers)
    
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(Strings.INDEXING_MSG.format(name=os.path.basename(path)), total=None)
        
        def update_progress():
            progress.advance(task)
            
        count = manager.run(path, progress_callback=update_progress)
        
    logger.success(Strings.SCAN_COMPLETE.format(total_files=count))

@app.command(help=Strings.STATS_DOC)
def stats():
    """
    Show insights about your files.
    """
    ensure_environment()
    database.init_db(str(DB_PATH))
    
    from peewee import fn
    
    # Example: Count by Category
    # SELECT category, COUNT(*) FROM fileindex GROUP BY category
    query = (database.FileIndex
             .select(database.FileIndex.category, fn.COUNT(database.FileIndex.id).alias('count'))
             .group_by(database.FileIndex.category)
             .order_by(fn.COUNT(database.FileIndex.id).desc()))
    
    # We can use Rich tables here too!
    from rich.table import Table
    
    table = Table(title=Strings.STATS_TITLE)
    table.add_column(Strings.CATEGORY_LABEL, style="cyan")
    table.add_column(Strings.COUNT_LABEL, justify="right", style="magenta")
    
    for row in query:
        table.add_row(row.category, str(row.count))
        
    console.print(table)

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        logger.info(f"\n{Strings.USER_ABORT}")
        sys.exit(0)