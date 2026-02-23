
import numpy as np

def normalize_score(x, min_v=-100, max_v=100):
    # map x into 0..100
    if np.isnan(x):
        return 0.0
    v = (x - min_v) / (max_v - min_v)
    return float(np.clip(v*100, 0, 100))

def compute_mpi(scores, weights):
    # scores: dict of component scores already in 0..100
    wsum = sum(weights.values())
    mpi = 0.0
    for k,w in weights.items():
        mpi += scores.get(k,0.0) * (w / wsum)
    return float(np.clip(mpi,0,100))
