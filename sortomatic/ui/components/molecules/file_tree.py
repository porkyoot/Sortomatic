from nicegui import ui
from typing import List, Dict, Optional, Callable, Any
import os
from ...theme import ColorPalette, CategoryStyles
from ..atoms.badges import CategoryBadge, AppBadge
from ..atoms.icons import AppIcon
from ....utils.formatters import format_size, format_date_human
from ....core.types import ScanContext
from ...protocols import FileTreeDataSource
from ...datasources import BridgeFileTreeDataSource

class FileTreeRow(ui.row):
    """
    A single row in the file tree with aligned columns.
    """
    def __init__(self, 
                 name: str, 
                 level: int, 
                 is_dir: bool, 
                 palette: ColorPalette,
                 file_data: Optional[ScanContext] = None,
                 show_category: bool = True,
                 show_size: bool = True,
                 show_date: bool = True,
                 expanded: bool = False,
                 toggle_func: Optional[Callable] = None):
        super().__init__()
        self.classes('w-full items-center py-1 px-4 hover:bg-white/5 transition-colors no-wrap shrink-0')
        self.style('min-width: 800px;') # Ensure columns don't squash
        
        with self:
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
                    ui.icon(CategoryStyles.get_icon(category), color=CategoryStyles.get_color(category, palette)).classes('mr-2')
                
                ui.label(name).classes('text-sm font-medium truncate')

            # 2. Category Column
            with ui.element('div').style('width: 15%;'):
                if show_category and not is_dir and file_data:
                    category = file_data.category or "Other"
                    CategoryBadge(category, palette, variant="glass")

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

