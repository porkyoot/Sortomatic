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

app = typer.Typer(help=Strings.APP_HELP, invoke_without_command=True)


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
    ctx: typer.Context,
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
    
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# --- SCAN GROUP ---
scan_app = typer.Typer(help=Strings.SCAN_DOC, invoke_without_command=True)
app.add_typer(scan_app, name="scan")

@scan_app.callback()
def scan_callback(
    ctx: typer.Context,
    path: Optional[str] = typer.Argument(None, help=Strings.SCAN_PATH_HELP),
    reset: bool = typer.Option(False, "--reset", help=Strings.SCAN_RESET_HELP),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    """
    Scanning pipeline commands. If no subcommand is provided and a path is given, runs full scan.
    """
    # If a subcommand was invoked, don't do anything here
    if ctx.invoked_subcommand is not None:
        return
    
    # If no path provided, show help
    if path is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
    # Run full scan pipeline
    _run_pipeline(path, reset, threads, mode="all")

@scan_app.command("all", help=Strings.SCAN_ALL_DOC)
def scan_all(
    path: str = typer.Argument(..., help=Strings.SCAN_PATH_HELP),
    reset: bool = typer.Option(False, "--reset", help=Strings.SCAN_RESET_HELP),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    _run_pipeline(path, reset, threads, mode="all")

@scan_app.command("index", help=Strings.SCAN_INDEX_DOC)
def scan_index(
    path: str = typer.Argument(..., help=Strings.SCAN_PATH_HELP),
    reset: bool = typer.Option(False, "--reset", help=Strings.SCAN_RESET_HELP),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    _run_pipeline(path, reset, threads, mode="index")

@scan_app.command("category", help=Strings.SCAN_CAT_DOC)
def scan_categorize(
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    _run_pipeline(None, False, threads, mode="category")

@scan_app.command("hash", help=Strings.SCAN_HASH_DOC)
def scan_hash(
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use")
):
    _run_pipeline(None, False, threads, mode="hash")

def _run_pipeline(path: Optional[str], reset: bool, threads: Optional[int], mode: str):
    """
    Common runner for all scan modes.
    """
    import time
    import humanize
    
    start_time = time.time()
    
    if threads:
        settings.max_workers = threads
        
    ensure_environment()
    database.init_db(str(DB_PATH))
    
    if reset and path:
        typer.confirm(Strings.WIPE_CONFIRM, abort=True)
        database.db.drop_tables([database.FileIndex])
        database.db.create_tables([database.FileIndex])
        logger.warning(Strings.WIPE_SUCCESS)

    manager = PipelineManager(str(DB_PATH), max_workers=settings.max_workers)
    
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, ProgressColumn
    from rich.text import Text
    from rich.table import Column
    
    # Custom speed column
    class SpeedColumn(ProgressColumn):
        def __init__(self, unit="files/s"):
            self.unit = unit
            super().__init__(table_column=Column(no_wrap=True, justify="right"))
            
        def render(self, task):
            speed = task.speed
            if speed is None or speed < 0.1:
                return Text("--", style="dim cyan")
            return Text(f"{speed:.1f} {self.unit}", style="cyan")
    
    # Determine task description based on mode
    if mode == 'all' or mode == 'index':
        task_desc = Strings.INDEXING_MSG
    elif mode == 'category':
        task_desc = Strings.CATEGORIZING_MSG
    elif mode == 'hash':
        task_desc = Strings.HASHING_MSG
    else:
        task_desc = f"Running {mode} pass..."
    
    # Pre-count for DB passes to show determinate progress
    total = None
    if mode == 'category':
        total = database.FileIndex.select().where(database.FileIndex.category.is_null()).count()
    elif mode == 'hash':
        total = database.FileIndex.select().where(
            (database.FileIndex.full_hash.is_null()) & 
            (database.FileIndex.entry_type == 'file')
        ).count()
    
    # Build progress columns
    progress_columns = [
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description:<20}"),  # Fixed width for alignment
        BarColumn(),
    ]
    
    # Add percentage or count based on whether we have a total
    if total is not None:
        progress_columns.append(TaskProgressColumn())
    else:
        progress_columns.append(MofNCompleteColumn())
    
    # Add speed column
    speed_unit = "op/s" if mode == 'hash' else "files/s"
    progress_columns.append(SpeedColumn(unit=speed_unit))
    
    with Progress(*progress_columns, console=console) as progress:
        task = progress.add_task(task_desc, total=total)
        
        def update_progress():
            progress.advance(task)
            
        result = None
        if mode == 'all':
            # For 'all' mode, just run index pass here
            result = manager.run_index(path, update_progress)
        elif mode == 'index':
             result = manager.run_index(path, update_progress)
        elif mode == 'category':
             result = manager.run_categorize(update_progress)
        elif mode == 'hash':
             result = manager.run_hash(update_progress)
        else:
            result = 0
    
    # Handle result - could be int (old) or dict (new)
    if isinstance(result, dict):
        count = result['count']
        total_bytes = result['bytes']
    else:
        count = result if result else 0
        total_bytes = 0
    
    elapsed = time.time() - start_time
    
    # Build summary message
    summary_parts = [f"✨ Scan Complete! {count} files"]
    if total_bytes > 0:
        summary_parts.append(f"({humanize.naturalsize(total_bytes, binary=True)})")
    summary_parts.append(f"in {humanize.naturaldelta(elapsed)}")
    
    logger.success(" ".join(summary_parts))
    
    # For 'all' mode, continue with categorize and hash passes
    if mode == 'all':
        _run_pipeline(None, False, threads, mode='category')
        _run_pipeline(None, False, threads, mode='hash')

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