import yaml
import os
import shutil
from pathlib import Path
from typing import Dict, List
from ..l8n import Strings

class Settings:
    def __init__(self):
        # Paths
        self.config_dir = Path.home() / ".config" / "sortomatic"
        self.settings_file = self.config_dir / "settings.yaml"
        self.filetypes_file = self.config_dir / "filetypes.yaml"
        
        # Internal defaults (used if files are missing or corrupted)
        self.categories: Dict[str, List[str]] = {
            Strings.CAT_IMAGES: ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "heic", "svg"],
            Strings.CAT_VIDEOS: ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"],
            Strings.CAT_DOCUMENTS: ["pdf", "doc", "docx", "txt", "md", "xls", "xlsx", "ppt", "pptx"],
            Strings.CAT_AUDIO: ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            Strings.CAT_ARCHIVES: ["zip", "rar", "7z", "tar", "gz"],
            Strings.CAT_CODE: ["py", "js", "html", "css", "json", "xml", "c", "cpp", "h", "java", "go", "rs"]
        }
        self.ignore_patterns: List[str] = [".git", "__pycache__", ".DS_Store", "node_modules", ".venv", ".sortomatic"]
        self.atomic_markers: List[str] = [".git", ".hg", "Makefile", "package.json", "requirements.txt", "venv"]
        self.batch_size: int = 1000
        self.reset_db: bool = False
        
        # New: Externalized magic numbers
        self.hashing_chunk_size: int = 1024 * 1024  # 1MB
        self.fast_hash_size: int = 4 * 1024        # 4KB
        self.categorization_timeout: float = 1.0    # 1 second
        self.hashing_timeout: float = 60.0          # 60 seconds (generous for large files)
        
        cpu_count = os.cpu_count() or 4
        self.max_workers = max(1, cpu_count // 2)

        # GUI Settings
        self.gui_port: int = 8080
        self.gui_theme: str = "solarized"
        self.gui_dark_mode: bool = True

        # Initialize and Load
        self._ensure_config_exists()
        self.load()

    def _ensure_config_exists(self):
        """Copies default config files to user directory if they don't exist."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

        package_config_dir = Path(__file__).parent.parent / "config"
        
        defaults = {
            "settings.yaml": self.settings_file,
            "filetypes.yaml": self.filetypes_file
        }

        for filename, dest_path in defaults.items():
            if not dest_path.exists():
                src_path = package_config_dir / filename
                if src_path.exists():
                    shutil.copy(src_path, dest_path)

    def load(self):
        """Loads configuration from the user's YAML files."""
        # 1. Load Settings
        if self.settings_file.exists():
            with open(self.settings_file, "r") as f:
                data = yaml.safe_load(f) or {}
                if data.get("max_workers") is not None:
                    self.max_workers = data["max_workers"]
                self.batch_size = data.get("batch_size", self.batch_size)
                self.reset_db = data.get("reset_db", self.reset_db)
                self.hashing_chunk_size = data.get("hashing_chunk_size", self.hashing_chunk_size)
                self.fast_hash_size = data.get("fast_hash_size", self.fast_hash_size)
                self.categorization_timeout = data.get("categorization_timeout", self.categorization_timeout)
                self.hashing_timeout = data.get("hashing_timeout", self.hashing_timeout)
                self.gui_port = data.get("gui_port", self.gui_port)
                self.gui_theme = data.get("gui_theme", self.gui_theme)
                self.gui_dark_mode = data.get("gui_dark_mode", self.gui_dark_mode)

        # 2. Load Filetypes
        if self.filetypes_file.exists():
            with open(self.filetypes_file, "r") as f:
                data = yaml.safe_load(f) or {}
                self.categories = data.get("categories", self.categories)
                self.ignore_patterns = data.get("ignore", self.ignore_patterns)
                self.atomic_markers = data.get("atomic_markers", self.atomic_markers)

    def get_category(self, extension: str) -> str:
        """Determine category based on file extension."""
        ext = extension.lower().lstrip(".")
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category
        return Strings.CAT_OTHERS

# Global singleton
settings = Settings()