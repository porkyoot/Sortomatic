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
        # Track current theme to avoid redundant injections
        client.theme_name = theme  # Store initial

        def handle_theme_change(theme_info):
            if not client.has_socket_connection:
                return
            is_dark = theme_info.get('is_dark', True)
            new_theme_name = "solarized_dark" if is_dark else "solarized_light"
            
            # Deduplicate: don't re-inject if already active
            if getattr(client, 'theme_name', None) == new_theme_name:
                return
            client.theme_name = new_theme_name

            from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT
            new_theme = SOLARIZED_DARK if is_dark else SOLARIZED_LIGHT
            load_global_styles(new_theme)

        bridge.on("theme_changed", handle_theme_change)
        
        # Cleanup bridge listener on disconnect
        client.on_disconnect(lambda: bridge.off("theme_changed", handle_theme_change))
        
        # Import badge components
        # Import StatusBar
        from .components.molecules.status_bars import StatusBar
        from sortomatic.core.database import db
        
        def on_theme_toggle(t, d):
            ui.notify(f"Theme switched", color="var(--c-primary)")
            bridge.emit("theme_changed", {'name': t, 'is_dark': d})

        # Instantiate the new top status bar
        status_bar = StatusBar(
            app_theme, 
            on_theme_change=on_theme_toggle
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
        # Main content area
        from .components.layout.smart_split import SmartSplitter
        from .components.organisms.scans import ScanCard
        from .components.organisms.terminals import AppTerminal

        # We need to track instances to update them, as SmartSplitter creates duplicates for responsiveness
        active_terminals = []
        active_scancards = []
        
        def create_scan_card():
            # Create a ScanCard and track it
            card = ScanCard(
                name="File Discovery",
                state="idle",
                progress=0.0,
                eta="--:--",
                theme=app_theme,
                on_play=lambda: ui.notify("Starting scan...", type='info'),
                on_restart=lambda: ui.notify("Restarting scan...", type='warning'),
            )
            # Layout is handled by CSS grid now
            card.classes('w-full h-full') 
            active_scancards.append(card)
            
        def create_terminal():
            # Create Terminal and track it
            term = AppTerminal(
                height='100%', 
                title="System Events"
            )
            term.classes('h-full')
            active_terminals.append(term)

        # Container for the main view content
        with ui.element('div').classes('s-main-view'):
            SmartSplitter(
                left_factory=create_scan_card,
                right_factory=create_terminal,
                initial_split=40, # 40% for scan card
                separator=True
            )

        # 3. Bridge Listeners for Updates
        def handle_log_record(record):
            if not client.has_socket_connection:
                return
            for term in active_terminals:
                term.log(record.get('message', ''), color=record.get('color'))
                
        bridge.on("log_record", handle_log_record)
        
        # Cleanup listeners
        client.on_disconnect(lambda: bridge.off("log_record", handle_log_record))

    ui.run(host='0.0.0.0', port=port, title="Sortomatic", dark=dark, reload=False)
