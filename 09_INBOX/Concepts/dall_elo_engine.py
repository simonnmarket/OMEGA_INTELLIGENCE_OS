# dall_elo_engine.py
"""
DALL-ELO Engine — "The Motor"
A unified, auditable, modular engine that fuses a latent generative model (DALL-style)
with Elliott Wave structural analysis (ELO) to produce actionable, explainable
market signals, conditional scenarios, and risk metrics.

This file is a research-grade scaffold: all heavy models are represented as
replaceable stubs or plugin hooks. The goal is to provide a single, well-documented
"motor" that can be extended to power many downstream products (signals, risk overlays,
regime detectors, strategy modules) across asset classes and timeframes.

Key components:
 - Config: typed configuration and defaults
 - Audit utilities: reproducibility, environment capture, file hashes
 - Interfaces / Abstract base classes: Encoder, Generator, ElliottAdapter, Strategy
 - Core Engine: DallEloEngine class that wires components and exposes a small API
 - Plugins: Strategy registry, Metric calculators, Persistence hooks
 - Examples: minimal in-memory stubs to allow local testing without external models

Usage (developer):
 - Replace Encoder/Generator stubs with real implementations (torch models, checkpoints)
 - Provide Elliott wave input (list of wave dicts) via ElliottAdapter or load from file
 - Call engine.analyze_window(window) for a single window, or engine.run_on_series(series) for sliding windows
 - Persist audits, scenarios, and results using engine.persist_run

This file intentionally does NOT download data or train models. It produces structured outputs and audit objects ready to be stored and tested.
"""

from __future__ import annotations
import json, os, time, uuid, hashlib, platform, socket, importlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Tuple
import numpy as np
import pandas as pd

# -------------------------------
# Configuration & dataclasses
# -------------------------------
@dataclass
class EngineConfig:
    name: str = "DALL-ELO-Engine"
    latent_dim: int = 64
    default_n_scenarios: int = 500
    default_noise_scale: float = 0.05
    seed: int = 12345
    audit_dir: str = "outputs_engine"
    save_scenarios: bool = True
    max_workers: int = 4  # for later parallelism

@dataclass
class AuditRecord:
    run_id: str
    utc: str
    command: str
    seed: int
    host: str
    platform: str
    python_version: str
    pkg_versions: Dict[str, str]
    artifacts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

# -------------------------------
# Audit utilities
# -------------------------------
def record_env(seed: int = 12345) -> Dict[str, Any]:
    env = {
        "run_id": time.strftime("%Y%m%dT%H%M%S") + "-" + str(uuid.uuid4())[:8],
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": int(seed),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "pkg_versions": {}
    }
    # record versions for common packages if available
    for p in ("numpy","pandas","scipy","sklearn","torch"):
        try:
            m = importlib.import_module(p)
            env["pkg_versions"][p] = getattr(m, "__version__", "n/a")
        except Exception:
            env["pkg_versions"][p] = "not_installed"
    return env

