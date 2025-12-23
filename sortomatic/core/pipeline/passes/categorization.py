try:
    import filetype
except ImportError:
    filetype = None

from pathlib import Path
from ...config import settings
from ....l8n import Strings

def detect_type(ctx: dict):
    """
    Pass 1: Detects category and mime type.
    """
    path = Path(ctx['path'])
    
    # 1. Extension Strategy
    ext = path.suffix.lower()
    category = settings.get_category(ext)
    
    # 2. Magic Bytes Strategy (if unknown or suspicious)
    mime = "application/octet-stream"
    if (category == Strings.CAT_OTHERS or category == "Unsorted") and filetype:
        try:
            kind = filetype.guess(str(path))
            if kind:
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