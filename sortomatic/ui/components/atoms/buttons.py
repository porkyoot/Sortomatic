from nicegui import ui
from typing import Optional, Callable

def AppButton(
    label: str = "",
    icon: Optional[str] = None,
    on_click: Optional[Callable] = None,
    variant: str = 'primary', # primary, secondary, ghost
    shape: str = 'default',   # default, pill, square, circle
    size: str = 'md',         # xs, sm, md, lg
    tooltip: Optional[str] = None,
):
    """
    Semantic Wrapper.
    No hardcoded styles here. Only semantic class names.
    """
    
    # 1. Base Class
    css_classes = ["s-btn"]
    
    # 2. Semantic Modifiers (BEM style naming convention)
    css_classes.append(f"s-btn--{variant}")
    
    if shape != 'default':
        css_classes.append(f"s-shape--{shape}")
        
    if size != 'md':
        css_classes.append(f"s-btn--{size}")

    # 3. Render
    # We use props('unelevated no-caps') to reset Quasar's defaults
    btn = ui.button(label, icon=icon, on_click=on_click) \
             .props('unelevated no-caps') \
             .classes(" ".join(css_classes))
             
    if tooltip:
        btn.tooltip(tooltip)
        
    return btn