from nicegui import ui
from typing import List, Dict, Optional, Callable, Any
import os
from ...theme import Theme, CategoryStyles
from ..atoms.badges import CategoryBadge, AppBadge
from ..atoms.icons import AppIcon
from ....utils.formatters import format_size, format_date_human
from ....core.types import ScanContext
from ...protocols import FileTreeDataSource
from ...datasources import BridgeFileTreeDataSource

def FileTreeRow(
    name: str, 
    level: int, 
    is_dir: bool, 
    theme: Theme,
    file_data: Optional[ScanContext] = None,
    show_category: bool = True,
    show_size: bool = True,
    show_date: bool = True,
    expanded: bool = False,
    toggle_func: Optional[Callable] = None
):
    """
    A single row in the file tree with aligned columns.
    """
    with ui.row().classes('s-tree-row s-tree-min-width') as row:
        # 1. Name Column (Tree Column)
        indent = level * 24
        with ui.row().classes('items-center no-wrap').style(f'width: 40%; padding-left: {indent}px;'):
            if is_dir:
                icon = "expand_more" if expanded else "chevron_right"
                ui.button(icon=icon, on_click=toggle_func).props('flat dense size=sm').classes('mr-1 color-[var(--app-text-sec)]')
                ui.icon("folder", color="var(--q-primary)").classes('mr-2')
            else:
                ui.element('div').classes('w-8') # Placeholder for chevron
                category = file_data.category if file_data else "Other"
                ui.icon(CategoryStyles.get_icon(category), color=CategoryStyles.get_color(category, theme)).classes('mr-2')
            
            ui.label(name).classes('text-sm font-medium truncate')

        # 2. Category Column
        with ui.element('div').style('width: 15%;'):
            if show_category and not is_dir and file_data:
                category = file_data.category or "Other"
                CategoryBadge(category, theme, variant="glass")

        # 3. Size Column
        with ui.element('div').style('width: 20%;'):
            if show_size and not is_dir and file_data:
                val, unit, color = format_size(file_data.size_bytes)
                AppBadge(label=unit, value=val, color=color, variant="glass", icon="storage")

        # 4. Date Column
        with ui.element('div').style('width: 25%;'):
            if show_date and not is_dir and file_data:
                date_str, color = format_date_human(file_data.modified_at)
                AppBadge(label="", value=date_str, color=color, variant="glass", icon="calendar_month")
                
    return row

