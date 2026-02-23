# MEMORY_ID: TASK_CRYPTO_MONITORING
# TIMESTAMP: 09-11-2025 22:12 CET
# AUTOR: Cursor_Omega

## README – Módulo CRYPTO Prometheus

### 1. Setup
```bash
pip install -r requirements.txt
python -m Modules.Crypto.metrics_server
```

### 2. Configuração (`config/config.yaml`)
```yaml
modules:
  crypto:
    api_url: "https://api.binance.com/api/v3/ticker/price"
    symbols: ["BTCUSDT", "ETHUSDT"]
    timeout: 5
    metrics_port: 8002
    metrics_interval_seconds: 15
```

### 3. Execução
- Coleta + persistência: `python -m Core.Main`
- Métricas: `python -m Modules.Crypto.metrics_server`

### 4. Prometheus/Grafana
- Adicionar job `crypto_metrics` no `prometheus.yml`.
- Criar painéis em Grafana com `crypto_price`.

### 5. Testes
```bash
python -m pytest SamsungGlobalMarket/Modules/Crypto/tests/test_crypto_client.py
```

### 6. Implantação
- Utilizar `run_core_with_fallback.*` ou adaptar `deploy_crypto.sh`.
- Registrar no cron/Airflow conforme `PROCEDIMENTO_IMPLANTACAO_SCHEDULER.md`.

### 7. Checklist
- Seguir `CHECKLIST_TESTES_CRYPTO.md` antes do go-live.

