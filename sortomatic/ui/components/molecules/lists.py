from nicegui import ui
import asyncio

def LazyCardList(item_provider, card_renderer=None):
    """
    A list that shows skeletons while loading data asynchronously.
    """
    container = ui.column().classes('w-full gap-4')
    
    # Initial Render: Skeleton
    with container:
        skeletons = ui.column().classes('w-full gap-4')
        with skeletons:
            for _ in range(5):
                with ui.card().classes('s-skeleton'):
                    pass
    
    async def load_real_data():
        # Allow UI to render first
        await asyncio.sleep(0.1) 
        items = item_provider() # Fetch data
        
        skeletons.set_visibility(False)
        container.clear() # Remove skeletons
        
        # Render real cards
        with container:
            for item in items:
                if card_renderer:
                    card_renderer(item)
                # If no renderer provided, we just skip or do a default
    
    # Trigger load
    ui.timer(0.1, load_real_data, once=True)
    
    container.load_real_data = load_real_data
    return container