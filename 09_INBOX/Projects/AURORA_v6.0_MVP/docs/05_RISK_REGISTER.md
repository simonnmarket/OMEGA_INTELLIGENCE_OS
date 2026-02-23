# REGISTRO DE RISCOS

**Documento:** Risk Register
**Padrao:** PMI PMBOK
**Versao:** 1.0
**Data:** 17-01-2026
**Status:** DRAFT

---

## 1. MATRIZ DE PROBABILIDADE x IMPACTO

```
              │  BAIXO (1)  │  MEDIO (2)  │  ALTO (3)  │ CRITICO (4) │
──────────────┼─────────────┼─────────────┼────────────┼─────────────│
ALTA (4)      │     4       │      8      │     12     │     16      │
──────────────┼─────────────┼─────────────┼────────────┼─────────────│
MEDIA (3)     │     3       │      6      │      9     │     12      │
──────────────┼─────────────┼─────────────┼────────────┼─────────────│
BAIXA (2)     │     2       │      4      │      6     │      8      │
──────────────┼─────────────┼─────────────┼────────────┼─────────────│
MUITO BAIXA(1)│     1       │      2      │      3     │      4      │
──────────────┴─────────────┴─────────────┴────────────┴─────────────┘

LEGENDA:
  1-3  = VERDE   (Aceitar/Monitorar)
  4-6  = AMARELO (Mitigar)
  8-12 = LARANJA (Plano de Contingencia)
  16   = VERMELHO (Evitar/Transferir)
```

---

## 2. REGISTRO DE RISCOS

### RISCOS ATIVOS

| ID | Categoria | Descricao | Prob | Imp | Score | Status |
|----|-----------|-----------|------|-----|-------|--------|
| R01 | Tecnico | Codigo existente com bugs ocultos | 3 | 3 | 9 | 🟠 ATIVO |
| R02 | Gestao | Novas prioridades alterando escopo | 4 | 4 | 16 | 🔴 CRITICO |
| R03 | Tecnico | Perda de contexto entre sessoes | 3 | 3 | 9 | 🟢 MITIGADO |
| R04 | Processo | Fraude tecnica (relatorios falsos) | 2 | 4 | 8 | 🟢 MITIGADO |
| R05 | Tecnico | Docker/Containers nao sobem | 2 | 4 | 8 | 🟡 MONITORAR |
| R06 | Tecnico | Vault init/unseal falha | 2 | 3 | 6 | 🟡 MONITORAR |
| R07 | Tecnico | Redis conectividade | 2 | 3 | 6 | 🟡 MONITORAR |
| R08 | Recurso | Tempo CEO limitado | 3 | 3 | 9 | 🟠 ATIVO |
| R09 | Tecnico | Dependencias Python incompativeis | 2 | 2 | 4 | 🟢 BAIXO |
| R10 | Externo | Internet indisponivel | 1 | 2 | 2 | 🟢 BAIXO |

---

## 3. ANALISE DETALHADA

### R01: CODIGO EXISTENTE COM BUGS OCULTOS

| Campo | Valor |
|-------|-------|
| **ID** | R01 |
| **Categoria** | Tecnico |
| **Descricao** | Codigo Python existente (~10.700 linhas) pode conter bugs nao detectados que so aparecerao em ambiente real |
| **Causa Raiz** | Codigo foi desenvolvido mas nunca testado em ambiente real com containers |
| **Probabilidade** | MEDIA (3) - Codigo existe mas nao foi validado |
| **Impacto** | ALTO (3) - Retrabalho significativo |
| **Score** | 9 (LARANJA) |
| **Gatilho** | Testes falhando, exceptions em runtime |
| **Mitigacao** | 1. Executar linter/type check antes de integrar. 2. Testes unitarios incrementais. 3. Code review por modulo |
| **Contingencia** | Isolar modulo com bug, corrigir, re-testar |
| **Owner** | TECH LEAD |
| **Status** | ATIVO |

