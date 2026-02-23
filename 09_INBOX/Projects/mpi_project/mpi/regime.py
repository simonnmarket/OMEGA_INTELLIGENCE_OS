
import ruptures as rpt
import numpy as np
import pandas as pd

def detect_change_points(series, model='rbf', pen=10):
    # series: 1D numpy array or pandas Series
    algo = rpt.Pelt(model=model).fit(series.astype(float))
    result = algo.predict(pen=pen)
    # returns breakpoints (indices)
    return result

def regime_score_from_breaks(bars_df, window=30):
    # compute change points on cum_delta or imbalance
    s = bars_df['cum_delta'].diff().fillna(0).values
    try:
        breaks = detect_change_points(s, pen=5)
        # if many breaks in short window -> unstable -> higher regime score
        recent_breaks = [b for b in breaks if b > len(s)-window]
        score = min(1.0, len(recent_breaks)/5.0)
        return float(score)
    except Exception:
        return 0.0
