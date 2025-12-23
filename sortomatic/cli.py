import typer
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


# Default folder for local scan data
DATA_FOLDER_NAME = ".sortomatic"
DB_NAME = "sortomatic.db"

def handle_exception(exc_type, exc_value, exc_traceback):
    """Catch uncaught exceptions and exit gracefully."""
    if issubclass(exc_type, KeyboardInterrupt):
        database.close_db()
        logger.info(f"\n{Strings.USER_ABORT}")
        sys.exit(0)

    logger.fatal(f"Uncaught exception: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
    database.close_db()
    sys.exit(1)

sys.excepthook = handle_exception
atexit.register(database.close_db)

def ensure_environment(base_path: Path):
    """Ensure data directories exist in the target path."""
    data_dir = base_path / DATA_FOLDER_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / DB_NAME

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show DEBUG logs"),
    threads: Optional[int] = typer.Option(None, "--threads", "-j", help="Max threads to use"),
    reset: bool = typer.Option(False, "--reset", help="Reset database before operation")
):
    """
    Global entry point callback.
    """
    if threads:
        settings.max_workers = threads
    if reset:
        settings.reset_db = True
        
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(log_level)
    
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# --- SCAN GROUP ---
scan_app = typer.Typer(help=Strings.SCAN_DOC, invoke_without_command=True)
app.add_typer(scan_app, name="scan")

@scan_app.callback(invoke_without_command=True)
def scan_callback(
    ctx: typer.Context,
):
    """Run full scan via subcommands."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

@scan_app.command("all", help=Strings.SCAN_ALL_DOC)
def scan_all(
    path: str = typer.Argument(..., help=Strings.SCAN_PATH_HELP),
):
    _run_pipeline(path, mode="all")

@scan_app.command("index", help=Strings.SCAN_INDEX_DOC)
def scan_index(
    path: str = typer.Argument(..., help=Strings.SCAN_PATH_HELP),
):
    _run_pipeline(path, mode="index")

@scan_app.command("category", help=Strings.SCAN_CAT_DOC)
def scan_categorize():
    _run_pipeline(None, mode="category")

@scan_app.command("hash", help=Strings.SCAN_HASH_DOC)
def scan_hash():
    _run_pipeline(None, mode="hash")

def _run_pipeline(path: Optional[str], mode: str):
    """Execute scan pipeline for specified mode."""
    import time
    import humanize
    
    reset = settings.reset_db
    
    start_time = time.time()
    
    # If no path provided (e.g. for subcommands like 'hash'), use CWD
    base_path = Path(path) if path else Path.cwd()
    db_path = ensure_environment(base_path)
    
    database.init_db(str(db_path))
    
    if reset and path:
        typer.confirm(Strings.WIPE_CONFIRM, abort=True)
        database.db.drop_tables([database.FileIndex])
        database.db.create_tables([database.FileIndex])
        logger.warning(Strings.WIPE_SUCCESS)
    elif mode in ['all', 'index'] and not reset:
        existing_count = database.FileIndex.select().count()
        if existing_count > 0:
            uncategorized = database.FileIndex.select().where(database.FileIndex.category.is_null()).count()
            unhashed = database.FileIndex.select().where(
                (database.FileIndex.full_hash.is_null()) & 
                (database.FileIndex.entry_type == 'file')
            ).count()
            
            if uncategorized > 0 or unhashed > 0:
                logger.info(f"Resuming scan ({existing_count} files already indexed)")

    manager = PipelineManager()
    from .utils.progress import create_scan_progress
    
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
    
    with create_scan_progress(console, mode, total) as progress:
        task = progress.add_task(task_desc, total=total)
        
        def update_progress():
            progress.advance(task)
        
        result = None
        try:
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
            
            # For indeterminate progress, update total at end to fill the bar
            if total is None and result:
                count = result['count'] if isinstance(result, dict) else result
                # This makes the bar fill to 100% and shows "X/X"
                progress.update(task, total=count, completed=count)
                # Force a refresh to show the completion
                progress.refresh()
                
        except KeyboardInterrupt:
            # Graceful but immediate interruption
            from .core.pipeline.manager import _shutdown_executor
            _shutdown_executor(wait=False)
            database.close_db()
            logger.warning(Strings.SCAN_INTERRUPTED)
            # os._exit bypasses the 'Join threads' stall in Python's atexit
            import os as native_os
            native_os._exit(130)
        except Exception as e:
            # Ungraceful error
            logger.critical(Strings.SCAN_ERROR)
            logger.critical(f"Error details: {str(e)}")
            raise typer.Exit(1)
    
    # Only show success if we didn't exit early
    if result is None:
        return
    
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
        _run_pipeline(None, mode='category')
        _run_pipeline(None, mode='hash')

@app.command(help=Strings.STATS_DOC)
def stats(path: Optional[str] = typer.Argument(None)):
    """
    Show insights about your files.
    """
    base_path = Path(path) if path else Path.cwd()
    db_path = base_path / DATA_FOLDER_NAME / DB_NAME
    
    if not db_path.exists():
        logger.error(f"No database found at {db_path}")
        raise typer.Exit(1)
        
    database.init_db(str(db_path))
    
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

@app.command(help="Wipe the local database.")
def reset(path: Optional[str] = typer.Argument(None)):
    """
    Wipe the database.
    """
    base_path = Path(path) if path else Path.cwd()
    db_path = ensure_environment(base_path)
    
    database.init_db(str(db_path))
    
    typer.confirm(Strings.WIPE_CONFIRM, abort=True)
    database.db.drop_tables([database.FileIndex])
    database.db.create_tables([database.FileIndex])
    logger.warning(Strings.WIPE_SUCCESS)

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        logger.info(f"\n{Strings.USER_ABORT}")
        sys.exit(0)

@app.command()
def gui(
    port: int = typer.Option(None, help=f"Port to run the GUI on (default: {settings.gui_port})"),
    theme: str = typer.Option(None, help=f"Theme name (default: {settings.gui_theme})"),
    dark: bool = typer.Option(None, "--dark/--light", help=f"Enable/Disable dark mode (default: {settings.gui_dark_mode})")
):
    """Launch the Web Interface."""
    from .ui.web.main import start_app
    
    final_port = port if port is not None else settings.gui_port
    final_theme = theme if theme is not None else settings.gui_theme
    final_dark = dark if dark is not None else settings.gui_dark_mode
    
    start_app(final_port, final_theme, final_dark)