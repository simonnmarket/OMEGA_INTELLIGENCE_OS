# PROJECT CHARTER - AURORA v6.0 MVP

**Documento:** Project Charter (Carta do Projeto)
**Padrao:** PMI PMBOK 7th Edition
**Versao:** 1.0
**Data:** 17-01-2026
**Status:** DRAFT - Aguardando aprovacao CEO + Conselho

---

## 1. INFORMACOES DO PROJETO

| Campo | Valor |
|-------|-------|
| **Nome do Projeto** | AURORA v6.0 MVP |
| **Tipo** | Sistema de Trading Institucional TIER-0 |
| **Sponsor** | CEO |
| **Project Manager** | TECH LEAD |
| **Data de Inicio** | 17-01-2026 |
| **Data Prevista de Conclusao** | A definir |
| **Orcamento** | A definir |
| **Prioridade** | CRITICA |

---

## 2. JUSTIFICATIVA DO PROJETO (Business Case)

### 2.1 Problema
Sistema de trading automatizado que atenda padroes institucionais (TIER-0) com:
- Latencia < 100ms (P99)
- Uptime 99.99%
- Compliance regulatorio
- Gestao de risco integrada

### 2.2 Oportunidade
- Automatizacao de operacoes de trading
- Reducao de erros humanos
- Operacao 24/7
- Escalabilidade institucional

### 2.3 Beneficios Esperados
1. Sistema operacional em ambiente de producao
2. Documentacao tecnica completa
3. Processos de CI/CD estabelecidos
4. Monitoring e alertas funcionais

---

## 3. ESCOPO DO PROJETO

### 3.1 DENTRO DO ESCOPO (In Scope)

| ID | Item | Descricao | Prioridade |
|----|------|-----------|------------|
| S01 | Infraestrutura Docker | Containers, compose, orquestracao | P0 |
| S02 | Sistema TIER-0 Core | aurora_core com auth, health, risk | P0 |
| S03 | Integracao Vault | Secrets management | P0 |
| S04 | Integracao Redis | Distributed locking | P0 |
| S05 | Monitoring | Prometheus + dashboards | P1 |
| S06 | Testes Automatizados | Unit, integration, load | P1 |
| S07 | Documentacao Tecnica | API, deployment, runbook | P1 |
| S08 | CI/CD Pipeline | Build, test, deploy automatizado | P2 |

### 3.2 FORA DO ESCOPO (Out of Scope)

| ID | Item | Motivo | Fase Futura |
|----|------|--------|-------------|
| O01 | Trading em producao real | MVP apenas | v7.0 |
| O02 | Multi-exchange | Complexidade | v7.0 |
| O03 | Machine Learning avancado | Apos validacao base | v7.0 |
| O04 | Mobile app | Nao prioritario | v8.0 |
| O05 | Integracao bancaria | Regulatorio complexo | v8.0 |

### 3.3 CRITERIOS DE EXCLUSAO

**Um item esta FORA do escopo se:**
1. Nao foi listado explicitamente em "Dentro do Escopo"
2. Aumenta prazo em mais de 20% sem aprovacao
3. Requer tecnologias nao aprovadas pelo CTO
4. Viola padroes de qualidade definidos pelo CQO

---

## 4. OBJETIVOS E CRITERIOS DE SUCESSO

### 4.1 Objetivos SMART

| ID | Objetivo | Metrica | Meta | Prazo |
|----|----------|---------|------|-------|
| OBJ01 | Containers operacionais | docker ps | Todos UP | Fase 1 |
| OBJ02 | Health checks verdes | /health endpoint | 200 OK | Fase 1 |
| OBJ03 | Testes passando | pytest exit code | 0 | Fase 1 |
| OBJ04 | Latencia aceitavel | P99 response time | < 100ms | Fase 2 |
| OBJ05 | Documentacao completa | Docs coverage | 100% | Fase 2 |
| OBJ06 | Zero vulnerabilidades criticas | Security scan | 0 critical | Fase 2 |

### 4.2 Criterios de Aceitacao do MVP

**O MVP sera considerado COMPLETO quando:**

- [ ] Todos containers Docker rodando sem erros por 24h
- [ ] Health checks retornando 200 OK
- [ ] Vault inicializado e operacional
- [ ] Redis cluster respondendo
- [ ] Testes unitarios passando (> 80% coverage)
- [ ] Testes de integracao passando
- [ ] Documentacao tecnica completa
- [ ] Zero vulnerabilidades criticas
- [ ] Aprovacao formal do Conselho (CQO + CTO)
- [ ] Aprovacao final do CEO

---

## 5. MARCOS PRINCIPAIS (Milestones)

| Marco | Descricao | Data Alvo | Criterio de Conclusao |
|-------|-----------|-----------|----------------------|
| M0 | Documentacao Completa | +3 dias | Todos docs criados e aprovados |
| M1 | Infraestrutura Operacional | +5 dias | Docker + WSL2 + containers UP |
| M2 | TIER-0 Core Validado | +7 dias | Health checks verdes |
| M3 | Integracao Completa | +10 dias | Vault + Redis + API funcionando |
| M4 | Testes Validados | +12 dias | Pytest passando, coverage > 80% |
| M5 | MVP Completo | +14 dias | Todos criterios de aceitacao |

---

## 6. RESTRICOES E PREMISSAS

### 6.1 Restricoes (Constraints)

| ID | Restricao | Impacto |
|----|-----------|---------|
| R01 | Sem budget para cloud (apenas local) | Desenvolvimento local apenas |
| R02 | Equipe: 1 CEO + Conselho + 1 TECH LEAD (AI) | Capacidade limitada |
| R03 | Horario de trabalho do CEO | Sessoes assincronas |
| R04 | Sem acesso a APIs de trading real | Mocks apenas no MVP |

