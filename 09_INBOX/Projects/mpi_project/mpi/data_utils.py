
import pandas as pd
import numpy as np

def load_ticks_csv(path, timestamp_col='timestamp', price_col='price', size_col='size', side_col='side'):
    df = pd.read_csv(path)
    # attempt to parse timestamp
    try:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    except Exception:
        # assume epoch ms
        df[timestamp_col] = pd.to_datetime(df[timestamp_col].astype(float), unit='ms')
    df = df.sort_values(timestamp_col).reset_index(drop=True)
    # normalize side
    if side_col in df.columns:
        df[side_col] = df[side_col].astype(str).str.upper().map(lambda s: 'B' if s.startswith('B') else ('S' if s.startswith('S') else np.nan))
    return df

def resample_to_bars(df, rule='1Min', price_col='price', size_col='size', timestamp_col='timestamp'):
    # simple OHLCV bars
    o = df.set_index(timestamp_col)[price_col].resample(rule).first()
    h = df.set_index(timestamp_col)[price_col].resample(rule).max()
    l = df.set_index(timestamp_col)[price_col].resample(rule).min()
    c = df.set_index(timestamp_col)[price_col].resample(rule).last()
    v = df.set_index(timestamp_col)[size_col].resample(rule).sum().fillna(0)
    bars = pd.concat([o,h,l,c,v], axis=1)
    bars.columns = ['open','high','low','close','volume']
    bars = bars.dropna(subset=['open'])
    return bars
