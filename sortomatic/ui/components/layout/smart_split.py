from nicegui import ui
from typing import Callable

def SmartSplitter(
    left_factory: Callable[[], None], 
    right_factory: Callable[[], None],
    initial_split: int = 30,
    separator: bool = True
):
    """
    Responsive layout component that switches between column (mobile) and splitter (desktop).
    """
    with ui.element('div').classes('w-full h-full') as container:
        # Mobile: Column layout (hidden on large screens)
        with ui.column().classes('w-full lg:hidden gap-0'):
            left_factory()
            if separator:
                ui.separator().classes('my-2')
            right_factory()

        # Desktop: Splitter layout (hidden on small screens)
        with ui.splitter(value=initial_split).classes('w-full h-full hidden lg:flex') as s:
            with s.before:
                left_factory()
            with s.after:
                right_factory()
                
    return container