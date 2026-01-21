import pandas as pd
import numpy as np

def generate_market_data():
    """Generates mock data for commodities and indices."""
    np.random.seed(42) # For consistent "random" data
    
    # 1. Commodity Sparklines
    dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='h')
    
    df_wti = pd.DataFrame({
        'Date': dates,
        'Price': np.cumsum(np.random.randn(50)) + 78.0
    })
    
    df_gold = pd.DataFrame({
        'Date': dates,
        'Price': np.cumsum(np.random.randn(50) * 2) + 2040.0
    })

    return df_wti, df_gold

def generate_vol_surface():
    """Generates a mock volatility surface dataframe."""
    strikes = [4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150]
    expiries = ['0DTE', '1DTE', '1W', '1M', '3M', '6M']
    
    data = []
    for exp_i, exp in enumerate(expiries):
        for s_i, strike in enumerate(strikes):
            # IV Model approximation (Smile + Term Structure)
            moneyness = (strike - 5000) / 5000
            smile_factor = moneyness ** 2 * 100
            term_factor = 20 - (exp_i * 2) # Backwardation simulation
            
            iv = 10 + smile_factor + term_factor + np.random.rand()  
            data.append({'Expiry': exp, 'Strike': str(strike), 'IV': iv})
            
    return pd.DataFrame(data)

def get_macro_signals():
    return [
        {"time": "14:32 EST", "type": "critical", "title": "SUEZ DISRUPTION", "desc": "Tanker rerouting confirmed. WTI Spreads widening > $1.20."},
        {"time": "14:15 EST", "type": "warning", "title": "VOL SPIKE", "desc": "VIX > 18.00. High put volume on SPX 4950 strikes."},
        {"time": "13:45 EST", "type": "info", "title": "FED SPEAKER", "desc": "Waller: 'No rush to cut'. DXY +0.2% on comments."}
    ]
