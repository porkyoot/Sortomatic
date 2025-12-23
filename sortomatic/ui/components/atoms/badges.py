from nicegui import ui
from typing import Optional
from .icons import AppIcon
from ...theme import CategoryStyles, ColorPalette, StatusStyles

def AppBadge(
    label: str,
    value: Optional[str] = None,
    icon: Optional[str] = None,
    color: str = 'var(--q-primary)',
    text_color: str = 'var(--app-text)',
    variant: str = 'solid', # solid, glass, subtle
    on_click: Optional[callable] = None,
    interactive: bool = False,
    disabled: bool = False
):
    """
    A styled badge for displaying statuses, categories, or counts.
    Supports solid, glass (translucent), and subtle (no background) variants.
    """
    classes = 'items-center gap-1 px-2 py-0.5 rounded-app shadow-sm vibrant-shadow transition-all'
    if (interactive or on_click) and not disabled:
        classes += ' cursor-pointer hover:scale-105 active:scale-95'
    
    if disabled:
        classes += ' opacity-30 grayscale'
        style = f'color: var(--app-text-sec); width: fit-content;'
    else:
        style = f'width: fit-content;'
        
        if variant == 'solid':
            style += f' background-color: {color};'
        elif variant == 'glass':
            classes += ' glass'
            style += f' background-color: {color}22;' # 13% opacity
            style += f' border: 1px solid {color}44;' # 26% opacity
    
    with ui.row().classes(classes).style(style) as badge:
        if on_click and not disabled:
            badge.on('click', on_click)
        elif on_click: # Still allow clicking for toggles even if disabled
            badge.on('click', on_click)
        if icon:
            AppIcon(icon, color=text_color, size='1.2em')
        
        # Explicitly set color on labels
        ui.label(label).classes('text-[10px] font-bold uppercase tracking-widest').style(f'color: {text_color}')
        
        if value:
            ui.label('|').classes('opacity-30').style(f'color: {text_color}')
            ui.label(value).classes('text-xs font-black').style(f'color: {text_color}')

def CategoryBadge(
    category: str,
    palette: ColorPalette,
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
    color = CategoryStyles.get_color(category, palette)
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
    palette: ColorPalette,
    value: Optional[str] = None
):
    """
    A specialized badge for statuses with automatic coloring and icon.
    """
    color = StatusStyles.get_color(state, palette)
    icon = StatusStyles.get_icon(state)
    return AppBadge(
        label=label,
        value=value,
        icon=icon,
        color=color,
        text_color=palette.fg  # Use the palette's foreground color
    )

def CopyBadge(
    text_to_copy: str,
    label: str = "Copy",
    value: Optional[str] = None,
    icon: str = "content_copy",
    color: str = "var(--q-primary)",
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
