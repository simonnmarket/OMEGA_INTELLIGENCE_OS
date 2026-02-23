#!/usr/bin/env bash
# MEMORY_ID: TASK_AUTOMATION_MONITORING
# TIMESTAMP: 09-11-2025 21:37 CET
# AUTHOR: Cursor_Omega

set -euo pipefail

PROJECT_ROOT="$(dirname "$(realpath "$0")")/.."
cd "$PROJECT_ROOT"

echo "[Prometheus] $(date -Iseconds) - Iniciando Core.Main"
python -m Core.Main >> logs/core_main.log 2>&1
echo "[Prometheus] $(date -Iseconds) - Execução concluída"

