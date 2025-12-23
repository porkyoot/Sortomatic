from ..theme import ColorPalette

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

# UI Defaults for Solarized
RECURSIVE_IMPORT = "https://fonts.googleapis.com/css2?family=Recursive:wght@300..1000&display=swap"
RECURSIVE_SANS = "'Recursive', sans-serif"

SOLARIZED_DARK = ColorPalette(
    bg=BASE03,
    bg_secondary=BASE02,
    fg=BASE3,
    fg_secondary=BASE01,
    primary=BLUE,
    secondary=ORANGE,
    accent_1=BLUE,
    accent_2=ORANGE,
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
    purple=VIOLET,
    grey=BASE01,
    # Decoration
    rounded="8px",
    font_family=RECURSIVE_SANS,
    font_import=RECURSIVE_IMPORT
)

SOLARIZED_LIGHT = ColorPalette(
    bg=BASE3,
    bg_secondary=BASE2,
    fg=BASE03,
    fg_secondary=BASE1,
    primary=BLUE,
    secondary=ORANGE,
    accent_1=BLUE,
    accent_2=ORANGE,
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
    purple=VIOLET,
    grey=BASE1,
    # Decoration
    rounded="8px",
    font_family=RECURSIVE_SANS,
    font_import=RECURSIVE_IMPORT
)
