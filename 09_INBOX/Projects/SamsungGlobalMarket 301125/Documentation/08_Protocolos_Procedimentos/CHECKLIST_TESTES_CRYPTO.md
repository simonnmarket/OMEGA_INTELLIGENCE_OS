# MEMORY_ID: TASK_CRYPTO_MONITORING
# TIMESTAMP: 09-11-2025 22:10 CET
# AUTOR: Cursor_Omega

## Checklist de Testes – Módulo CRYPTO (BTC/ETH)

### A. Preparação
1. Atualizar `config/config.yaml` (módulo `crypto`) com símbolos e limites.
2. Garantir que Prometheus e Grafana estejam disponíveis.
3. Iniciar o exporter de métricas (`serve_metrics(config["modules"]["crypto"])`).

### B. Testes de Coleta & Persistência
1. Executar `python -m Core.Main`.
2. Validar registros `segment='crypto'` na tabela `datapoints`.
3. Verificar logs (`logs/core_main_fallback.log`) sem erros.

### C. Métricas Prometheus
1. Adicionar job `crypto_metrics` no `prometheus.yml` e reiniciar serviço.
2. Confirmar exposição em `http://localhost:8002/metrics`.
3. Consultar `crypto_price` via Prometheus UI (target `BTCUSDT`, `ETHUSDT`).

### D. Dashboard Grafana
1. Criar painel de linha para `crypto_price{symbol="BTCUSDT"}`.
2. Adicionar painel de variação percentual (query PromQL).
3. Configurar alertas visuais (thresholds).

### E. Alertas
1. Configurar regra de alerta (ex.: variação >5% em 5 min).
2. Validar envio em Slack/e-mail (modo teste).

### F. Testes de Carga
1. Utilizar `Scripts/run_core_stresstest.sh` (ajustar RUNS/INTERVAL).
2. Monitorar tempo de resposta e estabilidade das métricas.

### G. Critérios de Aprovação
- Dados persistidos e visíveis em dashboards.
- Alertas disparando corretamente.
- Stress test concluído sem falhas críticas.
- Documentação atualizada com evidências (logs, screenshots).

