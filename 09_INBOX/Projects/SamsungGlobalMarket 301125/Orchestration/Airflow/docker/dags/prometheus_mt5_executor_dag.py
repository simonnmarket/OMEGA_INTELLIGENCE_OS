# MEMORY_ID: OP_PROMETHEUS_MT5_AIRFLOW_DAG
# TIMESTAMP: 2025-11-12T10:25:00+01:00
# AUTHOR: Cursor_Omega
"""
DAG Airflow para supervisionar o executor Prometheus MT5.

Requisitos:
- Conexão Airflow `prometheus_localhost` configurada para http://localhost:63000.
- Variável AIRFLOW_HOME configurada e Python 3.9+ disponível.
"""

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.ssh.operators.ssh import SSHOperator

EXECUTOR_COMMAND = os.environ.get("PROMETHEUS_MT5_EXECUTOR_COMMAND")
if not EXECUTOR_COMMAND:
    raise RuntimeError(
        "PROMETHEUS_MT5_EXECUTOR_COMMAND não definido. Configure com o comando completo para executar o "
        "Server/prometheus_mt5_executor.py via SSH no host Windows (ex.: python \"C:/.../prometheus_mt5_executor.py\")."
    )

default_args = {
    "owner": "PrometheusOps",
    "depends_on_past": False,
    "start_date": datetime(2025, 11, 13),
    "email": ["ops@prometheus.institution"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="prometheus_mt5_executor",
    default_args=default_args,
    description="Executa e monitora o executor Prometheus MT5",
    schedule="*/5 * * * *",
    catchup=False,
    tags=["prometheus", "mt5", "monitoring"],
) as dag:

    run_executor = SSHOperator(
        task_id="run_mt5_executor",
        ssh_conn_id="prometheus_executor_host",
        command=EXECUTOR_COMMAND,
        cmd_timeout=10 * 60,
        get_pty=True,
    )

    health_check = HttpOperator(
        task_id="check_prometheus_metrics",
        http_conn_id="prometheus_localhost",
        endpoint="metrics",
        method="GET",
        response_check=lambda response: "fx_balance" in response.text,
        log_response=True,
    )

    run_executor >> health_check

