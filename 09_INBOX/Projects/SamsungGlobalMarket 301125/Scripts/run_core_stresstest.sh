# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:52 CET
# AUTHOR: Cursor_Omega

#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(dirname "$(realpath "$0")")/.."
RUNS="${RUNS:-10}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-10}"

LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
STRESS_LOG="$LOG_DIR/core_stresstest.log"

echo "[Prometheus] $(date -Iseconds) - Iniciando stress test (RUNS=$RUNS, INTERVAL=$INTERVAL_SECONDS)" | tee -a "$STRESS_LOG"

for i in $(seq 1 "$RUNS"); do
  echo "[Prometheus] $(date -Iseconds) - Execução $i/$RUNS" | tee -a "$STRESS_LOG"
  if ! python -m Core.Main >>"$STRESS_LOG" 2>&1; then
    echo "[Prometheus] $(date -Iseconds) - Falha na execução $i" | tee -a "$STRESS_LOG"
  fi
  sleep "$INTERVAL_SECONDS"
done

echo "[Prometheus] $(date -Iseconds) - Stress test concluído" | tee -a "$STRESS_LOG"

