# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:52 CET
# AUTHOR: Cursor_Omega

#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(dirname "$(realpath "$0")")/.."
MAX_RETRIES="${MAX_RETRIES:-3}"
RETRY_DELAY="${RETRY_DELAY:-30}"

LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/core_main_fallback.log"
ERROR_LOG="$LOG_DIR/core_main_fallback_errors.log"

mkdir -p "$LOG_DIR"

attempt=0
success=false

while [ "$attempt" -lt "$MAX_RETRIES" ] && [ "$success" = false ]; do
  attempt=$((attempt + 1))
  echo "[Prometheus] $(date -Iseconds) - Tentativa $attempt de execução do Core.Main"
  if python -m Core.Main >>"$LOG_FILE" 2>&1; then
    success=true
    echo "[Prometheus] $(date -Iseconds) - Execução concluída com sucesso"
  else
    msg="[Prometheus] $(date -Iseconds) - Falha na tentativa $attempt"
    echo "$msg" | tee -a "$ERROR_LOG"
    if [ "$attempt" -lt "$MAX_RETRIES" ]; then
      echo "[Prometheus] $(date -Iseconds) - Aguardando $RETRY_DELAY segundos..." | tee -a "$ERROR_LOG"
      sleep "$RETRY_DELAY"
    fi
  fi
done

if [ "$success" = false ]; then
  echo "[Prometheus] $(date -Iseconds) - Falha após $MAX_RETRIES tentativas. Verifique $ERROR_LOG."
  exit 1
fi

