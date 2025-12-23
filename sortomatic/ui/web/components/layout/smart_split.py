from nicegui import ui

class SmartSplitter(ui.element):
    def __init__(self, left_content, right_content):
        super().__init__('div')
        self.classes('w-full h-full')
        
        # 1. Mobile View (Column) - Hidden on desktop (lg)
        with ui.column().classes('w-full lg:hidden'):
            left_content()
            ui.separator()
            right_content()
            
        # 2. Desktop View (Splitter) - Hidden on mobile
        with ui.splitter(value=30).classes('w-full h-full hidden lg:block') as splitter:
            with splitter.before:
                left_content()
            with splitter.after:
                right_content()