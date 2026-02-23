# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 2025-11-09T22:18:30+01:00
# AUTHOR: Cursor_Omega

"""
Cliente de coleta para dados FOREX (ex.: OANDA).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List

import requests

from Core.Logger import get_logger

logger = get_logger("prometheus.forex_client")


class ForexClient:
    def __init__(self, config: Dict[str, object]) -> None:
        self.api_url = config.get("api_url", "")
        self.account_id = config.get("account_id", "")
        self.api_token = config.get("api_token", "")
        self.instruments = config.get("instruments", ["EUR_USD", "GBP_USD"])
        self.timeout = config.get("timeout", 5)

        if not self.api_url or "{account_id}" not in self.api_url:
            raise ValueError("api_url deve conter placeholder {account_id}")
        if not self.account_id or not self.api_token:
            raise ValueError("Credenciais API inválidas para módulo FOREX.")

        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def coletar_dados(self) -> Iterable[dict]:
        dados: List[dict] = []
        for chunk in self._chunk_instruments(self.instruments, chunk_size=10):
            params = {"instruments": ",".join(chunk)}
            url = self.api_url.format(account_id=self.account_id)
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                prices = payload.get("prices", [])
                for price in prices:
                    instrument = price.get("instrument")
                    if not instrument:
                        continue
                    bid = float(price["bids"][0]["price"])
                    ask = float(price["asks"][0]["price"])
                    mid = (bid + ask) / 2
                    entry = {
                        "metal": instrument,  # reutilizamos campo para compatibilidade
                        "preco": mid,
                        "collected_at": datetime.now(timezone.utc),
                        "bid": bid,
                        "ask": ask,
                    }
                    dados.append(entry)
                    logger.info("Coletado %s (bid=%.5f, ask=%.5f)", instrument, bid, ask)
            except Exception as exc:
                logger.warning("Falha ao coletar instrumentos %s: %s", chunk, exc)
        return dados

    @staticmethod
    def _chunk_instruments(instruments: Iterable[str], chunk_size: int) -> Iterable[List[str]]:
        instruments = list(instruments)
        for i in range(0, len(instruments), chunk_size):
            yield instruments[i : i + chunk_size]

