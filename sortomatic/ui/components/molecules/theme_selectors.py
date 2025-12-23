from nicegui import ui
from typing import Optional, Callable
from ...theme import apply_theme
from ..atoms.buttons import AppButton
from ..atoms.inputs.selects import AppSelect

class ThemeSelector(ui.row):
    """
    A theme and dark-mode selector component.
    Features a theme dropdown and a dynamic Sun/Moon toggle.
    """
    def __init__(self, 
                 current_theme: str = "solarized", 
                 is_dark: bool = True, 
                 on_change: Optional[Callable] = None):
        super().__init__()
        self.classes('flex flex-row items-center gap-2 px-4 py-1 rounded-full border bg-app-base no-wrap')
        self.style('border-color: var(--app-text-sec);')

        self.current_theme = current_theme
        self.is_dark = is_dark
        self.on_change = on_change
        
        self.render()

    def render(self):
        self.clear()
        with self:
            # 1. Theme Dropdown (Label + Menu)
            # Replaced heavy AppSelect with lightweight Label+Menu to match Badge height
            with ui.row().classes('items-center gap-1 cursor-pointer group'):
                ui.label(self.current_theme.capitalize()).classes('text-[10px] font-bold uppercase tracking-widest text-app-main')
                ui.icon('mdi-chevron-down', size='12px').classes('opacity-50 group-hover:opacity-100 transition-opacity text-app-main')
                
                with ui.menu().classes('bg-app-base border border-app shadow-lg rounded-app'):
                    # Hardcoded options for now
                    ui.menu_item('Solarized', on_click=lambda: self._handle_theme_change('solarized')).classes('text-[10px] uppercase font-bold tracking-widest text-app-main')

            # 2. Vertical Divider (Height 3 to match BadgeRow)
            ui.element('div').classes('h-3 w-0 border-app-subtle')

            # 3. Dynamic Toggle Button
            # Dark Mode Enabled -> Show Sun (to switch to light)
            # Light Mode Enabled -> Show Moon with stars (to switch to dark)
            if self.is_dark:
                # Orange Sun
                btn = AppButton(
                    icon="mdi-white-balance-sunny",
                    on_click=self._toggle_mode,
                    shape="circle",
                    size="xs",  # Reduced to XS to match dense badges
                    variant="simple",
                    tooltip="Switch to Light Mode"
                ).style('--q-primary: var(--app-orange);') # Theme Orange
            else:
                # Blue Moon with Stars (nights_stay)
                btn = AppButton(
                    icon="mdi-weather-night",
                    on_click=self._toggle_mode,
                    shape="circle",
                    size="xs",  # Reduced to XS
                    variant="simple",
                    tooltip="Switch to Dark Mode"
                ).style('--q-primary: var(--app-blue);') # Theme Blue

    def _toggle_mode(self):
        self.is_dark = not self.is_dark
        ui.dark_mode(self.is_dark)
        self.render()
        if self.on_change:
            self.on_change(self.current_theme, self.is_dark)

    def _handle_theme_change(self, theme_name: str):
        self.current_theme = theme_name.lower()
        self.render()
        if self.on_change:
            self.on_change(self.current_theme, self.is_dark)
