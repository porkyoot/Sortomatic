try:
    import filetype
except ImportError:
    filetype = None

import threading
from pathlib import Path
from ...config import settings
from ....l8n import Strings

def detect_type(ctx: dict):
    """
    Pass 1: Detects category and mime type.
    """
    import os
    if not os.path.isfile(ctx['path']):
        return ctx
        
    path = Path(ctx['path'])
    
    # 1. Extension Strategy
    ext = path.suffix.lower()
    category = settings.get_category(ext)
    
    # 2. Magic Bytes Strategy (if unknown or suspicious)
    mime = Strings.DEFAULT_MIME
    if (category == Strings.CAT_OTHERS or category == Strings.CAT_UNSORTED) and filetype:
        # Use a thread to enforce a 1-second timeout on magic byte detection
        result_container = {"kind": None}
        def target():
            try:
                result_container["kind"] = filetype.guess(str(path))
            except:
                pass

        detect_thread = threading.Thread(target=target, daemon=True)
        detect_thread.start()
        
        warning_timeout = settings.categorization_timeout * 0.8
        detect_thread.join(timeout=warning_timeout)
        
        if detect_thread.is_alive():
            from ....utils.logger import logger
            logger.warning(f"⚠️ Categorization is slow for: {path}. Reached 80% of timeout...")
            detect_thread.join(timeout=settings.categorization_timeout - warning_timeout)
        
        kind = result_container["kind"]
        if kind:
            try:
                mime = kind.mime
                # Reverse lookup category from mime if possible
                if kind.mime.startswith("image"): 
                    category = Strings.CAT_IMAGES
                elif kind.mime.startswith("video"): 
                    category = Strings.CAT_VIDEOS
                elif kind.mime.startswith("audio"):
                    category = Strings.CAT_AUDIO
                elif kind.mime in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                    category = Strings.CAT_DOCUMENTS
                elif kind.mime in ["application/zip", "application/x-tar", "application/x-rar-compressed", "application/x-7z-compressed"]:
                    category = Strings.CAT_ARCHIVES
            except:
                pass
            
    ctx['extension'] = ext
    ctx['category'] = category
    ctx['mime_type'] = mime
    return ctx