from nicegui import ui
import os
from ...theme import Theme, CategoryStyles
from ..atoms.badges import AppBadge
from ..atoms.cards import AppCard
from ..atoms.icons import AppIcon
from ....utils.formatters import format_size, format_date_human
from ....core.types import ScanContext

def FileRow(file_data: ScanContext, theme: Theme):
    """
    A premium file row component displaying detailed metadata.
    """
    category = file_data.category or 'Other'
    icon_name = CategoryStyles.get_icon(category)
    icon_color = CategoryStyles.get_color(category, theme)
    
    # Path processing
    path = file_data.path or ''
    directory = os.path.dirname(path)
    filename = file_data.filename or os.path.basename(path)
    
    # Format size and date
    size_bytes = file_data.size_bytes or 0
    size_val, size_unit, size_color = format_size(size_bytes)
    
    modified_at = file_data.modified_at
    date_str, date_color = format_date_human(modified_at) if modified_at else ("Unknown", "var(--app-text-sec)")

    with AppCard(variant='subtle', padding='p-3'):
        with ui.row().classes('w-full items-center no-wrap gap-4'):
            # 1. Category Icon
            with ui.column().classes('items-center justify-center bg-white/5 rounded-app p-2 w-12 h-12'):
                AppIcon(icon_name, color=icon_color, size='1.8em')
            
            # 2. Main content: Path (top) and Filename (bottom)
            with ui.column().classes('flex-grow overflow-hidden'):
                # Static tree path
                with ui.row().classes('items-center gap-1 opacity-50'):
                    ui.label('▼').classes('text-[8px]') # Static tree marker
                    ui.label(directory).classes('text-[10px] font-mono truncate tracking-tight')
                
                # File title
                ui.label(filename).classes('text-sm font-bold truncate')
            
            # 3. Right Side: Vertical stack of badges
            with ui.column().classes('items-end gap-1.5'):
                # Size badge
                AppBadge(
                    label=size_unit,
                    value=size_val,
                    icon="storage",
                    color=size_color,
                    variant="glass"
                )
                
                # Date badge
                AppBadge(
                    label="",
                    value=date_str,
                    icon="calendar_month",
                    color=date_color,
                    variant="glass"
                )
