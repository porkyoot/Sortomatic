from nicegui import ui
from typing import List, Dict, Any, Optional, Callable, Union

def AppSelect(
    options: Union[List[str], Dict[Any, str]],
    label: Optional[str] = None,
    value: Any = None,
    on_change: Optional[Callable] = None,
    multiple: bool = False,
    use_chips: bool = False,  # Default to False to prevent removable chips
    clearable: bool = True,
    classes: str = "",
    props: str = ""
):
    """
    A premium themed select component. 
    Supports multiple selection with chips and consistent rounding.
    
    Args:
        options: List of options or dict mapping values to labels
        label: Input label
        value: Initial value
        on_change: Callback when value changes
        multiple: Allow multiple selection
        use_chips: Show selected items as chips (when multiple=True)
        clearable: Show clear button
        classes: Additional CSS classes to apply
        props: Additional Quasar props to apply
    """
    sel = ui.select(
        options=options, 
        label=label, 
        value=value, 
        on_change=on_change
    ).props(
        f'outlined dense hide-bottom-space rounded-app '
        f'{"multiple" if multiple else ""} {"use-chips" if use_chips else ""} '
        f'{props}'
    ).classes(f'w-full transition-all {classes}').style(
        'color: var(--app-text); background-color: var(--app-bg);'
    )
    
    # Only add clearable prop if explicitly requested
    if clearable:
        sel.props('clearable')

    # Apply theme colors to the popup menu
    sel.props('popup-content-class="rounded-app shadow-lg border border-white/10"')
    sel.props('popup-content-style="background-color: var(--app-bg); color: var(--app-text);"')
    
    return sel


