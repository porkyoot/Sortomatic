from nicegui import ui
from typing import List, Dict, Optional, Callable, Set
from ...theme import Theme, CategoryStyles
from ..atoms.badges import CategoryBadge
from ..atoms.buttons import AppButton
from ..atoms.inputs.sliders import AppRangeSlider
from ..atoms.inputs.date_pickers import AppDatePicker
from ....l8n import Strings

def FilterBar(theme: Theme, on_change: Optional[Callable] = None):
    """
    A premium filter component with search and a detailed filter popup.
    """
    # Internal State
    state = {
        'search_text': "",
        'disabled_categories': set(),
        'size_range': {'min': 0, 'max': 1024 * 1024 * 1024 * 10},
        'date_range': None
    }

    def _trigger_change():
        if on_change:
            on_change({
                'search': state['search_text'],
                'disabled_categories': list(state['disabled_categories']),
                'size_range': state['size_range'],
                'date_range': state['date_range']
            })

    def _handle_search(e):
        state['search_text'] = e.value
        _trigger_change()

    def _handle_size(val):
        state['size_range'] = val
        _trigger_change()

    def _handle_date(val):
        state['date_range'] = val
        _trigger_change()

    def reset():
        state['disabled_categories'].clear()
        state['search_text'] = ""
        search_input.set_value("")
        state['size_range'] = {'min': 0, 'max': 1024**4}
        state['date_range'] = None
        
        menu.clear()
        with menu:
            _render_popup()
        _trigger_change()

    def _render_popup():
        with ui.column().classes('w-full gap-6'):
            # Header
            with ui.row().classes('w-full items-center justify-between'):
                ui.label("Filters").classes('s-section-header')
                ui.button(icon="refresh", on_click=reset).props('flat dense size=sm').classes('color-[var(--q-primary)]')

            # Categories
            ui.label("Categories").classes('s-label-uppercase-bold -mb-4')
            with ui.row().classes('w-full gap-2'):
                for cat in CategoryStyles.get_order():
                    is_disabled = cat in state['disabled_categories']
                    
                    def toggle(c=cat):
                        if c in state['disabled_categories']:
                            state['disabled_categories'].remove(c)
                        else:
                            state['disabled_categories'].add(c)
                        menu.clear() # Re-render the interior
                        with menu:
                            _render_popup()
                        _trigger_change()

                    CategoryBadge(
                        cat, 
                        theme, 
                        interactive=True, 
                        disabled=is_disabled,
                        on_click=toggle
                    )

            # Size Range (Logarithmic)
            ui.label("Size Range").classes('s-label-uppercase-bold -mb-4')
            AppRangeSlider(
                min=0, 
                max=1024**4, # 1TB
                value=state['size_range'],
                log=True,
                on_change=_handle_size
            )

            # Date Range
            ui.label("Date Range").classes('s-label-uppercase-bold -mb-4')
            AppDatePicker(
                label="", 
                mode="range",
                value=state['date_range'],
                on_change=_handle_date
            )

    with ui.row().classes('w-full items-center gap-4 no-wrap') as row:
        # 1. Search input
        search_input = ui.input(placeholder="Search indexed files...").classes('flex-grow').props('outlined dense rounded-app')
        search_input.on('update:model-value', _handle_search)
        
        # 2. Filter Trigger Button
        with AppButton(icon="filter_list", variant="secondary", shape="pill"):
            with ui.menu().classes('s-select__popup min-w-[350px]') as menu:
                _render_popup()

    row.reset = reset
    return row
