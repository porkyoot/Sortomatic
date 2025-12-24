from nicegui import ui
from typing import Callable

def SmartSplitter(
    left_factory: Callable[[], None], 
    right_factory: Callable[[], None],
    initial_split: int = 30,
    separator: bool = True
):
    """
    Responsive layout component that switches between column (mobile) and grid (desktop).
    Uses CSS Grid for robust height matching.
    """
    with ui.element('div').classes('s-smart-splitter') as container:
        # Left Pane
        with ui.element('div').classes('s-smart-splitter__pane s-smart-splitter__pane-left'):
            left_factory()
            
        # Separator (Visual only, handled by grid gap or specific element)
        ui.element('div').classes('s-smart-splitter__separator')
        
        # Right Pane
        with ui.element('div').classes('s-smart-splitter__pane s-smart-splitter__pane-right'):
            right_factory()
                
    return container