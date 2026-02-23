# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:27:00+01:00
# AUTHOR: Cursor_Omega

"""
Orquestrador modular do Sistema Prometheus.
"""

from __future__ import annotations

import time
from typing import Dict, Iterable, Protocol

from Core.Database import DataPoint, session_scope
from Core.Logger import get_logger
from Core.Monitoring import AlertManager, MetricsRecorder

logger = get_logger("prometheus.orchestrator")


class CollectableModule(Protocol):
    def coletar_dados(self) -> Iterable[dict]:
        ...


class Orchestrator:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.submodules: Dict[str, CollectableModule] = {}
        self.alerts = AlertManager()
        self.metrics = MetricsRecorder()

    def registrar_submodulo(self, nome: str, instancia: CollectableModule) -> None:
        self.submodules[nome] = instancia
        logger.info("Submódulo %s registrado.", nome)

    def executar_coleta(self) -> None:
        if not self.submodules:
            logger.warning("Nenhum submódulo registrado. Nada a coletar.")
            return

        logger.info("Iniciando coleta de dados (%d submódulos).", len(self.submodules))
        with session_scope() as session:
            for nome, modulo in self.submodules.items():
                logger.info("Executando coleta em %s.", nome)
                start_time = time.perf_counter()
                try:
                    dados = modulo.coletar_dados()
                except Exception:  # pragma: no cover - log detalhado
                    logger.exception("Falha ao coletar dados de %s", nome)
                    self.metrics.record_error(nome, "Erro na coleta")
                    self.alerts.notify(
                        title=f"[Prometheus] Falha na coleta ({nome})",
                        message="Verificar logs para detalhes.",
                    )
                    continue

                novos_registros = 0
                for dado in dados:
                    registro = DataPoint(
                        segment=nome,
                        metal=dado.get("metal"),
                        price=dado.get("preco"),
                        timestamp=dado.get("collected_at"),
                    )
                    session.add(registro)
                    novos_registros += 1
                duration = time.perf_counter() - start_time
                logger.info("Coleta %s concluída. Registros inseridos: %d", nome, novos_registros)
                self.metrics.record_run(nome, novos_registros, duration)

        logger.info("Coleta finalizada.")

