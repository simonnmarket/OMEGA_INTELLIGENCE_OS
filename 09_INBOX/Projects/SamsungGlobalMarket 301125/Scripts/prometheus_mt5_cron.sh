# MEMORY_ID: OP_PROMETHEUS_MT5_CRON
# TIMESTAMP: 2025-11-12T10:25:00+01:00
# AUTHOR: Cursor_Omega
#!/bin/bash
#
# Loop de supervisão para o executor Prometheus MT5.
# Reinicia automaticamente o serviço em caso de falha e notifica via Slack.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EXECUTOR_PATH="${PROJECT_ROOT}/Server/prometheus_mt5_executor.py"
LOG_PATH="${PROJECT_ROOT}/logs/prometheus_mt5_restart.log"

if [[ ! -f "${EXECUTOR_PATH}" ]]; then
  echo "Executor não encontrado em ${EXECUTOR_PATH}" | tee -a "${LOG_PATH}"
  exit 1
fi

echo "Supervisor Prometheus MT5 iniciado ($(date -Iseconds))" | tee -a "${LOG_PATH}"

while true; do
  if ! python "${EXECUTOR_PATH}"; then
    message="Executor Prometheus MT5 caiu em $(date -Iseconds). Reinício automático em 60s."
    echo "${message}" | tee -a "${LOG_PATH}"
    # Envia alerta Slack se configurado (reutiliza config.yaml)
    python - <<'PYCODE'
import yaml
import requests
from pathlib import Path

config_path = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
with config_path.open("r", encoding="utf-8") as fh:
    cfg = yaml.safe_load(fh) or {}
webhook = (cfg.get("alerts") or {}).get("slack_webhook")
if webhook and "SEU_WEBHOOK" not in webhook:
    requests.post(webhook, json={"text": "Executor Prometheus MT5 reiniciado automaticamente."}, timeout=10)
PYCODE
    sleep 60
  else
    echo "Executor finalizado com status 0. Encerrando supervisor." | tee -a "${LOG_PATH}"
    exit 0
  fi
done