def FileTree(
    root_path: str, 
    theme: Theme,
    data_source: Optional[FileTreeDataSource] = None,
    show_category: bool = True,
    show_size: bool = True,
    show_date: bool = True
):
    """
    Powerful, lazy-loading file tree with sorting and configurable columns.
    """
    container = ui.column().classes('s-tree-container')
    
    # State managed as attributes on the container object (for easy access in methods)
    container.root_path = root_path
    container.theme = theme
    container.show_category = show_category
    container.show_size = show_size
    container.show_date = show_date
    container.data_source = data_source or BridgeFileTreeDataSource()
    container.sort_by = "name"
    container.sort_desc = False
    container.filters = {}
    container.expanded_paths = set()
    container.folder_containers = {}
    container.folder_rows = {}
    container.content_col = None

    def set_filter(text: str):
        container.filters['search'] = text
        render()

    def reload(filters: Optional[Dict[str, Any]] = None):
        if filters is not None:
            container.filters = filters
        container.expanded_paths.clear()
        render()

    def refresh():
        render()

    def sort_tree(field: str):
        if container.sort_by == field:
            container.sort_desc = not container.sort_desc
        else:
            container.sort_by = field
            container.sort_desc = False
        render()

    def render():
        container.clear()
        container.folder_containers.clear()
        container.folder_rows.clear()
        
        with container:
            # 1. Header
            with ui.row().classes('s-tree-header w-full'):
                _header_cell("Name", "name", "40%")
                _header_cell("Category", "category", "15%")
                _header_cell("Size", "size", "20%")
                _header_cell("Modified", "date", "25%")
            
            # 2. Tree Container (Scroll Area)
            with ui.scroll_area().classes('s-tree-scroll-area'):
                container.content_col = ui.column().classes('w-full gap-0')
                # Kick off rendering asynchronously
                ui.timer(0.01, lambda: _render_tree(), once=True)

    def _header_cell(label: str, field: str, width: str):
        with ui.element('div').style(f'width: {width};').classes('s-tree-header__cell group'):
            with ui.row().classes('items-center gap-1'):
                ui.label(label).classes('text-[10px] uppercase font-bold tracking-widest opacity-50')
                if container.sort_by == field:
                    icon = "arrow_upward" if not container.sort_desc else "arrow_downward"
                    ui.icon(icon, size='12px').classes('text-[var(--c-primary)]')
            ui.on('click', lambda field=field: sort_tree(field))

    async def _render_tree():
        await _render_level_recursive(container.root_path, 0, container.content_col)

    async def _render_level_recursive(path: str, level: int, parent_container: ui.column):
        folders, files_dicts = await container.data_source.get_children(path, container.filters)
        files = [ScanContext(**f) for f in files_dicts]
        folders, files = _sort_items(folders, files)

        with parent_container:
            for folder in folders:
                folder_path = os.path.join(path, folder)
                is_expanded = folder_path in container.expanded_paths
                row, button = _create_folder_row(folder, level, is_expanded, folder_path)
                container.folder_rows[folder_path] = (row, button)
                children_container = ui.column().classes('w-full gap-0')
                container.folder_containers[folder_path] = children_container
                if is_expanded:
                    await _render_level_recursive(folder_path, level + 1, children_container)
            for fileinfo in files:
                _create_file_row(fileinfo, level)

    def _sort_items(folders: List[str], files: List[ScanContext]):
        if container.sort_by == "name":
            folders.sort(reverse=container.sort_desc)
            files.sort(key=lambda f: f.filename, reverse=container.sort_desc)
        elif container.sort_by == "size":
            files.sort(key=lambda f: f.size_bytes, reverse=container.sort_desc)
        elif container.sort_by == "date":
            files.sort(key=lambda f: f.modified_at, reverse=container.sort_desc)
        elif container.sort_by == "category":
            files.sort(key=lambda f: f.category or "", reverse=container.sort_desc)
        return folders, files

    def _create_folder_row(name: str, level: int, expanded: bool, path: str):
        row = FileTreeRow(
            name=name, 
            level=level, 
            is_dir=True, 
            theme=container.theme,
            expanded=expanded,
            toggle_func=lambda p=path: _toggle_expansion_incremental(p)
        )
        button = None
        for child in row:
            if isinstance(child, ui.button):
                button = child
                break
        return row, button

    def _create_file_row(fileinfo: ScanContext, level: int):
        return FileTreeRow(
            name=fileinfo.filename,
            level=level,
            is_dir=False,
            theme=container.theme,
            file_data=fileinfo,
            show_category=container.show_category,
            show_size=container.show_size,
            show_date=container.show_date
        )

    async def _toggle_expansion_incremental(path: str):
        is_expanding = path not in container.expanded_paths
        if is_expanding:
            container.expanded_paths.add(path)
            if path in container.folder_rows:
                _, button = container.folder_rows[path]
                if button:
                    button.props('icon=expand_more')
                    button.update()
            
            c = container.folder_containers.get(path)
            if c:
                level = path.count(os.sep) - container.root_path.count(os.sep) + 1
                await _render_level_recursive(path, level, c)
        else:
            container.expanded_paths.remove(path)
            if path in container.folder_rows:
                _, button = container.folder_rows[path]
                if button:
                    button.props('icon=chevron_right')
                    button.update()
            
            c = container.folder_containers.get(path)
            if c:
                c.clear()

    # Attach methods for external use
    container.set_filter = set_filter
    container.reload = reload
    container.refresh = refresh
    container.sort_tree = sort_tree
    
    render()
    return container
