from nicegui import ui
from typing import List, Optional
from ..atoms.cards import AppCard

def AppTerminal(
    height: str = '300px', 
    title: str = "System Logs",
    flush_interval: float = 0.1,
    max_history: int = 500
):
    """
    A premium monospaced log terminal with sticky auto-scroll behavior.
    """
    # Terminal uses a very subtle, dark variant. 
    # Since AppCard is a function returning ui.card, we use it as context.
    card = AppCard(variant='', padding='', tight=True) 
    card.classes('s-terminal w-full flex flex-col')
    
    with card:
        # Header
        with ui.row().classes('w-full s-terminal__header'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('terminal', size='14px').classes('s-terminal__icon')
                ui.label(title).classes('s-terminal__title')
            
            with ui.row().classes('gap-1'):
                # Decorative dots
                ui.element('div').classes('s-terminal__dot s-terminal__dot--red')
                ui.element('div').classes('s-terminal__dot s-terminal__dot--yellow')
                ui.element('div').classes('s-terminal__dot s-terminal__dot--green')

        # Scroll Area
        # Handle height: if it contains 'h-' or 'min-h-', treat as class for responsiveness.
        # Otherwise treat as fixed CSS value for style attribute.
        is_css_class = any(x in height for x in ['h-', 'min-h-', 'max-h-'])
        
        scroll = ui.scroll_area().classes('w-full')
        if is_css_class:
            scroll.classes(height)
        else:
            scroll.style(f'height: {height};')
            
        with scroll:
            content = ui.html('', sanitize=False).classes('s-terminal__content')
    
    # Internal state managed in a closure
    state = {
        'is_sticky': True,
        'log_buffer': [],
        'pending_logs': [],
        'max_history': max_history
    }

    def _handle_scroll(e):
        """Track user scroll position to enable/disable auto-scroll."""
        if e.vertical_percentage >= 0.99:
            state['is_sticky'] = True
        else:
            state['is_sticky'] = False

    def log(message: str, color: Optional[str] = None):
        """Queue a message to be displayed in the terminal."""
        styled_msg = message
        if color:
            styled_msg = f'<span style="color: {color};">{message}</span>'
        state['pending_logs'].append(styled_msg)

    def _flush_logs():
        """Internal method called by timer to flush buffered logs to the UI."""
        if not state['pending_logs']:
            return
        
        state['log_buffer'].extend(state['pending_logs'])
        
        # Trim history if needed
        if len(state['log_buffer']) > state['max_history']:
            overflow = len(state['log_buffer']) - state['max_history']
            state['log_buffer'] = state['log_buffer'][overflow:]
        
        content.set_content("<br>".join(state['log_buffer']))
        state['pending_logs'].clear()
        
        if state['is_sticky']:
            ui.timer(0.05, lambda: scroll.scroll_to(percent=1.0), once=True)

    def clear_logs():
        """Clear all logs and pending messages."""
        state['log_buffer'] = []
        state['pending_logs'] = []
        content.set_content("")

    # Attach events and timers
    scroll.on('scroll', _handle_scroll)
    ui.timer(flush_interval, _flush_logs)

    # Attach methods to the returned element
    card.log = log
    card.push = log # Alias for log() to match NiceGUI's ui.log().push() API.
    card.clear_logs = clear_logs
    card.flush_immediately = _flush_logs
    
    return card

