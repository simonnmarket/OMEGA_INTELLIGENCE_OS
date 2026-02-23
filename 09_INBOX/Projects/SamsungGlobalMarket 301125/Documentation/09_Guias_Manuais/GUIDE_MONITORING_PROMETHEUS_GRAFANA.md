# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:53 CET
# AUTOR: Cursor_Omega

## Guia – Configuração Prometheus/Grafana + Alertas Slack/E-mail

### 1. Prometheus
1. **Configuração base (`prometheus.yml`)**
   ```yaml
   global:
     scrape_interval: 15s
     evaluation_interval: 15s

   scrape_configs:
     - job_name: 'prometheus'
       static_configs:
         - targets: ['localhost:9090']

     - job_name: 'core_metrics'
       static_configs:
         - targets: ['localhost:8000']

     - job_name: 'metals_client'
       static_configs:
         - targets: ['localhost:8001']

     - job_name: 'crypto_metrics'
       static_configs:
         - targets: ['localhost:8002']

     - job_name: 'forex_metrics'
       static_configs:
         - targets: ['localhost:8003']

   alerting:
     alertmanagers:
       - static_configs:
           - targets:
               - 'localhost:9093'
   ```
2. **Expondo métricas**
   - Servir `metrics/prometheus_metrics.json` via endpoint HTTP (ex.: FastAPI/Flask em `localhost:8000`/`8001`).
3. **Deploy rápido**
   - Script `deploy_monitoring.sh`:
     ```bash
     #!/bin/bash
     sudo apt-get install -y prometheus
     sudo cp prometheus.yml /etc/prometheus/prometheus.yml
     sudo systemctl restart prometheus

     sudo apt-get install -y grafana
     sudo systemctl start grafana-server
     sudo systemctl enable grafana-server
     echo "Monitoramento Prometheus e Grafana configurados."
     ```
4. Validar em `http://localhost:9090`.

### 2. Grafana
1. Acessar `http://localhost:3000` (login padrão `admin/admin`).
2. Adicionar Prometheus como data source (`http://localhost:9090`).
3. Criar dashboards customizados com queries PromQL (ex.: `crypto_price{symbol="BTCUSDT"}`, `forex_mid_price{instrument="EUR_USD"}`).
4. Configurar variáveis por job/instância e importar dashboards (`Dashboards/metals_dashboard.json`, `Dashboards/forex_dashboard.json`).
5. Configurar alertas:
   - Channel Slack: usar webhook definido em `config/config.yaml`.
   - Channel E-mail: SMTP corporativo.

### 3. Slack
1. Criar webhook incoming.
2. Atualizar `alerts.slack_webhook` no `config.yaml`.
3. Testar via:
   ```python
   from Core.Monitoring.alerts import AlertManager
   AlertManager().notify("Teste Slack", "Mensagem de validação")
   ```

### 4. E-mail
1. Obter credenciais SMTP.
2. Atualizar seção `alerts.email`.
3. Testar com o mesmo código acima.

### 5. Manutenção e Operação
- Revisar métricas e gráficos diariamente.
- Documentar incidentes/alertas acionados.
- Atualizar dashboards conforme novos KPIs.
- Registrar resultados no relatório diário (`TEMPLATE_RELATORIO_DIARIO_PROMETHEUS.md`).

### 6. Exemplos de Alertas (Alertmanager)
```yaml
groups:
  - name: forex_alerts
    rules:
      - alert: ForexPriceDrop
        expr: forex_mid_price{instrument="EUR_USD"} < avg_over_time(forex_mid_price{instrument="EUR_USD"}[15m]) * 0.95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Queda >5% no preço do EUR/USD"
          description: "Preço médio caiu mais de 5% nos últimos 15 minutos."

      - alert: ForexSpreadHigh
        expr: forex_spread{instrument="EUR_USD"} > 0.001
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Spread elevado no EUR/USD"
          description: "Spread acima do limite crítico."
```

