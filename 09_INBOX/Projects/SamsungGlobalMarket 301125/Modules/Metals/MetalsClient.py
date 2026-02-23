# MEMORY_ID: TASK_METALS_ADAPTER
# TIMESTAMP: 2025-11-09T21:28:30+01:00
# AUTHOR: Cursor_Omega

"""
Wrapper do serviço MetalsKitco para integração com o Core.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from Core.Feeds.MetalsKitco.Service import (
    DEFAULT_ALERT_LIMITS,
    MetalsKitcoService,
)
from Core.Logger import get_logger

logger = get_logger("prometheus.metals_client")


class MetalsClient:
    def __init__(self, config: Dict[str, object]) -> None:
        alert_limits = config.get("alert_limits")
        if isinstance(alert_limits, dict):
            limits = {k: float(v) for k, v in alert_limits.items()}
        else:
            limits = DEFAULT_ALERT_LIMITS.copy()

        self.service = MetalsKitcoService(alert_limits=limits)
        self.config = config

    def coletar_dados(self) -> Iterable[dict]:
        logger.info("Coletando dados de metais (Kitco).")
        prices: List[dict] = self.service.run_collection_cycle()
        return [
            {
                "metal": item.get("metal"),
                "preco": item.get("price"),
                "collected_at": item.get("collected_at"),
            }
            for item in prices
        ]

