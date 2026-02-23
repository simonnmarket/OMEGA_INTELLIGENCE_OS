# MEMORY_ID: TASK_MARKET_SESSION_MANAGER
# TIMESTAMP: 2025-11-09T19:47:30+01:00
# AUTHOR: Cursor_Omega

"""
Configurações padrão de janelas de negociação e grupos de ativos.

O objetivo é fornecer uma base institucional para controle de sessões, com
horários alinhados ao fuso CET (Europe/Berlin).
"""

from datetime import time
from typing import Dict, Iterable, List, Tuple

# --------------------------------------------------------------------------- #
# MODO PADRÃO POR JANELA (CET)
# --------------------------------------------------------------------------- #
SESSION_WINDOWS: List[Dict[str, object]] = [
    {
        "days": ("monday", "tuesday", "wednesday", "thursday"),
        "start": time(0, 0),
        "end": time(23, 59, 59),
        "mode": "full",
    },
    {
        "days": ("friday",),
        "start": time(0, 0),
        "end": time(22, 0),
        "mode": "full",
    },
    {
        "days": ("friday",),
        "start": time(22, 0),
        "end": time(23, 59, 59),
        "mode": "crypto_only",
    },
    {
        "days": ("saturday",),
        "start": time(0, 0),
        "end": time(23, 59, 59),
        "mode": "crypto_only",
    },
    {
        "days": ("sunday",),
        "start": time(0, 0),
        "end": time(23, 59, 59),
        "mode": "crypto_only",
    },
]

# --------------------------------------------------------------------------- #
# GRUPOS DE ATIVOS
# --------------------------------------------------------------------------- #
ASSET_GROUP_SYMBOLS: Dict[str, Tuple[str, ...]] = {
    "indices": (
        "US500",
        "US30",
        "US100",
        "US2000",
        "GER40",
        "UK100",
        "FR40",
        "EU50",
    ),
    "metals": (
        "XAUUSD",
        "XAGUSD",
        "XAUEUR",
        "XAUCHF",
    ),
    "energy": (
        "UKOIL+",
        "USOIL+",
    ),
    "forex": (
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "USDCHF",
        "USDCAD",
        "AUDUSD",
        "NZDUSD",
        "EURJPY",
        "EURGBP",
        "GBPJPY",
        "USDSEK",
        "USDCNH",
    ),
    "crypto": (
        "BTCUSD",
        "ETHUSD",
    ),
}

# --------------------------------------------------------------------------- #
# PERMISSÕES POR MODO
# --------------------------------------------------------------------------- #
MODE_ALLOWED_GROUPS: Dict[str, Tuple[str, ...]] = {
    "full": ("indices", "metals", "energy", "forex", "crypto"),
    "forex_only": ("forex",),
    "crypto_only": ("crypto",),
    "closed": tuple(),
}

# --------------------------------------------------------------------------- #
# LIMITE DE IDADE DE TICK POR GRUPO (segundos)
# --------------------------------------------------------------------------- #
GROUP_MAX_TICK_AGE_SECONDS: Dict[str, int] = {
    "indices": 4 * 3600,  # 4 horas
    "metals": 4 * 3600,
    "energy": 6 * 3600,
    "forex": 2 * 3600,
    "crypto": 15 * 60,  # 15 minutos
}

# --------------------------------------------------------------------------- #
# FERIADOS ESPECIAIS (placeholder para integração futura)
# --------------------------------------------------------------------------- #
SPECIAL_DATE_MODES: Dict[str, str] = {}


def flatten_groups(groups: Iterable[str]) -> List[str]:
    """Retorna a lista de símbolos pertencentes aos grupos informados."""
    symbols: List[str] = []
    for group in groups:
        symbols.extend(ASSET_GROUP_SYMBOLS.get(group, ()))
    return symbols

