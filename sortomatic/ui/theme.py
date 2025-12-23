from dataclasses import dataclass
from nicegui import ui

@dataclass
class ColorPalette:
    bg: str
    bg_secondary: str
    fg: str
    fg_secondary: str
    primary: str
    secondary: str
    accent_1: str
    accent_2: str
    info: str
    warning: str
    error: str
    success: str
    debug: str
    blue: str
    cyan: str
    green: str
    yellow: str
    orange: str
    red: str
    magenta: str
    purple: str
    grey: str = "#586e75" # Default grey if not provided
    
    # UI Decoration
    rounded: str = "4px"
    font_family: str = "'Inter', sans-serif"
    font_import: str = ""

def apply_theme(palette: ColorPalette):
    """
    Injects CSS variables and global styles to override Quasar/NiceGUI defaults.
    Must be called BEFORE any UI elements are created to prevent Flash of Unstyled Content (FOUC).
    """
    
    # Force dark mode IMMEDIATELY before any rendering
    # This prevents the white flash on page load
    is_dark = palette.bg == "#002b36"  # Solarized dark check
    ui.dark_mode(is_dark)
    
    import_html = f'<link href="{palette.font_import}" rel="stylesheet">' if palette.font_import else ""
    
    # Inject critical CSS FIRST to prevent FOUC
    ui.add_head_html(f'''
    {import_html}
    <style>
        /* CRITICAL: Prevent Flash of Unstyled Content */
        /* Apply background immediately, before full CSS loads */
        html, body {{
            background-color: {palette.bg} !important;
            color: {palette.fg} !important;
            font-family: {palette.font_family} !important;
            margin: 0;
            padding: 0;
        }}
        
        /* CSS Variables - available globally */
        :root {{
            --q-primary: {palette.primary};
            --q-secondary: {palette.secondary};
            --q-dark: {palette.bg};
            --app-bg: {palette.bg};
            --app-bg-secondary: {palette.bg_secondary};
            --app-text: {palette.fg};
            --app-text-sec: {palette.fg_secondary};
            --app-rounded: {palette.rounded};
            --app-font: {palette.font_family};
        }}
        
        /* Body styles using CSS variables */
        body {{
            background-color: var(--app-bg);
            color: var(--app-text);
            font-family: var(--app-font);
        }}
        
        /* Utility classes */
        .rounded-app {{
            border-radius: var(--app-rounded) !important;
        }}
        .glass {{
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .vibrant-shadow {{
            box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        /* Animations */
        @keyframes subtle-pulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.05); opacity: 0.8; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        .pulse-animation {{
            animation: subtle-pulse 2s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .spin-animation {{
            animation: spin 3s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .rotate-animation {{
            animation: rotate 2s linear infinite;
        }}
    </style>
    ''')


class CategoryStyles:
    """Centralized management for category colors and ordering."""
    
    @staticmethod
    def get_color(category: str, palette: ColorPalette) -> str:
        from sortomatic.l8n import Strings
        
        mapping = {
            Strings.CAT_IMAGE: palette.green,
            Strings.CAT_VIDEO: palette.red,
            Strings.CAT_DOCUMENT: palette.cyan,
            Strings.CAT_MUSIC: palette.orange,
            Strings.CAT_ARCHIVE: palette.yellow,
            Strings.CAT_CODE: palette.blue,
            Strings.CAT_3D: palette.magenta,
            Strings.CAT_SOFTWARE: palette.purple,
            Strings.CAT_OTHER: palette.grey,
        }
        return mapping.get(category, palette.grey)

    @staticmethod
    def get_icon(category: str) -> str:
        from sortomatic.l8n import Strings
        mapping = {
            Strings.CAT_IMAGE: "image",
            Strings.CAT_VIDEO: "videocam",
            Strings.CAT_DOCUMENT: "description",
            Strings.CAT_MUSIC: "audiotrack",
            Strings.CAT_ARCHIVE: "inventory_2",
            Strings.CAT_CODE: "terminal",
            Strings.CAT_3D: "view_in_ar",
            Strings.CAT_SOFTWARE: "apps",
            Strings.CAT_OTHER: "insert_drive_file",
        }
        return mapping.get(category, "insert_drive_file")

    @staticmethod
    def get_order() -> list[str]:
        from ..l8n import Strings
        return [
            Strings.CAT_OTHER,
            Strings.CAT_DOCUMENT,
            Strings.CAT_IMAGE,
            Strings.CAT_ARCHIVE,
            Strings.CAT_MUSIC,
            Strings.CAT_VIDEO,
            Strings.CAT_3D,
            Strings.CAT_SOFTWARE,
            Strings.CAT_CODE,
        ]

class StatusStyles:
    """Centralized management for status colors and icons."""
    
    # Generic state constants
    UNKNOWN = "unknown"
    PENDING = "pending"
    READY = "ready"
    ERROR = "error"
    IDLE = "idle"
    
    # Synonyms mapping
    _SYNONYMS = {
        "refreshing": PENDING,
        "active": READY, # Defaulting active to READY (Green) unless it's "transiently active" (Yellow)
        "busy": PENDING,
        "available": READY,
        "unavailable": ERROR,
        "inactive": ERROR,
        "running": PENDING,
        "stopped": UNKNOWN,
    }

    @staticmethod
    def resolve_state(state: str) -> str:
        s = state.lower()
        if s in [StatusStyles.UNKNOWN, StatusStyles.PENDING, StatusStyles.READY, StatusStyles.ERROR, StatusStyles.IDLE]:
            return s
        return StatusStyles._SYNONYMS.get(s, StatusStyles.UNKNOWN)

    @staticmethod
    def get_color(state: str, palette: ColorPalette) -> str:
        resolved = StatusStyles.resolve_state(state)
        mapping = {
            StatusStyles.UNKNOWN: palette.grey,
            StatusStyles.PENDING: palette.yellow,
            StatusStyles.READY: palette.green,
            StatusStyles.ERROR: palette.red,
            StatusStyles.IDLE: palette.blue,
        }
        return mapping.get(resolved, palette.grey)

    @staticmethod
    def get_icon(state: str) -> str:
        resolved = StatusStyles.resolve_state(state)
        mapping = {
            StatusStyles.UNKNOWN: "help_outline",
            StatusStyles.PENDING: "sync",
            StatusStyles.READY: "check_circle",
            StatusStyles.ERROR: "error_outline",
            StatusStyles.IDLE: "pause_circle",
        }
        return mapping.get(resolved, "help_outline")
