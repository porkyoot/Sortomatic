from typing import Protocol, List, Tuple, Any, Dict

class FileTreeDataSource(Protocol):
    """
    Protocol (interface) for FileTree data sources.
    
    This allows FileTree to work with any data source (database, filesystem, API, etc.)
    without being tightly coupled to a specific implementation.
    
    Usage:
        class MyDataSource:
            async def get_children(self, path: str, filters: Dict[str, Any]) -> Tuple[List[str], List[dict]]:
                # Your implementation
                return folders, files
        
        tree = FileTree(root_path="/", data_source=MyDataSource(), palette=palette)
    """
    
    async def get_children(self, path: str, filters: Dict[str, Any]) -> Tuple[List[str], List[dict]]:
        """
        Fetch children (folders and files) for a given path.
        
        Args:
            path: The directory path to fetch children from
            filters: Dictionary of filter criteria (e.g., {'search': 'test', 'category': 'Image'})
        
        Returns:
            Tuple of (folders, files) where:
            - folders: List of folder names (strings)
            - files: List of file dictionaries with keys: 
                    'filename', 'path', 'category', 'size_bytes', 'modified_at'
        """
        ...
