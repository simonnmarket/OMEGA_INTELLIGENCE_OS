# Theodora | MT5 Adapter (leve, sem pandas)
# Fornece OHLCV e indicadores institucionais básicos

from typing import Dict, Any, List, Optional

try:
    import MetaTrader5 as mt5
    _MT5_OK = True
except Exception:
    mt5 = None
    _MT5_OK = False

_INITIALIZED = False


def is_available() -> bool:
    return _MT5_OK


def _ensure_initialized() -> bool:
    global _INITIALIZED
    if not _MT5_OK:
        return False
    if _INITIALIZED:
        return True
    try:
        if mt5.initialize():
            _INITIALIZED = True
            return True
        return False
    except Exception:
        return False


_TF_MAP = {
    "M1": "TIMEFRAME_M1",
    "M5": "TIMEFRAME_M5",
    "M15": "TIMEFRAME_M15",
    "M30": "TIMEFRAME_M30",
    "H1": "TIMEFRAME_H1",
    "H4": "TIMEFRAME_H4",
    "D1": "TIMEFRAME_D1",
}


def _resolve_timeframe(tf_str: str):
    if not _MT5_OK:
        return None
    key = _TF_MAP.get((tf_str or "").upper(), "TIMEFRAME_H1")
    return getattr(mt5, key, mt5.TIMEFRAME_H1)


def _to_list_rates(rates) -> List[Dict[str, Any]]:
    out = []
    if rates is None:
        return out
    for r in rates:
        out.append({
            "time": int(r["time"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "tick_volume": float(r.get("tick_volume", r.get("real_volume", 0.0))),
        })
    return out


def _atr(values: List[Dict[str, Any]], period: int = 14) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    trs = []
    prev_close = values[0]["close"]
    for i in range(1, n):
        h = values[i]["high"]
        l = values[i]["low"]
        c_prev = prev_close
        tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
        trs.append(tr)
        prev_close = values[i]["close"]
    if not trs:
        return 0.0
    if len(trs) < period:
        period = len(trs)
    return float(sum(trs[-period:]) / max(1, period))


def _vwap(values: List[Dict[str, Any]]) -> float:
    num = 0.0
    den = 0.0
    for v in values:
        typical = (v["high"] + v["low"] + v["close"]) / 3.0
        vol = max(0.0, v["tick_volume"])  # proxy
        num += typical * vol
        den += vol
    if den <= 0.0:
        return values[-1]["close"] if values else 0.0
    return float(num / den)


def _volume_profile(values: List[Dict[str, Any]], bins: int = 20) -> Dict[str, float]:
    if not values:
        return {"poc": 0.0, "vah": 0.0, "val": 0.0}
    lo = min(v["low"] for v in values)
    hi = max(v["high"] for v in values)
    if hi <= lo:
        p = values[-1]["close"]
        return {"poc": p, "vah": p, "val": p}
    width = (hi - lo) / float(bins)
    hist = [0.0] * bins
    for v in values:
        # usa preço típico para histogramar por volume
        price = (v["high"] + v["low"] + v["close"]) / 3.0
        idx = int((price - lo) / width)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        hist[idx] += max(0.0, v["tick_volume"])
    # POC
    poc_idx = max(range(bins), key=lambda i: hist[i] if hist else 0.0)
    poc = lo + (poc_idx + 0.5) * width
    total = sum(hist) or 1.0
    target = 0.7 * total
    # expande em torno do POC até cobrir ~70%
    left = right = poc_idx
    acc = hist[poc_idx]
    while acc < target and (left > 0 or right < bins - 1):
        # escolhe lado mais volumoso
        l_val = hist[left - 1] if left > 0 else -1.0
        r_val = hist[right + 1] if right < bins - 1 else -1.0
        if r_val >= l_val:
            if right < bins - 1:
                right += 1
                acc += hist[right]
            else:
                left -= 1
                acc += hist[left]
        else:
            if left > 0:
                left -= 1
                acc += hist[left]
            else:
                right += 1
                acc += hist[right]
    val = lo + left * width
    vah = lo + (right + 1) * width
    return {"poc": float(poc), "vah": float(vah), "val": float(val)}


def _regime(values: List[Dict[str, Any]]) -> str:
    # tendência básica: razão entre deslocamento e volatilidade
    if len(values) < 5:
        return "UNKNOWN"
    closes = [v["close"] for v in values]
    mean = sum(closes) / len(closes)
    var = sum((c - mean) ** 2 for c in closes) / max(1, len(closes) - 1)
    std = var ** 0.5
    drift = closes[-1] - closes[0]
    score = abs(drift) / (std + 1e-9)
    if score >= 1.5:
        return "TREND"
    if score <= 0.5:
        return "BALANCED"
    return "RANGE"


def get_indicators(symbol: str, timeframe: str = "H1", bars: int = 500) -> Dict[str, Any]:
    ok = _ensure_initialized()
    if not ok:
        return {"status": "mt5_unavailable"}
    tf = _resolve_timeframe(timeframe)
    if tf is None:
        return {"status": "bad_timeframe"}
    try:
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(bars))
    except Exception as e:
        return {"status": "error", "error": str(e)}
    data = _to_list_rates(rates)
    if not data:
        return {"status": "no_data"}
    atr14 = _atr(data, 14)
    vwap = _vwap(data)
    vp = _volume_profile(data, 24)
    rg = _regime(data)
    return {
        "status": "ok",
        "symbol": symbol,
        "timeframe": timeframe,
        "bars": len(data),
        "atr14": atr14,
        "vwap": vwap,
        "poc": vp["poc"],
        "vah": vp["vah"],
        "val": vp["val"],
        "regime": rg,
        "ohlcv": data[-200:],  # limita para resposta compacta
    }


