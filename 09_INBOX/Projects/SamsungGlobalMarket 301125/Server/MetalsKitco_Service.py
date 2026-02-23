# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:03:00+01:00
# AUTHOR: Cursor_Omega

"""
Serviço stand-alone para coleta periódica do feed Kitco.
"""

from __future__ import annotations

import argparse
import time

from Core.Feeds.MetalsKitco import MetalsKitcoService
from Core.Feeds.MetalsKitco.Service import DEFAULT_ALERT_LIMITS
from Core.Feeds.MetalsKitco.Logger import get_logger

logger = get_logger("prometheus.kitco.runner")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MetalsKitco Feed Service")
    parser.add_argument(
        "--interval",
        type=int,
        default=900,
        help="Intervalo entre coletas (segundos). Default: 900",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Executa apenas uma coleta e finaliza.",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Abre dashboard Streamlit após a coleta.",
    )
    return parser.parse_args()


def run_service() -> None:
    args = parse_args()
    service = MetalsKitcoService(alert_limits=DEFAULT_ALERT_LIMITS.copy())

    if args.once:
        prices = service.run_collection_cycle()
        if args.dashboard:
            service.launch_dashboard()
        logger.info("Execução única finalizada (%d registros).", len(prices))
        return

    logger.info("Iniciando modo contínuo (intervalo %ds).", args.interval)
    try:
        while True:
            prices = service.run_collection_cycle()
            logger.info("Coleta concluída (%d registros).", len(prices))
            if args.dashboard:
                service.launch_dashboard()
            time.sleep(max(60, args.interval))
    except KeyboardInterrupt:
        logger.info("Serviço Kitco interrompido pelo usuário.")


if __name__ == "__main__":
    run_service()

