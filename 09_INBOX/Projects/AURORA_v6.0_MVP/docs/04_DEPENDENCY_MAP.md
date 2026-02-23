# MAPA DE DEPENDENCIAS

**Documento:** Dependency Map
**Versao:** 1.0
**Data:** 17-01-2026
**Status:** DRAFT

---

## 1. DIAGRAMA DE DEPENDENCIAS PRINCIPAL

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    AURORA v6.0 MVP                           │
                    │                   MAPA DE DEPENDENCIAS                       │
                    └─────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 0: GESTAO (Documentacao)                                               │
    │                                                                              │
    │  [Charter] ──► [WBS] ──► [Deps Map] ──► [Risks] ──► [Timeline]              │
    │      │                                                    │                  │
    │      └────────────────────────────────────────────────────┘                  │
    │                              │                                               │
    │                         [GATE G0]                                            │
    │                      Aprovacao Conselho                                      │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 1: INFRAESTRUTURA                                                      │
    │                                                                              │
    │  [WSL2 Validar] ──► [Docker Desktop] ──► [docker-compose]                   │
    │                              │                    │                          │
    │                              │          ┌────────┴────────┐                  │
    │                              │          │                 │                  │
    │                              │          ▼                 ▼                  │
    │                              │    [Vault Container] [Redis Container]        │
    │                              │          │                 │                  │
    │                              │          ▼                 ▼                  │
    │                              │    [Vault Init]     [Redis Config]            │
    │                              │          │                 │                  │
    │                              │          ▼                 │                  │
    │                              │    [Vault Unseal]         │                   │
    │                              │          │                 │                  │
    │                              │          └────────┬────────┘                  │
    │                              │                   │                           │
    │                              │              [GATE G1]                        │
    │                              │           Containers UP                       │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 2: SISTEMA TIER-0                                                      │
    │                                                                              │
    │  [Linter] ──► [Type Check] ──► [Security Scan]                              │
    │                    │                                                         │
    │          ┌────────┴────────┬─────────────┬─────────────┐                    │
    │          ▼                 ▼             ▼             ▼                    │
    │     [Auth Module]    [Health Module] [Risk Module] [Execution]              │
    │          │                 │             │             │                    │
    │          └────────┬────────┴─────────────┴─────────────┘                    │
    │                   │                                                          │
    │                   ▼                                                          │
    │     [Vault Client] ◄──────────────────────► [Redlock Manager]               │
    │          │                                        │                          │
    │          └───────────────┬────────────────────────┘                          │
    │                          │                                                   │
    │                     [GATE G2]                                                │
    │                  Codigo Validado                                             │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 3: TESTES                                                              │
    │                                                                              │
    │  [Unit Tests Auth] ──┐                                                       │
    │  [Unit Tests Health]─┼──► [Integration Tests] ──► [Load Tests]              │
    │  [Unit Tests Risk] ──┘            │                     │                   │
    │                                   │                     │                   │
    │                              [GATE G3]                  │                   │
    │                          Coverage > 80%                 │                   │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 4: MONITORING                                                          │
    │                                                                              │
    │  [Prometheus Deploy] ──► [Scrape Config] ──► [Alertas]                      │
    │          │                                       │                           │
    │          └────────────► [Dashboards] ◄──────────┘                           │
    │                              │                                               │
    │                         [GATE G4]                                            │
    │                     Metricas OK                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  FASE 5: DOCUMENTACAO                                                        │
    │                                                                              │
    │  [ARCHITECTURE.md] ◄─────────────────────────────────────────┐              │
    │         │                                                     │              │
    │         ▼                                                     │              │
    │  [DEPLOYMENT.md] ──► [RUNBOOK.md] ──► [API_REFERENCE.md]    │              │
    │                                              │                │              │
    │                                         [GATE G5]            │              │
    │                                      Docs Completos          │              │
    └──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │   GATE FINAL    │
                         │   MVP COMPLETO  │
                         │   Aprovacao CEO │
                         └─────────────────┘
