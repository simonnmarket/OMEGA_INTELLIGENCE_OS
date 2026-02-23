# CONTROLE DE MUDANCAS

**Documento:** Change Control Process
**Padrao:** PMI PMBOK + PRINCE2
**Versao:** 1.0
**Data:** 17-01-2026
**Status:** DRAFT - CRITICO

---

## ⚠️ CONTEXTO CRITICO

Este documento existe para resolver o problema identificado pelo CEO:

> "O projeto esta enfrentando dificuldades desde o inicio, pois aparecem 
> novas prioridades ou modulos que vao surgindo e alterando o trajeto 
> ja aprovado criando novas prioridades e camadas o que torna o projeto 
> mais dificil de ser executado."

**RISCO R02 - Score 16 (VERMELHO)**

---

## 1. PRINCIPIO FUNDAMENTAL

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   "NENHUMA MUDANCA SEM PROCESSO FORMAL"                        │
│                                                                 │
│   Toda solicitacao de mudanca deve passar pelo processo        │
│   definido neste documento. Sem excecoes.                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. TIPOS DE MUDANCA

### 2.1 Classificacao

| Tipo | Descricao | Exemplo | Aprovador | Tempo |
|------|-----------|---------|-----------|-------|
| **COSMETICA** | Nao afeta funcionamento | Renomear variavel, ajustar doc | TECH LEAD | Imediato |
| **MENOR** | Afeta modulo isolado | Refatorar funcao interna | CQO | 1 sessao |
| **SIGNIFICATIVA** | Nova funcionalidade | Adicionar endpoint | Conselho | 2 sessoes |
| **CRITICA** | Mudanca arquitetural | Trocar tecnologia | CEO + Conselho | 3+ sessoes |
| **EMERGENCIA** | Bug critico em producao | Sistema DOWN | CEO | Imediato |

### 2.2 Criterios de Classificacao

```
A mudanca e CRITICA se:
  □ Altera arquitetura definida pelo CTO
  □ Adiciona nova tecnologia nao aprovada
  □ Aumenta prazo em mais de 20%
  □ Afeta mais de 3 modulos simultaneamente
  □ Requer nova dependencia externa

A mudanca e SIGNIFICATIVA se:
  □ Adiciona nova feature ao escopo
  □ Altera interface publica (API)
  □ Afeta 2-3 modulos
  □ Aumenta prazo em 5-20%

A mudanca e MENOR se:
  □ Melhoria interna sem mudanca de interface
  □ Refatoracao de codigo existente
  □ Correcao de bug nao critico
  □ Afeta 1 modulo apenas

A mudanca e COSMETICA se:
  □ Documentacao apenas
  □ Formatacao de codigo
  □ Renomeacao sem impacto funcional
```

---

## 3. PROCESSO DE MUDANCA

### 3.1 Fluxo Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSO DE MUDANCA                          │
└─────────────────────────────────────────────────────────────────┘

    [1. IDENTIFICACAO]
          │
          │  Alguem identifica necessidade de mudanca
          │
          ▼
    [2. REGISTRO]
          │
          │  TECH LEAD documenta em CHANGE_REQUEST.md
          │  - Descricao da mudanca
          │  - Justificativa
          │  - Impacto estimado
          │
          ▼
    [3. CLASSIFICACAO]
          │
          │  TECH LEAD classifica:
          │  - Cosmetica? Menor? Significativa? Critica?
          │
          ▼
    [4. ANALISE DE IMPACTO]
          │
          │  TECH LEAD analisa:
          │  - Impacto em Timeline
          │  - Impacto em WBS
          │  - Impacto em Riscos
          │  - Impacto em Outros Modulos
          │
          ▼
    [5. REVISAO DO CONSELHO]
          │
          │  CQO avalia qualidade
          │  CTO avalia arquitetura
          │
          ▼
    [6. DECISAO]
          │
          │  ┌─────────────┐
          │  │   CEO       │
          │  │  DECIDE     │
          │  └─────────────┘
          │        │
          │   ┌────┴────┐
          │   │         │
          ▼   ▼         ▼
    [APROVADO]    [REJEITADO]    [ADIADO]
          │              │            │
          ▼              ▼            ▼
    [7. IMPLEMENTAR]  [ARQUIVAR]  [BACKLOG]
          │
          ▼
    [8. ATUALIZAR DOCS]
          │
          │  - WBS atualizado
          │  - Timeline atualizado
          │  - Riscos atualizados
          │
          ▼
    [9. REGISTRAR]
          │
          │  memory/changes/
          │
          ▼
        [FIM]
```

### 3.2 Tempo Maximo por Tipo

| Tipo | Tempo Maximo para Decisao |
|------|---------------------------|
| COSMETICA | Imediato |
| MENOR | 1 sessao (mesmo dia) |
| SIGNIFICATIVA | 2 sessoes (48h) |
| CRITICA | 3+ sessoes (72h+) |
| EMERGENCIA | Imediato |

---

## 4. TEMPLATE DE SOLICITACAO

```markdown
# SOLICITACAO DE MUDANCA - CR_[NUMERO]

**Data:** DD-MM-YYYY
**Solicitante:** [CEO/CQO/CTO/TECH LEAD]
**Classificacao:** [Cosmetica/Menor/Significativa/Critica]

## 1. DESCRICAO DA MUDANCA
[O que precisa mudar]

## 2. JUSTIFICATIVA
[Por que esta mudanca e necessaria]

