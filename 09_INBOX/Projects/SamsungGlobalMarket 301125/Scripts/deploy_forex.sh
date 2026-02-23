#!/usr/bin/env bash
# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 09-11-2025 22:24 CET
# AUTHOR: Cursor_Omega

set -euo pipefail

echo "[Prometheus] Iniciando implantação do módulo FOREX..."

PROJECT_ROOT="$(dirname "$(realpath "$0")")/.."
cd "$PROJECT_ROOT"

pip install --upgrade pip
pip install requests prometheus_client

nohup python -m Modules.Forex.metrics_server > logs/forex_metrics.log 2>&1 &

echo "[Prometheus] Módulo FOREX implantado com sucesso. Verifique logs/forex_metrics.log."

