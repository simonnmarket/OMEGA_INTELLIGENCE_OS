# MEMORY_ID: TASK_CRYPTO_MODULE
# TIMESTAMP: 2025-11-09T22:06:00+01:00
# AUTHOR: Cursor_Omega

"""
Servidor de métricas Prometheus para o módulo Crypto.
"""

from __future__ import annotations

import time
from typing import Dict

from prometheus_client import Gauge, start_http_server  # type: ignore

from Modules.Crypto.CryptoClient import CryptoClient
from Core.Logger import get_logger

logger = get_logger("prometheus.crypto_metrics")

price_gauge = Gauge("crypto_price", "Preço do ativo cripto", ["symbol"])


def serve_metrics(config: Dict[str, object]) -> None:
    client = CryptoClient(config)
    port = config.get("metrics_port", 8002)
    interval = config.get("metrics_interval_seconds", 15)

    start_http_server(port)
    logger.info("Servidor de métricas de cripto iniciado na porta %s", port)

    while True:
        dados = client.coletar_dados()
        for entry in dados:
            price_gauge.labels(symbol=entry["metal"]).set(entry["preco"])
        time.sleep(interval)

