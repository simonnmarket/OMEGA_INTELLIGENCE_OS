# SCRIPT DO PROJETO AURORA v6.0 MVP

**Versao:** 1.0
**Data de criacao:** 17-01-2026
**Ultima atualizacao:** 17-01-2026 22:30 (Berlin)
**Status:** ATIVO

---

## VISAO GERAL

**Nome do Projeto:** AURORA v6.0 MVP
**Tipo:** Sistema de Trading Institucional TIER-0
**Objetivo:** Sistema de trading automatizado com qualidade enterprise e compliance institucional

---

## ESTRUTURA ORGANIZACIONAL

### Governanca

```
CEO (Lider Geral)
    |
    v
CQO + CTO (Conselho Cientifico)
    |
    v
TECH LEAD (Implementacao)
```

### Papeis e Responsabilidades

**CEO:**
- Decisoes estrategicas finais
- Definicao de prioridades
- Validacao de funcionamento real
- Aprovacao de deploys

**CQO (Chief Quality Officer):**
- Definicao de padroes de qualidade
- Code review e validacao
- Estrategia de testes
- Quality gates

**CTO (Chief Technology Officer):**
- Decisoes de arquitetura
- Escolha de tecnologias
- Validacao de design tecnico
- Estrategia de infraestrutura

**TECH LEAD:**
- Proposta de solucoes tecnicas
- Implementacao de codigo
- Documentacao tecnica
- Troubleshooting

---

## OBJETIVOS DO PROJETO

### Objetivos de Negocio
1. Sistema de trading automatizado funcional
2. Compliance TIER-0 (institucional)
3. Latencia <100ms (P99)
4. Uptime 99.99%
5. Infraestrutura production-ready

### Objetivos Tecnicos
1. Arquitetura microservices
2. Docker + Kubernetes ready
3. HashiCorp Vault para secrets
4. Redis Cluster para distributed locking
5. Prometheus + Grafana para monitoring
6. CI/CD completo

---

## ESTADO ATUAL

**Fase:** 0 - Fundacao
**Progresso:** PMS v1.0 implementado
**Bloqueadores:** WSL2 nao instalado
**Confianca:** Protocolos rigorosos ativos

### O que existe
- Estrutura de pastas PMS
- Scripts PowerShell (init, update, load)
- Templates (decisao, tarefa)
- Codigo aurora_core (nao validado em ambiente real)

### O que NAO existe/NAO foi validado
- WSL2 instalado
- Docker containers rodando
- Testes de integracao reais
- Deploy em ambiente real

---

## ROADMAP

### Fase 0: Fundacao (2-4h) - EM PROGRESSO
- [x] Definir estrutura organizacional
- [x] Ativar protocolos rigorosos (Modo Critico)
- [x] Criar sistema de documentacao (PMS)
- [ ] Inventario completo do projeto
- [ ] Prioridades definidas pelo CEO

### Fase 1: Quick Wins (1-2 dias) - PENDENTE
- [ ] Resolver bloqueador WSL2
- [ ] Validar codigo existente
- [ ] Primeiro deploy real
- [ ] Containers rodando com evidencias

### Fase 2: Consolidacao (3-5 dias) - PENDENTE
- [ ] Documentacao tecnica completa
- [ ] Testes de integracao reais
- [ ] Integracao v6.0 + TIER-0
- [ ] Monitoring basico

### Fase 3: Producao (1-2 semanas) - FUTURO
- [ ] Deploy em ambiente de staging
- [ ] Testes de carga
- [ ] Runbooks operacionais
- [ ] Go-live

---

## RISCOS E MITIGACOES

### Risco 1: Repeticao de fraude tecnica
- **Probabilidade:** Baixa (protocolos ativos)
- **Impacto:** Muito Alto (perda de confianca)
- **Mitigacao:** Modo Critico + checkpoints obrigatorios

### Risco 2: WSL2 nao instala
- **Probabilidade:** Baixa (5-10%)
- **Impacto:** Alto (bloqueio total)
- **Mitigacao:** Plano B com VM

### Risco 3: Prazo nao cumprido
- **Probabilidade:** Media (30%)
- **Impacto:** Medio
- **Mitigacao:** Priorizacao clara, MVP iterativo

---

## REFERENCIAS-CHAVE

- **Governanca:** docs/01_GOVERNANCE.md
- **Inventario:** docs/02_INVENTORY.md
- **Roadmap Detalhado:** docs/03_ROADMAP.md
- **Decisoes:** memory/decisions/index.json
- **Tarefas Ativas:** memory/tasks/in_progress/
- **Status Atual:** .context/CURRENT_STATUS.md

---

## PROTOCOLOS ATIVOS

1. **Modo Critico v3.0** - Checkpoints obrigatorios
2. **Protocolo Vermelho** - Atualizacao automatica de contexto
3. **AIC TIER0 Rules v4** - Anti-fraude
4. **Protocolo OMEGA** - Excelencia tecnica

---

## COMUNICACAO

### Fluxo de Decisao
1. CEO define requisito
2. TECH LEAD propoe solucoes (multiplas opcoes)
3. Conselho (CQO + CTO) aprova/rejeita/ajusta
4. TECH LEAD implementa (se aprovado)
5. CQO valida qualidade
6. CEO valida funcionamento
7. Conselho aprova deploy

### Templates
- **Proposta Tecnica:** memory/decisions/_TEMPLATE_DECISION.md
- **Tarefa:** memory/tasks/_TEMPLATE_TASK.md

---

**Este documento e o SCRIPT MESTRE do projeto. Qualquer pessoa (humana ou AI) deve ler este documento PRIMEIRO para entender o projeto.**

---

**Ultima atualizacao:** 17-01-2026 22:30 (Berlin)
**Atualizado por:** TECH LEAD
**Proxima revisao:** Apos cada marco importante

