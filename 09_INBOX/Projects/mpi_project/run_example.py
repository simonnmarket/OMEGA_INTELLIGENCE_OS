
"""Run an example pipeline: ingestion -> features -> MPI -> output"""
import argparse
import os
import pandas as pd
import numpy as np
from mpi.data_utils import load_ticks_csv, resample_to_bars
from mpi.features import compute_signed_volume, aggregate_by_bar, compute_imbalance_per_bar, price_velocity
from mpi.volume_profile import volume_profile, poc_shift_score
from mpi.regime import regime_score_from_breaks
from mpi.mpi_index import normalize_score, compute_mpi
from mpi.config import MPI_CONFIG

def score_components(bars_df, profiles_hist):
    scores = {}
    # delta score: use recent delta normalized
    delta_val = bars_df['delta'].iloc[-1] if 'delta' in bars_df.columns else 0
    scores['delta'] = normalize_score(delta_val, min_v=-bars_df['volume'].max(), max_v=bars_df['volume'].max())
    # liquidity score: simple proxy: inverse of depth volatility (here use volume stability)
    vol_std = bars_df['volume'].std() if 'volume' in bars_df.columns else 1
    scores['liquidity'] = float(np.clip((1 - min(1, vol_std / (bars_df['volume'].mean()+1e-9)))*100,0,100))
    # volume profile score: POC shift magnitude
    vp_shift = poc_shift_score(profiles_hist)
    scores['volume_profile'] = normalize_score(vp_shift, min_v=-100, max_v=100)
    # velocity
    vel = bars_df['vel'].iloc[-1] if 'vel' in bars_df.columns else 0
    scores['velocity'] = normalize_score(vel, min_v=0, max_v=bars_df['close'].diff().abs().max()*10 if 'close' in bars_df.columns else 1)
    # regime
    scores['regime'] = float(np.clip(regime_score_from_breaks(bars_df, window=30)*100,0,100))
    return scores

def main(input_csv, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ticks = load_ticks_csv(input_csv)
    ticks = compute_signed_volume(ticks)
    bars = resample_to_bars(ticks, rule='1Min')
    bars = aggregate_by_bar(ticks, bars)
    bars = compute_imbalance_per_bar(bars)
    bars = price_velocity(bars)
    profiles = []
    mpi_series = []
    for i in range(5, len(bars)):
        window = bars.iloc[max(0,i-60):i]
        prof = volume_profile(window)
        profiles.append(prof)
        scores = score_components(window, profiles[-5:])
        mpi = compute_mpi(scores, MPI_CONFIG['weights'])
        mpi_series.append(mpi)
    out = bars.iloc[5:].copy()
    out['mpi'] = mpi_series
    out.to_csv(os.path.join(out_dir,'mpi_scores.csv'))
    print('Saved outputs to', out_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', required=True)
    parser.add_argument('--out', dest='out', default='outputs')
    args = parser.parse_args()
    main(args.input, args.out)
