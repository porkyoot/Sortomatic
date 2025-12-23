import concurrent.futures
import atexit
from ..config import settings

# Global executor instance
_executor = None

def get_executor():
    """
    Returns the global thread pool executor.
    Initializes it if it doesn't exist.
    """
    global _executor
    if _executor is None:
        _executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=settings.max_workers,
            thread_name_prefix="sortomatic_worker"
        )
    return _executor

def shutdown_executor():
    """
    Shuts down the global executor.
    """
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=True)
        _executor = None

# Ensure we clean up on exit
atexit.register(shutdown_executor)
