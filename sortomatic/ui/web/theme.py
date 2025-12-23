from dataclasses import dataclass
from nicegui import ui

@dataclass
class ColorPalette:
    bg: str
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

def apply_theme(palette: ColorPalette):
    """Injects CSS variables to override Quasar/NiceGUI defaults."""
    ui.add_head_html(f'''
    <style>
        :root {{
            --q-primary: {palette.primary};
            --q-secondary: {palette.secondary};
            --q-dark: {palette.bg};
            --app-bg: {palette.bg};
            --app-text: {palette.fg};
            --app-text-sec: {palette.fg_secondary};
        }}
        body {{
            background-color: var(--app-bg);
            color: var(--app-text);
        }}
    </style>
    ''')
    # Force Quasar into dark mode if background is dark
    ui.dark_mode(True if palette.bg == "#002b36" else False)
