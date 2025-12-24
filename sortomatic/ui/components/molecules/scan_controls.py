from nicegui import ui
from typing import Optional, Callable
from ...theme import Theme
from ..atoms.buttons import AppButton
from ..atoms.inputs.toggles import AppToggle

def ScanControls(
    state: str = "idle", 
    theme: Theme = None,
    on_play: Optional[Callable] = None,
    on_pause: Optional[Callable] = None,
    on_resume: Optional[Callable] = None,
    on_restart: Optional[Callable] = None,
    on_fast_mode: Optional[Callable] = None
):
    """
    A context-aware scan control component.
    Switches buttons based on scan state and includes a fast-mode toggle.
    """
    # State constants
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

    container = ui.row().classes('s-control-group')
    container.current_state = state

    def set_state(new_state: str):
        container.current_state = new_state
        _render()

    def _render():
        container.clear()
        with container:
            # 1. State-based Buttons
            with ui.row().classes('items-center gap-2'):
                if container.current_state == IDLE:
                    AppButton(
                        label="Start Scan",
                        icon="play_arrow",
                        variant="primary",
                        on_click=on_play
                    ).style(f'--c-primary: {theme.colors.success if theme else "var(--c-success)"}')
                
                elif container.current_state == RUNNING:
                    AppButton(
                        label="Pause",
                        icon="pause",
                        variant="primary",
                        on_click=on_pause
                    ).style(f'--c-primary: {theme.colors.warning if theme else "var(--c-warning)"}')
                
                elif container.current_state == PAUSED:
                    AppButton(
                        label="Resume",
                        icon="play_arrow",
                        variant="primary",
                        on_click=on_resume
                    ).style(f'--c-primary: {theme.colors.blue if theme else "var(--c-primary)"}')
                    
                    AppButton(
                        label="Restart",
                        icon="refresh",
                        variant="primary",
                        on_click=on_restart
                    ).style(f'--c-primary: {theme.colors.error if theme else "var(--c-error)"}')

                elif container.current_state == COMPLETED:
                    AppButton(
                        label="Restart Scan",
                        icon="refresh",
                        variant="primary",
                        on_click=on_restart
                    ).style(f'--c-primary: {theme.colors.error if theme else "var(--c-error)"}')

            # 2. Separator
            ui.element('div').classes('s-separator-vertical')

            # 3. Fast Mode Toggle
            AppToggle(
                label="Fast Mode",
                icon="bolt",
                tooltip="Enable high-concurrency partial scanning",
                on_change=on_fast_mode
            )

    container.set_state = set_state
    _render()
    return container
