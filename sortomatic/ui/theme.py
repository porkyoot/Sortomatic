from dataclasses import dataclass, field
from nicegui import ui

# --- 1. DESIGN TOKENS (The "DNA") ---

@dataclass
class ThemeColors:
    """Semantic color names, not just 'blue' or 'red'."""
    surface_1: str  # Main background
    surface_2: str  # Secondary background (cards)
    surface_3: str  # Tertiary (hovers, inputs)
    text_main: str
    text_subtle: str
    primary: str
    secondary: str
    
    # Accents (Solarized)
    green: str
    red: str
    cyan: str
    orange: str
    yellow: str
    blue: str
    magenta: str
    violet: str

    # Accents for visualization
    accents: dict[str, str] = field(default_factory=dict)
    
    # Functional
    debug: str
    info: str
    success: str
    warning: str
    error: str

@dataclass
class ThemeLayout:
    """Responsive spacing and sizing tokens (using REM)."""
    # Spacing scale: 0=0, 1=0.25rem, 2=0.5rem, 4=1rem, etc.
    spacing_unit: str = "0.25rem" 
    
    # Radii
    radius_sm: str = "0.25rem"  # 4px
    radius_md: str = "0.5rem"   # 8px
    radius_lg: str = "1rem"     # 16px
    radius_full: str = "9999px"
    
    # Typography
    font_sans: str = "'Inter', system-ui, sans-serif"
    font_mono: str = "'JetBrains Mono', monospace"

@dataclass
class Theme:
    colors: ThemeColors
    layout: ThemeLayout = field(default_factory=ThemeLayout)

# --- 2. CSS GENERATOR (The "Compiler") ---

def generate_css_variables(theme: Theme) -> str:
    """Converts the Python Theme object into CSS Variables."""
    
    # Generate Accent Vars programmatically
    accents = {
        'green': theme.colors.green,
        'red': theme.colors.red,
        'cyan': theme.colors.cyan,
        'orange': theme.colors.orange,
        'yellow': theme.colors.yellow,
        'blue': theme.colors.blue,
        'magenta': theme.colors.magenta,
        'violet': theme.colors.violet,
    }
    accents.update(theme.colors.accents)
    accent_vars = "\n".join([f"--c-accent-{k}: {v};" for k, v in accents.items()])
    
    return f"""
    :root {{
        /* COLORS */
        --c-surface-1: {theme.colors.surface_1};
        --c-surface-2: {theme.colors.surface_2};
        --c-surface-3: {theme.colors.surface_3};
        --c-text-main: {theme.colors.text_main};
        --c-text-subtle: {theme.colors.text_subtle};
        --c-primary: {theme.colors.primary};
        --c-secondary: {theme.colors.secondary};
        --c-success: {theme.colors.success};
        --c-warning: {theme.colors.warning};
        --c-error: {theme.colors.error};
        {accent_vars}

        /* LAYOUT (Responsive) */
        --unit: {theme.layout.spacing_unit};
        --r-sm: {theme.layout.radius_sm};
        --r-md: {theme.layout.radius_md};
        --r-lg: {theme.layout.radius_lg};
        --r-full: {theme.layout.radius_full};
        
        /* Spacing Scale */
        --s-0: 0px;
        --s-0_5: calc(var(--unit) * 0.5);
        --s-1: calc(var(--unit) * 1);
        --s-1_5: calc(var(--unit) * 1.5);
        --s-2: calc(var(--unit) * 2);
        --s-2_5: calc(var(--unit) * 2.5);
        --s-3: calc(var(--unit) * 3);
        --s-4: calc(var(--unit) * 4);
        --s-5: calc(var(--unit) * 5);
        --s-6: calc(var(--unit) * 6);
        --s-8: calc(var(--unit) * 8);
        --s-10: calc(var(--unit) * 10);
        --s-12: calc(var(--unit) * 12);
        --s-16: calc(var(--unit) * 16);
        --s-20: calc(var(--unit) * 20);
        --s-24: calc(var(--unit) * 24);
        --s-32: calc(var(--unit) * 32);
        --s-40: calc(var(--unit) * 40);
        --s-48: calc(var(--unit) * 48);
        --s-56: calc(var(--unit) * 56);
        --s-64: calc(var(--unit) * 64);
        
        /* TYPOGRAPHY */
        --font-main: {theme.layout.font_sans};
        --font-mono: {theme.layout.font_mono};
        
        /* SHADOWS (Semantic) */
        --shadow-subtle: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-card: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-float: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }}
    
    body {{
        background-color: var(--c-surface-1);
        color: var(--c-text-main);
        font-family: var(--font-main);
        margin: 0;
    }}
    """

# --- 3. LOGIC ADAPTERS (For Backward Compatibility & Helper Logic) ---

class CategoryStyles:
    """Centralized management for category colors and ordering."""
    
    @staticmethod
    def get_color(category: str, theme: Theme) -> str:
        from sortomatic.l8n import Strings
        
        # Map to accents or theme colors
        mapping = {
            Strings.CAT_IMAGE: theme.colors.green,
            Strings.CAT_VIDEO: theme.colors.red,
            Strings.CAT_DOCUMENT: theme.colors.cyan,
            Strings.CAT_MUSIC: theme.colors.orange,
            Strings.CAT_ARCHIVE: theme.colors.yellow,
            Strings.CAT_CODE: theme.colors.blue,
            Strings.CAT_3D: theme.colors.magenta,
            Strings.CAT_SOFTWARE: theme.colors.violet,
            Strings.CAT_OTHER: theme.colors.debug,
        }
        return mapping.get(category, theme.colors.debug)

    @staticmethod
    def get_icon(category: str) -> str:
        from sortomatic.l8n import Strings
        mapping = {
            Strings.CAT_IMAGE: "mdi-image",
            Strings.CAT_VIDEO: "mdi-video",
            Strings.CAT_DOCUMENT: "mdi-file-document",
            Strings.CAT_MUSIC: "mdi-music",
            Strings.CAT_ARCHIVE: "mdi-archive",
            Strings.CAT_CODE: "mdi-console",
            Strings.CAT_3D: "mdi-cube-outline",
            Strings.CAT_SOFTWARE: "mdi-apps",
            Strings.CAT_OTHER: "mdi-file",
        }
        return mapping.get(category, "mdi-file")

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
        "active": READY,
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
    def get_color(state: str, theme: Theme) -> str:
        resolved = StatusStyles.resolve_state(state)
        mapping = {
            StatusStyles.UNKNOWN: theme.colors.debug,
            StatusStyles.PENDING: theme.colors.warning,
            StatusStyles.READY: theme.colors.success,
            StatusStyles.ERROR: theme.colors.error,
            StatusStyles.IDLE: theme.colors.info,
        }
        return mapping.get(resolved, theme.colors.debug)

    @staticmethod
    def get_icon(state: str) -> str:
        resolved = StatusStyles.resolve_state(state)
        mapping = {
            StatusStyles.UNKNOWN: "mdi-help-circle-outline",
            StatusStyles.PENDING: "mdi-sync",
            StatusStyles.READY: "mdi-check-circle",
            StatusStyles.ERROR: "mdi-alert-circle-outline",
            StatusStyles.IDLE: "mdi-pause-circle",
        }
        return mapping.get(resolved, "mdi-help-circle-outline")
