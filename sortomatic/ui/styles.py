from nicegui import ui
from .theme import Theme, generate_css_variables

def load_global_styles(theme: Theme):
    """
    Injects the CSS Design System. 
    This is the ONLY place where CSS property values should live.
    """
    
    # 1. Inject Variables
    ui.add_head_html(f"<style>{generate_css_variables(theme)}</style>")
    
    # 2. Inject Semantic Classes (The Markdown-like approach)
    ui.add_head_html("""
    <style>
        /* --- ATOMS: BUTTONS --- */
        .s-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid transparent;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            
            /* Responsive sizes based on token units */
            padding: calc(var(--unit) * 2) calc(var(--unit) * 4);
            font-size: 0.875rem;
            border-radius: var(--r-md);
            gap: calc(var(--unit) * 2);
        }
        
        .s-btn:hover { transform: translateY(-1px); }
        .s-btn:active { transform: translateY(0px); }

        /* Variants */
        .s-btn--primary {
            background-color: var(--c-primary);
            color: var(--c-surface-1);
            box-shadow: var(--shadow-subtle);
        }
        .s-btn--primary:hover { filter: brightness(1.1); box-shadow: var(--shadow-card); }

        .s-btn--secondary {
            background-color: var(--c-secondary);
            color: var(--c-surface-1);
        }

        .s-btn--ghost {
            background-color: transparent;
            color: var(--c-text-subtle);
        }
        .s-btn--ghost:hover {
            background-color: var(--c-surface-2);
            color: var(--c-text-main);
        }

        /* Sizes */
        .s-btn--xs {
            padding: var(--unit) calc(var(--unit) * 2);
            font-size: 0.75rem;
            gap: var(--unit);
        }
        .s-btn--sm {
            padding: calc(var(--unit) * 1.5) calc(var(--unit) * 3);
            font-size: 0.8rem;
        }
        .s-btn--lg {
            padding: calc(var(--unit) * 3) calc(var(--unit) * 6);
            font-size: 1rem;
        }

        /* Shapes */
        .s-shape--pill { border-radius: var(--r-full); }
        .s-shape--square { aspect-ratio: 1/1; padding: calc(var(--unit) * 2); }

        /* --- ATOMS: CARDS --- */
        .s-card {
            background-color: var(--c-surface-2);
            border-radius: var(--r-lg);
            border: 1px solid color-mix(in srgb, var(--c-text-main), transparent 90%);
            padding: calc(var(--unit) * 6); /* 1.5rem padding */
            transition: box-shadow 0.3s ease;
        }
        
        .s-card--glass {
            background-color: color-mix(in srgb, var(--c-surface-2), transparent 20%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        
        .s-card:hover {
            box-shadow: var(--shadow-card);
            border-color: color-mix(in srgb, var(--c-text-main), transparent 80%);
        }

        /* --- UTILS: TYPOGRAPHY --- */
        .s-text-h1 { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em; }
        .s-text-body { font-size: 1rem; line-height: 1.5; color: var(--c-text-subtle); }
    </style>
    """)
