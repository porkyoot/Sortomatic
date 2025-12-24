from nicegui import ui
from typing import List, Dict, Optional, Callable
from ...theme import Theme


def StatusBar(theme: Theme, on_theme_change: Optional[Callable] = None):
    """
    A premium status bar for the top of the application.
    Provides system metrics, connectivity status, and global settings.
    """
    with ui.header() as header:
        header.classes('s-status-bar')
        header.theme = theme
        header.on_theme_change = on_theme_change
        
        # Internal State
        header.backend_state = "ready"
        header.db_state = "ready"
        header.scan_state = "idle"
        
        # Icon definitions
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
        SCAN_ICONS = {
            'ready': 'mdi-progress-check',
            'error': 'mdi-progress-alert',
            'pending': 'mdi-progress-helper',
            'default': 'mdi-progress-clock'
        }

        # 1. Left Section: Logo / App Name
        with ui.row().classes('items-center gap-2'):
            ui.label('Sortomatic').classes('s-text-h1 text-sm tracking-widest').tag = 'h1'

        # 2. Middle Section: Connectivity & Status (Unified with Metrics)
        header.status_container = ui.row().classes('absolute-center gap-4')
        
        # Initialize Pill
        from ..atoms.badges import StatusBadge
        from ..atoms.special.histograms import AppHistogram
        
        with header.status_container:
            # -- Pill 1: Connectivity Status --
            with ui.row().classes('s-status-badge-row'):
                header.web_badge_container = ui.row()
                ui.element('div').classes('s-separator-vertical')
                header.scan_badge_container = ui.row()
                ui.element('div').classes('s-separator-vertical')
                header.db_badge_container = ui.row()
            
            # -- Pill 2: System Metrics --
            with ui.row().classes('s-status-badge-row'):
                header.cpu_hist = AppHistogram([0]*6, label='CPU', color='var(--c-primary)', icon='mdi-cpu-64-bit', transparent=True, height='16px', bar_width='2px', max_bars=6)
                ui.element('div').classes('s-separator-vertical')
                header.gpu_hist = AppHistogram([0]*6, label='GPU', color='var(--c-success)', icon='mdi-expansion-card-variant', transparent=True, height='16px', bar_width='2px', max_bars=6)
                ui.element('div').classes('s-separator-vertical')
                header.ram_hist = AppHistogram([0]*6, label='RAM', color='var(--c-warning)', icon='mdi-memory', transparent=True, height='16px', bar_width='2px', max_bars=6)
                ui.element('div').classes('s-separator-vertical')
                header.disk_hist = AppHistogram([0]*6, label='Disk', color='var(--c-error)', icon='mdi-harddisk', transparent=True, height='16px', bar_width='2px', max_bars=6)

        # 3. Right Section: Global Controls
        with ui.row().classes('items-center gap-4'):
            from .theme_selectors import ThemeSelector
            ThemeSelector(is_dark=True, on_change=header.on_theme_change)

    def _update_badges():
        """Update only the status badge contents with descriptive tooltips."""
        from ..atoms.badges import StatusBadge
        
        # Web
        header.web_badge_container.clear()
        with header.web_badge_container:
            web_tooltip = f"Backend Connection: {header.backend_state.capitalize()}"
            StatusBadge('Web', header.backend_state, header.theme, icon=WEB_ICONS, variant='simple', interactive=False, tooltip=web_tooltip)
            
        # Scan
        header.scan_badge_container.clear()
        with header.scan_badge_container:
            scan_tooltip = f"System Scan: {header.scan_state.capitalize()}"
            StatusBadge('Scan', header.scan_state, header.theme, icon=SCAN_ICONS, rotate=header.scan_state == 'pending', variant='simple', interactive=False, tooltip=scan_tooltip)
            
        # DB
        header.db_badge_container.clear()
        with header.db_badge_container:
            db_tooltip = f"Database Status: {header.db_state.capitalize()}"
            StatusBadge('DB', header.db_state, header.theme, icon=DB_ICONS, variant='simple', interactive=False, tooltip=db_tooltip)

    def refresh_status(backend_state: str, db_state: str, scan_state: str):
        """Update system status badges."""
        if (backend_state, db_state, scan_state) == (header.backend_state, header.db_state, header.scan_state):
            return # No change
            
        header.backend_state = backend_state
        header.db_state = db_state
        header.scan_state = scan_state
        _update_badges()

    def update_metrics(cpu_history: List[float], 
                       gpu_history: List[float],
                       ram_history: List[float],
                       disk_history: List[float]):
        """Update histogram data without re-creating elements."""
        header.cpu_hist.update_data(cpu_history)
        header.gpu_hist.update_data(gpu_history)
        header.ram_hist.update_data(ram_history)
        header.disk_hist.update_data(disk_history)

    # Attach methods
    header.refresh_status = refresh_status
    header.update_metrics = update_metrics
    
    # Initial render
    _update_badges()
    
    return header
