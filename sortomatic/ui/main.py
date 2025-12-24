from nicegui import ui
from .styles import load_global_styles
from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT

def start_app(port: int, theme: str, dark: bool, path: str = None):
    """Entry point for the NiceGUI application."""
    print(f"DEBUG: Starting app on port {port} with path {path}")
    
    # Select Theme BEFORE page definition
    if theme == "solarized":
        app_theme = SOLARIZED_DARK if dark else SOLARIZED_LIGHT
    else:
        # Fallback or other themes
        app_theme = SOLARIZED_DARK if dark else SOLARIZED_LIGHT

    # Initialize Backend Bridge
    from sortomatic.core.bridge import bridge
    from sortomatic.core.service import init_bridge_handlers
    init_bridge_handlers()

    @ui.page('/')
    def main_page():
        # CRITICAL: Apply theme FIRST, before ANY other code
        # This prevents Flash of Unstyled Content (FOUC)
        load_global_styles(app_theme)
        
        # Now get client for event handlers
        client = ui.context.client
        
        # 1. Global Page State & Handlers
        def handle_theme_change(theme_info):
            # Check if client is still connected
            if not client.has_socket_connection:
                return
            # theme_info: { 'name': str, 'is_dark': bool }
            from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT
            is_dark = theme_info.get('is_dark', True)
            new_theme = SOLARIZED_DARK if is_dark else SOLARIZED_LIGHT
            load_global_styles(new_theme)
            ui.notify(f"Theme switched", color="var(--c-primary)")

        bridge.on("theme_changed", handle_theme_change)
        
        # Import badge components
        # Import StatusBar
        from .components.molecules.status_bars import StatusBar
        from sortomatic.core.database import db
        
        # Instantiate the new top status bar
        status_bar = StatusBar(
            app_theme, 
            on_theme_change=lambda t, d: bridge.emit("theme_changed", {'name': t, 'is_dark': d})
        )
        
        # Metrics history buffers
        history = {
            'cpu': [0.0] * 50,
            'gpu': [0.0] * 50,
            'ram': [0.0] * 50,
            'disk': [0.0] * 50
        }

        # Update status badges periodically
        async def update_status_badges():
            if not client.has_socket_connection:
                return
            
            try:
                # 1. Update Metrics (Real Data)
                metrics = await bridge.request("get_system_metrics")
                if metrics:
                    for key in ['cpu', 'gpu', 'ram', 'disk']:
                         val = metrics.get(key, 0.0)
                         history[key].append(val)
                         history[key] = history[key][-50:] # Keep buffer limited
                    
                    status_bar.update_metrics(
                        history['cpu'], 
                        history['gpu'], 
                        history['ram'], 
                        history['disk']
                    )
                
                # 2. Update System Status
                status = await bridge.request("get_system_status")
                if status:
                    status_bar.refresh_status(
                        backend_state=status.get("backend", "unknown"),
                        db_state=status.get("database", "unknown"),
                        scan_state=status.get("scan", "unknown")
                    )

            except Exception:
                pass
        
        ui.timer(1.0, update_status_badges)  # Check every 1 second for smooth histograms
        
        # Main content area (empty for now)
        with ui.column().classes('w-full h-full'):
            pass

    ui.run(host='0.0.0.0', port=port, title="Sortomatic", dark=dark, reload=False)
