from nicegui import ui
from typing import List, Dict, Optional, Callable, Union
from ...theme import Theme, StatusStyles
from ..atoms.buttons import AppButton
from ..atoms.progress_bar import AppProgressBar

class MenuStep(ui.column):
    """
    A single step in a menu workflow.
    Contains a button with status-based styling and optional progress bars.
    """
    def __init__(self, 
                 label: str, 
                 icon: str,
                 state: str = "inactive", # unavailable, available, inactive
                 theme: Theme = None,
                 on_click: Optional[Callable] = None,
                 progress_values: List[float] = []):
        super().__init__()
        self.classes('items-stretch gap-1.5 min-w-[120px]')
        
        self.state = state
        self.theme = theme
        self.progress_values = progress_values
        
        # Mapping my 3 states to StatusStyles and Button variants
        # available -> primary/ready (Green)
        # unavailable -> error (Red)
        # inactive -> grey (Unknown)
        
        variant = "secondary"
        btn_icon = icon
        btn_color = "var(--c-primary)"
        disabled = False
        
        if state == "available":
            btn_color = theme.colors.success if theme else "var(--c-success)"
            variant = "primary"
        elif state == "unavailable":
            btn_color = theme.colors.error if theme else "var(--c-error)"
            disabled = True
            btn_icon = "block"
        elif state == "inactive":
            btn_color = theme.colors.text_subtle if theme else "var(--c-text-subtle)"
            variant = "secondary"
            
        with self:
            self.button = AppButton(
                label=label,
                icon=btn_icon,
                variant=variant,
                on_click=on_click,
                shape="rectangle"
            ).classes('w-full')
            
            # Apply color override for states if needed
            self.button.style(f'--c-primary: {btn_color};')
            if disabled:
                self.button.props('disabled')
                self.button.classes('opacity-50 pointer-events-none grayscale')

            # Progress bars row
            if progress_values:
                with ui.row().classes('w-full gap-1 px-1'):
                    for val in progress_values:
                        AppProgressBar(
                            value=val, 
                            color=btn_color, 
                            size='4px', 
                            shape='pill'
                        ).classes('grow')

class WorkflowMenu(ui.row):
    """
    A row of MenuSteps representing a sequence of actions or a workflow.
    """
    def __init__(self):
        super().__init__()
        self.classes('w-full items-start gap-4 no-wrap overflow-x-auto py-2')
        
    def add_step(self, **kwargs):
        with self:
            return MenuStep(**kwargs)
