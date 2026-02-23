# Theodora | PHANTOM Core (leve) - sem dependências pesadas
# Objetivo: gerar métricas determinísticas e um edge_bps proxy por símbolo

import math
import time


def _seed_from_symbol(symbol: str) -> int:
    # Determinístico por símbolo
    h = 0
    for ch in symbol:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h or 42


def _pseudo_random(seed: int) -> float:
    # LCG simples determinístico
    a = 1103515245
    c = 12345
    m = 2 ** 31
    seed = (a * seed + c) % m
    return seed / m, seed


def _proxy_series(symbol: str, length: int = 32):
    seed = _seed_from_symbol(symbol)
    prices = []
    volumes = []
    base_price = 100.0 + (seed % 50)
    price = base_price
    vol_base = 1000.0 + (seed % 500)
    for i in range(length):
        r, seed = _pseudo_random(seed)
        drift = (r - 0.5) * 0.4  # pequeno drift
        price = max(1.0, price + drift)
        prices.append(price)

        r2, seed = _pseudo_random(seed)
        vol = vol_base * (0.8 + 0.4 * r2)
        volumes.append(vol)
    return prices, volumes


def _shannon_entropy(hist_probs):
    eps = 1e-12
    return -sum(p * math.log(p + eps) for p in hist_probs if p > 0)


def _std(values):
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(max(0.0, var))


def _zscore_last(values):
    n = len(values)
    if n < 3:
        return 0.0
    mean = sum(values) / n
    std = _std(values)
    if std <= 0:
        return 0.0
    return (values[-1] - mean) / std


def compute_phantom_for_symbol(symbol: str, volume_series=None, length: int = 32):
    # Gera séries proxy determinísticas; se volume_series vier, usa para métricas
    prices, vols = _proxy_series(symbol, length)
    if volume_series and len(volume_series) >= 3:
        vols = list(volume_series)[-length:]

    # Entropia (caos) via hist de retornos
    rets = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    if not rets:
        rets = [0.0]
    # histograma simples em 10 bins
    mn = min(rets)
    mx = max(rets)
    width = (mx - mn) / 10.0 if mx > mn else 1.0
    counts = [0] * 10
    for r in rets:
        idx = int((r - mn) / width)
        if idx >= 10:
            idx = 9
        if idx < 0:
            idx = 0
        counts[idx] += 1
    total = float(sum(counts)) or 1.0
    probs = [c / total for c in counts]
    chaos = _shannon_entropy(probs)

    # Incerteza (Heisenberg adaptado)
    uncertainty = _std(rets) * _std(vols)

    # Campo (order flow proxy) e liquidez
    # Campo: norma da soma de sinais de volume (compras-vendas simuladas)
    field = 0.0
    seed = _seed_from_symbol(symbol) ^ 0xA53
    for v in vols:
        r, seed = _pseudo_random(seed)
        sgn = 1.0 if r > 0.5 else -1.0
        field += sgn * v
    field = abs(field) / (sum(vols) + 1e-9)

    liquidity = sum(vols) / (len(vols) + 1e-9)

    # Normalizações toscas para [0..1]
    chaos_norm = min(1.0, chaos / 3.0)
    vol_z = _zscore_last(vols)
    vol_z_norm = min(1.0, max(0.0, (vol_z + 3.0) / 6.0))
    field_norm = min(1.0, field)

    # Edge em bps: valorizamos baixo caos, alto z de volume e campo/líquidez
    edge_bps = (
        (1.0 - chaos_norm) * 60.0 +
        vol_z_norm * 30.0 +
        field_norm * 20.0
    )

    return {
        "chaos": float(chaos),
        "uncertainty": float(uncertainty),
        "field": float(field),
        "liquidity": float(liquidity),
        "vol_z": float(vol_z),
        "edge_bps": float(edge_bps),
    }


