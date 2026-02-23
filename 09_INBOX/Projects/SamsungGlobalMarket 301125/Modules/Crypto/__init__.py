# MEMORY_ID: TASK_CRYPTO_MODULE
# TIMESTAMP: 2025-11-09T22:05:00+01:00
# AUTHOR: Cursor_Omega

"""
Módulo de integração de criptomoedas com o Core Prometheus.
"""

from .CryptoClient import CryptoClient
from .metrics_server import serve_metrics

__all__ = ["CryptoClient", "serve_metrics"]