### 6.2 Premissas (Assumptions)

| ID | Premissa | Risco se Falsa |
|----|----------|----------------|
| A01 | WSL2 + Docker funcionam | Bloqueio total |
| A02 | Codigo existente esta funcional | Retrabalho |
| A03 | Dependencias Python compativeis | Conflitos |
| A04 | Hardware suficiente para containers | Performance |

---

## 7. RISCOS INICIAIS

| ID | Risco | Probabilidade | Impacto | Mitigacao |
|----|-------|---------------|---------|-----------|
| R01 | Codigo existente com bugs | Media | Alto | Validacao antes de integrar |
| R02 | Novas prioridades surgindo | Alta | Alto | **CHANGE CONTROL RIGIDO** |
| R03 | Perda de contexto entre sessoes | Alta | Medio | PMS v1.0 implementado |
| R04 | Fraude tecnica (relatorios falsos) | Baixa | Critico | Modo Critico v3.0 |
| R05 | Prazo nao cumprido | Media | Medio | Milestones curtos |

---

## 8. ORGANIZACAO DO PROJETO

### 8.1 Estrutura

```
CEO (Sponsor + Decisor Final)
    |
    +-- Conselho Cientifico (Gate de Aprovacao)
    |       |
    |       +-- CQO (Qualidade)
    |       +-- CTO (Arquitetura)
    |
    +-- TECH LEAD (Execucao)
```

### 8.2 Matriz RACI

| Atividade | CEO | CQO | CTO | TECH LEAD |
|-----------|-----|-----|-----|-----------|
| Definir prioridades | **A** | C | C | I |
| Aprovar arquitetura | A | C | **R** | I |
| Aprovar qualidade | A | **R** | C | I |
| Propor solucoes | I | C | C | **R** |
| Implementar codigo | I | C | C | **R** |
| Validar funcionamento | **R** | C | C | A |
| Aprovar mudancas | **A** | R | R | I |

**Legenda:**
- **R** = Responsible (Executa)
- **A** = Accountable (Aprova/Responde)
- **C** = Consulted (Consultado)
- **I** = Informed (Informado)

---

## 9. CONTROLE DE MUDANCAS (Change Control)

### 9.1 Processo Obrigatorio

```
1. TECH LEAD identifica necessidade de mudanca
       |
       v
2. Documenta em CHANGE_REQUEST.md
       |
       v
3. Conselho (CQO + CTO) avalia impacto
       |
       v
4. CEO aprova/rejeita
       |
       v
5. Se aprovado: Atualiza WBS, Timeline, Riscos
       |
       v
6. Registra em memory/changes/
```

### 9.2 Criterios para Aprovar Mudanca

Uma mudanca so sera aprovada se:
- [ ] Nao aumenta prazo em mais de 20%
- [ ] Nao adiciona nova tecnologia sem justificativa
- [ ] Nao viola padroes de qualidade
- [ ] Tem beneficio claro documentado
- [ ] Tem analise de impacto completa

### 9.3 Tipos de Mudanca

| Tipo | Aprovador | Tempo Decisao |
|------|-----------|---------------|
| Cosmética (docs, nomes) | TECH LEAD | Imediato |
| Menor (refactor interno) | CQO | 1 sessao |
| Significativa (nova feature) | Conselho | 2 sessoes |
| Critica (arquitetura) | CEO + Conselho | 3 sessoes |

---

## 10. COMUNICACAO

### 10.1 Reunioes/Checkpoints

| Tipo | Frequencia | Participantes | Objetivo |
|------|------------|---------------|----------|
| Daily Status | Cada sessao | TECH LEAD + CEO | Progresso |
| Gate Review | Por milestone | Todos | Aprovacao |
| Risk Review | Semanal | Todos | Mitigacao |

### 10.2 Documentos de Comunicacao

| Documento | Frequencia | Responsavel |
|-----------|------------|-------------|
| CURRENT_STATUS.md | Cada sessao | TECH LEAD |
| CHANGE_LOG.md | Por mudanca | TECH LEAD |
| DECISION_LOG.md | Por decisao | Conselho |
| RISK_REGISTER.md | Semanal | TECH LEAD |

---

## 11. APROVACOES

### 11.1 Aprovacao do Project Charter

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| CEO | [Skyler] | ___/___/2026 | [ ] APROVADO |
| CQO | [Dr. Volkov] | ___/___/2026 | [ ] APROVADO |
| CTO | [Dr. Erik] | ___/___/2026 | [ ] APROVADO |
| TECH LEAD | [Opus 4.5] | 17/01/2026 | [x] PROPOSTO |

### 11.2 Condicoes de Aprovacao

Este documento entra em vigor quando:
- [ ] CEO aprova
- [ ] CQO aprova
- [ ] CTO aprova

**Apos aprovacao, qualquer mudanca requer novo ciclo de aprovacao.**

---

## 12. ANEXOS

- A: Work Breakdown Structure (WBS) - `docs/03_WBS.md`
- B: Mapa de Dependencias - `docs/04_DEPENDENCY_MAP.md`
- C: Registro de Riscos - `docs/05_RISK_REGISTER.md`
- D: Timeline/Cronograma - `docs/06_TIMELINE.md`

---

**Versao:** 1.0
**Status:** DRAFT
**Criado por:** TECH LEAD
**Data:** 17-01-2026
**Proxima revisao:** Apos aprovacao CEO

