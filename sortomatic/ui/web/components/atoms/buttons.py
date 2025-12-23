from nicegui import ui

def themed_button(text: str, icon: str = None, on_click=None, kind='primary'):
    """
    Kinds: primary (accent 1), secondary (accent 2), ghost (transparent)
    """
    colors = {
        'primary': 'bg-[var(--q-primary)] text-[var(--app-bg)]',
        'secondary': 'bg-[var(--q-secondary)] text-[var(--app-bg)]',
        'ghost': 'bg-transparent text-[var(--q-primary)] border border-[var(--q-primary)]'
    }
    
    return ui.button(text, icon=icon, on_click=on_click).classes(
        f"{colors.get(kind, 'primary')} rounded-md shadow-sm transition-transform hover:scale-105"
    ).props('unelevated no-caps')