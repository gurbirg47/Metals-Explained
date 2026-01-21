def get_custom_css():
    return """
    <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Bitter:ital,wght@0,300;0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            /* Backgrounds */
            --bg-void: #05070A;
            --bg-surface: #0F1216;
            --bg-depth: #1A232E;
            
            /* Text */
            --text-primary: #E8ECEF;
            --text-muted: #B0B8C0;

            /* Signals */
            --signal-accent: #33C5F4;
            --signal-up: #00E676;
            --signal-down: #FF453A;
            --signal-volatility: #FFD700;
            --signal-macro: #FF6B00;
        }

        /* RESET STREAMLIT DEFAULTS */
        .stApp {
            background-color: var(--bg-void);
            font-family: 'Bitter', serif;
            color: var(--text-primary);
            font-size: 1.1rem;
        }

        /* HEADER REMOVAL */
        header[data-testid="stHeader"] {
            display: none;
        }
        footer {
            display: none;
        }

        /* CUSTOM SCROLLBAR */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-void); 
        }
        ::-webkit-scrollbar-thumb {
            background: var(--bg-depth); 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted); 
        }

        /* ─────────────────────────────────────────────────────────────────────
           TYPOGRAPHY - EVEN LARGER SIZES
        ───────────────────────────────────────────────────────────────────── */
        
        h1 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 3.2rem !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 2.4rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        
        h3 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 1.8rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        
        h4 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 1.5rem !important;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        
        p, .stMarkdown p {
            font-size: 1.15rem;
            line-height: 1.8;
        }
        
        .mono-font {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           NAV BAR / TABS - LARGER AND MORE PROMINENT
        ───────────────────────────────────────────────────────────────────── */
        
        /* Tab container */
        div[data-testid="stTabs"] {
            background: var(--bg-surface);
            border-bottom: 2px solid var(--bg-depth);
            padding: 0.75rem 0;
            margin-bottom: 2rem;
        }
        
        /* Tab list */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.75rem;
            background: transparent;
        }
        
        /* Individual tabs - LARGER */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 1.5rem !important;
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            padding: 1rem 1.5rem !important;
            border-radius: 6px;
            color: var(--text-muted);
            background: transparent;
            border: none;
            transition: all 0.2s ease;
        }
        
        /* Tab hover */
        div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
            color: var(--text-primary);
            background: rgba(51, 197, 244, 0.1);
        }
        
        /* Active tab - STRONGER CONTRAST */
        div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
            color: #FFFFFF !important;
            background: rgba(51, 197, 244, 0.2) !important;
            border-bottom: 3px solid var(--signal-accent);
            font-weight: 700;
            font-size: 1.6rem !important;
        }
        
        /* Remove default underline */
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none;
        }
        
        div[data-testid="stTabs"] [data-baseweb="tab-border"] {
            display: none;
        }

        /* ─────────────────────────────────────────────────────────────────────
           METRIC CARDS - MUCH LARGER NUMBERS
        ───────────────────────────────────────────────────────────────────── */
        
        div[data-testid="stMetricValue"] {
            font-family: 'Barlow Condensed', sans-serif;
            font-weight: 700;
            font-size: 2.8rem !important;
            color: var(--text-primary);
            letter-spacing: 0.02em;
        }
        
        div[data-testid="stMetricLabel"] {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem !important;
            font-weight: 500;
            color: var(--text-muted);
            letter-spacing: 0.06em;
            margin-bottom: 0.3rem;
        }
        
        div[data-testid="stMetricDelta"] {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem !important;
            font-weight: 500;
        }
        
        /* Positive delta */
        div[data-testid="stMetricDelta"] svg {
            width: 20px;
            height: 20px;
        }

        /* ─────────────────────────────────────────────────────────────────────
           LOADING SCREEN STYLES
        ───────────────────────────────────────────────────────────────────── */
        
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
        }
        
        .loading-title {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 4rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
        }
        
        .loading-subtitle {
            font-family: 'Bitter', serif;
            font-size: 1.4rem;
            color: var(--text-muted);
            margin-bottom: 2rem;
            max-width: 500px;
        }
        
        .loading-status {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            color: var(--signal-accent);
            margin-top: 1rem;
        }
        
        .loading-creator {
            font-family: 'Bitter', serif;
            font-size: 1rem;
            color: var(--text-muted);
            margin-top: 3rem;
            opacity: 0.7;
        }

        /* ─────────────────────────────────────────────────────────────────────
           DATA MODE BANNER STYLES
        ───────────────────────────────────────────────────────────────────── */
        
        .data-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.25rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
        }
        
        .data-banner-demo {
            background: rgba(51, 197, 244, 0.12);
            border: 1px solid rgba(51, 197, 244, 0.4);
            color: var(--signal-accent);
        }
        
        .data-banner-partial {
            background: rgba(255, 215, 0, 0.12);
            border: 1px solid rgba(255, 215, 0, 0.4);
            color: var(--signal-volatility);
        }
        
        .data-banner-live {
            background: rgba(0, 230, 118, 0.12);
            border: 1px solid rgba(0, 230, 118, 0.4);
            color: var(--signal-up);
        }
        
        .feed-status {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.7rem;
            border-radius: 4px;
            font-size: 1rem;
            margin: 0.25rem;
        }
        
        .feed-live {
            background: rgba(0, 230, 118, 0.15);
            color: var(--signal-up);
        }
        
        .feed-demo {
            background: rgba(51, 197, 244, 0.15);
            color: var(--signal-accent);
        }

        /* ─────────────────────────────────────────────────────────────────────
           CHART TOGGLE BUTTONS
        ───────────────────────────────────────────────────────────────────── */
        
        .chart-toggle-container {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }
        
        .chart-toggle-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
            border-radius: 4px;
            border: 1px solid var(--text-muted);
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.15s ease;
        }
        
        .chart-toggle-btn:hover {
            border-color: var(--signal-accent);
            color: var(--signal-accent);
        }
        
        .chart-toggle-btn.active {
            background: rgba(51, 197, 244, 0.15);
            border-color: var(--signal-accent);
            color: var(--signal-accent);
            font-weight: 600;
        }

        /* ─────────────────────────────────────────────────────────────────────
           PLOTLY CHART OVERRIDES
        ───────────────────────────────────────────────────────────────────── */
        
        .js-plotly-plot .plotly .modebar {
            display: none !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           CUSTOM COMPONENTS
        ───────────────────────────────────────────────────────────────────── */
        
        .regime-card {
            background: rgba(15, 18, 22, 0.6);
            border: 1px solid rgba(232, 236, 239, 0.12);
            padding: 1.75rem;
            border-radius: 6px;
            margin-bottom: 1.25rem;
        }

        .ticker-tape {
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-surface);
            border-bottom: 1px solid rgba(232, 236, 239, 0.12);
            padding: 0.6rem;
            font-size: 1.1rem;
            white-space: nowrap;
            overflow-x: hidden;
            color: var(--text-muted);
        }

        .signal-badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 3px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: bold;
            margin-right: 0.6rem;
        }
        .signal-critical { background: rgba(255, 69, 58, 0.2); color: var(--signal-down); border: 1px solid var(--signal-down); }
        .signal-warning { background: rgba(255, 215, 0, 0.12); color: var(--signal-volatility); border: 1px solid var(--signal-volatility); }
        .signal-info { background: rgba(51, 197, 244, 0.12); color: var(--signal-accent); border: 1px solid var(--signal-accent); }
        .signal-macro { background: rgba(255, 107, 0, 0.12); color: var(--signal-macro); border: 1px solid var(--signal-macro); }

        /* ─────────────────────────────────────────────────────────────────────
           EXPANDER STYLING
        ───────────────────────────────────────────────────────────────────── */
        
        div[data-testid="stExpander"] {
            background: transparent;
            border: none;
        }
        
        div[data-testid="stExpander"] summary {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.05rem;
            color: var(--text-muted);
        }

        /* ─────────────────────────────────────────────────────────────────────
           BUTTON OVERRIDES
        ───────────────────────────────────────────────────────────────────── */
        
        .stButton button {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 1.25rem !important;
            font-weight: 600;
            letter-spacing: 0.03em;
            padding: 0.7rem 1.4rem !important;
        }
        
        .stButton button[kind="primary"] {
            background: var(--signal-accent) !important;
            color: var(--bg-void) !important;
        }
        
        .stButton button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid var(--text-muted) !important;
            color: var(--text-muted) !important;
        }
        
        .stButton button[kind="secondary"]:hover {
            border-color: var(--signal-accent) !important;
            color: var(--signal-accent) !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           CAPTION STYLING (chart takeaways)
        ───────────────────────────────────────────────────────────────────── */
        
        .stCaption, [data-testid="stCaption"] {
            font-size: 1.05rem !important;
            color: var(--text-muted) !important;
            line-height: 1.6;
        }

    </style>
    """
