from nicegui import ui
from typing import Optional, Callable
from ...theme import Theme, StatusStyles
from ..atoms.cards import AppCard
from ..atoms.badges import StatusBadge
from ..molecules.scan_controls import ScanControls

def ScanCard(
    name: str, 
    state: str = "idle", # "running", "idle", "paused", "completed", "error"
    progress: float = 0.0, # 0.0 to 100.0
    eta: str = "Calculating...",
    theme: Theme = None,
    on_play: Optional[Callable] = None,
    on_pause: Optional[Callable] = None,
    on_resume: Optional[Callable] = None,
    on_restart: Optional[Callable] = None,
    on_fast_mode: Optional[Callable] = None
):
    """
    A comprehensive scan task card showing progress, state, and controls.
    """
    # Internal variables for state (if needed for refresh)
    card_state = {
        'state': state,
        'progress': progress,
        'eta': eta
    }
    
    # Internal render function
    def _render_content():
        card.clear()
        
        # Internal state mapping to ScanControls states
        control_state = card_state['state']
        if card_state['state'] == "error":
            control_state = "idle" # Allow restart
            
        with card:
            # Row 1: Title and Controls
            with ui.row().classes('w-full items-center justify-between no-wrap'):
                ui.label(name).classes('s-scan-card__title')
                
                ScanControls(
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
                s = card_state['state']
                if s == "running": badge_state = "pending"
                if s == "completed": badge_state = "ready"
                if s == "error": badge_state = "error"
                if s == "idle": badge_state = "unknown"
                if s == "paused": badge_state = "pending"
                
                StatusBadge(label="Status", state=badge_state, theme=theme)
                
                # Colored state name
                state_color = StatusStyles.get_color(badge_state, theme)
                ui.label(s.upper()).classes('s-scan-card__state').style(f'color: {state_color};')
                
                ui.element('div').classes('flex-grow') # Spacer
                
                # Progress and ETA
                with ui.row().classes('items-center gap-4'):
                    # Percent
                    with ui.row().classes('items-center gap-1'):
                        ui.label(f"{card_state['progress']:.1f}").classes('s-scan-card__percent')
                        ui.label('%').classes('s-scan-card__percent-sub')
                    
                    # Vertical divider
                    ui.element('div').classes('s-separator-vertical')
                    
                    # ETA
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('schedule', size='16px').classes('opacity-40')
                        ui.label(card_state['eta']).classes('s-scan-card__eta')

    def update_progress(new_progress: float, new_eta: str):
        card_state['progress'] = new_progress
        card_state['eta'] = new_eta
        _render_content()

    def update_state(new_state: str):
        card_state['state'] = new_state
        _render_content()

    card = AppCard(variant='glass')
    card.classes('s-scan-card')
    card.update_progress = update_progress
    card.update_state = update_state
    
    _render_content()
    return card
