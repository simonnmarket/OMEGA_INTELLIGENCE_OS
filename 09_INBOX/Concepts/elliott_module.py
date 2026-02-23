# elliott_module.py
"""
Scaffold para Teoria de Elliott: detecção, taxonomia, agregação de evidências e laudo.
Não executa trading nem faz claims de previsão — é um framework de pesquisa auditable.
"""

import numpy as np
import pandas as pd
import json, time, hashlib, uuid, platform, socket

# -----------------------
# Data classes / taxonomy
# -----------------------
class Wave:
    def __init__(self, id, degree, wtype, start_idx, end_idx, start_ts=None, end_ts=None, amplitude=None, duration=None, subwaves=None, features=None, confidence=0.0, source=None):
        self.id = id
        self.degree = degree
        self.type = wtype  # 'impulse' or 'corrective' or other
        self.start_idx = int(start_idx)
        self.end_idx = int(end_idx)
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.amplitude = float(amplitude) if amplitude is not None else None
        self.duration = int(duration) if duration is not None else None
        self.subwaves = subwaves or []
        self.features = features or {}
        self.confidence = float(confidence)
        self.source = source

    def to_dict(self):
        return {
            "id": self.id,
            "degree": self.degree,
            "type": self.type,
            "start_idx": int(self.start_idx),
            "end_idx": int(self.end_idx),
            "start_ts": str(self.start_ts),
            "end_ts": str(self.end_ts),
            "amplitude": float(self.amplitude) if self.amplitude is not None else None,
            "duration": int(self.duration) if self.duration is not None else None,
            "subwaves": [s.to_dict() for s in self.subwaves],
            "features": self.features,
            "confidence": self.confidence,
            "source": self.source
        }

class WaveTaxonomy:
    """Definitions of degrees, typical patterns and Fibonacci expectations."""
    FIBS = [0.236, 0.382, 0.5, 0.618, 1.0, 1.272, 1.618, 2.618]
    DEGREES = ["GrandSupercycle", "Supercycle", "Cycle", "Primary", "Intermediate", "Minor", "Minute", "Minuette"]

# -----------------------
# Utilities / Audit
# -----------------------
def sha256_of_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def record_env(seed=12345):
    import importlib
    env = {
        "run_id": time.strftime("%Y%m%dT%H%M%S") + "-" + str(uuid.uuid4())[:8],
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": seed,
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "pkg_versions": {}
    }
    # record versions for common packages if available
    for p in ("numpy","pandas","scipy","sklearn"):
        try:
            m = importlib.import_module(p)
            env["pkg_versions"][p] = getattr(m, "__version__", "n/a")
        except Exception:
            env["pkg_versions"][p] = "not_installed"
    return env

# -----------------------
# Detection heuristics (starter)
# -----------------------
def find_turning_points(series, prominence=0.0):
    """
    Find peaks and troughs (turning points).
    Tries to use scipy.signal.find_peaks; if not available uses a simple local-check fallback.
    Returns (peaks_list, troughs_list) as indices.
    """
    try:
        from scipy.signal import find_peaks
        arr = series.values if isinstance(series, pd.Series) else np.asarray(series)
        peaks, _ = find_peaks(arr, prominence=prominence)
        troughs, _ = find_peaks(-arr, prominence=prominence)
        return list(map(int, peaks)), list(map(int, troughs))
    except Exception:
        arr = series.values if isinstance(series, pd.Series) else np.asarray(series)
        peaks, troughs = [], []
        for i in range(1, len(arr)-1):
            if arr[i] > arr[i-1] and arr[i] > arr[i+1]:
                peaks.append(int(i))
            if arr[i] < arr[i-1] and arr[i] < arr[i+1]:
                troughs.append(int(i))
        return peaks, troughs

def build_candidate_waves_from_extrema(peaks, troughs, prices_indexed):
    """
    Build simple candidate waves as sequences peak->trough->peak etc.
    Returns list of Wave objects (degree 'Intermediate' by default).
    """
    extrema = sorted([(int(i), 'peak') for i in peaks] + [(int(i), 'trough') for i in troughs], key=lambda x: x[0])
    waves = []
    for j in range(len(extrema)-1):
        i0, t0 = extrema[j]
        i1, t1 = extrema[j+1]
        p0 = float(prices_indexed[int(i0)])
        p1 = float(prices_indexed[int(i1)])
        amp = (p1 - p0) / p0 if p0 != 0 else 0.0
        wtype = 'impulse' if amp > 0 else 'corrective'
        w = Wave(id=f"w_{i0}_{i1}", degree="Intermediate", wtype=wtype, start_idx=i0, end_idx=i1, amplitude=amp, duration=(i1-i0), source="extrema_heuristic")
        waves.append(w)
    return waves

