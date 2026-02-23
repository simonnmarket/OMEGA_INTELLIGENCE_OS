"""
🧠 Núcleo Central do Sistema NCNT
Sistema de orquestração e comunicação entre módulos
"""

__version__ = "1.0.0"
__author__ = "AURORA NCNT System"

from .orchestrator import NCNTOrchestrator
from .message_bus import NCNTMessageBus
from .registry import NCNTRegistry

__all__ = [
    "NCNTOrchestrator",
    "NCNTMessageBus",
    "NCNTRegistry"
]

