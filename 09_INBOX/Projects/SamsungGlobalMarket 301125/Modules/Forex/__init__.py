# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 2025-11-09T22:18:00+01:00
# AUTHOR: Cursor_Omega

"""
Módulo FOREX integrado ao Core Prometheus.
"""

from .ForexClient import ForexClient

__all__ = ["ForexClient", "serve_metrics"]


def serve_metrics(config):
    from .metrics_server import serve_metrics as _serve_metrics
    return _serve_metrics(config)

