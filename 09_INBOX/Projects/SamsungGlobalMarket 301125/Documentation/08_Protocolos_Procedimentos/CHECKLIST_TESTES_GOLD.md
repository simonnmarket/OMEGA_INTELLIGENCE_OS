# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:50 CET
# AUTOR: Cursor_Omega

## Checklist de Testes Integrados e de Carga – Ativo GOLD

### A. Preparação
1. Atualizar base de dados com coleta recente (`python -m Core.Main`).
2. Verificar `config/config.yaml` (alertas e monitoramento configurados).
3. Iniciar serviços auxiliares (Prometheus, Grafana, Slack webhook de teste).

### B. Testes Integrados
1. **Coleta padrão**
   - Executar `python -m Core.Main`.
   - Validar registros na tabela `datapoints` (`metal = 'gold'`).
   - Confirmar métricas em `metrics/prometheus_metrics.json`.
2. **Resiliência a falhas**
   - Simular indisponibilidade do Kitco (alterar `kitco_url` temporariamente).
   - Garantir que alertas Slack/e-mail são disparados.
   - Confirmar rollback no banco (sem registros corrompidos).
3. **Processamento em sequência**
   - Executar três rodadas consecutivas com intervalo curto (<5 min).
   - Verificar ausência de deadlocks ou duplicações.
4. **Integração com Dashboard**
   - Abrir `Dashboards/MetalsDashboard.py` (Streamlit).
   - Validar exibição de séries e sentimento para `gold`.

### C. Testes de Carga (Cenário GOLD)
1. Popular base com histórico (mínimo 50k registros).
2. Executar script de stress (`Scripts/run_core_stresstest.sh` ou PowerShell).
3. Monitorar consumo de CPU/memória e tempo de coleta (via métricas).
4. Validar que alertas não saturam durante carga.

### D. Critérios de Aprovação
- 0 falhas críticas nos logs.
- Alertas e métricas funcionando em tempo real.
- Dashboard atualizado sem erros.
- Resultados documentados no relatório diário.

