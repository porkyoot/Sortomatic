import logging
from sortomatic.core.bridge import bridge
from sortomatic.core.database import get_children
from sortomatic.core.metrics import metrics_monitor
from sortomatic.utils.logger import logger

class BridgeLogHandler(logging.Handler):
    """
    A custom logging handler that emits log records to the bridge event bus.
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            # Determine color based on level
            color = None
            if record.levelno >= logging.ERROR:
                color = "#ef4444" # Red
            elif record.levelno >= logging.WARNING:
                color = "#eab308" # Yellow
            elif record.levelno == 25: # SUCCESS
                color = "#22c55e" # Green
            elif record.levelno == logging.DEBUG:
                color = "#94a3b8" # Slate 400
                
            bridge.emit("log_record", {
                "message": msg,
                "color": color,
                "level": record.levelname
            })
        except Exception:
            self.handleError(record)

def init_bridge_handlers():
    """
    Registers backend handlers for the bridge.
    This connects the decoupled UI requests to the actual database/logic.
    """
    
    # 0. Initialize Logger Bridge
    # Add handler if not already present to avoid duplicates
    if not any(isinstance(h, BridgeLogHandler) for h in logger.handlers):
        bridge_handler = BridgeLogHandler()
        # Set format to just the message for UI cleanliness, or keeping standard
        # For the terminal, we might want just message or time+message
        formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="%H:%M:%S")
        bridge_handler.setFormatter(formatter)
        logger.addHandler(bridge_handler)

    
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
