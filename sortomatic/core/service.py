from sortomatic.core.bridge import bridge
from sortomatic.core.database import get_children
from sortomatic.core.metrics import metrics_monitor
from sortomatic.utils.logger import logger

def init_bridge_handlers():
    """
    Registers backend handlers for the bridge.
    This connects the decoupled UI requests to the actual database/logic.
    """
    
    # 1. File Tree Children Request
    @bridge.handle_request("get_file_tree")
    async def handle_get_file_tree(payload):
        """
        Payload: { 'path': str, 'search': Optional[str] }
        """
        path = payload.get('path', '/')
        search = payload.get('search')
        
        logger.debug(f"Service: Fetching tree for {path} (search: {search})")
        folders, files = get_children(path, search=search)
        
        # We can format the data here if needed to make it pure JSON-like,
        # but for now we'll pass the model instances or dictionaries.
        return {
            "folders": folders,
            "files": [
                {
                    "filename": f.filename,
                    "path": f.path,
                    "category": f.category,
                    "size_bytes": f.size_bytes,
                    "modified_at": f.modified_at,
                } for f in files
            ]
        }

    # 2. System Status Request
    @bridge.handle_request("get_system_status")
    async def handle_get_system_status(payload):
        """
        Returns the current status of the system.
        """
        from sortomatic.core.database import db
        
        # Check DB status
        db_state = "ready"
        if not db.obj or db.is_closed():
             db_state = "error"
             
        # TODO: Connect to ScanManager to get real scan state
        # For now, we assume idle or check a global flag if available
        scan_state = "idle" 
        
        return {
            "backend": "ready",
            "database": db_state,
            "scan": scan_state
        }

    # 3. System Metrics Request
    @bridge.handle_request("get_system_metrics")
    async def handle_get_system_metrics(payload):
        """
        Returns performance metrics (CPU, RAM, etc).
        """
        return metrics_monitor.get_all_metrics()

    logger.info("Bridge handlers initialized.")
