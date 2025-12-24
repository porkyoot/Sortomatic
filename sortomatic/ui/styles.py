from nicegui import ui
from .theme import Theme


def generate_css_variables(theme: Theme) -> str:
    """Converts the Python Theme object into CSS Variables."""
    
    # Generate Accent Vars programmatically
    accents = {
        'green': theme.colors.green,
        'red': theme.colors.red,
        'cyan': theme.colors.cyan,
        'orange': theme.colors.orange,
        'yellow': theme.colors.yellow,
        'blue': theme.colors.blue,
        'magenta': theme.colors.magenta,
        'violet': theme.colors.violet,
    }
    accents.update(theme.colors.accents)
    accent_vars = "\n".join([f"--c-accent-{k}: {v};" for k, v in accents.items()])
    
    return f"""
    :root {{
        /* COLORS */
        --c-surface-1: {theme.colors.surface_1};
        --c-surface-2: {theme.colors.surface_2};
        --c-surface-3: {theme.colors.surface_3};
        --c-text-main: {theme.colors.text_main};
        --c-text-subtle: {theme.colors.text_subtle};
        --c-text-active: {theme.colors.text_active};
        --c-primary: {theme.colors.primary};
        --c-secondary: {theme.colors.secondary};
        --c-success: {theme.colors.success};
        --c-warning: {theme.colors.warning};
        --c-error: {theme.colors.error};
        {accent_vars}

        /* LAYOUT (Responsive) */
        --unit: {theme.layout.spacing_unit};
        --r-sm: {theme.layout.radius_sm};
        --r-md: {theme.layout.radius_md};
        --r-lg: {theme.layout.radius_lg};
        --r-full: {theme.layout.radius_full};
        
        /* Spacing Scale */
        --s-0: 0px;
        --s-0_5: calc(var(--unit) * 0.5);
        --s-1: calc(var(--unit) * 1);
        --s-1_5: calc(var(--unit) * 1.5);
        --s-2: calc(var(--unit) * 2);
        --s-2_5: calc(var(--unit) * 2.5);
        --s-3: calc(var(--unit) * 3);
        --s-4: calc(var(--unit) * 4);
        --s-5: calc(var(--unit) * 5);
        --s-6: calc(var(--unit) * 6);
        --s-8: calc(var(--unit) * 8);
        --s-10: calc(var(--unit) * 10);
        --s-12: calc(var(--unit) * 12);
        --s-16: calc(var(--unit) * 16);
        --s-20: calc(var(--unit) * 20);
        --s-24: calc(var(--unit) * 24);
        --s-32: calc(var(--unit) * 32);
        --s-40: calc(var(--unit) * 40);
        --s-48: calc(var(--unit) * 48);
        --s-56: calc(var(--unit) * 56);
        --s-64: calc(var(--unit) * 64);
        
        /* BORDERS */
        --b-thin: 1px;
        --b-medium: calc(var(--b-thin) * 2);
        --b-thick: calc(var(--b-thin) * 4);
        
        /* TYPOGRAPHY */
        --font-main: {theme.layout.font_sans};
        --font-mono: {theme.layout.font_mono};
        
        /* TYPOGRAPHY SCALE */
        --text-base: var(--s-3);                  /* 12px (0.75rem) */
        --text-xs: calc(var(--text-base) * 0.85); /* ~10px */
        --text-md: calc(var(--text-base) * 1.166);/* ~14px */
        --text-lg: calc(var(--text-base) * 1.333);/* ~16px */
        --text-xl: calc(var(--text-base) * 2);    /* 24px */
        --text-2xl: calc(var(--text-xl) * 1.5);   /* 36px */
        
        /* LAYOUT CONSTANTS */
        --header-height: 60px;
        
        /* SHADOWS (Semantic) */
        --shadow-subtle: 0 1px 2px 0 color-mix(in srgb, var(--c-text-main), transparent 95%);
        --shadow-card: 0 4px 6px -1px color-mix(in srgb, var(--c-text-main), transparent 90%), 0 2px 4px -2px color-mix(in srgb, var(--c-text-main), transparent 90%);
        --shadow-float: 0 10px 15px -3px color-mix(in srgb, var(--c-text-main), transparent 90%);

        /* QUASAR OVERRIDES */
        --q-primary: {theme.colors.primary} !important;
        --q-secondary: {theme.colors.secondary} !important;
        --q-positive: {theme.colors.success} !important;
        --q-warning: {theme.colors.warning} !important;
        --q-negative: {theme.colors.error} !important;
    }}
    """

import re
from pathlib import Path

def load_global_styles(theme: Theme):
    """
    Injects the CSS Design System. 
    Loads separate CSS files from assets/css, minifies them, and injects them.
    """
    
    # 0. Load Material Design Icons & Recursive Font
    ui.add_head_html('<link href="https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/css/materialdesignicons.min.css" rel="stylesheet">')
    ui.add_head_html('<link rel="preconnect" href="https://fonts.googleapis.com">')
    ui.add_head_html('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Recursive:wght,MONO@300..1000,0;300..1000,1&display=swap" rel="stylesheet">')


    # 1. Inject Variables (Dynamic)
    ui.add_head_html(f"<style>{generate_css_variables(theme)}</style>")
    
    # 2. Load and Minify Static CSS
    # Order matters: Global -> Atoms -> Molecules -> Organisms
    base_dir = Path(__file__).parent / 'assets' / 'css'
    files = ['global.css', 'atoms.css', 'molecules.css', 'organisms.css']
    
    combined_css = ""
    for filename in files:
        file_path = base_dir / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
                # Simple Minification
                # 1. Remove comments
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                # 2. Remove whitespace around symbols
                content = re.sub(r'\s*([:;{}])\s*', r'\1', content)
                # 3. Collapse multiple spaces
                content = re.sub(r'\s+', ' ', content)
                
                combined_css += content
        else:
            print(f"Warning: CSS file not found: {file_path}")

    ui.add_head_html(f"<style>{combined_css}</style>")