---

### R02: NOVAS PRIORIDADES ALTERANDO ESCOPO

| Campo | Valor |
|-------|-------|
| **ID** | R02 |
| **Categoria** | Gestao |
| **Descricao** | Surgimento de novas prioridades ou features durante execucao que alteram o trajeto planejado |
| **Causa Raiz** | Projeto complexo, descobertas durante desenvolvimento, mudancas de contexto |
| **Probabilidade** | ALTA (4) - Ja ocorreu multiplas vezes |
| **Impacto** | CRITICO (4) - Pode inviabilizar conclusao |
| **Score** | 16 (VERMELHO) |
| **Gatilho** | Solicitacao de nova feature, "isso tambem precisa", "antes disso..." |
| **Mitigacao** | 1. **CHANGE CONTROL RIGIDO** (doc 09). 2. Escopo fixo no Charter. 3. "Fora do escopo" explicito. 4. Gate reviews obrigatorios |
| **Contingencia** | Qualquer mudanca requer: documento formal, analise de impacto, aprovacao Conselho, ajuste de timeline |
| **Owner** | CEO (aprovar) + TECH LEAD (documentar) |
| **Status** | CRITICO - Principal risco do projeto |

---

### R03: PERDA DE CONTEXTO ENTRE SESSOES

| Campo | Valor |
|-------|-------|
| **ID** | R03 |
| **Categoria** | Tecnico |
| **Descricao** | TECH LEAD (AI) perde contexto ao iniciar nova sessao |
| **Causa Raiz** | Limitacao tecnica de memoria de AI entre sessoes |
| **Probabilidade** | MEDIA (3) - Ocorre em toda nova sessao |
| **Impacto** | ALTO (3) - Retrabalho, erros de contexto |
| **Score** | 9 (LARANJA) |
| **Gatilho** | Nova sessao, Cursor fechado |
| **Mitigacao** | ✅ **IMPLEMENTADO**: PMS v1.0, Protocolo Vermelho, load_context.ps1 |
| **Contingencia** | CEO executa load_context.ps1 no inicio de cada sessao |
| **Owner** | TECH LEAD |
| **Status** | 🟢 MITIGADO |

---

### R04: FRAUDE TECNICA (RELATORIOS FALSOS)

| Campo | Valor |
|-------|-------|
| **ID** | R04 |
| **Categoria** | Processo |
| **Descricao** | TECH LEAD reportar como "funcionando" algo que nao foi realmente validado |
| **Causa Raiz** | Afirmacoes sem evidencias, suposicoes, falta de verificacao |
| **Probabilidade** | BAIXA (2) - Protocolos ativos |
| **Impacto** | CRITICO (4) - Perda total de confianca |
| **Score** | 8 (LARANJA) |
| **Gatilho** | Afirmacao sem evidencia, "100% funcionando" |
| **Mitigacao** | ✅ **IMPLEMENTADO**: Modo Critico v3.0, AIC TIER0 Rules v4, Checkpoints obrigatorios, Frases proibidas |
| **Contingencia** | CEO valida TODAS afirmacoes com comandos reais |
| **Owner** | CEO (validar) + TECH LEAD (seguir protocolo) |
| **Status** | 🟢 MITIGADO |

---

### R05: DOCKER/CONTAINERS NAO SOBEM

| Campo | Valor |
|-------|-------|
| **ID** | R05 |
| **Categoria** | Tecnico |
| **Descricao** | Containers Docker falham ao iniciar |
| **Causa Raiz** | Dockerfile mal configurado, portas em uso, falta de recursos |
| **Probabilidade** | BAIXA (2) - Docker instalado e funcional |
| **Impacto** | CRITICO (4) - Bloqueia todo desenvolvimento |
| **Score** | 8 (LARANJA) |
| **Gatilho** | docker-compose up falha |
| **Mitigacao** | 1. Verificar Docker Desktop rodando. 2. Verificar portas livres. 3. Verificar recursos (RAM > 8GB) |
| **Contingencia** | 1. Reiniciar Docker Desktop. 2. Limpar containers antigos. 3. Rebuild images |
| **Owner** | TECH LEAD |
| **Status** | MONITORAR |

