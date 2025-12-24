from nicegui import ui
from typing import Optional, Callable
from ...theme import Theme
from ..atoms.buttons import AppButton
from ..atoms.inputs.toggles import AppToggle

class ScanControls(ui.row):
    """
    A context-aware scan control component.
    Switches buttons based on scan state and includes a fast-mode toggle.
    """
    
    # State constants
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

    def __init__(self, 
                 state: str = "idle", 
                 theme: Theme = None,
                 on_play: Optional[Callable] = None,
                 on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_restart: Optional[Callable] = None,
                 on_fast_mode: Optional[Callable] = None):
        super().__init__()
        self.classes('items-center gap-4 py-2 px-4 rounded-app bg-white/5 border border-white/5')
        
        self.state = state
        self.theme = theme
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_restart = on_restart
        self.on_fast_mode = on_fast_mode
        
        self.render()

    def set_state(self, new_state: str):
        self.state = new_state
        self.render()

    def render(self):
        self.clear()
        with self:
            # 1. State-based Buttons
            with ui.row().classes('items-center gap-2'):
                if self.state == self.IDLE:
                    AppButton(
                        label="Start Scan",
                        icon="play_arrow",
                        variant="primary",
                        on_click=self.on_play
                    ).style(f'--c-primary: {self.theme.colors.success if self.theme else "var(--c-success)"}')
                
                elif self.state == self.RUNNING:
                    AppButton(
                        label="Pause",
                        icon="pause",
                        variant="primary",
                        on_click=self.on_pause
                    ).style(f'--c-primary: {self.theme.colors.warning if self.theme else "var(--c-warning)"}')
                
                elif self.state == self.PAUSED:
                    AppButton(
                        label="Resume",
                        icon="play_arrow",
                        variant="primary",
                        on_click=self.on_resume
                    ).style(f'--c-primary: {self.theme.colors.blue if self.theme else "var(--c-primary)"}')
                    
                    AppButton(
                        label="Restart",
                        icon="refresh",
                        variant="primary",
                        on_click=self.on_restart
                    ).style(f'--c-primary: {self.theme.colors.error if self.theme else "var(--c-error)"}')

                elif self.state == self.COMPLETED:
                    AppButton(
                        label="Restart Scan",
                        icon="refresh",
                        variant="primary",
                        on_click=self.on_restart
                    ).style(f'--c-primary: {self.theme.colors.error if self.theme else "var(--c-error)"}')

            # 2. Separator
            ui.element('div').classes('w-px h-6 bg-white/10 mx-2')

            # 3. Fast Mode Toggle
            AppToggle(
                label="Fast Mode",
                icon="bolt",
                tooltip="Enable high-concurrency partial scanning",
                on_change=self.on_fast_mode
            )
