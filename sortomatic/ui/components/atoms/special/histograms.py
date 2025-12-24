from nicegui import ui
from typing import List, Optional

def AppHistogram(
    values: List[float], 
    color: str = 'var(--q-primary)',
    height: str = '24px',
    bar_width: str = '3px',
    gap: str = '1px',
    max_bars: int = 10,
    label: Optional[str] = None,
    icon: Optional[str] = None,
    transparent: bool = False
):
    """
    A premium inline histogram (sparkline) for performance monitoring.
    Supports dynamic updates to prevent UI flickering/blinking.
    """
    container_classes = 's-histogram'
    if not transparent:
        container_classes += ' shadow-sm'
    
    container_style = f'color: {color};'
    if transparent:
        container_style += ' background-color: transparent; border: none;'
        
    with ui.row().classes(container_classes).style(container_style) as container:
        container.tooltip = ui.tooltip('').classes('text-[10px] font-bold')
        
        if icon:
            from ..icons import AppIcon
            AppIcon(icon, size="1.2em", color=color).classes('opacity-80')

        # Bars Container
        with ui.row().classes('items-end no-wrap shrink-0 group').style(f'height: {height}; gap: {gap};') as bars_container:
            # Pre-create bars
            container.bars = [ui.element('div').classes('s-histogram__bar') for _ in range(max_bars)]
    
    def update_data(values: List[float]):
        """Update histogram bars and tooltip text without re-creating elements."""
        display_values = values[-max_bars:] if len(values) > max_bars else values
        latest_val = display_values[-1] if display_values else 0
        
        # Update tooltip
        container.tooltip.text = f"{label}: {latest_val*100:.1f}%" if label else f"{latest_val*100:.1f}%"
        
        # Update bars
        for i, bar in enumerate(container.bars):
            if i < len(display_values):
                val = display_values[i]
                # Ensure value is clamped
                clamped_val = max(0.05, min(1.0, val))
                
                bar.style(
                    f'height: {clamped_val * 100}%; '
                    f'width: {bar_width}; '
                    f'opacity: {0.4 + (clamped_val * 0.6)};'
                )
                bar.set_visibility(True)
            else:
                bar.set_visibility(False)

    container.update_data = update_data
    container.update_data(values)
    return container
