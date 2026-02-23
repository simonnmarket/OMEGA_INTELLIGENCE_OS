# PROTOCOLO DE PROTEÇÃO MARKDOWN - AURORA

**Data de Criação:** 2025-12-21  
**Versão:** 1.0  
**Status:** Ativo

---

## 🛡️ OBJETIVO

Prevenir erros de linting Markdown que causaram 613+ erros no documento técnico principal.

---

## 📋 ERROS IDENTIFICADOS E CORRIGIDOS

### Erros Encontrados (Total: 1226+)

1. **MD012**: Múltiplas linhas em branco consecutivas (276 erros)
2. **MD013**: Linhas muito longas (563 erros)
3. **MD022**: Blanks around headings (5 erros)
4. **MD025**: Múltiplos H1 no documento (5 erros)
5. **MD031**: Blanks around fenced code blocks (89 erros)
6. **MD032**: Blanks around lists (266 erros)
7. **MD040**: Fenced code languages ausentes (27 erros)

**Total corrigido:** 663+ erros principais

---

## 🔧 FERRAMENTAS DE PROTEÇÃO

### 1. `PROTECAO_MARKDOWN_LINT.py`
Sistema principal de validação e correção automática.

**Uso:**
```bash
# Validar arquivo específico
python PROTECAO_MARKDOWN_LINT.py arquivo.md

# Corrigir automaticamente todos os .md
python PROTECAO_MARKDOWN_LINT.py --fix

# Modo pré-commit (valida apenas arquivos modificados)
python PROTECAO_MARKDOWN_LINT.py --pre-commit
```

### 2. `VALIDAR_MARKDOWN_ANTES_SALVAR.py`
Validação interativa antes de salvar documentos.

**Uso:**
```bash
python VALIDAR_MARKDOWN_ANTES_SALVAR.py
```

---

## 📜 PROTOCOLO OBRIGATÓRIO

### ANTES DE SALVAR QUALQUER DOCUMENTO MARKDOWN:

1. **Executar validação:**
   ```bash
   python VALIDAR_MARKDOWN_ANTES_SALVAR.py
   ```

2. **Se houver erros:**
   - Revisar os erros reportados
   - Aplicar correções automáticas (se apropriado)
   - Verificar manualmente correções críticas

3. **Verificar conformidade:**
   - Apenas 1 H1 por documento (MD025)
   - Máximo 1 linha em branco consecutiva (MD012)
   - Blanks ao redor de headings, listas e blocos de código
   - Linguagem especificada em todos os blocos de código (MD040)

### REGRAS OBRIGATÓRIAS:

✅ **SEMPRE:**
- Usar apenas 1 H1 por documento (título principal)
- Usar H2+ para seções principais
- Especificar linguagem em blocos de código (```python, ```yaml, etc.)
- Adicionar linha em branco antes e depois de headings
- Adicionar linha em branco antes e depois de listas
- Adicionar linha em branco antes e depois de blocos de código
- Limitar linhas em branco consecutivas a 1

❌ **NUNCA:**
- Criar múltiplos H1 no mesmo documento
- Deixar blocos de código sem linguagem especificada
- Omitir blanks ao redor de elementos estruturais
- Usar múltiplas linhas em branco consecutivas

---

## 🔄 PROCESSO AUTOMÁTICO

### Integração com Git (Opcional)

Para validação automática antes de commits:

```bash
# Criar hook de pré-commit
python PROTECAO_MARKDOWN_LINT.py --setup-hook
```

---

## 📊 MONITORAMENTO

### Verificação Periódica

Executar semanalmente:
```bash
python PROTECAO_MARKDOWN_LINT.py --fix
```

### Relatório de Conformidade

O sistema gera automaticamente:
- Lista de erros encontrados
- Correções aplicadas
- Erros restantes (se houver)

---

## 🚨 AÇÃO EM CASO DE ERROS

1. **Erros detectados:**
   - Sistema cria backup automático (.md.auto_backup)
   - Aplica correções quando possível
   - Reporta erros que precisam de correção manual

2. **Erros críticos:**
   - MD025 (múltiplos H1): Correção automática aplicada
   - MD012 (múltiplas linhas em branco): Correção automática aplicada
   - MD040 (linguagem ausente): Correção automática com inferência

3. **Erros que podem precisar revisão manual:**
   - MD013 (linhas muito longas): Não corrigido automaticamente (pode quebrar formatação)
   - Alguns casos específicos de MD022, MD031, MD032

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de considerar um documento Markdown como "pronto":

- [ ] Apenas 1 H1 no documento
- [ ] Todos os blocos de código têm linguagem especificada
- [ ] Headings têm blanks antes e depois
- [ ] Listas têm blanks antes e depois
- [ ] Blocos de código têm blanks antes e depois
- [ ] Máximo 1 linha em branco consecutiva
- [ ] Validação executada sem erros críticos

---

## 📝 NOTAS IMPORTANTES

1. **Backups automáticos:** Sistema sempre cria backup antes de corrigir
2. **Inferência de linguagem:** Sistema tenta inferir linguagem do contexto
3. **Preservação de formatação:** Correções não alteram conteúdo, apenas formatação
4. **Compatibilidade:** Sistema funciona com padrões markdownlint

---

## 🔗 REFERÊNCIAS

- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- Padrões IEEE/IETF para documentação técnica

---

**Última Atualização:** 2025-12-21  
**Responsável:** Sistema de Proteção AURORA

