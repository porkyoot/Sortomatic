from nicegui import ui
import asyncio

class LazyCardList(ui.column):
    def __init__(self, item_provider):
        super().__init__()
        self.classes('w-full gap-4')
        self.provider = item_provider
        self.is_loaded = False
        
        # Initial Render: Skeleton
        with self:
            self.skeletons = ui.column().classes('w-full gap-4')
            with self.skeletons:
                for _ in range(5):
                    with ui.card().classes('w-full h-32 animate-pulse bg-gray-700'):
                        pass
                        
        # Trigger load
        ui.timer(0.1, self.load_real_data, once=True)

    async def load_real_data(self):
        # Allow UI to render first
        await asyncio.sleep(0.1) 
        items = self.provider() # Fetch data
        
        self.skeletons.set_visibility(False)
        self.clear() # Remove skeletons
        
        # Render real cards
        with self:
            for item in items:
                self._render_card(item)