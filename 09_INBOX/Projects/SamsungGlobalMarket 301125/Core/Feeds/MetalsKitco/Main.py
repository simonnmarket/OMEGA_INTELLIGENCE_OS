# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:02:00+01:00
# AUTHOR: Cursor_Omega

"""
Ponto de entrada utilitário para o serviço Kitco.
"""

from __future__ import annotations

from .Service import MetalsKitcoService, DEFAULT_ALERT_LIMITS


def run_once() -> None:
    service = MetalsKitcoService(alert_limits=DEFAULT_ALERT_LIMITS.copy())
    service.run_collection_cycle()


def run_with_dashboard() -> None:
    service = MetalsKitcoService(alert_limits=DEFAULT_ALERT_LIMITS.copy())
    service.run_collection_cycle()
    service.launch_dashboard()


if __name__ == "__main__":
    run_with_dashboard()

