from nicegui import ui
from .theme import apply_theme
from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT

def start_app(port: int, theme: str, dark: bool, path: str = None):
    """Entry point for the NiceGUI application."""
    print(f"DEBUG: Starting app on port {port} with path {path}")
    
    # Select Palette BEFORE page definition
    if theme == "solarized":
        palette = SOLARIZED_DARK if dark else SOLARIZED_LIGHT
    else:
        # Fallback or other themes
        palette = SOLARIZED_DARK if dark else SOLARIZED_LIGHT

    # Initialize Backend Bridge
    from sortomatic.core.bridge import bridge
    from sortomatic.core.service import init_bridge_handlers
    init_bridge_handlers()

    @ui.page('/')
    def main_page():
        # CRITICAL: Apply theme FIRST, before ANY other code
        # This prevents Flash of Unstyled Content (FOUC)
        apply_theme(palette)
        
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
            new_palette = SOLARIZED_DARK if is_dark else SOLARIZED_LIGHT
            apply_theme(new_palette)
            ui.notify(f"Theme switched", color="var(--q-primary)")

        bridge.on("theme_changed", handle_theme_change)
        
        # Import badge components
        from .components.atoms.badges import StatusBadge
        from .components.molecules.theme_selectors import ThemeSelector
        from sortomatic.core.database import db
        
        # Simple status bar at the top with app name on the left, status badges in the middle
        with ui.header().classes('bg-[var(--app-bg-secondary)] border-b border-white/10 px-4 py-2 items-center justify-between'):
            # Left: App name and theme selector
            with ui.row().classes('items-center gap-3'):
                ui.label('Sortomatic').classes('text-lg font-bold text-[var(--app-text)]')
                ThemeSelector(
                    current_theme=theme,
                    is_dark=dark,
                    on_change=lambda t, d: bridge.emit("theme_changed", {'name': t, 'is_dark': d})
                )
            
            # Middle: Status badges
            with ui.row().classes('items-center gap-3'):
                # Backend status
                backend_badge_container = ui.row()
                with backend_badge_container:
                    StatusBadge("Backend", "ready", palette)
                
                # Database status
                db_badge_container = ui.row()
                with db_badge_container:
                    db_state = "ready" if db.obj and not db.is_closed() else "error"
                    StatusBadge("Database", db_state, palette)
                
                # Scan status
                scan_badge_container = ui.row()
                with scan_badge_container:
                    StatusBadge("Scan", "idle", palette)
            
            # Right: Empty for now (could add controls later)
            ui.element('div').classes('w-20')  # Spacer to keep badges centered
        
        # Update status badges periodically
        def update_status_badges():
            if not client.has_socket_connection:
                return
            
            try:
                # Update DB status
                db_state = "ready" if db.obj and not db.is_closed() else "error"
                db_badge_container.clear()
                with db_badge_container:
                    StatusBadge("Database", db_state, palette)
                
                # Update scan status (placeholder - will be connected to actual scan state later)
                # scan_state = get_scan_state()  # TODO: implement actual scan state checking
                scan_badge_container.clear()
                with scan_badge_container:
                    StatusBadge("Scan", "idle", palette)
            except Exception:
                pass
        
        ui.timer(5.0, update_status_badges)  # Check every 5 seconds
        
        # Main content area (empty for now)
        with ui.column().classes('w-full h-full'):
            pass

    ui.run(host='0.0.0.0', port=port, title="Sortomatic", dark=dark, reload=False)
