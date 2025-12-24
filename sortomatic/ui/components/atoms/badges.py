from nicegui import ui
from typing import Optional, Union, Dict
from .icons import AppIcon
from ...theme import CategoryStyles, Theme, StatusStyles

def AppBadge(
    label: str,
    value: Optional[str] = None,
    icon: Optional[str] = None,
    color: str = 'var(--c-primary)',
    text_color: str = 'var(--c-text-main)',
    variant: str = 'solid', # solid, glass, subtle
    on_click: Optional[callable] = None,
    interactive: bool = False,
    disabled: bool = False,
    icon_classes: str = ""
):
    """
    A styled badge for displaying statuses, categories, or counts.
    Supports solid, glass (translucent), and subtle (no background) variants.
    """
    classes = 'items-center gap-1 px-2 py-0.5 rounded-app transition-all'
    if (interactive or on_click) and not disabled:
        classes += ' cursor-pointer hover:scale-105 active:scale-95'
    
    # Determine styles and colors based on variant
    effective_text_color = text_color
    
    if variant != 'simple':
        classes += ' shadow-sm vibrant-shadow'

    if disabled:
        classes += ' opacity-30 grayscale'
        style = f'color: var(--c-text-subtle); width: fit-content;'
    else:
        style = f'width: fit-content;'
        
        if variant == 'solid':
            style += f' background-color: {color};'
        elif variant == 'glass':
            classes += ' glass'
            style += f' background-color: {color}22;' # 13% opacity
            style += f' border: 1px solid {color}44;' # 26% opacity
        elif variant == 'simple':
            # Simple: No background, text/icon takes the main color
            style += f' background-color: transparent;'
            effective_text_color = color
            # Force opacity 1.0 logic or similar if needed, but color usually handles it
    
    with ui.row().classes(classes).style(style) as badge:
        if on_click and not disabled:
            badge.on('click', on_click)
        elif on_click: # Still allow clicking for toggles even if disabled
            badge.on('click', on_click)
        if icon:
            AppIcon(icon, color=effective_text_color, size='1.2em', classes=icon_classes)
        
        # Explicitly set color on labels
        ui.label(label).classes('text-[10px] font-bold uppercase tracking-widest').style(f'color: {effective_text_color}')
        
        if value:
            ui.label('|').classes('opacity-30').style(f'color: {effective_text_color}')
            ui.label(value).classes('text-xs font-black').style(f'color: {effective_text_color}')

def CategoryBadge(
    category: str,
    theme: Theme,
    value: Optional[str] = None,
    icon: Optional[str] = None,
    interactive: bool = False,
    disabled: bool = False,
    on_click: Optional[callable] = None,
    variant: str = 'glass'
):
    """
    A specialized badge for categories with automatic coloring.
    """
    color = CategoryStyles.get_color(category, theme)
    return AppBadge(
        label=category,
        value=value,
        icon=icon or CategoryStyles.get_icon(category),
        color=color,
        interactive=interactive,
        disabled=disabled,
        on_click=on_click,
        variant=variant
    )

def StatusBadge(
    label: str,
    state: str,
    theme: Theme,
    value: Optional[str] = None,
    variant: str = 'solid',
    icon: Optional[Union[str, Dict[str, str]]] = None,
    rotate: bool = False,
    **kwargs
):
    """
    A specialized badge for statuses with automatic coloring and icon.
    Args:
        icon: Can be a single icon name (used for all states) or a dictionary mapping 
              state names (ready, error, pending, idle, unknown) to icon names.
        rotate: If True, applies rotation animation to the icon.
    """
    color = StatusStyles.get_color(state, theme)
    
    # Resolve Icon
    effective_icon = None
    if isinstance(icon, dict):
        # Resolve state to canonical form (e.g. 'active' -> 'ready')
        resolved_state = StatusStyles.resolve_state(state)
        # Try specific state, then 'default', then fallback to standard styles
        effective_icon = icon.get(resolved_state) or icon.get('default')
    elif isinstance(icon, str):
        effective_icon = icon
        
    # Final fallback to standard status icons if no override provides one
    if not effective_icon:
        effective_icon = StatusStyles.get_icon(state)
        
    icon_cls = ""
    if rotate:
        icon_cls = "rotate-animation"

    return AppBadge(
        label=label,
        value=value,
        icon=effective_icon,
        color=color,
        text_color=theme.colors.text_main,  # Use the theme's foreground color
        variant=variant,
        icon_classes=icon_cls,
        **kwargs
    )

def CopyBadge(
    text_to_copy: str,
    label: str = "Copy",
    value: Optional[str] = None,
    icon: str = "mdi-content-copy",
    color: str = "var(--c-primary)",
    variant: str = "glass",
    success_message: str = "Copied to clipboard!"
):
    """
    A badge that copies specific text to the clipboard when clicked.
    """
    def handle_copy():
        ui.clipboard.write(text_to_copy)
        ui.notify(success_message, type='positive', color='var(--q-success)')

    return AppBadge(
        label=label,
        value=value or (text_to_copy[:12] + "..." if len(text_to_copy) > 15 else text_to_copy),
        icon=icon,
        color=color,
        variant=variant,
        on_click=handle_copy,
        interactive=True
    )
