"""
analysis_engine.py
Content generation for the Gold & Silver Market Context Dashboard.
Professional educational reference for students studying financial markets.
"""

from typing import Dict, Tuple, List
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# DRIVER DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def determine_drivers(market_data: Dict) -> Dict:
    """
    Analyze market conditions to rank the primary and secondary drivers
    of precious metals price action.
    """
    us10y = market_data.get("us10y", {}).get("metrics", {})
    dxy = market_data.get("dxy", {}).get("metrics", {})
    gold = market_data.get("gold", {}).get("metrics", {})
    silver = market_data.get("silver", {}).get("metrics", {})
    
    yield_chg = us10y.get("change_pct") or 0
    dxy_chg = dxy.get("change_pct") or 0
    gold_chg = gold.get("change_pct") or 0
    silver_chg = silver.get("change_pct") or 0
    
    yield_score = abs(yield_chg) * 15
    dxy_score = abs(dxy_chg) * 10
    
    yield_bearish = yield_chg > 0
    dxy_bearish = dxy_chg > 0
    gold_down = gold_chg < 0
    
    yield_aligned = (yield_bearish == gold_down) if abs(yield_chg) > 0.1 else None
    dxy_aligned = (dxy_bearish == gold_down) if abs(dxy_chg) > 0.1 else None
    
    if yield_score > dxy_score:
        primary = "Interest Rates"
        secondary = "U.S. Dollar"
    else:
        primary = "U.S. Dollar"
        secondary = "Interest Rates"
    
    metals_move = max(abs(gold_chg), abs(silver_chg))
    if metals_move > 1.5:
        vol_level = "Elevated"
    elif metals_move > 0.7:
        vol_level = "Moderate"
    else:
        vol_level = "Subdued"
    
    if yield_aligned is not None and dxy_aligned is not None:
        if yield_aligned != dxy_aligned:
            conflict = True
            conflict_note = "Interest rates and the U.S. dollar are providing divergent signals."
        else:
            conflict = False
            conflict_note = "Both primary macro drivers are directionally aligned."
    elif yield_aligned is None and dxy_aligned is None:
        conflict = None
        conflict_note = "Neither rates nor the dollar exhibited sufficient movement to establish a directional signal."
    else:
        conflict = False
        conflict_note = "One driver is providing a clearer signal than the other."
    
    return {
        "primary": primary,
        "secondary": secondary,
        "vol_level": vol_level,
        "conflict": conflict,
        "conflict_note": conflict_note,
        "yield_score": yield_score,
        "dxy_score": dxy_score,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TODAY TAB: MARKET CONTEXT SECTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_what_moved(market_data: Dict) -> str:
    """Observation: Describe price movements in precise terms."""
    gold = market_data.get("gold", {}).get("metrics", {})
    silver = market_data.get("silver", {}).get("metrics", {})
    
    gold_price = gold.get("latest")
    gold_chg = gold.get("change_pct")
    silver_price = silver.get("latest")
    silver_chg = silver.get("change_pct")
    
    if gold_price is None:
        return "Market data is currently loading."
    
    if gold_chg is None:
        g = f"Gold is trading at ${gold_price:,.2f}."
    elif abs(gold_chg) < 0.15:
        g = f"Gold is trading largely unchanged at ${gold_price:,.2f} ({gold_chg:+.2f}%)."
    elif gold_chg > 0:
        g = f"Gold has advanced {gold_chg:.2f}% to ${gold_price:,.2f}."
    else:
        g = f"Gold has declined {abs(gold_chg):.2f}% to ${gold_price:,.2f}."
    
    if silver_chg is None:
        s = f"Silver is trading at ${silver_price:,.2f}."
    elif abs(silver_chg) < 0.2:
        s = f"Silver is trading largely unchanged at ${silver_price:,.2f}."
    elif silver_chg > 0:
        s = f"Silver has advanced {silver_chg:.2f}% to ${silver_price:,.2f}."
    else:
        s = f"Silver has declined {abs(silver_chg):.2f}% to ${silver_price:,.2f}."
    
    if gold_chg and silver_chg and abs(silver_chg) > abs(gold_chg) * 1.3:
        compare = " Silver is exhibiting greater percentage movement than gold, which is consistent with its historically higher volatility."
    elif gold_chg and silver_chg and abs(gold_chg) > abs(silver_chg) * 1.3:
        compare = " Gold is exhibiting greater percentage movement than silver, which may indicate defensive positioning."
    else:
        compare = ""
    
    return f"{g} {s}{compare}"


def get_clean_story(market_data: Dict) -> str:
    """Mechanism: Explain the macroeconomic relationship driving price action."""
    drivers = determine_drivers(market_data)
    us10y = market_data.get("us10y", {}).get("metrics", {})
    dxy = market_data.get("dxy", {}).get("metrics", {})
    
    yield_val = us10y.get("latest")
    yield_chg = us10y.get("change_pct") or 0
    dxy_val = dxy.get("latest")
    dxy_chg = dxy.get("change_pct") or 0
    
    primary = drivers["primary"]
    
    if primary == "Interest Rates" and yield_val:
        if yield_chg > 0.1:
            return (
                f"The 10-year Treasury yield has risen to {yield_val:.2f}%. "
                f"Higher nominal yields increase the opportunity cost of holding non-yielding assets such as gold, "
                f"as investors can obtain greater returns from interest-bearing instruments. "
                f"This relationship historically tends to create downward pressure on precious metals prices."
            )
        elif yield_chg < -0.1:
            return (
                f"The 10-year Treasury yield has declined to {yield_val:.2f}%. "
                f"Lower nominal yields reduce the opportunity cost of holding gold, "
                f"as the relative attractiveness of interest-bearing alternatives diminishes. "
                f"This environment has historically tended to be supportive for precious metals."
            )
        else:
            return (
                "Treasury yields have exhibited limited movement during this session. "
                "In the absence of a clear directional signal from interest rates, "
                "other factors may be influencing price action."
            )
    
    elif primary == "U.S. Dollar" and dxy_val:
        if dxy_chg > 0.15:
            return (
                f"The U.S. Dollar Index has strengthened to {dxy_val:.2f}. "
                f"Gold and silver are priced in U.S. dollars; when the dollar appreciates, "
                f"these metals become more expensive for holders of other currencies, "
                f"which historically tends to reduce international demand and exert downward pressure on prices."
            )
        elif dxy_chg < -0.15:
            return (
                f"The U.S. Dollar Index has weakened to {dxy_val:.2f}. "
                f"A depreciating dollar makes dollar-denominated commodities less expensive for international buyers, "
                f"which historically tends to support demand and provide a tailwind for precious metals prices."
            )
        else:
            return (
                "The U.S. dollar has exhibited limited movement during this session. "
                "Currency dynamics do not appear to be a primary driver of price action."
            )
    
    return (
        "Neither interest rates nor the U.S. dollar exhibited decisive movement during this session. "
        "Price action may reflect positioning, technical factors, or sentiment-driven flows "
        "that are not fully captured by macro variables."
    )


def get_why_hard_or_easy(market_data: Dict) -> str:
    """Implication: Explain driver alignment or divergence."""
    drivers = determine_drivers(market_data)
    conflict = drivers["conflict"]
    conflict_note = drivers["conflict_note"]
    
    gold = market_data.get("gold", {}).get("metrics", {})
    gold_chg = gold.get("change_pct") or 0
    
    if conflict is True:
        return (
            f"{conflict_note} "
            f"When primary macro drivers provide conflicting signals, market interpretation becomes more complex. "
            f"In such environments, price action may reflect a balance of offsetting forces, "
            f"and attributing causation to a single factor should be approached with appropriate caution."
        )
    elif conflict is False:
        return (
            f"{conflict_note} "
            f"When multiple macro drivers point in the same direction, the interpretive framework is more straightforward. "
            f"The observed price action appears consistent with established macroeconomic relationships."
        )
    else:
        if abs(gold_chg) > 0.5:
            return (
                f"{conflict_note} "
                f"Despite the absence of clear macro signals, precious metals exhibited notable movement. "
                f"This may indicate the influence of factors such as positioning adjustments, headline-driven trading, "
                f"or sentiment shifts that are not fully reflected in rates or currency data."
            )
        else:
            return (
                f"{conflict_note} "
                f"With subdued macro movement and limited price action in metals, "
                f"the current session does not present a strong interpretive signal."
            )


def get_chart_bullets(market_data: Dict) -> List[str]:
    """Reference each chart with structured observations."""
    bullets = []
    
    gold = market_data.get("gold", {}).get("metrics", {})
    us10y = market_data.get("us10y", {}).get("metrics", {})
    dxy = market_data.get("dxy", {}).get("metrics", {})
    
    gold_above_50 = gold.get("above_50")
    if gold_above_50 is True:
        bullets.append(
            "The price chart indicates gold is trading above its 50-day moving average, "
            "which is often interpreted as a constructive near-term trend signal."
        )
    elif gold_above_50 is False:
        bullets.append(
            "The price chart indicates gold is trading below its 50-day moving average, "
            "which may suggest near-term technical weakness."
        )
    else:
        bullets.append(
            "The price chart displays the recent trajectory of gold and silver prices, "
            "providing context for current levels relative to recent history."
        )
    
    yield_val = us10y.get("latest")
    if yield_val and yield_val > 4.5:
        bullets.append(
            f"The yield chart shows the 10-year Treasury at {yield_val:.2f}%, "
            f"an elevated level that historically tends to create headwinds for non-yielding assets."
        )
    elif yield_val and yield_val < 3.5:
        bullets.append(
            f"The yield chart shows the 10-year Treasury at {yield_val:.2f}%, "
            f"a relatively low level that historically tends to be more supportive for precious metals."
        )
    elif yield_val:
        bullets.append(
            f"The yield chart shows the 10-year Treasury at {yield_val:.2f}%, "
            f"a moderate level that does not provide a strong directional signal."
        )
    
    dxy_val = dxy.get("latest")
    dxy_chg = dxy.get("change_pct") or 0
    if dxy_val:
        if dxy_chg > 0.2:
            bullets.append(
                f"The dollar chart shows DXY strengthening to {dxy_val:.2f}, "
                f"a movement that historically tends to coincide with softer commodity prices."
            )
        elif dxy_chg < -0.2:
            bullets.append(
                f"The dollar chart shows DXY weakening to {dxy_val:.2f}, "
                f"a movement that historically tends to support dollar-denominated commodities."
            )
        else:
            bullets.append(
                f"The dollar chart shows DXY near {dxy_val:.2f} with limited directional movement, "
                f"suggesting currency dynamics are not a primary factor in this session."
            )
    
    bullets.append(
        "The volatility chart displays realized price variability, "
        "which provides context for the intensity of recent trading activity."
    )
    
    return bullets


def get_plain_takeaway(market_data: Dict) -> str:
    """Concise professional takeaway for non-specialist readers."""
    drivers = determine_drivers(market_data)
    gold = market_data.get("gold", {}).get("metrics", {})
    gold_chg = gold.get("change_pct")
    
    if gold_chg is None:
        return "Market data is currently loading."
    
    primary = drivers["primary"]
    
    if abs(gold_chg) < 0.15:
        return (
            "Gold and silver exhibited limited price movement during this session, "
            "with no dominant macro driver identified."
        )
    
    if primary == "Interest Rates":
        if gold_chg > 0:
            return (
                "Gold advanced during this session, with price action appearing consistent with "
                "declining Treasury yields, which reduce the opportunity cost of holding non-yielding assets."
            )
        else:
            return (
                "Gold declined during this session, with price action appearing consistent with "
                "rising Treasury yields, which increase the relative attractiveness of interest-bearing instruments."
            )
    else:
        if gold_chg > 0:
            return (
                "Gold advanced during this session, with price action appearing consistent with "
                "U.S. dollar weakness, which historically tends to support dollar-denominated commodities."
            )
        else:
            return (
                "Gold declined during this session, with price action appearing consistent with "
                "U.S. dollar strength, which historically tends to create headwinds for precious metals."
            )


# ─────────────────────────────────────────────────────────────────────────────
# CHART TAKEAWAYS
# ─────────────────────────────────────────────────────────────────────────────

def get_chart_takeaways(market_data: Dict) -> Dict[str, str]:
    """One-sentence professional takeaways for each chart."""
    gold = market_data.get("gold", {}).get("metrics", {})
    silver = market_data.get("silver", {}).get("metrics", {})
    us10y = market_data.get("us10y", {}).get("metrics", {})
    dxy = market_data.get("dxy", {}).get("metrics", {})
    
    takeaways = {}
    
    gold_chg = gold.get("change_pct") or 0
    silver_chg = silver.get("change_pct") or 0
    if gold_chg > 0 and silver_chg > 0:
        takeaways["prices"] = "Both metals are trading higher, indicating broad precious metals strength."
    elif gold_chg < 0 and silver_chg < 0:
        takeaways["prices"] = "Both metals are trading lower, indicating broad precious metals weakness."
    elif abs(gold_chg) < 0.1 and abs(silver_chg) < 0.1:
        takeaways["prices"] = "Both metals are exhibiting limited price movement during this session."
    else:
        takeaways["prices"] = "Gold and silver are exhibiting divergent price action, which may warrant closer analysis."
    
    yield_val = us10y.get("latest")
    yield_chg = us10y.get("change_pct") or 0
    if yield_val:
        if yield_chg > 0.1:
            takeaways["yields"] = f"Yields have risen to {yield_val:.2f}%, historically a headwind for precious metals."
        elif yield_chg < -0.1:
            takeaways["yields"] = f"Yields have declined to {yield_val:.2f}%, historically supportive for precious metals."
        else:
            takeaways["yields"] = f"Yields are steady near {yield_val:.2f}%, providing limited directional signal."
    else:
        takeaways["yields"] = "Yield data is loading."
    
    dxy_val = dxy.get("latest")
    dxy_chg = dxy.get("change_pct") or 0
    if dxy_val:
        if dxy_chg > 0.1:
            takeaways["dxy"] = f"The dollar has strengthened to {dxy_val:.2f}, historically a headwind for commodities."
        elif dxy_chg < -0.1:
            takeaways["dxy"] = f"The dollar has weakened to {dxy_val:.2f}, historically supportive for commodities."
        else:
            takeaways["dxy"] = f"The dollar is steady at {dxy_val:.2f}, providing limited directional signal."
    else:
        takeaways["dxy"] = "Dollar data is loading."
    
    takeaways["volatility"] = "Realized volatility indicates the intensity of recent price movements."
    
    return takeaways


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: WHY GOLD & SILVER MATTER
# ─────────────────────────────────────────────────────────────────────────────

def get_why_metals_matter() -> str:
    return """
**Gold and Silver as Macroeconomic Indicators**

Gold and silver occupy a distinctive position in financial markets. Unlike equities or fixed income instruments, precious metals do not generate earnings or pay interest. Their value derives from scarcity, durability, and their historical role as stores of value and mediums of exchange.

**Sensitivity to Macroeconomic Conditions**

Precious metals prices are influenced by several interconnected factors:

*Interest Rates*: Gold and silver do not provide yield. When interest rates rise, the opportunity cost of holding non-yielding assets increases, as investors can obtain returns from interest-bearing instruments. Conversely, when rates decline—particularly when real rates (nominal rates minus inflation) turn negative—the relative attractiveness of precious metals tends to increase.

*Currency Dynamics*: Gold and silver are predominantly priced in U.S. dollars. When the dollar strengthens, these metals become more expensive for holders of other currencies, which historically tends to reduce international demand. The inverse relationship—dollar weakness supporting precious metals—is well documented in market literature.

*Investor Confidence and Risk Appetite*: During periods of economic uncertainty, financial stress, or geopolitical instability, investors often allocate capital to assets perceived as safe havens. Gold, in particular, has historically served this function, sometimes appreciating during equity market declines.

**Silver's Dual Character**

Silver differs from gold in one important respect: it has significant industrial applications. Approximately half of annual silver demand derives from industrial uses, including electronics, solar photovoltaic cells, and medical devices. This industrial component causes silver to exhibit characteristics of both a precious metal and an industrial commodity, often resulting in greater price volatility than gold.

**Relevance for Financial Education**

Studying precious metals markets provides valuable insight into the interconnections between interest rates, currencies, inflation expectations, and investor behavior. These markets are liquid, globally traded, and responsive to macroeconomic developments, making them useful for understanding how different asset classes interact within the broader financial system.
"""


def get_mental_model() -> Dict[str, str]:
    return {
        "gold": "Interest Rates + Currency + Risk Sentiment",
        "silver": "Gold Drivers + Industrial Demand + Higher Volatility"
    }


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: DRIVERS
# ─────────────────────────────────────────────────────────────────────────────

def get_drivers_content() -> List[Dict]:
    return [
        {
            "title": "Interest Rates and Real Yields",
            "what": "The nominal return available from risk-free instruments such as U.S. Treasury securities. Real yields adjust nominal yields for expected inflation.",
            "why": "Gold does not generate income. When yields rise, investors can earn meaningful returns from interest-bearing assets, increasing the opportunity cost of holding gold. Real yields—nominal yields minus inflation expectations—are particularly important because they represent the true return after accounting for purchasing power erosion.",
            "signal": "Rising real yields have historically tended to create headwinds for gold. Declining or negative real yields have historically tended to be supportive."
        },
        {
            "title": "U.S. Dollar Strength",
            "what": "The value of the U.S. dollar relative to a basket of major international currencies, typically measured by the DXY index.",
            "why": "Gold and silver are quoted in U.S. dollars. When the dollar appreciates, these metals become more expensive for buyers holding other currencies, which can reduce international demand. The inverse also holds: dollar depreciation has historically tended to support precious metals prices.",
            "signal": "Dollar strength often coincides with softer precious metals prices. Dollar weakness often coincides with firmer precious metals prices."
        },
        {
            "title": "Risk Sentiment and Uncertainty",
            "what": "The general willingness of investors to hold risky assets versus seeking safety in traditionally defensive investments.",
            "why": "Gold has historically functioned as a safe-haven asset during periods of financial stress, geopolitical instability, or elevated uncertainty. When risk appetite declines, capital flows may shift toward gold as a hedge against potential losses elsewhere in portfolios.",
            "signal": "Risk-off environments—characterized by equity weakness and elevated volatility—have historically tended to be supportive for gold."
        },
        {
            "title": "Inflation Expectations",
            "what": "Market-based or survey-based measures of anticipated future inflation.",
            "why": "Gold has a long-standing reputation as an inflation hedge, though empirical evidence suggests this relationship is inconsistent in the short term. Gold tends to respond more reliably when inflation expectations are rising rapidly or when central banks appear to be falling behind the curve.",
            "signal": "Rising inflation expectations can be supportive for gold, though the relationship is often mediated by the accompanying movement in real yields."
        },
        {
            "title": "Positioning and Fund Flows",
            "what": "The aggregate exposure of institutional and speculative traders to gold and silver, as well as inflows and outflows from precious metals investment vehicles.",
            "why": "Large changes in positioning can influence prices independently of fundamental factors. When positions become extended in one direction, markets may become susceptible to reversals if those positions are unwound.",
            "signal": "Positioning is difficult to observe in real-time and should be considered when fundamental factors do not fully explain observed price action."
        },
        {
            "title": "Industrial Demand (Silver)",
            "what": "Physical consumption of silver in manufacturing, electronics, solar energy, and other industrial applications.",
            "why": "Unlike gold, silver has substantial industrial utility. When economic growth expectations improve, anticipated industrial demand may support silver prices. Conversely, growth concerns can create headwinds specific to silver.",
            "signal": "Silver outperformance relative to gold may indicate optimism about economic growth. Silver underperformance may indicate growth concerns."
        },
        {
            "title": "Gold-Silver Ratio",
            "what": "The number of ounces of silver required to purchase one ounce of gold at current prices.",
            "why": "This ratio provides context for relative valuation. Historically, the ratio has averaged approximately 60-80, though it has varied significantly over time.",
            "signal": "An elevated ratio may suggest silver is relatively inexpensive versus gold, though this metric should be interpreted as context rather than as a timing signal."
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: HISTORY (EXPANDED)
# ─────────────────────────────────────────────────────────────────────────────

def get_history_content() -> List[Dict]:
    """Detailed historical patterns with mechanisms and context."""
    return [
        {
            "title": "Gold and Real Interest Rates",
            "content": """The relationship between gold and real interest rates is among the most robust in precious metals analysis. Real rates represent the return available from safe assets after adjusting for inflation—calculated as nominal yield minus expected inflation.

**The Mechanism**: Gold does not pay interest or dividends. When real rates are positive and rising, investors can earn meaningful inflation-adjusted returns from Treasury securities or other interest-bearing instruments. This raises the opportunity cost of holding gold, which generates no income. Conversely, when real rates decline—particularly when they turn negative—gold becomes relatively more attractive because alternative safe assets offer diminished or negative real returns.

**Historical Evidence**: The 2011-2013 gold decline coincided with rising real yields as the Federal Reserve signaled potential tapering of quantitative easing. The 2019-2020 gold rally occurred alongside declining and eventually negative real yields. The 2022 gold weakness accompanied aggressive Federal Reserve tightening that pushed real yields sharply higher.

**Limitations**: This relationship is not mechanical or immediate. Real yields are themselves influenced by growth expectations, inflation surprises, and central bank policy. Short-term deviations are common, and positioning can temporarily overwhelm fundamental drivers."""
        },
        {
            "title": "The U.S. Dollar and Precious Metals",
            "content": """Gold and silver are predominantly quoted and traded in U.S. dollars, creating a structural relationship between dollar strength and metals pricing.

**The Mechanism**: When the dollar appreciates, gold becomes more expensive for buyers holding euros, yen, or other currencies. This reduces international demand at any given dollar price. Additionally, dollar strength often reflects relative economic outperformance or tighter U.S. monetary policy, which independently tends to weigh on gold. The inverse holds for dollar weakness.

**Historical Evidence**: Multi-year dollar trends have historically correlated inversely with gold. The weak dollar period of 2002-2008 coincided with gold rising from approximately $300 to nearly $1,000. The strong dollar period of 2014-2016 coincided with gold declining from $1,300 to below $1,100.

**Limitations**: The dollar-gold relationship can weaken during periods of global financial stress, when both the dollar and gold may appreciate simultaneously as safe-haven assets. Currency dynamics interact with yield differentials, central bank policy, and risk sentiment in complex ways."""
        },
        {
            "title": "Inflation and Gold: A Complicated Relationship",
            "content": """Gold has a long-standing reputation as an inflation hedge, though empirical evidence suggests this relationship is more nuanced than commonly assumed.

**The Mechanism**: In theory, gold preserves purchasing power when fiat currency loses value through inflation. Gold supply is limited, while currency supply can expand indefinitely. This scarcity should make gold an effective store of value during inflationary periods.

**Historical Complexity**: The relationship holds over very long horizons but is inconsistent at shorter intervals. The 1970s stagflation period saw gold appreciate dramatically as inflation surged. However, the 2021-2022 period demonstrated that rising inflation does not automatically support gold—if central banks respond aggressively, rising real rates can overwhelm the inflation hedge narrative.

**Key Insight**: The critical variable is often not inflation itself, but how real yields respond. Gold tends to perform well when inflation is rising faster than interest rates (negative real rates). Gold tends to struggle when central banks tighten sufficiently to generate positive real rates, even if inflation remains elevated."""
        },
        {
            "title": "Silver's Higher Volatility",
            "content": """Silver consistently exhibits greater price volatility than gold—typically moving 1.5 to 2 times as much on a percentage basis during directional moves.

**The Mechanism**: Several factors contribute to this pattern. The silver market is substantially smaller than gold in terms of dollar value, making it more susceptible to positioning-driven moves. Silver has split demand between investment and industrial uses, causing it to respond to both precious metals and growth-related factors. Speculative positioning in silver is often more aggressive relative to market size.

**Historical Evidence**: During the 2010-2011 precious metals rally, silver more than doubled while gold rose approximately 50%. During the subsequent decline, silver fell more sharply. This amplification pattern—silver leading on the upside and downside—has repeated across multiple cycles.

**Interpretation**: Silver's volatility is a feature, not a bug. Analysts interpret silver outperformance as a sign of aggressive risk-on behavior or growth optimism, while silver underperformance relative to gold often signals defensiveness or growth concerns."""
        },
        {
            "title": "Silver's Industrial Demand Component",
            "content": """Approximately 50% of annual silver demand derives from industrial applications, distinguishing it fundamentally from gold.

**Key Industrial Uses**: Electronics and electrical applications account for a significant portion of industrial demand, as silver has the highest electrical conductivity of any element. Solar photovoltaic cells use silver paste in panel manufacturing—a sector with structural growth. Medical applications utilize silver for its antimicrobial properties. Other industrial uses include brazing, soldering, and catalytic chemistry.

**Market Implications**: When economic growth expectations improve, anticipated industrial demand can provide silver-specific support not applicable to gold. Conversely, recession fears or manufacturing slowdowns can create silver-specific headwinds. This industrial component causes silver to trade partially like an industrial commodity rather than a pure precious metal.

**Historical Example**: The 2020-2021 green energy narrative—anticipating rapid solar capacity expansion—contributed to silver outperformance, as the market priced in higher future industrial demand independent of monetary factors."""
        },
        {
            "title": "When Historical Relationships Break Down",
            "content": """Disciplined analysis requires acknowledging that historical tendencies are probabilistic, not deterministic. Relationships can weaken or temporarily reverse.

**Common Causes of Breakdown**:

*Positioning Extremes*: When speculative positioning becomes extremely one-sided, unwinding of those positions can drive price action contrary to fundamental signals.

*Macro Regime Shifts*: The transition between inflationary and deflationary environments, or between risk-on and risk-off regimes, can temporarily disrupt established relationships as markets recalibrate.

*Unprecedented Policy*: Central bank interventions—quantitative easing, yield curve control, or emergency liquidity measures—can alter traditional transmission mechanisms.

*Liquidity Events*: During acute market stress, correlations often move toward one as investors sell liquid assets indiscriminately.

**Historical Examples**: The March 2020 liquidity crisis saw gold decline alongside equities as investors raised cash—the opposite of typical safe-haven behavior. The relationship normalized once emergency Fed interventions restored market functioning. The 2013 "taper tantrum" saw gold decline despite still-accommodative policy, as the rate-of-change in expectations proved more important than absolute levels.

**Analytical Discipline**: When price action diverges from fundamental expectations, the first response should be to check whether drivers are conflicting, whether positioning is extreme, or whether unusual structural factors are present. Forcing a narrative onto unexplained moves undermines analytical credibility."""
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: TERMINOLOGY / GLOSSARY
# ─────────────────────────────────────────────────────────────────────────────

def get_glossary() -> List[Dict]:
    return [
        {
            "term": "Gold Price",
            "what": "The current market price for one troy ounce of gold, denominated in U.S. dollars. Prices are determined by continuous trading on global exchanges.",
            "why": "Gold prices respond to interest rates, currency movements, and investor risk appetite. Changes in gold prices can provide insight into shifting macroeconomic expectations.",
            "today": "Observe the direction and magnitude of price change. Consider whether the movement aligns with changes in yields and the dollar."
        },
        {
            "term": "Silver Price",
            "what": "The current market price for one troy ounce of silver, denominated in U.S. dollars.",
            "why": "Silver responds to similar factors as gold but also has significant industrial demand components. Silver typically exhibits higher volatility than gold.",
            "today": "Compare silver's movement to gold. Significantly greater silver volatility is normal; divergence between the two metals may warrant investigation."
        },
        {
            "term": "U.S. 10-Year Treasury Yield",
            "what": "The annualized return an investor would receive by holding a U.S. government bond maturing in ten years. This yield is a benchmark for risk-free returns.",
            "why": "This yield represents the opportunity cost of holding non-yielding assets. Higher yields increase this cost; lower yields reduce it.",
            "today": "Rising yields typically create headwinds for gold. Declining yields typically provide support."
        },
        {
            "term": "Basis Points (bps)",
            "what": "A unit of measurement equal to one-hundredth of one percent (0.01%). A 25 basis point move equals a 0.25 percentage point change.",
            "why": "Basis points provide precision when discussing interest rate changes, avoiding confusion that can arise from percentage-of-percentage calculations.",
            "today": "A move of 5-10 basis points is notable. A move exceeding 20 basis points is substantial."
        },
        {
            "term": "U.S. Dollar Index (DXY)",
            "what": "A weighted index measuring the value of the U.S. dollar against a basket of six major currencies: the euro, Japanese yen, British pound, Canadian dollar, Swedish krona, and Swiss franc.",
            "why": "Gold and silver are priced in dollars. Dollar strength increases the cost for international buyers; dollar weakness reduces it.",
            "today": "Dollar strength often coincides with softer metals. Dollar weakness often coincides with firmer metals."
        },
        {
            "term": "Volatility",
            "what": "A statistical measure of the dispersion of returns, indicating how much prices fluctuate over a given period.",
            "why": "Volatility indicates the intensity of market conditions. Elevated volatility suggests larger price movements are occurring, though it does not indicate direction.",
            "today": "Consider whether current volatility is elevated or subdued relative to recent history."
        },
        {
            "term": "Realized vs. Implied Volatility",
            "what": "Realized volatility measures actual historical price movement. Implied volatility is derived from options prices and reflects expected future movement.",
            "why": "Realized volatility looks backward at what occurred. Implied volatility looks forward at what markets expect. This dashboard uses realized volatility for simplicity.",
            "today": "Compare current realized volatility to its recent range to assess whether conditions are calm or turbulent."
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: HOW TO READ THE CHARTS (EXPANDED)
# ─────────────────────────────────────────────────────────────────────────────

def get_chart_walkthrough() -> List[Dict]:
    """Detailed step-by-step analytical framework."""
    return [
        {
            "step": 1, 
            "title": "Begin with Price Observation",
            "desc": "Identify the direction and magnitude of gold and silver price movements.",
            "detail": """Before examining drivers, establish what actually happened. Record whether metals are up, down, or flat, and note the percentage magnitude. Observe whether gold and silver are moving together or diverging—divergence may signal different forces at work.

Key questions: How large is the move in context? Is silver moving proportionally more than gold (normal) or less (unusual)?"""
        },
        {
            "step": 2, 
            "title": "Examine Interest Rates",
            "desc": "Assess Treasury yield movements and their directional implications.",
            "detail": """Interest rates are often the most important driver. Check whether the 10-year Treasury yield has risen or fallen during the session. A move of 5+ basis points is notable; 10+ basis points is significant.

Apply the mechanism: Rising yields increase the opportunity cost of holding gold—bearish for metals. Falling yields reduce opportunity cost—bullish for metals. Determine whether the observed price action is consistent with this relationship."""
        },
        {
            "step": 3, 
            "title": "Examine the U.S. Dollar",
            "desc": "Determine whether currency dynamics reinforce or conflict with the rates signal.",
            "detail": """After rates, check the dollar (DXY). A move of 0.2-0.3% or more is notable.

Apply the mechanism: Dollar strength makes gold more expensive for international buyers—bearish for metals. Dollar weakness makes gold cheaper globally—bullish for metals.

Critical step: Determine whether rates and the dollar are providing the same directional signal or conflicting signals. Aligned signals support confident interpretation; conflicting signals require more cautious analysis."""
        },
        {
            "step": 4, 
            "title": "Assess Volatility Context",
            "desc": "Evaluate whether trading conditions are calm or turbulent.",
            "detail": """Volatility does not indicate direction, but it contextualizes the significance of price moves. Elevated volatility means larger swings are occurring—a 1% move in a low-vol environment is more significant than a 1% move in a high-vol environment.

Check whether current realized volatility is above or below its recent average. During periods of elevated volatility, increased uncertainty should inform how confidently you assert causal explanations."""
        },
        {
            "step": 5, 
            "title": "Evaluate Driver Alignment",
            "desc": "Determine whether macro signals are consistent or conflicting.",
            "detail": """This is the critical synthesis step. Based on steps 2-3, determine:

*Aligned*: Both rates and dollar point the same direction (both bearish or both bullish for gold). Interpretation is relatively straightforward.

*Conflicting*: Rates and dollar point in opposite directions. Interpretation requires ranking which driver likely dominated, or acknowledging that offsetting forces may explain muted price action.

*Quiet*: Neither rates nor dollar moved meaningfully. If metals still moved, consider positioning, sentiment, or headline-driven flows.

Professional discipline requires explicitly categorizing the signal environment before formulating an explanation."""
        },
        {
            "step": 6, 
            "title": "Formulate a Structured Explanation",
            "desc": "Construct a clear explanation using the Observation-Mechanism-Implication framework.",
            "detail": """With analysis complete, structure your explanation:

*Observation*: What happened to prices? (Direction, magnitude, relative behavior)

*Mechanism*: Why did it likely happen? (Which driver dominated, and what is the causal relationship?)

*Implication*: What does this tell us about current market conditions? (Aligned signals suggest clearer interpretation; conflicting signals or quiet macro suggest caution)

If drivers conflict or the data is ambiguous, state this explicitly. Never force a confident narrative onto uncertain data—acknowledge what the data does and does not support."""
        }
    ]


def get_common_mistakes() -> List[str]:
    return [
        "Describing drivers as 'mixed' without specifying which factors are conflicting and why the conflict matters.",
        "Overstating causality based on correlation—prices and rates moving together does not prove rates caused the move.",
        "Ignoring divergence between gold and silver, which often contains information about the nature of the move.",
        "Using jargon without explanation, making analysis inaccessible to non-specialists.",
        "Adding technical indicators or complexity that do not improve explanatory clarity.",
        "Forcing a confident narrative when data is ambiguous—credibility requires acknowledging uncertainty.",
        "Failing to consider positioning or sentiment when fundamental drivers do not explain observed moves.",
        "Treating short-term price action as confirmation of longer-term trends without appropriate qualification."
    ]


def get_interpretation_principles() -> List[Dict]:
    """Additional principles for disciplined interpretation."""
    return [
        {
            "title": "Rates First, Then Dollar",
            "content": "Interest rates typically have a more direct relationship with gold via opportunity cost than currency effects. When both are moving, assess rates first to establish the primary expected effect."
        },
        {
            "title": "Magnitude Matters",
            "content": "A 50 basis point yield move commands attention; a 3 basis point move is noise. Calibrate confidence in driver attribution to the magnitude of macro movements, not just their direction."
        },
        {
            "title": "Conflicting Signals Are Normal",
            "content": "Professional markets often send mixed signals. When rates suggest one direction and the dollar suggests another, the result is often muted or choppy price action. This is not analytical failure—it reflects genuine uncertainty."
        },
        {
            "title": "Beware Over-Attribution",
            "content": "Just because rates rose and gold fell on the same day does not prove rates caused the decline. Correlation is not causation. Qualify assertions appropriately."
        },
        {
            "title": "Acknowledge What You Cannot Know",
            "content": "Positioning data is lagged. Sentiment is unobservable in real-time. Headline sensitivity is unpredictable. When macro does not explain the move, admit it rather than fabricating explanations."
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: EXAMPLES
# ─────────────────────────────────────────────────────────────────────────────

def get_example_scenarios() -> List[Dict]:
    return [
        {
            "title": "Interest Rate-Driven Session",
            "charts": "Treasury yields exhibit substantial movement. The dollar is relatively stable. Precious metals move inversely to yields.",
            "explanation": "Gold declined as the 10-year Treasury yield rose to 4.50%. This movement is consistent with the established relationship between nominal yields and non-yielding assets: higher yields increase the opportunity cost of holding gold, as investors can obtain greater returns from interest-bearing instruments. Currency dynamics showed limited movement and do not appear to be a primary factor."
        },
        {
            "title": "Currency-Driven Session",
            "charts": "The U.S. dollar exhibits substantial movement. Treasury yields are relatively stable. Precious metals move inversely to the dollar.",
            "explanation": "Gold advanced as the U.S. Dollar Index declined to 103.50. This movement is consistent with the historically inverse relationship between dollar strength and dollar-denominated commodities: a weaker dollar reduces the cost for international buyers, which tends to support demand. Interest rates showed limited movement and do not appear to be a primary factor."
        },
        {
            "title": "Risk-Off Session",
            "charts": "Equity markets decline. Volatility indicators rise. Gold advances despite mixed signals from rates and the dollar.",
            "explanation": "Gold appreciated during a session characterized by equity market weakness and elevated volatility. The movement appears consistent with gold's historical role as a safe-haven asset: during periods of risk aversion, investors may allocate capital to gold as a hedge against losses elsewhere in portfolios. The move occurred despite mixed signals from rates and the dollar, suggesting risk sentiment was the dominant driver."
        },
        {
            "title": "Industrial-Led Session (Silver Outperformance)",
            "charts": "Silver substantially outperforms gold. Growth-sensitive assets show strength. The dollar may be stable or weaker.",
            "explanation": "Silver outperformed gold significantly during this session. This relative strength is consistent with improved expectations for economic growth, as silver has substantial industrial demand from electronics, solar energy, and manufacturing sectors. Gold drivers—rates and the dollar—showed limited movement, suggesting silver's industrial characteristics were the primary factor."
        },
        {
            "title": "Conflicting Signals Session",
            "charts": "Yields rise (typically bearish for gold). The dollar weakens (typically bullish for gold). Precious metals exhibit choppy or range-bound behavior.",
            "explanation": "Gold exhibited limited net movement during a session with conflicting macro signals. Rising yields created headwinds, as higher opportunity costs reduce the attractiveness of non-yielding assets. However, simultaneous dollar weakness provided offsetting support, as a weaker dollar makes commodities less expensive for international buyers. The conflicting signals resulted in inconclusive price action, illustrating why caution is warranted when interpreting mixed environments."
        },
        {
            "title": "Non-Macro Session",
            "charts": "Both yields and the dollar exhibit limited movement. Precious metals move despite the absence of clear macro catalysts.",
            "explanation": "Gold exhibited notable movement despite limited changes in Treasury yields or the dollar. In the absence of obvious macro drivers, price action may reflect positioning adjustments, technical factors, or sentiment shifts not fully captured by standard macro variables. Interpretation should acknowledge that the observed movement cannot be confidently attributed to the usual fundamental factors."
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: RESOURCES
# ─────────────────────────────────────────────────────────────────────────────

def get_resources() -> List[Dict]:
    return [
        {
            "name": "Bloomberg Terminal",
            "desc": "Professional platform providing real-time market data, news, and analytics. Available at universities and institutional trading desks."
        },
        {
            "name": "Federal Reserve Economic Data (FRED)",
            "desc": "Comprehensive database of economic and financial data maintained by the Federal Reserve Bank of St. Louis. Freely accessible at fred.stlouisfed.org."
        },
        {
            "name": "CME Group / COMEX",
            "desc": "Primary exchange for gold and silver futures trading. The CME website provides educational resources on metals markets at cmegroup.com."
        },
        {
            "name": "World Gold Council",
            "desc": "Industry organization providing research on gold demand, supply, and investment trends. Available at gold.org."
        },
        {
            "name": "Bank for International Settlements (BIS)",
            "desc": "International institution publishing research on global markets, currencies, and monetary policy. Papers available at bis.org."
        },
        {
            "name": "Financial News and Research",
            "desc": "Regular reading of Reuters, Bloomberg, and the Financial Times develops familiarity with market dynamics and professional communication standards."
        }
    ]
