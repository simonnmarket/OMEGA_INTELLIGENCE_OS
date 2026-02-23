# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:54 CET
# AUTOR: Cursor_Omega

## Procedimento – Implantação Cron/Airflow (Ambiente Produtivo)

### Cron (Linux)
1. Copiar `Scripts/run_core_with_fallback.sh` para `/opt/prometheus/bin/`.
2. Editar crontab:
   ```bash
   crontab -e
   0 * * * * /opt/prometheus/bin/run_core_with_fallback.sh >> /var/log/prometheus/cron.log 2>&1
   0 3 * * * /usr/bin/env python3 /opt/prometheus/Core/Integration/create_backup.py >> /var/log/prometheus/backup.log 2>&1
   ```
3. Validar com `grep CRON /var/log/syslog`.

### Airflow (Alternativa)
1. Criar DAG `prometheus_core_dag.py`:
   ```python
   from airflow import DAG
   from airflow.operators.bash import BashOperator
   from datetime import datetime, timedelta

   with DAG(
       dag_id="prometheus_core",
       start_date=datetime(2025, 11, 9),
       schedule_interval="0 * * * *",
       catchup=False,
   ) as dag:
       run_core = BashOperator(
           task_id="run_core",
           bash_command="/opt/prometheus/bin/run_core_with_fallback.sh"
       )
   ```
2. Registrar DAG em `$AIRFLOW_HOME/dags`.
3. Monitorar execução via UI do Airflow.

### Pós-Implantação
- Registrar execuções no relatório diário.
- Acompanhar métricas e alertas após cada ciclo.
- Ajustar janela de execução conforme capacidade de processamento.

