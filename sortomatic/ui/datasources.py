from typing import List, Tuple, Dict, Any
from ..core.bridge import bridge

class BridgeFileTreeDataSource:
    """
    Implementation of FileTreeDataSource that uses the Bridge for data fetching.
    This is the default data source for FileTree.
    """
    
    async def get_children(self, path: str, filters: Dict[str, Any]) -> Tuple[List[str], List[dict]]:
        """
        Fetch children via the Bridge API.
        
        Args:
            path: The directory path
            filters: Filter criteria (supports 'search' key for text filtering)
        
        Returns:
            Tuple of (folders, files)
        """
        search_text = filters.get('search', '')
        
        response = await bridge.request("get_file_tree", {
            "path": path,
            "search": search_text
        })
        
        if not response:
            return [], []
        
        folders = response.get("folders", [])
        files = response.get("files", [])
        
        return folders, files
