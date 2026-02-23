# MEMORY_ID: TASK_EXPANSAO_CORE_METALS
# TIMESTAMP: 09-11-2025 21:05 CET
# AUTOR: Cursor_Omega

## Objetivo
Consolidar o plano de expansão do Core institucional Prometheus e da ramificação Metais, registrando cada componente possível, justificativas técnicas (“defesas”) e status de integração. O documento será vivo durante o ciclo de desenvolvimento para garantir rastreabilidade.

## Visão Geral
O sistema atual já possui:
- Servidor tático (`Server/Numeia_v6_0_Tactical_Server.py`).
- Submódulo `Core/Feeds/MetalsKitco` com coleta Kitco, persistência SQLite e alertas básicos.
- Scripts institucionais (backup, monitoramento).
- Módulo de calendário (`Core/Calendars`) para sessões de mercado.

Precisamos evoluir para um **Core unificado** que ofereça:
- Configuração centralizada.
- Logger institucional único.
- Persistência compartilhada.
- Orquestração de submódulos.
- Scheduler institucional.
- Suporte a novos submódulos (Metais, Forex, Índices, Cripto etc.) com testes e dashboards padronizados.

## Itens Potenciais de Integração (com defesas)

### 1. Configuração Central (`Core/Config`)
- **Inclusão:** `config.yaml`, `ConfigManager.py`.
- **Defesa:** garante fonte única de verdade para credenciais/paths, reduz risco de parâmetros divergentes entre submódulos.
- **Status atual:** inexistente (cada módulo usa constantes locais).
- **Ação proposta:** criar pacote `Core/Config/`, definir YAML com seções (`database`, `modules`, `schedules`, `logging`, `alerts`). Implementar loader usando `yaml.safe_load` com fallback para variáveis de ambiente.

### 2. Logger Institucional (`Core/Logger`)
- **Inclusão:** `Logger.py` central (structured logging, formato uniforme).
- **Defesa:** logs consistentes, auditáveis e prontos para streaming (ELK/Splunk). Facilita compliance.
- **Status atual:** módulo MetalsKitco possui logger próprio; demais usam `logging.basicConfig`.
- **Ação proposta:** criar `get_logger(name)` que configure handlers compartilhados, possivelmente formato JSON. Atualizar módulos críticos para usar esse logger.

### 3. Persistência Unificada (`Core/Database`)
- **Inclusão:** `Database.py` com engine SQLAlchemy global + Base declarativa.
- **Defesa:** evita múltiplas conexões, facilita migração para bancos institucionais (Postgres/Redshift). Permite reuso de session factory e controle transacional.
- **Status atual:** `MetalsKitco` possui engine local (`sqlite:///...`) independente.
- **Ação proposta:** mover engine/session/`Base` para `Core/Database`, atualizar `MetalsKitco.Repository` e futuros módulos a reutilizar essa infraestrutura.

### 4. Contratos de Submódulo (`Core/Modules/BaseModule.py`)
- **Inclusão:** classes abstratas/protocolos (`CollectableModule`, `NormalizableModule`, `PersistableModule`) com métodos claros (`collect`, `normalize`, `persist`, `alert`, `report`).
- **Defesa:** garante que todos os módulos implementem a mesma interface, facilitando acoplamento ao orquestrador.
- **Status atual:** `MetalsKitcoService` implementa fluxo, mas sem interface formal.
- **Ação proposta:** definir ABCs e adaptar `MetalsKitcoService` (e futuros) para cumpri-los.

### 5. Orquestrador (`Core/Orchestrator.py`)
- **Inclusão:** classe responsável por carregar módulos registrados, executar ciclo (`collect → normalize → persist → alert → report`), registrar resultados e lidar com falhas.
- **Defesa:** ponto único de controle, facilita auditoria e extensão. Possibilita ativar/desativar módulos via config.
- **Status atual:** inexistente (cada serviço roda por conta própria).
- **Ação proposta:** criar orquestrador, com suporte a execução única ou contínua; integrá-lo ao `Main.py` e ao scheduler.

