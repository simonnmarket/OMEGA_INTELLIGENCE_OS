# MEMORY_ID: TASK_AUTOMATION_MONITORING
# TIMESTAMP: 2025-11-09T21:35:00+01:00
# AUTHOR: Cursor_Omega

"""
Monitoramento institucional do Sistema Prometheus.
"""

from .alerts import AlertManager
from .metrics import MetricsRecorder

__all__ = [
    "AlertManager",
    "MetricsRecorder",
]

