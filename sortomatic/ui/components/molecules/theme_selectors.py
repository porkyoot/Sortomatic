from nicegui import ui
from typing import Optional, Callable
from ..atoms.buttons import AppButton
from ..atoms.inputs.selects import AppSelect

def ThemeSelector(
    current_theme: str = "solarized", 
    is_dark: bool = True, 
    on_change: Optional[Callable] = None
):
    """
    A theme and dark-mode selector component.
    Features a theme dropdown and a dynamic Sun/Moon toggle.
    """
    # State managed by local variables (will be captured by closures)
    state = {
        'theme': current_theme,
        'dark': is_dark
    }

    def _toggle_mode():
        state['dark'] = not state['dark']
        ui.dark_mode(state['dark'])
        _render()
        if on_change:
            on_change(state['theme'], state['dark'])

    def _handle_theme_change(theme_name: str):
        new_theme = theme_name.lower()
        if new_theme == state['theme']:
            return
        state['theme'] = new_theme
        _render()
        if on_change:
            on_change(state['theme'], state['dark'])

    def _render():
        row.clear()
        with row:
            # 1. Theme Dropdown (AppSelect)
            AppSelect(
                options={'solarized': 'Solarized'},
                value=state['theme'],
                on_change=lambda e: _handle_theme_change(e.value),
                variant="simple",
                clearable=False,
                classes='s-label-uppercase-bold'
            )

            # 2. Vertical Divider
            ui.element('div').classes('s-separator-vertical')

            # 3. Dynamic Toggle Button
            if state['dark']:
                AppButton(
                    icon="mdi-white-balance-sunny",
                    on_click=_toggle_mode,
                    shape="circle",
                    size="xs",
                    variant="simple",
                    tooltip="Switch to Light Mode"
                ).classes('s-theme-toggle--light')
            else:
                AppButton(
                    icon="mdi-weather-night",
                    on_click=_toggle_mode,
                    shape="circle",
                    size="xs",
                    variant="simple",
                    tooltip="Switch to Dark Mode"
                ).classes('s-theme-toggle--dark')

    row = ui.row().classes('s-theme-selector shadow-sm')
    _render()
    return row
