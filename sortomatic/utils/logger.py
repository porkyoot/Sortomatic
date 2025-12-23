import logging
import sys
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# 1. Define Custom Levels
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

logging.Logger.success = success

# 2. Define Custom Theme
custom_theme = Theme({
    "logging.level.debug": "cyan",
    "logging.level.info": "blue",
    "logging.level.success": "bold green",
    "logging.level.warning": "yellow",
    "logging.level.error": "bold red",
    "logging.level.fatal": "bold white on red",
})

# 3. Create a Console that writes to stderr (standard for logs)
# We keep soft_wrap=False to allow nice formatting, but you can change it.
console = Console(theme=custom_theme, stderr=True)

class AtomicRichHandler(RichHandler):
    """
    A RichHandler that flushes the stream immediately after every log.
    Crucial for avoiding lost logs during crashes or race conditions.
    """
    def emit(self, record):
        try:
            super().emit(record)
            # Force the underlying stream (usually stderr) to write to OS immediately
            self.console.file.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def setup_logger(level: str = "INFO"):
    """
    Configures the global logger with atomic flushing.
    """
    # Use our custom Atomic handler
    rich_handler = AtomicRichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True
    )
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler],
        force=True # Ensures we overwrite any previous config
    )

    # Quiet down noisy 3rd party libraries
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("peewee").setLevel(logging.INFO)

logger = logging.getLogger("sortomatic")