def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def save_audit(audit_obj: Dict[str,Any], outdir: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "audit.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit_obj, f, indent=2, ensure_ascii=False)
    ph = sha256_of_file(path)
    with open(os.path.join(outdir, "audit_sha256.txt"), "w", encoding="utf-8") as f:
        f.write(ph)
    return ph

# -------------------------------
# Interfaces / Stubs (replaceable)
# -------------------------------
class BaseEncoder:
    """Interface: encode a price window -> latent vector"""
    def encode(self, window: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implement encode() to return latent vector (np.ndarray)")

class BaseGenerator:
    """Interface: sample trajectories from latent + condition"""
    def sample(self, latent: np.ndarray, condition: Dict[str,Any], n: int, noise_scale: float) -> np.ndarray:
        raise NotImplementedError("Implement sample() to return array (n, traj_len) or (n, latent_dim)")

class BaseElliottAdapter:
    """Adapter to normalise Elliott outputs to engine-friendly state"""
    def __init__(self, waves: Optional[List[Dict[str,Any]]] = None):
        self.waves = waves or []
    def latest_state(self) -> Dict[str,Any]:
        if not self.waves:
            return {"type":None,"degree":None,"amplitude":0.0,"duration":0,"confidence":0.0}
        latest = max(self.waves, key=lambda w: int(w.get("end_idx",0)))
        return {"type":latest.get("type"), "degree":latest.get("degree"), "amplitude":float(latest.get("amplitude") or 0.0), "duration":int(latest.get("duration") or 0), "confidence":float(latest.get("confidence") or 0.0)}

# -------------------------------
# Minimal example implementations
# -------------------------------
class SimpleEncoder(BaseEncoder):
    """Simple deterministic encoder (placeholder)."""
    def __init__(self, latent_dim:int):
        self.latent_dim = int(latent_dim)
    def encode(self, window: np.ndarray) -> np.ndarray:
        x = np.asarray(window).astype(float).ravel()
        if x.size < self.latent_dim:
            x = np.pad(x, (0, self.latent_dim - x.size), 'constant')
        else:
            x = x[: self.latent_dim]
        z = (x - x.mean()) / (x.std() + 1e-9)
        return z

class SimpleGenerator(BaseGenerator):
    """Simple generator that perturbs latent to create 'trajectories' (stub)."""
    def __init__(self, output_len:int):
        self.output_len = int(output_len)
    def sample(self, latent: np.ndarray, condition: Dict[str,Any], n: int, noise_scale: float) -> np.ndarray:
        base = np.asarray(latent).ravel()
        if base.size < self.output_len:
            base = np.pad(base, (0, self.output_len - base.size), 'constant')
        else:
            base = base[: self.output_len]
        samples = []
        cond_shift = 0.0
        if condition.get("type") == "impulse":
            cond_shift += 0.25 * condition.get("confidence", 0.0)
        elif condition.get("type") == "corrective":
            cond_shift -= 0.15 * condition.get("confidence", 0.0)
        scale = 1.0 + 0.5 * abs(condition.get("amplitude", 0.0))
        for i in range(int(n)):
            noise = np.random.normal(loc=cond_shift, scale=noise_scale*scale, size=base.shape)
            samples.append(base + noise)
        return np.vstack(samples)

# -------------------------------
# Metric calculators & helpers
# -------------------------------
def compute_alignment_score(latent: np.ndarray, elo_state: Dict[str,Any]) -> float:
    z = np.asarray(latent).ravel()
    z_mean = float(np.mean(z))
    amp = float(elo_state.get("amplitude",0.0))
    conf = float(elo_state.get("confidence",0.0))
    sign_agree = 1.0 if (z_mean * amp) > 0 else 0.0
    mag_score = 1.0 - np.tanh(abs(z_mean) - abs(amp))
    score = 0.5 * (sign_agree * (0.5 + 0.5 * conf)) + 0.5 * max(0.0, mag_score)
    return float(max(0.0, min(1.0, score)))

def scenarios_to_pnl(trajectories: np.ndarray, last_price: float) -> np.ndarray:
    # assume trajectories are log-return like; compute final price per scenario and pnl
    cum = np.sum(trajectories, axis=1)
    final_prices = last_price * np.exp(cum)
    pnl = (final_prices - last_price) / last_price  # relative pnl
    return pnl

def var_es_from_pnl(pnl: np.ndarray, alpha: float=0.95) -> Tuple[float,float]:
    q = np.quantile(pnl, 1-alpha)
    var = -q
    tail = pnl[pnl <= q]
    es = -float(np.mean(tail)) if tail.size>0 else var
    return float(var), float(es)

# -------------------------------
# Strategy interface & registry
# -------------------------------
class BaseStrategy:
    """Strategy receives fusion results and decides signals or sizing"""
    def on_fusion(self, fusion_output: Dict[str,Any]) -> Dict[str,Any]:
        raise NotImplementedError("Implement on_fusion to return dict with keys: action, size, reason")

STRATEGY_REGISTRY: Dict[str, Callable[[],BaseStrategy]] = {}

def register_strategy(name: str):
    def _inner(cls):
        STRATEGY_REGISTRY[name] = cls
        return cls
    return _inner

@register_strategy("simple_breakout")
class SimpleBreakoutStrategy(BaseStrategy):
    """
    Example: If alignment high + up_prob > threshold => 'enter long' with size proportional to alignment.
    """
    def __init__(self, up_prob_thresh: float=0.6, align_thresh: float=0.6):
        self.up_prob_thresh = float(up_prob_thresh)
        self.align_thresh = float(align_thresh)
    def on_fusion(self, fusion_output: Dict[str,Any]) -> Dict[str,Any]:
        metrics = fusion_output.get("metrics", {})
        up_prob = metrics.get("up_prob", 0.0)
        align = metrics.get("alignment_mean", 0.0)
        if up_prob >= self.up_prob_thresh and align >= self.align_thresh:
            size = float(min(1.0, align))  # normalized position sizing
            return {"action":"enter_long", "size": size, "reason": f"up_prob={up_prob:.2f}, align={align:.2f}"}
        return {"action":"hold", "size":0.0, "reason":"no signal"}

# -------------------------------
# Core Engine
# -------------------------------
class DallEloEngine:
    def __init__(self, config: Optional[EngineConfig]=None, encoder: Optional[BaseEncoder]=None, generator: Optional[BaseGenerator]=None, elo_adapter: Optional[BaseElliottAdapter]=None):
        self.config = config or EngineConfig()
        np.random.seed(self.config.seed)
        self.encoder = encoder or SimpleEncoder(self.config.latent_dim)
        self.generator = generator or SimpleGenerator(output_len=self.config.latent_dim)
        self.elo = elo_adapter or BaseElliottAdapter([])
        self.strategies: Dict[str, BaseStrategy] = {}
        # instantiate registered strategies with default params
        for k,cls in STRATEGY_REGISTRY.items():
            try:
                self.strategies[k] = cls()
            except Exception:
                # instantiate without args if signature differs
                self.strategies[k] = cls if isinstance(cls, BaseStrategy) else cls()

    def analyze_window(self, window: np.ndarray, n_scenarios: Optional[int]=None, noise_scale: Optional[float]=None, last_price: Optional[float]=None) -> Dict[str,Any]:
        n_scenarios = int(n_scenarios or self.config.default_n_scenarios)
        noise_scale = float(noise_scale or self.config.default_noise_scale)
        latent = self.encoder.encode(window)
        elo_state = self.elo.latest_state()
        trajectories = self.generator.sample(latent, elo_state, n=n_scenarios, noise_scale=noise_scale)
        # compute metrics
        last_price = float(last_price) if last_price is not None else float(np.exp(window[-1]) if window.size>0 else 1.0)
        pnl = scenarios_to_pnl(trajectories, last_price)
        var, es = var_es_from_pnl(pnl, alpha=0.95)
        up_prob = float(np.mean(pnl > 0))
        down_prob = float(np.mean(pnl < 0))
        alignment = compute_alignment_score(latent, elo_state)
        metrics = {"var95":var, "es95":es, "up_prob":up_prob, "down_prob":down_prob, "vol": float(np.std(pnl)), "alignment_mean": alignment}
        meta = {"elo_state": elo_state, "latent_mean": float(np.mean(latent)), "n_scenarios": n_scenarios, "noise_scale": noise_scale}
        fusion_output = {"metrics": metrics, "meta": meta, "trajectories_summary": {"pnl_mean": float(np.mean(pnl)), "pnl_std": float(np.std(pnl))} }
        # run strategies
        strategy_results = {}
        for name, strat in self.strategies.items():
            try:
                res = strat.on_fusion(fusion_output)
                strategy_results[name] = res
            except Exception as e:
                strategy_results[name] = {"error": str(e)}
        fusion_output["strategies"] = strategy_results
        return fusion_output

    def run_on_series(self, series: pd.Series, window_len: int, step: int=1, **analyze_kwargs) -> Dict[str,Any]:
        results = []
        idxs = []
        for i in range(0, len(series)-window_len, step):
            window = np.diff(np.log(series.values[i:i+window_len+1])) if window_len>0 else np.array([])
            if window.size==0:
                continue
            last_price = float(series.values[i+window_len])
            out = self.analyze_window(window, last_price=last_price, **analyze_kwargs)
            results.append(out)
            idxs.append(series.index[i+window_len])
        return {"index": idxs, "results": results}

    def persist_run(self, outdir: Optional[str]=None, fusion_result: Optional[Dict]=None, raw_window: Optional[np.ndarray]=None):
        outdir = outdir or os.path.join(self.config.audit_dir, record_env(self.config.seed)["run_id"])
        os.makedirs(outdir, exist_ok=True)
        env = record_env(self.config.seed)
        audit = AuditRecord(run_id=env["run_id"], utc=env["utc"], command="dall_elo_analyze", seed=env["seed"], host=env["host"], platform=env["platform"], python_version=env["python_version"], pkg_versions=env["pkg_versions"])
        audit.artifacts["fusion"] = "fusion.json"
        fusion_path = os.path.join(outdir, "fusion.json")
        with open(fusion_path, "w", encoding="utf-8") as f:
            json.dump(fusion_result or {}, f, indent=2, ensure_ascii=False)
        if self.config.save_scenarios and fusion_result and "trajectories_summary" in fusion_result:
            # optionally save trajectories or a placeholder
            pass
        save_audit(audit.to_dict(), outdir)
        return outdir

# -------------------------------
# Developer utilities / example
# -------------------------------
def example_engine_demo():
    # synthetic example to show API use (no external I/O)
    window = np.random.normal(scale=0.01, size=64)  # log-return-like window
    elo_waves = [{"id":"w_0_10","type":"impulse","degree":"Intermediate","amplitude":0.05,"duration":10,"confidence":0.8,"start_idx":0,"end_idx":10}]
    elo = BaseElliottAdapter(elo_waves)
    engine = DallEloEngine(config=EngineConfig(), encoder=SimpleEncoder(latent_dim=64), generator=SimpleGenerator(output_len=64), elo_adapter=elo)
    out = engine.analyze_window(window, n_scenarios=200, noise_scale=0.03, last_price=100.0)
    print("Example fusion output metrics:", out["metrics"])
    print("Strategy outputs:", out["strategies"])

if __name__ == "__main__":
    example_engine_demo()
