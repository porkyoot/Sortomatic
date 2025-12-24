from nicegui import ui
from typing import Optional, Union, List
from ..atoms.cards import AppCard

def AppThumbnail(
    type: str = 'image', 
    content: Union[str, List[str]] = "",
    size: str = '180px'
):
    """
    A premium square thumbnail component for diverse file previews.
    """
    card = AppCard(variant='', padding='', tight=True)
    card.classes(remove='s-card rounded-app border w-full border-app glass shadow-md bg-app-surface shadow-none vibrant-shadow')
    card.classes('s-thumbnail group')
    card.style(f'width: {size}; height: {size}; aspect-ratio: 1/1;')

    with card:
        if type == 'image':
            ui.image(content).classes('s-thumbnail__image')
        elif type == 'text':
            with ui.column().classes('s-thumbnail__content'):
                ui.label(content).classes('s-thumbnail__text')
                ui.element('div').classes('s-thumbnail__fade-overlay')
        elif type == 'html':
            with ui.column().classes('s-thumbnail__content bg-[var(--c-surface-1)]'):
                with ui.element('div').classes('s-thumbnail__preview-scale'):
                    ui.html(content, sanitize=False).classes('text-[10px] prose prose-invert')
        elif type == 'tree':
            items = content if isinstance(content, list) else ['src/', 'docs/', 'main.py', 'config.yaml']
            with ui.column().classes('s-thumbnail__content gap-1.5'):
                with ui.row().classes('items-center gap-2 mb-1'):
                    ui.icon('folder_open', size='18px', color='var(--c-primary)')
                    ui.label('Root').classes('text-[11px] font-bold tracking-tight')
                for item in items[:6]:
                    with ui.row().classes('items-center gap-2 pl-4'):
                        is_dir = item.endswith('/')
                        icon = 'folder' if is_dir else 'insert_drive_file'
                        ui.icon(icon, size='14px').classes('s-thumbnail__tree-icon')
                        ui.label(item).classes('text-[10px] opacity-70')

        # Subtle Interactive Overlay
        with ui.column().classes('s-thumbnail__overlay'):
            ui.icon('visibility', size='28px').classes('drop-shadow-lg text-[var(--c-text-main)]')
            
    return card
