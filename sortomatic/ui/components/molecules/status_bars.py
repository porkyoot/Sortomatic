from nicegui import ui
from typing import List, Dict, Optional, Callable
from ...theme import Theme
from ..atoms.icons import StatusIcon
from ..atoms.special.histograms import AppHistogram
from ..atoms.buttons import AppButton

class StatusBar(ui.header):
    """
    A premium status bar for the top of the application.
    Provides system metrics, connectivity status, and global settings.
    """
    def __init__(self, theme: Theme, on_theme_change: Optional[Callable] = None):
        super().__init__()
        # Glassmorphism header
        self.classes('backdrop-blur-md border-b px-6 py-2 items-center justify-between no-wrap gap-4 bg-app-surface')
        self.style('border-color: var(--app-text-sec);')
        self.theme = theme
        self.on_theme_change = on_theme_change
        
        with self:
            # 1. Left Section: Performance Metrics
            # 1. Left Section: Performance Metrics
            with ui.row().classes('items-center gap-2'):
                # CPU (Blue)
                self.cpu_container = ui.row()
                with self.cpu_container:
                    AppHistogram([0.1]*20, color=theme.colors.blue, height="16px", bar_width="2px", max_bars=10, icon="mdi-cpu-64-bit", label="CPU")
                
                # GPU (Green)
                self.gpu_container = ui.row()
                with self.gpu_container:
                    AppHistogram([0.1]*20, color=theme.colors.green, height="16px", bar_width="2px", max_bars=10, icon="mdi-expansion-card-variant", label="GPU")

                # RAM (Yellow)
                self.ram_container = ui.row()
                with self.ram_container:
                    AppHistogram([0.2]*20, color=theme.colors.yellow, height="16px", bar_width="2px", max_bars=10, icon="mdi-memory", label="RAM")

                # Disk IO (Red)
                self.disk_container = ui.row()
                with self.disk_container:
                    AppHistogram([0.1]*20, color=theme.colors.red, height="16px", bar_width="2px", max_bars=10, icon="mdi-harddisk", label="Disk IO")

            # 2. Middle Section: Connectivity & Status
            # 2. Middle Section: Connectivity & Status
            self.status_container = ui.row()
            self._render_badges()

            # 3. Right Section: Global Controls
            with ui.row().classes('items-center gap-4'):
                from .theme_selectors import ThemeSelector
                ThemeSelector(is_dark=True, on_change=self.on_theme_change)

    def _render_badges(self, backend="ready", db="ready", scan="idle"):
        """Render the status badges row configuration."""
        
        # Icon definitions per status type
        WEB_ICONS = {
            'ready': 'mdi-cloud-check',
            'error': 'mdi-cloud-alert',
            'pending': 'mdi-cloud-sync',
            'default': 'mdi-cloud'
        }
        
        DB_ICONS = {
            'ready': 'mdi-database-check',
            'error': 'mdi-database-alert',
            'pending': 'mdi-database-sync',
            'default': 'mdi-database'
        }
        
        # For Scan, user requested "radar", so we stick to that base,
        # but we can add variants if available or desired.
        # MDI doesn't have mdi-radar-check etc. easily, so we fallback to base.
        SCAN_ICONS = {
            'ready': 'mdi-progress-check',
            'error': 'mdi-progress-alert',
            'pending': 'mdi-progress-helper',
            'default': 'mdi-progress-clock'
        }

        self.status_container.clear()
        with self.status_container:
            from .badges import StatusBadgeRow
            StatusBadgeRow([
                {'label': 'Web', 'state': backend, 'icon': WEB_ICONS},
                {'label': 'Scan', 'state': scan, 'icon': SCAN_ICONS, 'rotate': scan == 'pending'},
                {'label': 'DB', 'state': db, 'icon': DB_ICONS}
            ], self.theme)

    def refresh_status(self, backend_state: str, db_state: str, scan_state: str):
        """Update the status badges."""
        if not self.client or not self.client.has_socket_connection:
            return
            
        try:
            self._render_badges(backend_state, db_state, scan_state)
        except Exception:
            pass

    def update_metrics(self, 
                       cpu_history: List[float], 
                       gpu_history: List[float],
                       ram_history: List[float],
                       disk_history: List[float]):
        """Update histograms with fresh data."""
        # Check if client is still connected before updating
        if not self.client or not self.client.has_socket_connection:
            return
            
        try:
            self.cpu_container.clear()
            with self.cpu_container:
                AppHistogram(cpu_history, color=self.theme.colors.blue, height="16px", bar_width="2px", max_bars=10, icon="mdi-cpu-64-bit", label="CPU")
            
            self.gpu_container.clear()
            with self.gpu_container:
                AppHistogram(gpu_history, color=self.theme.colors.green, height="16px", bar_width="2px", max_bars=10, icon="mdi-expansion-card-variant", label="GPU")
                
            self.ram_container.clear()
            with self.ram_container:
                AppHistogram(ram_history, color=self.theme.colors.yellow, height="16px", bar_width="2px", max_bars=10, icon="mdi-memory", label="RAM")

            self.disk_container.clear()
            with self.disk_container:
                AppHistogram(disk_history, color=self.theme.colors.red, height="16px", bar_width="2px", max_bars=10, icon="mdi-harddisk", label="Disk IO")
        except Exception:
            # Silently ignore updates if the client is no longer available
            pass