# -----------------------
# Wave classifier / scorer
# -----------------------
def fib_fit_error(amplitude, reference_amp):
    """Normalized error to nearest Fibonacci multiple of reference_amp."""
    if reference_amp == 0:
        return 1.0
    ratios = WaveTaxonomy.FIBS
    errors = [abs(amplitude / reference_amp - r) for r in ratios]
    return float(min(errors))

def score_wave_by_rules(wave, context=None):
    """
    Heuristic scoring:
      - amplitude magnitude and short duration favors 'impulse' classification
      - fib fit error reduces score
    """
    amp = abs(wave.amplitude or 0.0)
    dur = wave.duration or 1
    score = 0.0
    score += min(1.0, amp * 10.0)
    score *= (1.0 / (1.0 + np.log1p(dur)))
    if context and "reference_amp" in context:
        ferr = fib_fit_error(amp, context["reference_amp"])
        score *= max(0.0, 1.0 - ferr)
    wave.confidence = float(score)
    return wave

# -----------------------
# Evidence aggregator & Laudo
# -----------------------
class EvidenceAggregator:
    def __init__(self):
        self.evidence = []  # list of dicts

    def add(self, source, claim, support_score):
        self.evidence.append({"source": source, "claim": claim, "score": float(support_score)})

    def aggregate(self):
        from collections import defaultdict
        agg = defaultdict(list)
        for e in self.evidence:
            agg[e["claim"]].append(e["score"])
        return {k: float(np.mean(v)) for k,v in agg.items()}

class LaudoGenerator:
    def __init__(self, author="elliott_module"):
        self.author = author

    def generate(self, context):
        lines = []
        lines.append(f"Laudo – Elliott Research ({self.author})")
        lines.append(f"Data: {context.get('date')}")
        lines.append(f"Resumo: {context.get('summary')}")
        lines.append("")
        lines.append("Waves summary (top 10 by confidence):")
        waves = sorted(context.get("waves", []), key=lambda w: w.confidence, reverse=True)[:10]
        for w in waves:
            lines.append(f"- {w.id} | type:{w.type} | amp:{w.amplitude:.4f} | dur:{w.duration} | conf:{w.confidence:.2f}")
        lines.append("")
        lines.append("Métricas:")
        for k,v in (context.get("metrics") or {}).items():
            lines.append(f"- {k}: {v}")
        lines.append("")
        lines.append("Conclusão:")
        lines.append(context.get("conclusion", "Nenhuma conclusão formal."))
        return "\n".join(lines)

# -----------------------
# Orchestrator
# -----------------------
class ElliottModule:
    def __init__(self, name="ElliottModule"):
        self.name = name
        self.aggregator = EvidenceAggregator()
        self.laudo = LaudoGenerator(author=name)
        self.registered_waves = []

    def detect_waves(self, price_series, prominence=0.0):
        peaks, troughs = find_turning_points(price_series, prominence=prominence)
        waves = build_candidate_waves_from_extrema(peaks, troughs, price_series.values)
        for i,w in enumerate(waves):
            ref = abs(waves[i-1].amplitude) if i>0 else abs(w.amplitude if w.amplitude is not None else 0.0)
            score_wave_by_rules(w, context={"reference_amp": ref})
        self.registered_waves = waves
        return waves

    def aggregate_and_report(self):
        agg = self.aggregator.aggregate()
        context = {"date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "summary": f"Report for {self.name}", "waves": self.registered_waves, "metrics": agg, "conclusion": "Ver relatório detalhado."}
        return self.laudo.generate(context)

    def save_waves(self, path):
        data = [w.to_dict() for w in self.registered_waves]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# -----------------------
# Demo usage (for reference only)
# -----------------------
def demo_usage():
    import yfinance as yf
    df = yf.download("^GSPC", start="2020-01-01", end="2025-01-01", progress=False)
    pm = ElliottModule("demo")
    waves = pm.detect_waves(df['Close'], prominence=0.01)
    laudo = pm.aggregate_and_report()
    print(laudo)
    pm.save_waves("waves_demo.json")
