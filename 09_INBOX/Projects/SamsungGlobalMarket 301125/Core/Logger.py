# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:26:00+01:00
# AUTHOR: Cursor_Omega

"""
Logger institucional do Sistema Prometheus.
"""

import logging
from typing import Optional

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LEVEL = logging.INFO


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retorna logger configurado com formato institucional.
    """

    logger = logging.getLogger(name if name else "prometheus")
    if not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root = logging.getLogger()
        root.setLevel(DEFAULT_LEVEL)
        root.addHandler(handler)
    return logger

