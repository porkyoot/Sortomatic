from nicegui import ui
from typing import Optional

def AppCard(
    variant: str = 'glass', # 'solid', 'glass', 'subtle', 'vibrant'
    padding: str = '',      # Optional override, s-card has default p-6 equivalent
    tight: bool = False
):
    """
    A premium themed card wrapper for NiceGUI.
    Consolidates rounding, shadows, borders, and glassmorphism.
    """
    # Base Class
    css_classes = ["s-card"]
    
    # Variants
    if variant != 'solid': # solid is default s-card style basically
         css_classes.append(f"s-card--{variant}")

    # Padding/Tightness
    if tight:
        css_classes.append('p-0 gap-0')
    elif padding:
         css_classes.append(padding)

    return ui.card().classes(" ".join(css_classes))