## 3. ALTERNATIVAS CONSIDERADAS
- Alternativa A: [descricao]
- Alternativa B: [descricao]
- **Recomendacao:** [qual e por que]

## 4. ANALISE DE IMPACTO

### 4.1 Escopo
- Modulos afetados: [lista]
- Linhas de codigo estimadas: [X]

### 4.2 Timeline
- Esforco adicional: [X horas]
- Impacto no prazo: [X dias]
- Novo prazo proposto: [DD-MM-YYYY]

### 4.3 Riscos
- Novos riscos: [lista]
- Riscos mitigados: [lista]

### 4.4 Qualidade
- Impacto em testes: [descricao]
- Documentacao necessaria: [lista]

## 5. RECOMENDACAO DO TECH LEAD
[Aprovar/Rejeitar/Adiar com justificativa]

## 6. DECISAO

### Revisao CQO
- Data: ___/___/____
- Parecer: [Favoravel/Desfavoravel]
- Observacoes: [...]

### Revisao CTO
- Data: ___/___/____
- Parecer: [Favoravel/Desfavoravel]
- Observacoes: [...]

### Decisao CEO
- Data: ___/___/____
- Decisao: [APROVADO/REJEITADO/ADIADO]
- Condicoes: [...]

---
**Status Final:** [APROVADO/REJEITADO/ADIADO]
**CR Arquivado em:** memory/changes/CR_[NUMERO].md
```

---

## 5. CRITERIOS DE APROVACAO/REJEICAO

### 5.1 Aprovar SE:

- [ ] Alinhado com objetivos do Charter
- [ ] Impacto em timeline < 20%
- [ ] Nao adiciona tecnologia nao aprovada
- [ ] Beneficio claro e documentado
- [ ] Riscos identificados e mitigaveis
- [ ] Recursos disponiveis

### 5.2 Rejeitar SE:

- [ ] Fora do escopo definido
- [ ] Impacto em timeline > 20% sem justificativa critica
- [ ] Adiciona complexidade sem beneficio claro
- [ ] Viola padroes de qualidade
- [ ] Recursos insuficientes

### 5.3 Adiar SE:

- [ ] Valido mas nao prioritario agora
- [ ] Depende de outra entrega
- [ ] Requer mais analise
- [ ] Melhor para proxima versao

---

## 6. REGISTRO DE MUDANCAS

### 6.1 Local de Armazenamento

```
memory/
└── changes/
    ├── index.json           # Indice de todas mudancas
    ├── CR_001.md            # Change Request 1
    ├── CR_002.md            # Change Request 2
    └── ...
```

### 6.2 Formato do Index

```json
{
  "change_requests": [
    {
      "id": "CR_001",
      "date": "17-01-2026",
      "title": "Adicionar endpoint X",
      "type": "SIGNIFICATIVA",
      "status": "APROVADO",
      "requestor": "CEO",
      "file": "CR_001.md"
    }
  ],
  "statistics": {
    "total": 1,
    "approved": 1,
    "rejected": 0,
    "pending": 0
  }
}
```

---

## 7. ESCALACAO

### 7.1 Quando Escalar

| Situacao | Escalar Para |
|----------|--------------|
| TECH LEAD discorda do Conselho | CEO |
| Conselho empatado | CEO |
| Mudanca impacta prazo > 50% | CEO + reuniao especial |
| Emergencia de seguranca | CEO imediato |

### 7.2 Processo de Escalacao

1. Documentar divergencia
2. Apresentar argumentos de ambos lados
3. CEO decide final
4. Registrar decisao e razoes

---

## 8. EXCECOES

### 8.1 Mudancas que NAO precisam de CR

- Correcao de typo em documentacao
- Ajuste de formatacao (black/prettier)
- Atualizacao de comentarios
- Mudanca em arquivos de teste apenas

### 8.2 Mudancas que SEMPRE precisam de CR

- Qualquer alteracao em escopo
- Qualquer nova dependencia
- Qualquer mudanca em API publica
- Qualquer mudanca em arquitetura

---

## 9. METRICAS DE CONTROLE

| Metrica | Meta | Alerta |
|---------|------|--------|
| CRs por semana | < 3 | > 5 |
| Tempo medio de decisao | < 24h | > 48h |
| Taxa de aprovacao | 60-80% | < 50% ou > 90% |
| CRs rejeitados por escopo | < 20% | > 40% |

---

## 10. CHECKLIST DE IMPLEMENTACAO

Apos aprovacao de CR:

- [ ] WBS atualizado (docs/03_WBS.md)
- [ ] Timeline atualizado (docs/06_TIMELINE.md)
- [ ] Riscos revisados (docs/05_RISK_REGISTER.md)
- [ ] Charter atualizado se necessario
- [ ] PMS atualizado (update_context.ps1)
- [ ] Comunicado a todos stakeholders

---

## 11. COMPROMISSO

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  EU, TECH LEAD, ME COMPROMETO A:                               │
│                                                                 │
│  1. Nao implementar NENHUMA mudanca sem CR aprovado            │
│  2. Documentar TODA solicitacao de mudanca                     │
│  3. Analisar impacto ANTES de propor                          │
│  4. Respeitar decisoes do CEO/Conselho                        │
│  5. Atualizar TODOS documentos apos aprovacao                  │
│                                                                 │
│  Data: 17-01-2026                                              │
│  Assinatura: TECH LEAD                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**Versao:** 1.0
**Status:** DRAFT - AGUARDANDO APROVACAO
**Criado por:** TECH LEAD
**Data:** 17-01-2026
**Criticidade:** ALTA - Resolve Risco R02

