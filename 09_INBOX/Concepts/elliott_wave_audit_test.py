# elliott_wave_audit_test.py
"""
Auditable test script to run Elliott detection on a real asset and produce:
 - waves.json (detected waves)
 - laudo.txt (human-readable report)
 - audit.json (provenance: data hash, seed, package versions)
Usage (local):
 python elliott_wave_audit_test.py --ticker "^GSPC" --start "2020-01-01" --end "2025-01-01"
Dependencies:
 pip install yfinance numpy pandas scipy
"""

import argparse, json, time, uuid, hashlib, socket, platform, os
from pathlib import Path
import numpy as np, pandas as pd
from elliott_module import ElliottModule, sha256_of_file, record_env

def fetch_series(ticker, start, end, interval='1d'):
    import yfinance as yf
    df = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for ticker {ticker}")
    return df[['Open','High','Low','Close','Volume']].dropna()

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def main(args):
    run_id = time.strftime("%Y%m%dT%H%M%S") + "-" + str(uuid.uuid4())[:8]
    outdir = Path("outputs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)

    env = record_env(seed=args.seed)
    env["command"] = " ".join(os.sys.argv)
    env["ticker"] = args.ticker
    env["start"] = args.start
    env["end"] = args.end

    print("[DATA] Downloading", args.ticker)
    df = fetch_series(args.ticker, args.start, args.end, interval=args.interval)
    raw_path = outdir / "raw_data.csv"
    df.to_csv(raw_path)
    env["raw_data_sha256"] = sha256_of_file(str(raw_path))
    env["rows"] = len(df)

    # Run detection
    em = ElliottModule(name="audit_run")
    waves = em.detect_waves(df['Close'], prominence=args.prominence)
    waves_path = outdir / "waves.json"
    em.save_waves(str(waves_path))
    env["waves_sha256"] = sha256_of_file(str(waves_path))

    # Generate laudo
    laudo = em.aggregate_and_report()
    laudo_path = outdir / "laudo.txt"
    with open(laudo_path, "w", encoding="utf-8") as f:
        f.write(laudo)

    # Save audit info
    audit = env.copy()
    audit["run_id"] = run_id
    audit["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    audit_path = outdir / "audit.json"
    save_json(audit_path, audit)
    # Save a simple run summary
    summary = {
        "run_id": run_id,
        "ticker": args.ticker,
        "rows": env["rows"],
        "n_waves": len(waves),
        "outdir": str(outdir)
    }
    save_json(outdir / "summary.json", summary)

    print("[DONE] Outputs saved to", outdir)
    print("Detected waves:", len(waves))
    print("Laudo path:", laudo_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elliott wave audit test")
    parser.add_argument("--ticker", type=str, default="^GSPC")
    parser.add_argument("--start", type=str, default="2020-01-01")
    parser.add_argument("--end", type=str, default="2025-11-01")
    parser.add_argument("--interval", type=str, default="1d")
    parser.add_argument("--prominence", type=float, default=0.0, help="Prominence for peak detection (try 0.01 for stronger)")
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args()
    main(args)
