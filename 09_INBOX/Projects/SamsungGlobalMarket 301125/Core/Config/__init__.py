# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:25:00+01:00
# AUTHOR: Cursor_Omega

"""
Gerenciador central de configuração do Sistema Prometheus.
"""

from .config_manager import ConfigManager, load_config

__all__ = [
    "ConfigManager",
    "load_config",
]