```

---

## 2. MATRIZ DE DEPENDENCIAS

### 2.1 Dependencias por Componente

| Componente | Depende de | Bloqueia |
|------------|------------|----------|
| WSL2 | Windows | Docker Desktop |
| Docker Desktop | WSL2 | Todos containers |
| Vault Container | Docker | Vault Client |
| Redis Container | Docker | Redlock Manager |
| Auth Module | Type Check | Unit Tests Auth |
| Health Module | Type Check | Unit Tests Health |
| Vault Client | Vault Unseal | Integration Tests |
| Redlock Manager | Redis Config | Integration Tests |
| Integration Tests | Unit Tests, Vault, Redis | Load Tests |
| Prometheus | Docker | Dashboards |
| RUNBOOK.md | All Systems UP | MVP Final |

### 2.2 Dependencias Externas

| Dependencia | Tipo | Risco | Mitigacao |
|-------------|------|-------|-----------|
| Python 3.11 | Software | Baixo | Ja instalado |
| Docker Desktop | Software | Medio | Ja instalado |
| WSL2/Ubuntu | Software | Baixo | Ja instalado |
| Internet | Rede | Baixo | Pull images offline |
| HashiCorp Vault | Container | Medio | Versao fixa |
| Redis | Container | Baixo | Versao fixa |

---

## 3. GARGALOS IDENTIFICADOS

### 3.1 Gargalos Criticos

```
┌─────────────────────────────────────────────────────────────────┐
│  GARGALO #1: INICIALIZACAO VAULT                                │
│                                                                 │
│  [Vault Deploy] ──► [Vault Init] ──► [Vault Unseal]            │
│                          │                │                     │
│                          ▼                ▼                     │
│                    Requer CEO        Requer CEO                 │
│                   (interacao)       (interacao)                 │
│                                                                 │
│  IMPACTO: Bloqueia Vault Client e todos testes de integracao   │
│  MITIGACAO: Documentar passo-a-passo claro para CEO            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  GARGALO #2: APROVACOES DO CONSELHO                             │
│                                                                 │
│  Cada GATE requer:                                              │
│  - Revisao CQO (qualidade)                                      │
│  - Revisao CTO (arquitetura)                                    │
│  - Aprovacao CEO                                                │
│                                                                 │
│  IMPACTO: Pode adicionar 1-2 dias por gate                     │
│  MITIGACAO: Preparar evidencias claras antes de cada gate      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  GARGALO #3: TESTES DE INTEGRACAO                               │
│                                                                 │
│  Requer TODOS funcionando simultaneamente:                      │
│  - Vault UP + Unsealed                                          │
│  - Redis UP + Configured                                        │
│  - Aurora Core UP                                               │
│  - Network connectivity                                         │
│                                                                 │
│  IMPACTO: Falha em qualquer um bloqueia todos                  │
│  MITIGACAO: Health checks individuais antes de integrar        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Pontos de Atencao

| # | Ponto | Risco | Acao Preventiva |
|---|-------|-------|-----------------|
| 1 | Vault unseal keys | Perda = reset | Backup seguro das keys |
| 2 | Redis data | Perda em restart | Volumes persistentes |
| 3 | Network entre containers | DNS issues | docker network dedicada |
| 4 | Ordem de startup | Containers dependentes | depends_on + healthcheck |

---

## 4. CAMINHOS PARALELOS

### 4.1 Tarefas Paralelizaveis

```
APOS docker-compose UP:

    Thread 1                Thread 2              Thread 3
    ────────               ────────              ────────
    [Vault Deploy]         [Redis Deploy]        [Prometheus Deploy]
         │                      │                      │
         ▼                      ▼                      ▼
    [Vault Init]           [Redis Config]        [Scrape Config]
         │                      │                      │
         ▼                      │                      │
    [Vault Unseal]              │                      │
         │                      │                      │
         └──────────────────────┴──────────────────────┘
                               │
                               ▼
                    [Integration Tests]
```

### 4.2 Otimizacao de Tempo

| Execucao Sequencial | Execucao Paralela | Economia |
|---------------------|-------------------|----------|
| 6h (infra) | 3h (paralelo) | 3h |
| 4h (testes unit) | 2h (paralelo) | 2h |
| **Total: 10h** | **Total: 5h** | **50%** |

---

## 5. FLUXO DE DADOS

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO DE DADOS AURORA                        │
└─────────────────────────────────────────────────────────────────┘

                         ┌─────────────┐
                         │   CLIENT    │
                         │  (Request)  │
                         └──────┬──────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    AURORA API         │
                    │  tier0_endpoints.py   │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │   AUTH MODULE   │ │HEALTH CHECK │ │  RISK ENGINE    │
    │  tier0_auth.py  │ │tier0_health │ │ finite_state    │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                  │
             ▼                 │                  │
    ┌─────────────────┐        │                  │
    │  VAULT CLIENT   │        │                  │
    │  (secrets)      │        │                  │
    └────────┬────────┘        │                  │
             │                 │                  │
             │                 │         ┌────────┴────────┐
             │                 │         │                 │
             │                 │         ▼                 ▼
             │                 │ ┌─────────────┐ ┌─────────────────┐
             │                 │ │   REDLOCK   │ │   EXECUTION     │
             │                 │ │  (locking)  │ │ safe_execution  │
             │                 │ └──────┬──────┘ └────────┬────────┘
             │                 │        │                 │
             ▼                 ▼        ▼                 ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                     PROMETHEUS                               │
    │                    (metricas)                                │
    └─────────────────────────────────────────────────────────────┘
```

---

## 6. CHECKLIST DE VALIDACAO

### Antes de Iniciar Cada Fase

- [ ] Todas dependencias da fase anterior estao verdes
- [ ] Gate anterior foi aprovado
- [ ] Recursos necessarios estao disponiveis
- [ ] Riscos da fase foram revisados

### Antes de Cada Gate Review

- [ ] Todos deliverables da fase estao completos
- [ ] Evidencias documentadas
- [ ] Testes passando
- [ ] Documentacao atualizada

---

**Versao:** 1.0
**Status:** DRAFT
**Criado por:** TECH LEAD
**Data:** 17-01-2026

