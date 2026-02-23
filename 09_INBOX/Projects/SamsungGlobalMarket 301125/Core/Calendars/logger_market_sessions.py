# MEMORY_ID: TASK_MARKET_SESSION_MANAGER
# TIMESTAMP: 2025-11-09T19:48:00+01:00
# AUTHOR: Cursor_Omega

"""
Logger institucional para o subsistema de calendários.
"""

import logging


def get_calendar_logger() -> logging.Logger:
    """
    Retorna logger configurado para o módulo de sessões de mercado.
    """

    logger = logging.getLogger("prometheus.market_sessions")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger

