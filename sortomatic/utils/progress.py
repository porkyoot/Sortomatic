"""Progress bar UI components for CLI."""
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    ProgressColumn
)
from rich.text import Text
from rich.table import Column


class SpeedColumn(ProgressColumn):
    """Custom progress column for displaying processing speed."""
    
    def __init__(self, unit="files/s"):
        self.unit = unit
        super().__init__(table_column=Column(no_wrap=True, justify="right"))
        
    def render(self, task):
        speed = task.speed
        if speed is None or speed < 0.1:
            return Text("--", style="dim cyan")
        return Text(f"{speed:.1f} {self.unit}", style="cyan")


def create_scan_progress(console, mode: str, total=None):
    """Create a Rich Progress bar configured for scanning.
    
    Args:
        console: Rich console instance
        mode: Scan mode ('index', 'category', 'hash', 'all')
        total: Total items if known (for determinate progress)
        
    Returns:
        Configured Progress instance
    """
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
    
    # Add speed column with appropriate unit
    speed_unit = "op/s" if mode == 'hash' else "files/s"
    progress_columns.append(SpeedColumn(unit=speed_unit))
    
    return Progress(*progress_columns, console=console)
