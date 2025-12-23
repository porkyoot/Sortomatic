from nicegui import ui
from typing import List, Dict, Optional, Callable
from ...theme import ColorPalette
from ..atoms.icons import StatusIcon
from ..atoms.special.histograms import AppHistogram
from ..atoms.buttons import AppButton

class StatusBar(ui.footer):
    """
    A premium status bar for the bottom of the application.
    Provides system metrics, connectivity status, and global settings.
    """
    def __init__(self, palette: ColorPalette, on_theme_change: Optional[Callable] = None):
        super().__init__()
        # Glassmorphism footer
        self.classes('bg-white/5 backdrop-blur-md border-t border-white/10 px-6 py-2 items-center justify-between no-wrap gap-4')
        self.palette = palette
        self.on_theme_change = on_theme_change
        
        with self:
            # 1. Left Section: Performance Metrics
            with ui.row().classes('items-center gap-6'):
                with ui.row().classes('items-center gap-2'):
                    ui.label("CPU").classes('text-[10px] font-bold opacity-40 uppercase tracking-widest')
                    # We'll need to update these values periodically via a timer in the main app
                    self.cpu_container = ui.row()
                    with self.cpu_container:
                        AppHistogram([0.1]*20, color=palette.green, height="16px", bar_width="2px")

                with ui.row().classes('items-center gap-2'):
                    ui.label("RAM").classes('text-[10px] font-bold opacity-40 uppercase tracking-widest')
                    self.ram_container = ui.row()
                    with self.ram_container:
                        AppHistogram([0.2]*20, color=palette.blue, height="16px", bar_width="2px")

            # 2. Middle Section: Connectivity & Status
            with ui.row().classes('items-center gap-4 bg-black/20 px-4 py-1 rounded-full border border-white/5'):
                # Database Status
                with ui.row().classes('items-center gap-1.5'):
                    StatusIcon("ready", palette, size="14px", tooltip="Database Connected")
                    ui.label("DB").classes('text-[10px] font-bold opacity-60 uppercase')
                
                ui.element('div').classes('w-px h-3 bg-white/10')

                # Engine Status
                with ui.row().classes('items-center gap-1.5'):
                    StatusIcon("pending", palette, size="14px", tooltip="Engine Idle", animate=True)
                    ui.label("ENGINE").classes('text-[10px] font-bold opacity-60 uppercase')

            # 3. Right Section: Global Controls
            with ui.row().classes('items-center gap-4'):
                from .theme_selectors import ThemeSelector
                ThemeSelector(is_dark=True, on_change=self.on_theme_change) 

                ui.element('div').classes('w-px h-4 bg-white/10')

                # Role/Mode Select
                ui.select(
                    options=["Full Control", "Read Only", "Expert"],
                    value="Full Control"
                ).props('dense borderless dark flat hide-underline').classes('text-[10px] uppercase font-bold tracking-widest opacity-60 w-32')

                # Refresh
                AppButton(icon="refresh", variant="secondary", shape="circle").props('flat dense size=sm')

    def update_metrics(self, cpu_history: List[float], ram_history: List[float]):
        """Update histograms with fresh data."""
        # Check if client is still connected before updating
        if not self.client or not self.client.has_socket_connection:
            return
            
        try:
            self.cpu_container.clear()
            with self.cpu_container:
                AppHistogram(cpu_history, color=self.palette.green, height="16px", bar_width="2px")
                
            self.ram_container.clear()
            with self.ram_container:
                AppHistogram(ram_history, color=self.palette.blue, height="16px", bar_width="2px")
        except Exception:
            # Silently ignore updates if the client is no longer available
            pass
