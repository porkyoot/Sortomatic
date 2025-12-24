from nicegui import ui
from typing import Optional, Callable
from ...theme import Theme, StatusStyles
from ..atoms.cards import AppCard
from ..atoms.badges import StatusBadge
from ..molecules.scan_controls import ScanControls

class ScanCard(AppCard):
    """
    A comprehensive scan task card showing progress, state, and controls.
    """
    def __init__(self, 
                 name: str, 
                 state: str = "idle", # "running", "idle", "paused", "completed", "error"
                 progress: float = 0.0, # 0.0 to 100.0
                 eta: str = "Calculating...",
                 theme: Theme = None,
                 on_play: Optional[Callable] = None,
                 on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_restart: Optional[Callable] = None,
                 on_fast_mode: Optional[Callable] = None):
        
        super().__init__(variant='glass', padding='p-4')
        self.classes('gap-4')
        
        self.state = state
        self.progress = progress
        self.eta = eta
        self.theme = theme
        
        # Internal state mapping to ScanControls states
        # Map "running" to "running", "idle" to "idle", "paused" to "paused", etc.
        # "error" also maps to specific visual
        control_state = state
        if state == "error":
            control_state = "idle" # Allow restart
        
        with self:
            # Row 1: Title and Controls
            with ui.row().classes('w-full items-center justify-between no-wrap'):
                ui.label(name).classes('text-lg font-black truncate flex-grow')
                
                self.controls = ScanControls(
                    state=control_state,
                    theme=theme,
                    on_play=on_play,
                    on_pause=on_pause,
                    on_resume=on_resume,
                    on_restart=on_restart,
                    on_fast_mode=on_fast_mode
                ).classes('shrink-0')

            # Row 2: Status Details
            with ui.row().classes('w-full items-center gap-3 no-wrap'):
                # Map state to StatusBadge state
                badge_state = "unknown"
                if state == "running": badge_state = "pending"
                if state == "completed": badge_state = "ready"
                if state == "error": badge_state = "error"
                if state == "idle": badge_state = "unknown"
                if state == "paused": badge_state = "pending"
                
                StatusBadge(label="Status", state=badge_state, theme=theme)
                
                # Colored state name
                state_color = StatusStyles.get_color(badge_state, theme)
                ui.label(state.upper()).classes('text-[10px] font-black tracking-widest').style(f'color: {state_color};')
                
                ui.element('div').classes('flex-grow') # Spacer
                
                # Progress and ETA
                with ui.row().classes('items-center gap-4'):
                    # Percent
                    with ui.row().classes('items-center gap-1'):
                        ui.label(f'{progress:.1f}').classes('text-sm font-black')
                        ui.label('%').classes('text-[10px] opacity-50 font-bold')
                    
                    # Vertical divider
                    ui.element('div').classes('w-px h-4 bg-white/10')
                    
                    # ETA
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('schedule', size='16px').classes('opacity-40')
                        ui.label(eta).classes('text-xs font-medium opacity-70')

    def update_progress(self, progress: float, eta: str):
        self.progress = progress
        self.eta = eta
        # Since this is a simple component without data binding on these specific labels yet, 
        # a full refresh might be needed or we could target the labels.
        # For a premium component, we'll usually use ui.label().bind_text_from(...) 
        # but here we'll just clear and re-render or use better binding if we had a state object.
        # Internal refresh for demo purposes:
        self.render()

    def render(self):
        # In a real app we'd use reactive state, but for this component definition
        # we'll assume the parent refreshes or we use binding.
        pass
