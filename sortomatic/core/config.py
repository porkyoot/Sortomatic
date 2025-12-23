import yaml
from pathlib import Path
from typing import Dict, List
from ..l8n import Strings

# Default rules if no config file is found
DEFAULT_CATEGORIES = {
    Strings.CAT_IMAGES: ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "heic", "svg"],
    Strings.CAT_VIDEOS: ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"],
    Strings.CAT_DOCUMENTS: ["pdf", "doc", "docx", "txt", "md", "xls", "xlsx", "ppt", "pptx"],
    Strings.CAT_AUDIO: ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
    Strings.CAT_ARCHIVES: ["zip", "rar", "7z", "tar", "gz"],
    Strings.CAT_CODE: ["py", "js", "html", "css", "json", "xml", "c", "cpp", "h", "java", "go", "rs"]
}

class Settings:
    def __init__(self):
        self.categories: Dict[str, List[str]] = DEFAULT_CATEGORIES
        self.ignore_patterns: List[str] = [".git", "__pycache__", ".DS_Store", "node_modules"]

    def load_from_file(self, path: Path):
        """Load external YAML config if available."""
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                self.categories = data.get("categories", self.categories)
                self.ignore_patterns = data.get("ignore", self.ignore_patterns)

    def get_category(self, extension: str) -> str:
        """Determine category based on file extension."""
        ext = extension.lower().lstrip(".")
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category
        return Strings.CAT_OTHERS

# Global singleton
settings = Settings()