from nicegui import ui
from .theme import apply_theme
from .themes.solarized import SOLARIZED_DARK, SOLARIZED_LIGHT

def start_app(port: int, theme: str, dark: bool, path: str = None):
    """Entry point for the NiceGUI application."""
    print(f"DEBUG: Starting app on port {port} with path {path}")
    
    # Select Palette
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
        client = ui.context.client
        apply_theme(palette)
        
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
        
        with ui.header().classes('bg-[var(--q-primary)] text-white p-4'):
            ui.label('Sortomatic').classes('text-2xl font-bold')
            
        with ui.column().classes('w-full items-center p-8 gap-6'):
            ui.label(f'Sortomatic Web Interface').classes('text-3xl font-black italic tracking-tighter color-[var(--q-primary)]')
            
            with ui.row().classes('gap-4'):
                from .components.atoms.badges import AppBadge, CategoryBadge, StatusBadge, CopyBadge
                from .components.atoms.buttons import AppButton
                from .components.atoms.cards import AppCard
                from .components.molecules.status_bars import StatusBar
                from ..l8n import Strings
                
                StatusBadge("System", "ready", palette)
                CategoryBadge("Code", palette)
                CopyBadge("SHA256:e3b0c442...", label="Hash")

            with AppCard(variant='vibrant', padding='p-8').classes('max-w-lg'):
                ui.label("Hello World!").classes('text-2xl font-bold mb-4')
                ui.label("The GUI components are now initialized and themed.").classes('opacity-70 mb-6')
                
                AppButton(
                    "Launch Scan", 
                    icon="rocket_launch", 
                    variant="primary", 
                    shape="pill",
                    on_click=lambda: ui.notify("Scan triggered!", color="var(--q-primary)")
                )

            # Showcase FileRow
            ui.label("Sample File Row").classes('text-xl font-bold mt-8 self-start')
            from .components.molecules.file_rows import FileRow
            from ..core.types import ScanContext
            from datetime import datetime
            
            sample_file = ScanContext({
                'path': '/home/user/projects/sortomatic/l8n/strings.py',
                'filename': 'strings.py',
                'category': 'Code',
                'size_bytes': 2049,
                'modified_at': datetime.now()
            })
            FileRow(sample_file, palette)

            sample_file_big = ScanContext({
                'path': '/home/user/downloads/movies/big_buck_bunny.mp4',
                'filename': 'big_buck_bunny.mp4',
                'category': 'Video',
                'size_bytes': 1024 * 1024 * 1500, # 1.5 GB
                'modified_at': datetime(2022, 5, 20)
            })
            FileRow(sample_file_big, palette)

            # Showcase FileTree
            ui.label("Interactive File Tree").classes('text-xl font-bold mt-12 self-start')
            
            from .components.molecules.filters import FilterBar
            FilterBar(palette, on_change=lambda e: ui.notify(f"Filters updated: {e}"))
            
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                search = ui.input(placeholder="Search files...").classes('flex-grow').props('outlined dense')

            from .components.molecules.file_tree import FileTree
            tree = FileTree(path or "/", palette)
            
            # Hook search to tree
            search.on('update:model-value', lambda e: tree.set_filter(e.value))

            # Showcase WorkflowMenu
            ui.label("Workflow Menu").classes('text-xl font-bold mt-12 self-start')
            from .components.molecules.menus import WorkflowMenu, MenuStep
            
            with WorkflowMenu():
                MenuStep("Analysis", "search", state="available", progress_values=[1.0, 0.4], palette=palette)
                MenuStep("Categorize", "category", state="inactive", progress_values=[0], palette=palette)
                MenuStep("Hash", "fingerprint", state="unavailable", palette=palette)
                MenuStep("Clean", "delete", state="inactive", palette=palette)

            # Showcase AppHistogram (Performance)
            ui.label("System Monitor").classes('text-xl font-bold mt-12 self-start')
            from .components.atoms.special.histograms import AppHistogram
            import random
            
            # Persistent state for demo
            stats = {
                'cpu': [random.random() for _ in range(30)],
                'ram': [random.random() for _ in range(30)],
                'disk': [random.random() for _ in range(30)]
            }

            with ui.row().classes('w-full items-center gap-8 p-4 bg-white/5 rounded-app border border-white/5'):
                with ui.column().classes('items-center gap-1'):
                    ui.label("CPU").classes('text-[10px] font-bold opacity-50 uppercase')
                    cpu_hist = ui.row()
                    with cpu_hist: AppHistogram(stats['cpu'], color=palette.green, label="CPU")
                
                with ui.column().classes('items-center gap-1'):
                    ui.label("RAM").classes('text-[10px] font-bold opacity-50 uppercase')
                    ram_hist = ui.row()
                    with ram_hist: AppHistogram(stats['ram'], color=palette.blue, label="RAM")

                with ui.column().classes('items-center gap-1'):
                    ui.label("DISK").classes('text-[10px] font-bold opacity-50 uppercase')
                    disk_hist = ui.row()
                    with disk_hist: AppHistogram(stats['disk'], color=palette.orange, label="I/O")

            def update_stats():
                # Check if client is still connected
                if not client.has_socket_connection:
                    return
                    
                try:
                    for key in stats:
                        stats[key].append(random.random())
                    cpu_hist.clear()
                    with cpu_hist: AppHistogram(stats['cpu'], color=palette.green, label="CPU")
                    ram_hist.clear()
                    with ram_hist: AppHistogram(stats['ram'], color=palette.blue, label="RAM")
                    disk_hist.clear()
                    with disk_hist: AppHistogram(stats['disk'], color=palette.orange, label="I/O")
                except Exception:
                    pass

            ui.timer(1.0, update_stats)

            # Showcase ScanControls
            ui.label("Scan Controls").classes('text-xl font-bold mt-12 self-start')
            from .components.molecules.scan_controls import ScanControls
            
            with ui.row().classes('w-full items-center justify-between'):
                controls = ScanControls(
                    palette=palette,
                    on_play=lambda: ui.notify("Scan Started!"),
                    on_pause=lambda: (controls.set_state("paused"), ui.notify("Scan Paused")),
                    on_resume=lambda: (controls.set_state("running"), ui.notify("Scan Resumed")),
                    on_restart=lambda: (controls.set_state("running"), ui.notify("Scan Restarted")),
                    on_fast_mode=lambda v: ui.notify(f"Fast Mode: {'ON' if v else 'OFF'}")
                )
                
                # Mock state switcher for demo
                with ui.row().classes('gap-2 items-center'):
                    ui.label("Demo State:").classes('text-xs opacity-50')
                    ui.select(
                        options=["idle", "running", "paused", "completed"],
                        value="idle",
                        on_change=lambda e: controls.set_state(e.value)
                    ).props('dense outlined rounded-app').classes('w-32')

            # Showcase ScanCard
            ui.label("Scan Task Management").classes('text-xl font-bold mt-12 self-start')
            from .components.organisms.scans import ScanCard
            
            with ui.column().classes('w-full gap-4'):
                ScanCard(
                    name="Primary Disk Index",
                    state="running",
                    progress=45.2,
                    eta="12m 30s",
                    palette=palette,
                    on_play=lambda: ui.notify("Started"),
                    on_pause=lambda: ui.notify("Paused")
                )
                
                ScanCard(
                    name="External Archive Scan",
                    state="completed",
                    progress=100.0,
                    eta="Done",
                    palette=palette
                )

                ScanCard(
                    name="Network Shared Drive",
                    state="error",
                    progress=12.5,
                    eta="Failed",
                    palette=palette
                )

            # Showcase Terminal
            ui.label("System Logs").classes('text-xl font-bold mt-12 self-start')
            from .components.organisms.terminals import AppTerminal
            
            terminal = AppTerminal(height='200px')
            
            # Simulated logs
            log_btn = AppButton("Generate Log", icon="add", on_click=lambda: terminal.log(f"[{datetime.now().strftime('%H:%M:%S')}] Event: New data packet received.", color=palette.cyan))
            
            def auto_log():
                if not client.has_socket_connection:
                    return
                msgs = [
                    ("Index: Scanning /home/user/photos...", palette.blue),
                    ("Hash: Match found for image_01.jpg", palette.green),
                    ("Error: Permission denied on /root/hidden", palette.red),
                    ("Status: 500 files items processed", palette.yellow),
                ]
                import random
                m, c = random.choice(msgs)
                terminal.log(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", color=c)
            
            ui.timer(3.0, auto_log)

            # Showcase Thumbnails
            ui.label("Content Previews").classes('text-xl font-bold mt-12 self-start')
            from .components.organisms.thumbnails import AppThumbnail
            
            with ui.row().classes('w-full gap-6 overflow-x-auto py-4 no-wrap'):
                # Image
                AppThumbnail(type='image', content='https://picsum.photos/id/237/200/200')
                
                # Text
                AppThumbnail(type='text', content="""def main():
    print("Hello Sortomatic!")
    for i in range(10):
        process_file(i)
        
# Internal logic starts here
# Very long file sample...""")

                # HTML
                AppThumbnail(type='html', content="""<h1 style='color:var(--q-primary)'>Report</h1>
<p>This is a <b>sample document</b> preview with custom styles and scaling.</p>
<ul>
  <li>Fast scanning</li>
  <li>AI grouping</li>
</ul>""")

                # Tree
                AppThumbnail(type='tree', content=['app/', 'static/', 'index.html', 'package.json', 'README.md'])

        # StatusBar must be a direct child of the page
        status_bar = StatusBar(palette, on_theme_change=lambda t, d: bridge.emit("theme_changed", {'name': t, 'is_dark': d}))
        
        # Handle metric updates via Bridge
        def on_metrics(data):
            status_bar.update_metrics(data['cpu'], data['ram'])
        bridge.on("metrics_updated", on_metrics)

        # Mock metric emitter
        def emit_mock_metrics():
            if not client.has_socket_connection:
                return
            bridge.emit("metrics_updated", {
                'cpu': [random.random() for _ in range(20)],
                'ram': [random.random() for _ in range(20)]
            })
        ui.timer(1.0, emit_mock_metrics)

    ui.run(host='0.0.0.0', port=port, title="Sortomatic", dark=dark, reload=False)
