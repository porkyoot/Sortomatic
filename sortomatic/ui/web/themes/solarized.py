from .theme import ColorPalette

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

SOLARIZED_DARK = ColorPalette(
    bg=BASE03,
    fg=BASE0,
    fg_secondary=BASE01,
    primary=BLUE,
    secondary=ORANGE,
    info=BLUE,
    warning=YELLOW,
    error=RED,
    success=GREEN,
    debug=BASE01,
    blue=BLUE,
    cyan=CYAN,
    green=GREEN,
    yellow=YELLOW,
    orange=ORANGE,
    red=RED,
    magenta=MAGENTA,
    purple=VIOLET
)

SOLARIZED_LIGHT = ColorPalette(
    bg=BASE3,
    fg=BASE00,
    fg_secondary=BASE1,
    primary=BLUE,
    secondary=ORANGE
    info=BLUE,
    warning=YELLOW,
    error=RED,
    success=GREEN,
    debug=BASE1,
    blue=BLUE,
    cyan=CYAN,
    green=GREEN,
    yellow=YELLOW,
    orange=ORANGE,
    red=RED,
    magenta=MAGENTA,
    purple=VIOLET
)
