from nicegui import ui
from typing import Optional

def AppIcon(
    name: str,
    color: str = 'var(--c-text-main)',
    size: str = 'sm', # xs, sm, md, lg, xl OR explicit size like '1.5em'
    tooltip: Optional[str] = None,
    classes: str = ""
):
    """
    A unified icon component with support for colors, tooltips, and standard sizes.
    
    Args:
        name: Material icon name
        color: CSS color value
        size: Quasar size (xs, sm, md, lg, xl) or explicit size
        tooltip: Optional tooltip text
        classes: Additional CSS classes to apply
    """
    icon = ui.icon(name).style(f'color: {color};').props(f'size={size}')
    
    if classes:
        icon.classes(classes)
    
    if tooltip:
        icon.tooltip(tooltip)
        
    return icon

def StatusIcon(
    state: str,
    theme: 'Theme',
    size: str = 'sm',
    tooltip: Optional[str] = None,
    animate: bool = False,
    classes: str = ""
):
    """
    A specialized icon for displaying statuses with automatic coloring,
    icon selection, and optional animations.
    
    Args:
        state: Status state name
        theme: Theme instance for theming
        size: Quasar size (xs, sm, md, lg, xl) or explicit size
        tooltip: Optional tooltip text
        animate: Enable rotation animation for pending states
        classes: Additional CSS classes to apply
    """
    from ...theme import StatusStyles
    
    name = StatusStyles.get_icon(state)
    color = StatusStyles.get_color(state, theme)
    
    # Combine animation class with custom classes
    combined_classes = classes
    if animate and state.lower() == StatusStyles.PENDING:
        combined_classes = f'rotate-animation {classes}'
    
    icon = AppIcon(name, color=color, size=size, tooltip=tooltip, classes=combined_classes)
        
    return icon

