# RELATÓRIO CONSELHO – ESTADO GERAL PROMETHEUS / NUMEIA  
# Data de Referência: 11-11-2025 23:55 CET  

---

## 1. Sumário Executivo
- **Sistema Legado (Numeia v5.1/v6.0):** operação suspensa; falha estrutural no motor de índices e execução manual de ordens inviabilizam produção.  
- **Novo Core Prometheus:** arquitetura modular completa (config, logging, banco, orquestração, calendários, monitoramento) entregue e validada.  
- **Módulos de Mercado:** Metals operacional (carece recalibração), Crypto em stand-by estratégico, Forex migrado para coleta via MetaTrader 5 com métricas Prometheus.  
- **Monitoramento & Governança:** pipelines Prometheus/Grafana implementados, alertas estruturados e documentação institucional atualizada.  
- **Prioridade Imediata:** diagnóstico forense do motor de índices, reengenharia do executor MT5 (EA) e calibração do módulo de metais antes de reconectar fluxo de sinais.  

---

## 2. Visão Geral da Arquitetura

### 2.1 Núcleo Prometheus
- `config/config.yaml` + `Core/Config/ConfigManager.py`: gestão central de parâmetros (DB, módulos, alertas, news).  
- `Core/Logger.py`: logging padronizado (JSON-ready, níveis institucionais).  
- `Core/Database.py`: SQLAlchemy (engine singleton + modelo `DataPoint`).  
- `Core/Orchestrator.py`: registro de submódulos, coleta unificada, persistência, métricas.  
- `Core/Main.py`: entry-point orquestrador (Metals, Crypto, Forex).  
- `Core/Calendars/MarketSessionManager`: classificação de regimes/sessões (CET), filtro de universo e `max_tick_age`.  
- `Core/Monitoring/alerts.py` & `metrics.py`: Prometheus client + webhooks (Slack/e-mail).  
- CI/CD: `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`.  

### 2.2 Módulos de Coleta
- **Metals:** `Modules/Metals/MetalsClient.py` (Kitco scraping + Core.Feeds), testes unitários, exporter Prometheus, dashboards e alertas dedicados.  
- **Crypto:** `Modules/Crypto/CryptoClient.py`, exporter com `CollectorRegistry`, testes, documentação e scripts de deploy; estado operacional suspenso por decisão estratégica.  
- **Forex:**  
  - Cliente REST legado substituído por `Modules/Forex/forex_client_mt5.py` (MetaTrader5 → Prometheus).  
  - Exporter dedicado, dashboards (`Dashboards/forex_dashboard.json`) e alertas (`AlertRules/forex_alerts.yml`).  

### 2.3 Servidor Python e EA MT5
- `Server/Numeia_v6_0_Tactical_Server.py`: consolidador multi-estratégia (Momentum, Breakout, FX Mean Reversion) com integração ao `MarketSessionManager` e à data layer (`DataHubIntraday`).  
- `Experts/Numeia_v6_0_Tactical_EA.mq5`: executor tático com leitura de `TacticalSignals.json`, suporte a controle de múltiplas posições (`InpAllowMultiplePositions`) e validações de mercado aberto.  
- Status atual: necessidade de reengenharia da camada de ordens (SL/TP automáticos, kill-switch, cooldown).  

### 2.4 Automação & Ferramentas
- Scripts PowerShell/Bash (`Scripts/*.ps1/.sh`) para execução com fallback, deploy de exporters e stress tests.  
- `Scripts/run_core_orchestrator.*`, `run_core_with_fallback.*`, `deploy_*`.  
- Cron template `Scripts/cron_entry_example.txt`.  

### 2.5 Analytics & Dashboards
- `Core/Analytics/MLDataPipeline.py`: exportação de séries temporais para futuras fases ML (ARIMA/LSTM/boosting).  
- `Core/Feeds/News/NewsSentimentPipeline.py`: pipeline NewsAPI + VADER (pré-operacional).  
- Dashboards Streamlit (`Dashboards/MetalsDashboard.py`) e Grafana (`Dashboards/*.json`).  

### 2.6 Documentação & Governança
- Relatórios conselho, checklists de testes (`Documentation/08_Protocolos_Procedimentos`), guias de monitoramento e módulos (`Documentation/09_Guias_Manuais`).  
- Protocolos de scheduler, alerta e relatórios diários (`TEMPLATE_RELATORIO_DIARIO_PROMETHEUS.md`).  

---

## 3. Estado Operacional dos Subsistemas

