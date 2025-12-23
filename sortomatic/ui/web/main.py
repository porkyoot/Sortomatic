from nicegui import ui
from .theme import apply_theme
from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT

def start_app(port: int, theme: str, dark: bool):
    """Entry point for the NiceGUI application."""
    
    # Select Palette
    if theme == "solarized":
        palette = SOLARIZED_DARK if dark else SOLARIZED_LIGHT
    else:
        # Fallback or other themes
        palette = SOLARIZED_DARK if dark else SOLARIZED_LIGHT

    @ui.page('/')
    def main_page():
        apply_theme(palette)
        
        with ui.header().classes('bg-[var(--q-primary)] text-white p-4'):
            ui.label('Sortomatic').classes('text-2xl font-bold')
            
        with ui.column().classes('w-full items-center p-8'):
            ui.label(f'Welcome to Sortomatic GUI').classes('text-3xl font-bold')
            ui.label(f'Theme: {theme} ({"Dark" if dark else "Light"})').classes('text-lg opacity-70')
            
            with ui.row().classes('gap-4 mt-8'):
                ui.button('Dashboard', icon='dashboard').props('unelevated color=primary')
                ui.button('Explorer', icon='folder').props('unelevated color=secondary')

    ui.run(port=port, title="Sortomatic", dark=dark)
