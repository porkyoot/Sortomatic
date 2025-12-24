from ..theme import Theme, ThemeColors, ThemeLayout

# Solarized Colors
BASE03 = "#002b36"
BASE02 = "#073642"
BASE01 = "#586e75"
BASE00 = "#657b83"
BASE0  = "#839496"
BASE1  = "#93a1a1"
BASE2  = "#eee8d5"
BASE3  = "#fdf6e3"
YELLOW = "#b58900"
ORANGE = "#cb4b16"
RED    = "#dc322f"
MAGENTA= "#d33682"
VIOLET = "#6c71c4"
BLUE   = "#268bd2"
CYAN   = "#2aa198"
GREEN  = "#859900"

SOLARIZED_DARK = Theme(
    colors=ThemeColors(
        surface_1=BASE03,     # Deep background
        surface_2=BASE02,     # Card background
        surface_3=BASE01,     # Hover state
        text_main=BASE1,      # Primary text
        text_subtle=BASE01,   # Secondary text
        primary=BLUE,
        secondary=ORANGE,
        debug=BASE0,
        info=BLUE,
        success=GREEN,
        warning=YELLOW,
        error=RED,
        green=GREEN,
        red=RED,
        cyan=CYAN,
        orange=ORANGE,
        yellow=YELLOW,
        blue=BLUE,
        magenta=MAGENTA,
        violet=VIOLET,
    
    ),
    layout=ThemeLayout(
        spacing_unit="0.25rem",
        radius_md="0.5rem" # Responsive radius
    )
)

SOLARIZED_LIGHT = Theme(
    colors=ThemeColors(
        surface_1=BASE3,
        surface_2=BASE2,
        surface_3=BASE1,
        text_main=BASE01,
        text_subtle=BASE01, # Maybe BASE00 for better contrast? Sticking to logic
        primary=BLUE,
        secondary=ORANGE,
        success=GREEN,
        warning=YELLOW,
        error=RED,
        green=GREEN,
        red=RED,
        cyan=CYAN,
        orange=ORANGE,
        yellow=YELLOW,
        blue=BLUE,
        magenta=MAGENTA,
        violet=VIOLET,
    
    ),
    layout=ThemeLayout(
        spacing_unit="0.25rem",
        radius_md="0.5rem"
    )
)