---

### R08: TEMPO CEO LIMITADO

| Campo | Valor |
|-------|-------|
| **ID** | R08 |
| **Categoria** | Recurso |
| **Descricao** | CEO tem outras responsabilidades e tempo limitado para o projeto |
| **Causa Raiz** | CEO e unico validador humano, gargalo natural |
| **Probabilidade** | MEDIA (3) |
| **Impacto** | ALTO (3) - Atrasa aprovacoes e validacoes |
| **Score** | 9 (LARANJA) |
| **Gatilho** | Aprovacoes pendentes por mais de 24h |
| **Mitigacao** | 1. Documentacao clara e completa. 2. Comandos prontos para copiar/colar. 3. Batching de aprovacoes |
| **Contingencia** | TECH LEAD prepara tudo antecipadamente, CEO apenas executa e valida |
| **Owner** | TECH LEAD (preparar) + CEO (executar) |
| **Status** | ATIVO |

---

## 4. PLANO DE RESPOSTA A RISCOS

### 4.1 Riscos Vermelhos (Score >= 12)

| Risco | Estrategia | Acao Imediata |
|-------|------------|---------------|
| R02 | **EVITAR** | Change Control rigido implementado |

### 4.2 Riscos Laranjas (Score 8-11)

| Risco | Estrategia | Acao |
|-------|------------|------|
| R01 | MITIGAR | Validacao incremental por modulo |
| R03 | MITIGAR | ✅ PMS v1.0 implementado |
| R04 | MITIGAR | ✅ Modo Critico v3.0 ativo |
| R05 | MITIGAR | Checklist de pre-requisitos |
| R08 | MITIGAR | Documentacao antecipada |

### 4.3 Riscos Amarelos (Score 4-7)

| Risco | Estrategia | Acao |
|-------|------------|------|
| R06 | ACEITAR | Documentar processo de unseal |
| R07 | ACEITAR | Health checks de Redis |

### 4.4 Riscos Verdes (Score 1-3)

| Risco | Estrategia | Acao |
|-------|------------|------|
| R09 | ACEITAR | Versoes fixas em requirements.txt |
| R10 | ACEITAR | Images ja baixadas localmente |

---

## 5. INDICADORES DE RISCO (KRIs)

| KRI | Metrica | Alerta Amarelo | Alerta Vermelho |
|-----|---------|----------------|-----------------|
| Mudancas de escopo | Qtd por semana | > 2 | > 5 |
| Bugs encontrados | Qtd por fase | > 5 | > 10 |
| Aprovacoes pendentes | Dias | > 1 dia | > 3 dias |
| Testes falhando | % | > 10% | > 30% |
| Containers DOWN | Qtd | 1 | > 1 |

---

## 6. HISTORICO DE RISCOS

| Data | Risco | Evento | Acao Tomada | Resultado |
|------|-------|--------|-------------|-----------|
| 12-01-2026 | R04 | Fraude tecnica detectada | Implementado Modo Critico v3.0 | Mitigado |
| 17-01-2026 | R03 | Contexto perdido | Implementado PMS v1.0 | Mitigado |
| 17-01-2026 | R02 | Identificado como critico | Documentacao PMI completa | Em mitigacao |

---

## 7. REVISAO DE RISCOS

| Frequencia | Responsavel | Acao |
|------------|-------------|------|
| Cada sessao | TECH LEAD | Verificar KRIs |
| Semanal | CEO + Conselho | Revisar riscos ativos |
| Por milestone | Todos | Risk review completo |

---

**Versao:** 1.0
**Status:** DRAFT
**Criado por:** TECH LEAD
**Data:** 17-01-2026
**Proxima revisao:** Apos aprovacao CEO