| Pilar | Subcomponente | Status | Observações / Próximos Passos |
|-------|---------------|--------|-------------------------------|
| **Core** | Config, Logger, Database, Orchestrator, Calendars, Monitoring | **Ativo** | Testes unitários e integração concluídos. |
| **Core** | `Core/DataProviders/DataHubIntraday` | **Ativo** | Fallback yfinance operacional; logs `last_update` registrados. |
| **Servidor Python** | Numeia v6.0 | **Pendente** | Necessita instrumentação `DEBUG` e validação condicionais; abastecido via Prometheus core. |
| **EA MT5** | Executor Tactical | **Pendente crítico** | SL/TP automáticos falhando; depende de reengenharia. |
| **Metals Module** | Coleta, métricas, docs | **Ativo** | Precisa calibração de risco e integração com EA após fix. |
| **Crypto Module** | Coleta, métricas | **Inativo estratégico** | Estrutura pronta; aguarda nova tese de sinal. |
| **Forex Module** | Coleta via MT5 | **Ativo (aguardando operação contínua)** | `forex_client_mt5` pronto; requer MT5 logado + agendamento. |
| **Alertas** | Prometheus/Grafana/Alertmanager | **Pendente operacional** | Falta configurar no ambiente oficial (jobs + dashboards + webhooks). |
| **Automation** | Scripts deploy/cron | **Ativo** | Necessário agendar em produção e testar fallback. |
| **Analytics** | MLDataPipeline, NewsSentiment | **Inativo planejado** | Depende da estabilização do core. |
| **Legado** | Motor de índices v6.0 | **Falha catastrófica** | Nenhum sinal pós-migração; prioridade zero de investigação. |

---

## 4. Evoluções Realizadas (2025-11-09 a 2025-11-11)
- Integração do `MarketSessionManager` ao servidor tático e filtros de universo.  
- Implementação do exporter Metals/Crypto/Forex com Prometheus e dashboards templated.  
- Ajuste do `Modules/Forex/metrics_server.py` (CollectorRegistry) para eliminar conflitos de timeseries.  
- Criação do novo `Modules/Forex/forex_client_mt5.py` (MetaTrader5 → Prometheus).  
- Documentação atualizada (guides, checklists, relatórios conselho) e scripts de deploy (PowerShell/Bash).  
- Análise forense do histórico de trades (06-11 a 11-11) identificando falhas de índices, execução manual e reentradas agressivas.  

---

## 5. Pendências e Ações Prioritárias

### 5.1 Técnicas Críticas (T0)
1. **Diagnóstico motor índices (Numeia v6.0)**  
   - Ativar sandbox logging detalhado; executar backtest 06-11 ↔ 11-11 comparando sinais esperados vs. ausência de operações.  
2. **Reengenharia executor MT5**  
   - Garantir SL/TP automáticos, bloqueios de múltiplas entradas, cooldown e kill-switch institucional.  
3. **Calibração Metals**  
   - Definir métricas de risco (lot size, trailing, stacking máximo) e validar em ambiente controlado.  

### 5.2 Operacionais (T1)
4. **Operacionalizar exporters Prometheus**  
   - Executar `forex_client_mt5`, `deploy_metals.sh`, `deploy_crypto.sh` (modo demo) em ambiente oficial; atualizar `prometheus.yml` e Grafana/Alertmanager.  
5. **Reconectar Prometheus ↔ EA**  
   - Somente após ajustes T0, começando por metais calibrados.  
6. **Checklists de validação**  
   - Rodar `CHECKLIST_TESTES_*` e registrar no relatório diário.  

### 5.3 Estratégicas (T2)
7. **Nova tese Crypto/FX** (após estabilização).  
8. **Iniciar fase ML/NLP** (quando core estiver estável).  
9. **Dashboards executivos & relatórios automatizados**.  

---

## 6. Dependências Externas / Acesso do Conselho
- **MT5 / Broker Hantec:** terminal deve permanecer logado; sem API REST disponível.  
- **Configuração Prometheus/Grafana:** requer acesso aos servidores oficiais para incluir jobs, dashboards e webhooks.  
- **Webhooks Slack/E-mail:** preencher URL/credenciais reais em `config/config.yaml`.  
- **Cron/Airflow:** provisionar jobs com permissões adequadas.  
- **Dados Market Watch:** garantir exportação atualizada para `Documents/Market Watch *.csv`.  

---

## 7. Recomendações ao Conselho
1. **Manter o NO-GO operacional** até concluir diagnóstico índices e reengenharia do executor.  
2. **Aprovar sprint dedicado** às pendências críticas (diagnóstico + motor ordens + calibração metals).  
3. **Desbloquear recursos** para operacionalizar exporters (infra Prometheus) e registros cron/Airflow.  
4. **Estabelecer meta de relatório**: apresentar resultados do diagnóstico índices, plano de calibração metals e protótipo do novo executor antes de retomar capital em produção.  

---

## 8. Referências Principais
- Core Prometheus: `Core/*`, `config/config.yaml`.  
- Módulos Mercado: `Modules/Metals`, `Modules/Crypto`, `Modules/Forex`.  
- Servidor/EA: `Server/Numeia_v6_0_Tactical_Server.py`, `Experts/Numeia_v6_0_Tactical_EA.mq5`.  
- Monitoramento: `Core/Monitoring`, `Dashboards/*.json`, `AlertRules/*.yml`.  
- Automação: `Scripts/*.ps1` / `.sh`, `docker-compose.yml`.  
- Documentação: `Documentation/03_*, 08_*, 09_*`.  

---

**Responsável Técnico:** Cursor_Omega  
**Data/Hora de Emissão:** 2025-11-11T23:55:00+01:00 (CET – Berlin)  