### 6. Scheduler (`Core/Scheduler.py`)
- **Inclusão:** tarefa de agendamento (usar `apscheduler` ou integração com scripts PowerShell) para rodar módulos em intervalos configurados.
- **Defesa:** automatiza coletas, garante janelas constantes, evita dependência manual.
- **Status atual:** nenhum scheduler central; `MetalsKitco_Service.py` faz loop simples.
- **Ação proposta:** implementar `Core/Scheduler` capaz de ler config (`cron`, `interval`) e disparar orquestrador.

### 7. Backup Automatizado
- **Inclusão:** acionar `Core/Integration/create_backup.py` via scheduler antes de cada janela crítica ou daily cron.
- **Defesa:** minimiza risco de perda de estado; essencial antes de deploy em produção.
- **Status atual:** script manual executado sob demanda.
- **Ação proposta:** integrar chamada ao scheduler e registrar no orquestrador.

### 8. Ramificação Metais (refinamento)
- **Itens incluíveis:** `filters.py`, normalizadores, testes unitários (mocks), dashboards integrados, alertas avançados (ex.: variação intradiária, correlação com FX).
- **Defesa:** assegura qualidade do submódulo, prepara base para replicar abordagens em outros mercados.
- **Status atual:** coleta/persistência básica implementada; faltam filtros/testes/hardening.
- **Ação proposta:** criar `filters.py` com regras de negocio; mover orquestração para Core; adaptar `MetalsClient` sugerido para atuar como wrapper do `MetalsKitcoService`, garantindo saída no formato `{metal, preco}` esperado pelo Core-Orchestrator e reaproveitando scraping/alertas existentes.

### 9. Testes
- **Inclusão:** `Core/tests/` com suíte `pytest`, fixtures, mocks de requests, DB em memória.
- **Defesa:** garante estabilidade e detecta regressões antes do deploy.
- **Status atual:** não há testes automatizados; modelo de teste mínimo para `MetalsClient` proposto (Coletar dados e verificar chaves) será adotado como base e ampliado com mocks.
- **Ação proposta:** iniciar com testes para `MetalsKitco` (client + alerts + repository) e para o adaptador `MetalsClient`, usando `pytest` e `requests` mockados; depois ampliar para orquestrador.

### 10. Monitoramento e Alertas Transversais
- **Inclusão:** integrar com `Core/Monitoring` (e.g. watchers), emitir eventos para dashboards/logs centrais (Prometheus, Grafana, etc.).
- **Defesa:** visibilidade em tempo real, responde a incidentes rapidamente.
- **Status atual:** `Monitoring/server_watchdog.py` existe, mas não monitora submódulos novos.
- **Ação proposta:** adaptar watchers para incluir orquestrador, base de dados e saturação de alertas.

### 11. Documentação
- **Inclusão:** manter guias atualizados (`GUIA_METALS_KITCO`, novo `GUIA_CORE_ORCHESTRATION`, etc.).
- **Defesa:** garante onboarding rápido e transferência de conhecimento.
- **Status atual:** guias específicos (EA, Metals) já existem; falta documento do core.
- **Ação proposta:** este protocolo servirá como base; atualizar à medida que entregas ocorrerem.

