# MEMORY_ID: TASK_AUTOMATION_MONITORING
# TIMESTAMP: 2025-11-09T21:36:00+01:00
# AUTHOR: Cursor_Omega

"""
Registro simples de métricas (JSON) para Prometheus/monitoramento.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from Core.Config import ConfigManager
from Core.Logger import get_logger

logger = get_logger("prometheus.metrics")


class MetricsRecorder:
    def __init__(self, metrics_path: Optional[Path] = None) -> None:
        cfg = ConfigManager.get_instance()
        default_path = cfg.get("monitoring", "metrics_path", default="metrics/prometheus_metrics.json")
        self.metrics_path = Path(metrics_path or default_path)
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)

    def record_run(self, module: str, records: int, duration_seconds: float) -> None:
        data = self._read_current()
        timestamp = datetime.utcnow().isoformat()

        module_metrics = data.setdefault(module, {"runs": []})
        module_metrics["last_run"] = timestamp
        module_metrics["last_records"] = records
        module_metrics["last_duration_seconds"] = duration_seconds
        module_metrics["runs"].append(
            {
                "timestamp": timestamp,
                "records": records,
                "duration_seconds": duration_seconds,
            }
        )

        self._write(data)
        logger.info("Métricas registradas (%s): %d registros em %.2fs", module, records, duration_seconds)

    def record_error(self, module: str, error: str) -> None:
        data = self._read_current()
        timestamp = datetime.utcnow().isoformat()
        module_metrics = data.setdefault(module, {"errors": []})
        errors = module_metrics.setdefault("errors", [])
        errors.append({"timestamp": timestamp, "error": error})
        module_metrics["last_error"] = error
        module_metrics["last_error_at"] = timestamp
        self._write(data)
        logger.info("Erro registrado em métricas (%s).", module)

    def _read_current(self) -> Dict:
        if not self.metrics_path.exists():
            return {}
        try:
            return json.loads(self.metrics_path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Falha ao ler métricas existentes. Recriando arquivo.")
            return {}

    def _write(self, data: Dict) -> None:
        self.metrics_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

