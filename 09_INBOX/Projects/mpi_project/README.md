
# Market Pressure Index (MPI) - Prototype

This repository contains a **prototype implementation** (reference implementation) of the Market Pressure Index (MPI) described in the project documentation.

**Components**
- Data ingestion (CSV tick/trades + optional LOB levels)
- Feature engineering: delta, cumulative delta, imbalance, volume profile, POC shifts, price velocity
- Regime detection (change-point via `ruptures`)
- MPI aggregation and scoring (0-100)
- Backtest / evaluation helper
- Visualizations (matplotlib)

This prototype is intended for research, backtesting and engineering integration. It is **not** production-ready (no low-latency feeds, no persistence, minimal error handling).

## Requirements
- Python 3.9+
- pandas, numpy, scipy, scikit-learn, ruptures, matplotlib

Install dependencies:
```
pip install -r requirements.txt
```

## Usage (example)
1. Prepare a CSV with tick/trade data with columns: `timestamp,price,size,side` where `side` is 'B' or 'S' (buy/sell) or missing.
2. Run example:
```
python run_example.py --input data/sample_ticks.csv
```

Outputs:
- `outputs/mpi_scores.csv`
- Plots in `outputs/`

