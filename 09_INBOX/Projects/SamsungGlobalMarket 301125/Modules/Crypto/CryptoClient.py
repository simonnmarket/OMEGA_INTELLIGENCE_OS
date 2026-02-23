# MEMORY_ID: TASK_CRYPTO_MODULE
# TIMESTAMP: 2025-11-09T22:05:30+01:00
# AUTHOR: Cursor_Omega

"""
Cliente de coleta para dados de criptomoedas (ex.: Binance).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List

import requests

from Core.Logger import get_logger

logger = get_logger("prometheus.crypto_client")


class CryptoClient:
    def __init__(self, config: Dict[str, object]) -> None:
        self.api_url = config.get("api_url", "https://api.binance.com/api/v3/ticker/price")
        self.symbols = config.get("symbols", ["BTCUSDT", "ETHUSDT"])
        self.timeout = config.get("timeout", 5)

    def coletar_dados(self) -> Iterable[dict]:
        dados: List[dict] = []
        for symbol in self.symbols:
            try:
                response = requests.get(self.api_url, params={"symbol": symbol}, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                price = float(data["price"])
                entry = {
                    "metal": data["symbol"],  # reutilizamos campo 'metal' para compatibilidade
                    "preco": price,
                    "collected_at": datetime.now(timezone.utc),
                }
                dados.append(entry)
                logger.info("Coletado %s: %.2f", symbol, price)
            except Exception as exc:
                logger.warning("Falha ao coletar %s: %s", symbol, exc)
        return dados