### 12. Ambiente de Desenvolvimento & Automação
- **Inclusão:** ambientes Python 3.11+ isolados (venv/pyenv), `requirements.txt`, scripts de setup, cron/Airflow para agendamentos, Dockerfiles e pipelines CI/CD (GitHub Actions/Jenkins), monitoramento com Prometheus/Grafana, alertas Slack/e-mail/SMS.
- **Defesa:** garante repetibilidade, governança institucional, deploy contínuo e observabilidade.
- **Status atual:** ambiente manual; sem cron/Airflow; CI/CD ainda não estruturado; monitoramento limitado a logs locais.
- **Ação proposta:** 
  - padronizar ambiente (venv + `requirements.txt`/Poetry),
  - provisionar **Dockerfile** (python:3.11-slim, `requirements.txt`, copy código) e **docker-compose** (serviço `app` + `postgres:15` com volume `pgdata`),
  - configurar cron inicial (execução horária do orquestrador) e planejar Airflow para futuros workflows,
  - criar CI pipeline (ex.: `.github/workflows/ci.yml` com checkout, setup-python 3.11, `pip install -r requirements.txt`, `pytest --maxfail=1 --disable-warnings`),
  - preparar infra de monitoramento (logging estruturado → ELK/Grafana/Prometheus, alertas Slack/e-mail/SMS),
  - documentar dashboards (Streamlit com séries históricas, filtros, exportação CSV/PDF) e relatórios exportáveis.

### 13. Roadmap Avançado (ML, Sentimento, Dashboards)
- **Fase 1 (Atual):** Core modular + Metals + CI/CD básico (GitHub Actions com pytest, Docker, cron).
- **Fase 2 (Machine Learning):** coleta histórica + features, modelos ARIMA/LSTM/Boosting, libs `scikit-learn`, `statsmodels`, `tensorflow`, deploy integrado ao orquestrador.
- **Fase 3 (Sentimento/NLP):** conectores de notícias (NewsAPI etc.), classificação de sentimento com `nltk`, `spaCy`, `transformers`, integração com alertas e sinais.
- **Fase 4 (Dashboards Avançados):** painéis interativos (Streamlit/Plotly Dash/Bokeh) + BI corporativo (PowerBI/Tableau), relatórios automatizados.
- **Pipeline recomendado:** desenvolvimento local → CI (GitHub Actions) → container Docker → staging → testes integrados → produção.

### 14. Checklist de Validação (Cursor / Ambiente Local)
- **Ambiente & Dependências:** Python 3.11+, `requirements.txt` instalado, versões compatíveis, `config.yaml` revisado.
- **Testes Unitários:** executar `pytest` (core + metals), garantir 100% sucesso, expandir cobertura conforme necessário.
- **Execução do Sistema:** rodar `main.py`, validar coleta Kitco, persistência, integridade dos dados e logs sem warnings críticos.
- **Alertas & Monitoramento:** logging estruturado (INFO/ERROR), alertas iniciais (Slack/e-mail/webhook), métricas básicas (tempo, registros, falhas), plano para Prometheus/Grafana.
- **Automação:** cron job (ou Airflow) para `main.py`, validar execuções automáticas e logs.
- **Preparação Fases Futuras:** notebooks de séries temporais, conectores de notícias + NLP, dashboards interativos (Streamlit/PowerBI).

## Estrutura Recomendada (Resumo)
```
Core/
  Config/
  Logger.py
  Database.py
  Orchestrator.py
  Scheduler.py
  Modules/
    BaseModule.py
    Registry.py
Modules/
  Metals/
    __init__.py
    client.py
    filters.py
    service.py
    tests/
Main/
  main.py  (ponto único de entrada)
Documentation/
  08_Protocolos_Procedimentos/PROTOCOLO_EXPANSAO_CORE_METALS.md
  09_Guias_Manuais/GUIA_CORE_ORCHESTRATION.md (futuro)
```

## Próximos Passos (Iterativos)
1. Implementar ConfigManager + Logger + Database (fase 1).
2. Introduzir Orchestrator + Scheduler (fase 2).
3. Adaptar MetalsKitco ao novo core (fase 3) + criar filtros/testes.
4. Validar pipeline completo (fase 4).
5. Replicar padrão para novos mercados (fase 5).
6. Ativar monitoramento abrangente e estratégias avançadas (fase 6).

Cada nova instrução recebida será comparada com esta matriz para atualizar o que foi planejado, executado ou ainda pendente, garantindo que nenhuma informação ou comando se perca.

