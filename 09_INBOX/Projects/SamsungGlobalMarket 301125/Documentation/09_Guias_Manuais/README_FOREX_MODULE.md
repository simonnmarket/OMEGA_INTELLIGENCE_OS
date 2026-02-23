# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 09-11-2025 22:21 CET
# AUTOR: Cursor_Omega

## README – Módulo FOREX Prometheus

### 1. Requisitos
```bash
pip install -r requirements.txt
```

### 2. Configuração (`config/config.yaml`)
```yaml
modules:
  forex:
    api_url: "https://api-fxpractice.oanda.com/v3/accounts/{account_id}/pricing"
    account_id: "SUA_CONTA"
    api_token: "SEU_TOKEN"
    instruments: ["EUR_USD", "GBP_USD"]
    timeout: 5
    metrics_port: 8003
    metrics_interval_seconds: 15
```

### 3. Execução
- Coleta e persistência: `python -m Core.Main` (já registra ForexClient).
- Métricas Prometheus: `python -m Modules.Forex.metrics_server`.

### 4. Prometheus & Grafana
- Adicionar job `forex_metrics` ao `prometheus.yml`.
- Criar painéis com:
  - `forex_price{instrument="EUR_USD"}`
  - `forex_spread{instrument="EUR_USD"}`

### 5. Testes
```bash
python -m pytest SamsungGlobalMarket/Modules/Forex/tests/test_forex_client.py
```

### 6. Implantação
- Usar scripts `run_core_with_fallback.*`/cron ou adaptar `deploy_forex.sh`.
- Registrar execução no relatório diário.

### 7. Checklist
- Seguir `CHECKLIST_TESTES_FOREX.md` (coleta, métricas, dashboards, alertas, carga).
- Importar dashboard `Dashboards/forex_dashboard.json` e regras `AlertRules/forex_alerts.yml`.