class FileTree(ui.column):
    """
    Powerful, lazy-loading file tree with sorting and configurable columns.
    
    Features:
    - True lazy loading: Only fetches children when folders are expanded
    - Protocol-based data source: Works with any FileTreeDataSource implementation
    - State management: refresh() and reload() for dynamic updates
    - Incremental rendering: No full-tree re-renders on expansion
    
    Usage:
        # Default with Bridge data source
        tree = FileTree(root_path="/", palette=palette)
        
        # Custom data source
        tree = FileTree(root_path="/", data_source=MyDataSource(), palette=palette)
        
        # Apply filters and reload
        tree.reload(filters={'search': 'test.py', 'category': 'Code'})
        
        # Refresh current view
        tree.refresh()
    """
    def __init__(self, 
                 root_path: str, 
                 palette: ColorPalette,
                 data_source: Optional[FileTreeDataSource] = None,
                 show_category: bool = True,
                 show_size: bool = True,
                 show_date: bool = True):
        super().__init__()
        self.classes('w-full border border-white/10 rounded-app overflow-hidden bg-white/5')
        self.root_path = root_path
        self.palette = palette
        self.show_category = show_category
        self.show_size = show_size
        self.show_date = show_date
        
        # Data source (defaults to Bridge if not provided)
        self.data_source = data_source or BridgeFileTreeDataSource()
        
        self.sort_by = "name"
        self.sort_desc = False
        
        # Filter criteria (dict for extensibility)
        self.filters: Dict[str, Any] = {}
        
        # State management for expansion
        self.expanded_paths = set()
        
        # Track DOM containers for each folder path
        # This allows us to insert/remove children without re-rendering everything
        self.folder_containers: Dict[str, ui.column] = {}
        
        # Track folder rows for updating chevron icons
        self.folder_rows: Dict[str, tuple] = {}  # path -> (row, button)
        
        self.render()

    def set_filter(self, text: str):
        """
        Legacy method for backward compatibility.
        Sets a search filter and re-renders the tree.
        
        Args:
            text: Search text to filter files/folders
        """
        self.filters['search'] = text
        self.render()

    def reload(self, filters: Optional[Dict[str, Any]] = None):
        """
        Reload the tree with new filter criteria.
        Clears all expanded state and re-fetches from root.
        
        Args:
            filters: New filter criteria dict (e.g., {'search': 'test', 'category': 'Image'})
                    If None, keeps current filters
        
        Usage:
            tree.reload({'search': 'test.py'})
            tree.reload({'category': 'Code', 'min_size': 1024})
        """
        if filters is not None:
            self.filters = filters
        
        # Clear all state
        self.expanded_paths.clear()
        
        # Re-render from root
        self.render()

    def refresh(self):
        """
        Refresh the current tree view without changing filters or expansion state.
        Re-fetches data for currently expanded folders.
        
        Usage:
            tree.refresh()  # After file system changes
        """
        # Re-render preserving expanded state
        self.render()

    def sort_tree(self, field: str):
        if self.sort_by == field:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = field
            self.sort_desc = False
        self.render()

    def render(self):
        """
        Rebuilds the ENTIRE tree from scratch.
        Only renders the root level initially + any expanded folders.
        """
        self.clear()
        self.folder_containers.clear()
        self.folder_rows.clear()
        
        with self:
            # 1. Header
            with ui.row().classes('w-full items-center bg-white/10 py-2 px-4 no-wrap shrink-0 border-b border-white/5'):
                self._header_cell("Name", "name", "40%")
                self._header_cell("Category", "category", "15%")
                self._header_cell("Size", "size", "20%")
                self._header_cell("Modified", "date", "25%")
            
            # 2. Tree Container (Scroll Area)
            with ui.scroll_area().classes('w-full h-[600px]'):
                self.content_col = ui.column().classes('w-full gap-0')
                # Kick off rendering asynchronously
                ui.timer(0.01, lambda: self._render_tree(), once=True)

    def _header_cell(self, label: str, field: str, width: str):
        with ui.element('div').style(f'width: {width};').classes('cursor-pointer hover:text-white transition-colors group'):
            with ui.row().classes('items-center gap-1'):
                ui.label(label).classes('text-[10px] uppercase font-bold tracking-widest opacity-50')
                if self.sort_by == field:
                    icon = "arrow_upward" if not self.sort_desc else "arrow_downward"
                    ui.icon(icon, size='12px').classes('color-[var(--q-primary)]')
            ui.on('click', lambda: self.sort_tree(field))

    async def _render_tree(self):
        """
        Renders the entire tree structure based on expanded_paths.
        """
        await self._render_level_recursive(self.root_path, 0, self.content_col)

    async def _render_level_recursive(self, path: str, level: int, parent_container: ui.column):
        """
        Fetches and renders a single level, then recursively renders expanded children.
        Uses the data_source to fetch children (protocol-based, decoupled from Bridge).
        This is called during full re-renders (e.g., after sorting changes).
        """
        # Fetch children using the data source (not hardcoded bridge!)
        folders, files_dicts = await self.data_source.get_children(path, self.filters)
        
        # Convert dicts to ScanContext for dot access in UI
        files = [ScanContext(**f) for f in files_dicts]
        
        # Apply sorting
        folders, files = self._sort_items(folders, files)

        with parent_container:
            # Render Folders
            for folder in folders:
                folder_path = os.path.join(path, folder)
                is_expanded = folder_path in self.expanded_paths
                
                # Create folder row with chevron button
                row, button = self._create_folder_row(
                    folder, level, is_expanded, folder_path
                )
                self.folder_rows[folder_path] = (row, button)
                
                # Create a container for this folder's children
                children_container = ui.column().classes('w-full gap-0')
                self.folder_containers[folder_path] = children_container
                
                # Only render children if this folder is expanded
                if is_expanded:
                    await self._render_level_recursive(folder_path, level + 1, children_container)
            
            # Render Files
            for fileinfo in files:
                self._create_file_row(fileinfo, level)

    def _sort_items(self, folders: List[str], files: List[ScanContext]):
        """Apply current sorting to folders and files."""
        if self.sort_by == "name":
            folders.sort(reverse=self.sort_desc)
            files.sort(key=lambda f: f.filename, reverse=self.sort_desc)
        elif self.sort_by == "size":
            files.sort(key=lambda f: f.size_bytes, reverse=self.sort_desc)
        elif self.sort_by == "date":
            files.sort(key=lambda f: f.modified_at, reverse=self.sort_desc)
        elif self.sort_by == "category":
            files.sort(key=lambda f: f.category or "", reverse=self.sort_desc)
        return folders, files

    def _create_folder_row(self, name: str, level: int, expanded: bool, path: str):
        """Creates a folder row and returns (row, button) for later updates."""
        row = FileTreeRow(
            name=name, 
            level=level, 
            is_dir=True, 
            palette=self.palette,
            expanded=expanded,
            toggle_func=lambda p=path: self._toggle_expansion_incremental(p)
        )
        # Find the button within the row (it's the first button)
        button = None
        for child in row:
            if isinstance(child, ui.button):
                button = child
                break
        return row, button

    def _create_file_row(self, fileinfo: ScanContext, level: int):
        """Creates a file row."""
        return FileTreeRow(
            name=fileinfo.filename,
            level=level,
            is_dir=False,
            palette=self.palette,
            file_data=fileinfo,
            show_category=self.show_category,
            show_size=self.show_size,
            show_date=self.show_date
        )

    async def _toggle_expansion_incremental(self, path: str):
        """
        Toggles folder expansion incrementally.
        Only fetches and renders the children of this specific folder.
        NO full tree re-render!
        """
        is_expanding = path not in self.expanded_paths
        
        if is_expanding:
            # ADD children
            self.expanded_paths.add(path)
            
            # Update chevron icon
            if path in self.folder_rows:
                _, button = self.folder_rows[path]
                if button:
                    button.props('icon=expand_more')
                    button.update()
            
            # Fetch and render children
            container = self.folder_containers.get(path)
            if container:
                # Get the level from the path depth
                level = path.count(os.sep) - self.root_path.count(os.sep) + 1
                await self._render_level_recursive(path, level, container)
        else:
            # REMOVE children
            self.expanded_paths.remove(path)
            
            # Update chevron icon
            if path in self.folder_rows:
                _, button = self.folder_rows[path]
                if button:
                    button.props('icon=chevron_right')
                    button.update()
            
            # Clear children container
            container = self.folder_containers.get(path)
            if container:
                container.clear()
