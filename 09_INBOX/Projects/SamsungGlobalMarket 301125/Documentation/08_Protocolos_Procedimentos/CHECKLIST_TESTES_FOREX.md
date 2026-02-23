# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 09-11-2025 22:22 CET
# AUTOR: Cursor_Omega

## Checklist de Testes – Módulo FOREX (EUR/USD, GBP/USD)

### A. Preparação
1. Configurar `modules.forex` em `config/config.yaml` com conta/token válidos.
2. Garantir acesso à API (OANDA practice ou similar).
3. Iniciar exporter (`python -m Modules.Forex.metrics_server`).

### B. Coleta & Persistência
1. Executar `python -m Core.Main`.
2. Validar registros `segment='forex'` na tabela `datapoints`.
3. Revisar logs para garantir ausência de falhas.

### C. Métricas Prometheus
1. Atualizar `prometheus.yml` com job `forex_metrics`.
2. Confirmar target `localhost:8003` UP.
3. Consultar métricas (`forex_mid_price`, `forex_spread`).

### D. Dashboard Grafana
1. Painel de preço (mid) por instrumento.
2. Painel de spread e variação% intradiária.
3. Alertas visuais para spikes de spread.

### E. Alertas
1. Configurar regra (spread > X pips).
2. Validar envio Slack/e-mail (modo teste).

### F. Stress Test
1. Executar `Scripts/run_core_stresstest.sh` focado em Forex.
2. Monitorar consumo e tempos de resposta.

### G. Aprovação
- Dados corretos e atualizados nos dashboards.
- Alertas funcionando.
- Stress test concluído sem erros críticos.
- Documentação evidenciando resultados anexada ao relatório diário.

