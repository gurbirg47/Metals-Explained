import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from styles import get_custom_css
from market_data import get_all_market_data, format_price, format_change
from analysis_engine import (
    determine_drivers,
    get_what_moved,
    get_clean_story,
    get_why_hard_or_easy,
    get_chart_bullets,
    get_plain_takeaway,
    get_chart_takeaways,
    get_why_metals_matter,
    get_mental_model,
    get_drivers_content,
    get_history_content,
    get_glossary,
    get_chart_walkthrough,
    get_common_mistakes,
    get_interpretation_principles,
    get_example_scenarios,
    get_resources,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Metals, Explained",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "line"

# ─────────────────────────────────────────────────────────────────────────────
# LOADING SCREEN
# ─────────────────────────────────────────────────────────────────────────────
loading_placeholder = st.empty()

with loading_placeholder.container():
    st.markdown("""
    <div class="loading-container">
        <div class="loading-title">Metals, Explained</div>
        <div class="loading-subtitle">A learning-focused guide to understanding gold and silver markets.</div>
        <div class="loading-status">Loading market data...</div>
        <div class="loading-creator">Created by Gurbir Gill</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
market_data = get_all_market_data()
last_updated = datetime.now().strftime("%H:%M:%S")
loading_placeholder.empty()

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_data_mode(market_data):
    """Determine if data is live, demo, or partial."""
    feed_status = {
        "Gold": not market_data.get("gold", {}).get("is_mock", True),
        "Silver": not market_data.get("silver", {}).get("is_mock", True),
        "DXY": not market_data.get("dxy", {}).get("is_mock", True),
        "10Y Yield": not market_data.get("us10y", {}).get("is_mock", True),
    }
    live_count = sum(feed_status.values())
    total_count = len(feed_status)
    
    if live_count == total_count:
        return "live", feed_status
    elif live_count == 0:
        return "demo", feed_status
    else:
        return "partial", feed_status

def render_price_chart(df_gold, df_silver, chart_type):
    """Render Gold & Silver chart in line or candlestick mode."""
    fig = go.Figure()
    
    if chart_type == "candlestick" and df_gold is not None and not df_gold.empty:
        fig.add_trace(go.Candlestick(
            x=df_gold["Date"],
            open=df_gold["Open"],
            high=df_gold["High"],
            low=df_gold["Low"],
            close=df_gold["Close"],
            name="Gold",
            increasing_line_color='#00E676',
            decreasing_line_color='#FF453A',
            increasing_fillcolor='rgba(0, 230, 118, 0.3)',
            decreasing_fillcolor='rgba(255, 69, 58, 0.3)',
        ))
        y_title = "Price ($)"
    else:
        if df_gold is not None and not df_gold.empty:
            gold_base = df_gold["Close"].iloc[0]
            fig.add_trace(go.Scatter(
                x=df_gold["Date"], y=(df_gold["Close"] / gold_base) * 100,
                mode='lines', name='Gold', line=dict(color='#FFD700', width=2)
            ))
        if df_silver is not None and not df_silver.empty:
            silver_base = df_silver["Close"].iloc[0]
            fig.add_trace(go.Scatter(
                x=df_silver["Date"], y=(df_silver["Close"] / silver_base) * 100,
                mode='lines', name='Silver', line=dict(color='#C0C0C0', width=2)
            ))
        y_title = "Indexed (Base=100)"
    
    fig.update_layout(
        height=320,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=15, b=10),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color='#A0A8B0', size=13),
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(160,168,176,0.15)',
            title=dict(text=y_title, font=dict(size=14, color='#A0A8B0')),
            tickfont=dict(color='#A0A8B0', size=13)
        ),
        legend=dict(
            orientation='h',
            y=1.02,
            x=1,
            xanchor='right',
            font=dict(color='#E8ECEF', size=14)
        )
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "◉ Today",
    "◈ Why Metals Matter",
    "⚙ Drivers",
    "◷ History",
    "▤ Terminology",
    "◎ Interpretation",
    "◫ Examples",
    "◆ Resources"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: TODAY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    data_mode, feed_status = get_data_mode(market_data)
    
    # ───────────────────────────────────────────────────────────────────────
    # DATA STATUS BANNER + REFRESH CONTROL
    # ───────────────────────────────────────────────────────────────────────
    banner_col, refresh_col = st.columns([4, 1])
    
    with banner_col:
        if data_mode == "live":
            st.markdown(f'''
            <div class="data-banner data-banner-live">
                <span>● Live market data</span>
                <span style="font-size:0.8rem; color:var(--text-muted);">Last updated: {last_updated} · To view the most recent data, refresh the page.</span>
            </div>
            ''', unsafe_allow_html=True)
        elif data_mode == "demo":
            st.markdown(f'''
            <div class="data-banner data-banner-demo">
                <span>◆ Demo mode: sample data displayed</span>
                <span style="font-size:0.8rem; color:var(--text-muted);">Last updated: {last_updated} · Refresh the page to retry live data.</span>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="data-banner data-banner-partial">
                <span>◐ Partial: some feeds are sample data</span>
                <span style="font-size:0.8rem; color:var(--text-muted);">Last updated: {last_updated}</span>
            </div>
            ''', unsafe_allow_html=True)
    
    with refresh_col:
        if st.button("↻ Refresh Data", key="refresh_data", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    with st.expander("View feed status"):
        cols = st.columns(4)
        for i, (feed, is_live) in enumerate(feed_status.items()):
            with cols[i]:
                if is_live:
                    st.markdown(f'<span class="feed-status feed-live">✓ {feed}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="feed-status feed-demo">◆ {feed}</span>', unsafe_allow_html=True)
    
    # ───────────────────────────────────────────────────────────────────────
    # HEADER
    # ───────────────────────────────────────────────────────────────────────
    st.markdown("<h1 style='margin-bottom:5px;'>METALS, EXPLAINED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted); margin-bottom:20px; font-size:1.1rem;'>A learning-focused guide to understanding gold and silver markets.</p>", unsafe_allow_html=True)
    
    # ───────────────────────────────────────────────────────────────────────
    # MARKET SNAPSHOT
    # ───────────────────────────────────────────────────────────────────────
    gold_m = market_data.get("gold", {}).get("metrics", {})
    silver_m = market_data.get("silver", {}).get("metrics", {})
    us10y_m = market_data.get("us10y", {}).get("metrics", {})
    dxy_m = market_data.get("dxy", {}).get("metrics", {})
    
    drivers = determine_drivers(market_data)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        gold_price = format_price(gold_m.get("latest"))
        gold_chg, _ = format_change(gold_m.get("change_pct"))
        st.metric("GOLD", f"${gold_price}", gold_chg)
    
    with col2:
        silver_price = format_price(silver_m.get("latest"))
        silver_chg, _ = format_change(silver_m.get("change_pct"))
        st.metric("SILVER", f"${silver_price}", silver_chg)
    
    with col3:
        y10 = us10y_m.get("latest")
        y10_chg = us10y_m.get("change_pct") or 0
        bps = y10_chg * 10
        bps_str = f"{bps:+.0f} bps" if bps != 0 else "flat"
        st.metric("10Y YIELD", f"{y10:.2f}%" if y10 else "N/A", bps_str)
    
    with col4:
        dxy_val = format_price(dxy_m.get("latest"))
        dxy_chg, _ = format_change(dxy_m.get("change_pct"))
        st.metric("DXY", dxy_val, dxy_chg)
    
    with col5:
        df_gold = market_data.get("gold", {}).get("df")
        if df_gold is not None and "Close" in df_gold.columns and len(df_gold) >= 20:
            returns = df_gold["Close"].pct_change().dropna()
            realized_vol = returns.tail(20).std() * np.sqrt(252) * 100
            st.metric("VOLATILITY", f"{realized_vol:.1f}%", "20D realized")
        else:
            st.metric("VOLATILITY", "N/A", "—")
    
    # Driver ranking
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border-left:3px solid var(--signal-accent); padding:12px 16px; margin:20px 0; border-radius:0 4px 4px 0;">
        <span style="font-family:'Barlow Condensed'; font-size:1.05rem; letter-spacing:0.03em;">DRIVER RANKING:</span> 
        <span style="font-weight:600; color:var(--signal-accent);">Primary = {drivers['primary']}</span>
        <span style="color:var(--text-muted);"> | </span>
        <span style="color:var(--text-muted);">Secondary = {drivers['secondary']}</span>
        <span style="color:var(--text-muted);"> | </span>
        <span style="color:var(--text-muted);">Volatility = {drivers['vol_level']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ───────────────────────────────────────────────────────────────────────
    # CHART TOGGLE
    # ───────────────────────────────────────────────────────────────────────
    st.markdown("<h3 style='margin-top:20px;'>PRICE CHARTS</h3>", unsafe_allow_html=True)
    
    toggle_col1, toggle_col2, _ = st.columns([1, 1, 6])
    with toggle_col1:
        if st.button("📈 Line", key="btn_line", type="primary" if st.session_state.chart_type == "line" else "secondary"):
            st.session_state.chart_type = "line"
            st.rerun()
    with toggle_col2:
        if st.button("🕯️ Candlestick", key="btn_candle", type="primary" if st.session_state.chart_type == "candlestick" else "secondary"):
            st.session_state.chart_type = "candlestick"
            st.rerun()
    
    chart_takeaways = get_chart_takeaways(market_data)
    
    # ───────────────────────────────────────────────────────────────────────
    # CHARTS ROW 1
    # ───────────────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<h4>GOLD & SILVER</h4>", unsafe_allow_html=True)
        df_gold = market_data.get("gold", {}).get("df")
        df_silver = market_data.get("silver", {}).get("df")
        fig = render_price_chart(df_gold, df_silver, st.session_state.chart_type)
        st.plotly_chart(fig, use_container_width=True, key="chart_prices")
        st.caption(chart_takeaways.get("prices", ""))

    with c2:
        st.markdown("<h4>U.S. 10-YEAR YIELD</h4>", unsafe_allow_html=True)
        df_10y = market_data.get("us10y", {}).get("df")
        if df_10y is not None and not df_10y.empty:
            fig = px.area(df_10y, x='Date', y='Close', height=320)
            fig.update_traces(line_color='#FF6B00', fillcolor='rgba(255,107,0,0.1)')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=15, b=10),
                xaxis=dict(showgrid=False, tickfont=dict(color='#A0A8B0', size=13)),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(160,168,176,0.15)',
                    title=dict(text="Yield %", font=dict(size=14, color='#A0A8B0')),
                    tickfont=dict(color='#A0A8B0', size=13)
                )
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_yield")
            st.caption(chart_takeaways.get("yields", ""))

    # ───────────────────────────────────────────────────────────────────────
    # CHARTS ROW 2
    # ───────────────────────────────────────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("<h4>U.S. DOLLAR INDEX (DXY)</h4>", unsafe_allow_html=True)
        df_dxy = market_data.get("dxy", {}).get("df")
        if df_dxy is not None and not df_dxy.empty:
            fig = px.area(df_dxy, x='Date', y='Close', height=320)
            fig.update_traces(line_color='#33C5F4', fillcolor='rgba(51,197,244,0.1)')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=15, b=10),
                xaxis=dict(showgrid=False, tickfont=dict(color='#A0A8B0', size=13)),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(160,168,176,0.15)',
                    title=dict(text="Index", font=dict(size=14, color='#A0A8B0')),
                    tickfont=dict(color='#A0A8B0', size=13)
                )
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_dxy")
            st.caption(chart_takeaways.get("dxy", ""))

    with c4:
        st.markdown("<h4>GOLD VOLATILITY (20D REALIZED)</h4>", unsafe_allow_html=True)
        df_gold = market_data.get("gold", {}).get("df")
        if df_gold is not None and "Close" in df_gold.columns and len(df_gold) >= 25:
            df_vol = df_gold.copy()
            df_vol["Returns"] = df_vol["Close"].pct_change()
            df_vol["RealizedVol"] = df_vol["Returns"].rolling(20).std() * np.sqrt(252) * 100
            df_vol = df_vol.dropna(subset=["RealizedVol"])
            if not df_vol.empty:
                fig = px.area(df_vol, x='Date', y='RealizedVol', height=320)
                fig.update_traces(line_color='#FF453A', fillcolor='rgba(255,69,58,0.1)')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=15, b=10),
                    xaxis=dict(showgrid=False, tickfont=dict(color='#A0A8B0', size=13)),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(160,168,176,0.15)',
                        title=dict(text="Vol %", font=dict(size=14, color='#A0A8B0')),
                        tickfont=dict(color='#A0A8B0', size=13)
                    )
                )
                st.plotly_chart(fig, use_container_width=True, key="chart_vol")
                st.caption(chart_takeaways.get("volatility", ""))

    # ───────────────────────────────────────────────────────────────────────
    # MARKET EXPLANATION
    # ───────────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="border-bottom:1px solid var(--text-muted); padding-bottom:10px;">MARKET ANALYSIS</h2>', unsafe_allow_html=True)

    st.markdown("<h4 style='color:var(--signal-accent);'>Observation: What Moved</h4>", unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Bitter; line-height:1.7; color:var(--text-muted);">{get_what_moved(market_data)}</p>', unsafe_allow_html=True)

    st.markdown("<h4 style='color:var(--signal-accent); margin-top:20px;'>Mechanism: Primary Driver</h4>", unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Bitter; line-height:1.7; color:var(--text-muted);">{get_clean_story(market_data)}</p>', unsafe_allow_html=True)

    st.markdown("<h4 style='color:var(--signal-accent); margin-top:20px;'>Implication: Signal Alignment</h4>", unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Bitter; line-height:1.7; color:var(--text-muted);">{get_why_hard_or_easy(market_data)}</p>', unsafe_allow_html=True)

    st.markdown("<h4 style='color:var(--signal-accent); margin-top:20px;'>Chart Observations</h4>", unsafe_allow_html=True)
    for bullet in get_chart_bullets(market_data):
        st.markdown(f'<p style="font-family:Bitter; line-height:1.6; color:var(--text-muted); margin-bottom:8px;">• {bullet}</p>', unsafe_allow_html=True)

    st.markdown("<h4 style='color:var(--signal-accent); margin-top:20px;'>Summary</h4>", unsafe_allow_html=True)
    takeaway = get_plain_takeaway(market_data)
    st.markdown(f'<p style="font-family:Bitter; font-size:1.05rem; line-height:1.7; color:var(--text-primary); background:rgba(255,255,255,0.03); padding:15px; border-radius:4px;">{takeaway}</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: WHY METALS MATTER
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("<h1>WHY GOLD & SILVER MATTER</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:Bitter; line-height:1.8; color:var(--text-muted);">{get_why_metals_matter()}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 style="border-bottom:1px solid var(--text-muted); padding-bottom:10px;">MENTAL MODEL</h3>', unsafe_allow_html=True)
    
    model = get_mental_model()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:rgba(255,215,0,0.1); border:1px solid rgba(255,215,0,0.3); padding:20px; border-radius:4px; text-align:center;">
            <h4 style="color:#FFD700; margin-bottom:10px;">GOLD</h4>
            <p style="font-family:'JetBrains Mono'; color:var(--text-muted);">{model['gold']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:rgba(192,192,192,0.1); border:1px solid rgba(192,192,192,0.3); padding:20px; border-radius:4px; text-align:center;">
            <h4 style="color:#C0C0C0; margin-bottom:10px;">SILVER</h4>
            <p style="font-family:'JetBrains Mono'; color:var(--text-muted);">{model['silver']}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: DRIVERS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("<h1>WHAT MOVES GOLD & SILVER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>Understanding the macroeconomic forces that influence precious metals prices.</p>", unsafe_allow_html=True)
    
    for driver in get_drivers_content():
        st.markdown(f"""
        <div style="margin-bottom:25px; padding:20px; background:rgba(255,255,255,0.02); border-left:3px solid var(--signal-accent);">
            <h4 style="color:var(--text-primary); margin-bottom:10px;">{driver['title']}</h4>
            <p style="font-family:Bitter; color:var(--text-muted); margin-bottom:8px;"><strong>Definition:</strong> {driver['what']}</p>
            <p style="font-family:Bitter; color:var(--text-muted); margin-bottom:8px;"><strong>Mechanism:</strong> {driver['why']}</p>
            <p style="font-family:Bitter; color:var(--signal-accent);"><strong>Market Signal:</strong> {driver['signal']}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: HISTORY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("<h1>WHAT HISTORY TENDS TO SHOW</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>Historical patterns in precious metals markets, with mechanisms explained.</p>", unsafe_allow_html=True)
    
    for section in get_history_content():
        st.markdown(f"""
        <div style="margin-bottom:30px; padding:20px; background:rgba(255,255,255,0.02); border-radius:4px;">
            <h3 style="color:var(--signal-accent); margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">{section['title']}</h3>
            <div style="font-family:Bitter; line-height:1.8; color:var(--text-muted);">
                {section['content'].replace(chr(10)+chr(10), '</p><p style="margin-top:12px;">')}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: TERMINOLOGY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("<h1>TERMINOLOGY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>Definitions, relevance, and interpretation guidance for key terms.</p>", unsafe_allow_html=True)
    
    for item in get_glossary():
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:15px; background:rgba(255,255,255,0.02); border-left:2px solid var(--signal-accent);">
            <h4 style="color:var(--text-primary); margin-bottom:10px;">{item['term']}</h4>
            <p style="font-family:Bitter; color:var(--text-muted); margin-bottom:6px;"><strong>Definition:</strong> {item['what']}</p>
            <p style="font-family:Bitter; color:var(--text-muted); margin-bottom:6px;"><strong>Relevance:</strong> {item['why']}</p>
            <p style="font-family:Bitter; color:var(--signal-accent);"><strong>Interpretation:</strong> {item['today']}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: INTERPRETATION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("<h1>HOW TO INTERPRET THE CHARTS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>A disciplined analytical framework for market interpretation.</p>", unsafe_allow_html=True)
    
    st.markdown('<h3 style="margin-top:20px; border-bottom:1px solid var(--text-muted); padding-bottom:10px;">ANALYTICAL FRAMEWORK</h3>', unsafe_allow_html=True)
    
    for step in get_chart_walkthrough():
        st.markdown(f"""
        <div style="margin-bottom:20px; padding:20px; background:rgba(255,255,255,0.02); border-radius:4px;">
            <div style="display:flex; align-items:flex-start;">
                <div style="background:var(--signal-accent); color:var(--bg-void); font-weight:bold; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-right:15px; flex-shrink:0; font-family:'Barlow Condensed'; font-size:1.1rem;">{step['step']}</div>
                <div style="flex:1;">
                    <h4 style="color:var(--text-primary); margin:0 0 8px 0;">{step['title']}</h4>
                    <p style="font-family:Bitter; color:var(--text-muted); margin:0 0 10px 0;">{step['desc']}</p>
                    <p style="font-family:Bitter; color:var(--text-muted); font-size:0.95rem; line-height:1.7;">{step['detail']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="margin-top:30px; border-bottom:1px solid var(--text-muted); padding-bottom:10px;">INTERPRETATION PRINCIPLES</h3>', unsafe_allow_html=True)
    
    for principle in get_interpretation_principles():
        st.markdown(f"""
        <div style="margin-bottom:15px; padding:15px; background:rgba(255,255,255,0.02); border-left:2px solid var(--signal-macro);">
            <h4 style="color:var(--signal-macro); margin-bottom:8px;">{principle['title']}</h4>
            <p style="font-family:Bitter; color:var(--text-muted); margin:0;">{principle['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="margin-top:30px; border-bottom:1px solid var(--text-muted); padding-bottom:10px;">COMMON ANALYTICAL ERRORS</h3>', unsafe_allow_html=True)
    
    for mistake in get_common_mistakes():
        st.markdown(f'<p style="font-family:Bitter; color:var(--signal-down); margin-bottom:8px;">✗ {mistake}</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: EXAMPLES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("<h1>EXAMPLE SCENARIOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>Educational case studies demonstrating analytical reasoning.</p>", unsafe_allow_html=True)
    
    for scenario in get_example_scenarios():
        st.markdown(f"""
        <div style="margin-bottom:25px; padding:20px; background:rgba(255,255,255,0.03); border-radius:4px; border:1px solid rgba(255,255,255,0.1);">
            <h4 style="color:var(--signal-accent); margin-bottom:10px;">{scenario['title']}</h4>
            <p style="font-family:'JetBrains Mono'; font-size:0.85rem; color:var(--text-muted); margin-bottom:10px;"><em>Observable Conditions: {scenario['charts']}</em></p>
            <p style="font-family:Bitter; line-height:1.7; color:var(--text-primary);">{scenario['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: RESOURCES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown("<h1>RESOURCES</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);'>Professional tools and references for continued learning.</p>", unsafe_allow_html=True)
    
    for resource in get_resources():
        st.markdown(f"""
        <div style="margin-bottom:15px; padding:15px; background:rgba(255,255,255,0.02); border-left:2px solid var(--signal-accent);">
            <h4 style="color:var(--text-primary); margin-bottom:5px;">{resource['name']}</h4>
            <p style="font-family:Bitter; color:var(--text-muted); margin:0;">{resource['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 style="border-bottom:1px solid var(--text-muted); padding-bottom:10px;">ABOUT THIS PROJECT</h3>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-family:Bitter; line-height:1.8; color:var(--text-muted);">
    This project is designed to help students understand how macro factors, rates, currencies, and volatility 
    interact in precious metals markets. It focuses on explanation and context rather than prediction.
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; font-family:'JetBrains Mono'; font-size:0.7rem; color:var(--text-muted); margin-top:50px; border-top:1px solid rgba(255,255,255,0.1); padding-top:15px;">
    <p style="margin-bottom:8px;">DATA: YAHOO FINANCE | MANUAL REFRESH | FOR LEARNING ONLY | NOT INVESTMENT ADVICE</p>
    <p style="margin:0; font-family:Bitter; font-size:0.75rem;">Created by Gurbir Gill<br>
    <span style="font-size:0.7rem;">Accounting & Finance student with an interest in Sales & Trading and market structure.</span></p>
</div>
""", unsafe_allow_html=True)
