# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:01:30+01:00
# AUTHOR: Cursor_Omega

"""
Serviço orquestrador para o feed Kitco.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .Alerts import check_price_alerts
from .Config import METALS
from .Dashboard import render_dashboard
from .KitcoClient import collect_prices
from .Logger import get_logger
from .Repository import create_database, fetch_recent, persist_prices

logger = get_logger("prometheus.kitco.service")

DEFAULT_ALERT_LIMITS: Dict[str, float] = {
    "gold": 2000.0,
    "silver": 50.0,
    "platinum": 2000.0,
    "palladium": 1500.0,
}


@dataclass
class MetalsKitcoService:
    alert_limits: Dict[str, float] = field(default_factory=lambda: DEFAULT_ALERT_LIMITS.copy())
    initialized: bool = field(default=False, init=False)

    def initialize(self) -> None:
        if not self.initialized:
            create_database()
            self.initialized = True

    def run_collection_cycle(self) -> List[dict]:
        """
        Executa uma coleta, persistência e avaliação de alertas.
        Retorna lista de preços coletados.
        """

        self.initialize()
        prices = collect_prices()
        if not prices:
            logger.warning("Nenhum preço coletado na execução atual.")
            return []

        persist_prices(prices)
        triggered = check_price_alerts(prices, self.alert_limits)
        if triggered:
            logger.info("Alertas disparados para: %s", ", ".join(item["metal"] for item in triggered))
        return prices

    def get_recent_prices(self, limit: int = 20) -> List[dict]:
        records = fetch_recent(limit)
        return [
            {
                "metal": record.metal,
                "price": record.price,
                "source": record.source,
                "collected_at": record.collected_at,
            }
            for record in records
        ]

    def launch_dashboard(self, limit: int = 200) -> None:
        """
        Inicia dashboard Streamlit.
        """

        self.initialize()
        render_dashboard(limit=limit)

    def describe(self) -> str:
        return (
            "MetalsKitcoService: coleta metais {metals}, limites {limits}".format(
                metals=", ".join(METALS),
                limits=self.alert_limits,
            )
        )

