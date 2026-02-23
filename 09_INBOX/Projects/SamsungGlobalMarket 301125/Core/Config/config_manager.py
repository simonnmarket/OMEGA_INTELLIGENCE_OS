# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:25:30+01:00
# AUTHOR: Cursor_Omega

"""
ConfigManager centralizado para o projeto Prometheus.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # type: ignore

from Core.Logger import get_logger

logger = get_logger("prometheus.config")


class ConfigManager:
    """
    Carrega e armazena configuração em memória com suporte a overrides.
    """

    _instance: Optional["ConfigManager"] = None
    _lock = threading.Lock()

    def __init__(self, config_data: Dict[str, Any]) -> None:
        self._config = config_data

    @classmethod
    def initialize(cls, path: Optional[Path] = None) -> "ConfigManager":
        if cls._instance is not None:
            return cls._instance

        with cls._lock:
            if cls._instance is None:
                config_data = _load_yaml_config(path)
                cls._instance = cls(config_data)
                logger.info("ConfigManager inicializado com arquivo %s", path or "config/config.yaml")

        return cls._instance

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        if cls._instance is None:
            return cls.initialize()
        return cls._instance

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Recupera valor aninhado usando sequência de chaves.
        """

        current: Any = self._config
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current


def _load_yaml_config(path: Optional[Path]) -> Dict[str, Any]:
    candidates = []
    if path is not None:
        candidates.append(path)

    # Caminhos padrão
    project_root = Path(__file__).resolve().parents[2]
    candidates.append(project_root / "config" / "config.yaml")
    candidates.append(project_root / "config.yaml")

    for candidate in candidates:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}

    logger.warning("Nenhum arquivo de configuração encontrado. Usando configuração vazia.")
    return {}


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Wrapper para inicializar e retornar dicionário de configuração.
    """

    manager = ConfigManager.initialize(path)
    return manager._config.copy()

