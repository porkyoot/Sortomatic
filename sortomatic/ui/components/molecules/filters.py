from nicegui import ui
from typing import List, Dict, Optional, Callable, Set
from ...theme import Theme, CategoryStyles
from ..atoms.badges import CategoryBadge
from ..atoms.buttons import AppButton
from ..atoms.inputs.sliders import AppRangeSlider
from ..atoms.inputs.date_pickers import AppDatePicker
from ....l8n import Strings

class FilterBar(ui.row):
    """
    A premium filter component with search and a detailed filter popup.
    """
    def __init__(self, theme: Theme, on_change: Optional[Callable] = None):
        super().__init__()
        self.classes('w-full items-center gap-4 no-wrap')
        self.theme = theme
        self.on_change = on_change
        
        # Internal State
        self.search_text = ""
        self.disabled_categories: Set[str] = set()
        self.size_range = {'min': 0, 'max': 1024 * 1024 * 1024 * 10} # Default 10GB
        self.date_range = None # {'from': '...', 'to': '...'}
        
        with self:
            # 1. Search input
            self.search_input = ui.input(placeholder="Search indexed files...").classes('flex-grow').props('outlined dense rounded-app')
            self.search_input.on('update:model-value', self._handle_search)
            
            # 2. Filter Trigger Button
            with AppButton(icon="filter_list", variant="secondary", shape="pill") as self.btn:
                with ui.menu().classes('p-4 min-w-[350px] rounded-app glass vibrant-shadow border border-white/10') as self.menu:
                    self._render_popup()

    def _render_popup(self):
        with ui.column().classes('w-full gap-6'):
            # Header
            with ui.row().classes('w-full items-center justify-between'):
                ui.label("Filters").classes('text-lg font-black uppercase tracking-widest opacity-80')
                ui.button(icon="refresh", on_click=self.reset).props('flat dense size=sm').classes('color-[var(--q-primary)]')

            # Categories
            ui.label("Categories").classes('text-[10px] font-bold uppercase tracking-widest opacity-40 -mb-4')
            with ui.row().classes('w-full gap-2'):
                for cat in CategoryStyles.get_order():
                    is_disabled = cat in self.disabled_categories
                    # Note: We need to use a closure to capture the category name correctly
                    def toggle(c=cat):
                        if c in self.disabled_categories:
                            self.disabled_categories.remove(c)
                        else:
                            self.disabled_categories.add(c)
                        self.menu.clear() # Re-render the interior
                        with self.menu:
                            self._render_popup()
                        self._trigger_change()

                    CategoryBadge(
                        cat, 
                        self.theme, 
                        interactive=True, 
                        disabled=is_disabled,
                        on_click=toggle
                    )

            # Size Range (Logarithmic)
            ui.label("Size Range").classes('text-[10px] font-bold uppercase tracking-widest opacity-40 -mb-4')
            AppRangeSlider(
                min=0, 
                max=1024**4, # 1TB
                value=self.size_range,
                log=True,
                on_change=self._handle_size
            )

            # Date Range
            ui.label("Date Range").classes('text-[10px] font-bold uppercase tracking-widest opacity-40 -mb-4')
            AppDatePicker(
                label="", 
                mode="range",
                value=self.date_range,
                on_change=self._handle_date
            )

    def _handle_search(self, e):
        self.search_text = e.value
        self._trigger_change()

    def _handle_size(self, val):
        self.size_range = val
        self._trigger_change()

    def _handle_date(self, val):
        self.date_range = val
        self._trigger_change()

    def reset(self):
        self.disabled_categories.clear()
        self.search_text = ""
        self.search_input.set_value("")
        self.size_range = {'min': 0, 'max': 1024**4}
        self.date_range = None
        
        self.menu.clear()
        with self.menu:
            self._render_popup()
        self._trigger_change()

    def _trigger_change(self):
        if self.on_change:
            self.on_change({
                'search': self.search_text,
                'disabled_categories': list(self.disabled_categories),
                'size_range': self.size_range,
                'date_range': self.date_range
            })
