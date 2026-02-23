
import numpy as np
import pandas as pd

def volume_profile(bars_df, bins=50):
    # create a simple volume profile across price range for the given window (bars_df)
    prices = bars_df[['high','low','close']].stack().values
    low = bars_df['low'].min()
    high = bars_df['high'].max()
    if high <= low:
        return None
    edges = np.linspace(low, high, bins+1)
    vols = np.zeros(bins)
    # distribute bar volumes across bin where close sits (simplification)
    for _, r in bars_df.iterrows():
        # find bin for close
        idx = np.searchsorted(edges, r['close']) - 1
        idx = max(0, min(bins-1, idx))
        vols[idx] += r['volume']
    profile = {
        "edges": edges,
        "vols": vols,
        "poc_price": edges[np.argmax(vols)],
        "hvns": np.where(vols > np.percentile(vols,75))[0].tolist(),
        "lvns": np.where(vols < np.percentile(vols,25))[0].tolist()
    }
    return profile

def poc_shift_score(profiles_history):
    # profiles_history: list of profile dicts; compute shift magnitude of POC normalized
    if len(profiles_history) < 2:
        return 0.0
    pocs = [p['poc_price'] for p in profiles_history if p]
    shift = (pocs[-1] - pocs[0]) / (np.mean(pocs) if np.mean(pocs)!=0 else 1)
    return float(np.tanh(shift)*100)  # scale to -100..100 then normalized later
