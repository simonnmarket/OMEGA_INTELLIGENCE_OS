
import numpy as np
import pandas as pd

def compute_signed_volume(df, price_col='price', size_col='size', side_col='side'):
    # side: 'B' buy aggressive, 'S' sell aggressive. if missing, infer by tick rule (compare to previous price)
    df = df.copy()
    if side_col not in df.columns or df[side_col].isna().all():
        df['side_infer'] = np.where(df[price_col].diff().fillna(0) > 0, 'B', 
                                     np.where(df[price_col].diff().fillna(0) < 0, 'S', 'U'))
        side = 'side_infer'
    else:
        side = side_col
    df['signed_size'] = np.where(df[side]=='B', df[size_col], np.where(df[side]=='S', -df[size_col], 0))
    return df

def aggregate_by_bar(ticks_df, bars_df, price_col='price', size_col='size', timestamp_col='timestamp'):
    # compute delta per bar
    ticks = ticks_df.copy()
    ticks['bar_time'] = pd.cut(ticks[timestamp_col], bins=list(bars_df.index) + [bars_df.index[-1] + (bars_df.index[-1]-bars_df.index[-2])])
    agg = ticks.groupby('bar_time').agg(
        delta = ('signed_size','sum'),
        buy_volume = (lambda x: (x>0).sum(), 'size') if False else ('size','sum')
    )
    # simpler: for each bar, compute signed volume sum
    signed = ticks.groupby(pd.Grouper(key=timestamp_col, freq=bars_df.index.inferred_freq or '1T'))['signed_size'].sum()
    bars_df = bars_df.copy()
    bars_df['delta'] = signed.reindex(bars_df.index, method='pad').fillna(0).values
    bars_df['cum_delta'] = bars_df['delta'].cumsum()
    return bars_df

def compute_imbalance_per_bar(bars_df):
    # simple imbalance: delta / volume
    bars = bars_df.copy()
    bars['imbalance'] = bars['delta'] / bars['volume'].replace(0, np.nan)
    bars['imbalance'] = bars['imbalance'].fillna(0)
    return bars

def price_velocity(bars_df):
    bars = bars_df.copy()
    bars['vel'] = bars['close'].diff().abs() / (bars.index.to_series().diff().dt.total_seconds().replace(0,1))
    bars['vel'] = bars['vel'].fillna(0)
    return bars
