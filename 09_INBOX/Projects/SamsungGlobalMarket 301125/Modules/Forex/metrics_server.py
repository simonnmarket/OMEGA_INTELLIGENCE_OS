# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 2025-11-09T22:19:00+01:00
# AUTHOR: Cursor_Omega

"""
Servidor de métricas Prometheus para o módulo Forex.
"""

from __future__ import annotations

import time
from typing import Dict

from prometheus_client import CollectorRegistry, Gauge, start_http_server  # type: ignore

from Modules.Forex.ForexClient import ForexClient
from Core.Logger import get_logger

logger = get_logger("prometheus.forex_metrics")

registry = CollectorRegistry()
mid_price_gauge = Gauge("forex_price", "Preço médio bid/ask", ["instrument"], registry=registry)
spread_gauge = Gauge("forex_spread", "Spread bid-ask", ["instrument"], registry=registry)


def serve_metrics(config: Dict[str, object]) -> None:
    client = ForexClient(config)
    port = config.get("metrics_port", 8003)
    interval = config.get("metrics_interval_seconds", 15)

    start_http_server(port, registry=registry)
    logger.info("Servidor de métricas Forex iniciado na porta %s", port)

    while True:
        dados = client.coletar_dados()
        for entry in dados:
            instrument = entry["metal"]
            bid = entry["bid"]
            ask = entry["ask"]
            mid_price_gauge.labels(instrument=instrument).set(entry["preco"])
            spread_gauge.labels(instrument=instrument).set(ask - bid)
        time.sleep(interval)

