# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T19:59:00+01:00
# AUTHOR: Cursor_Omega

"""
Logger institucional para o módulo Kitco.
"""

import logging

from .Config import LOG_LEVEL

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name: str) -> logging.Logger:
    """
    Retorna logger com formatação institucional.
    """

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        logger.propagate = False

    return logger

