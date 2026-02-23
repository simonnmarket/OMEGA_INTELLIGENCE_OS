# 📋 GUIA DE USO - TEMPLATE DE PLANO DE AÇÃO

## 🎯 OBJETIVO

O template de plano de ação permite planejar e executar atualizações no sistema Aurora de forma segura, controlada e rastreável, seguindo o protocolo de governança institucional.

---

## 📝 COMO USAR

### Passo 1: Criar Novo Plano

1. Copie o template:
   ```bash
   cp TEMPLATE_PLANO_ACAO_GOVERNANCA.md PLANO_[NOME]_[DATA].md
   ```

2. Preencha todas as seções do template:
   - Objetivo do plano
   - Módulos afetados
   - Ações planejadas
   - Checklist completo

### Passo 2: Validar Template

Antes de enviar, verifique:
- [ ] Todos os campos obrigatórios preenchidos
- [ ] IDs dos módulos corretos (MOD-XXX)
- [ ] Transições FSM válidas
- [ ] Checklist completo

### Passo 3: Processar Template

**Opção 1: Processamento Automático (Recomendado)**

```bash
# Dry run (apenas validar, não executar)
python PROCESSAR_TEMPLATE_PLANO_ACAO.py PLANO_[NOME]_[DATA].md --dry-run

# Execução real
python PROCESSAR_TEMPLATE_PLANO_ACAO.py PLANO_[NOME]_[DATA].md
```

**Opção 2: Processamento Manual**

Envie o template preenchido para o agente IA, que irá:
1. Validar contra sistema de governança
2. Verificar transições FSM
3. Executar ações de forma segura
4. Registrar no audit trail
5. Gerar relatório de execução

---

## 🔍 O QUE O PROCESSADOR FAZ

### Validações Automáticas

1. **Validação Pré-Execução:**
   - Executa `PROTOCOLO_FONTE_VERDADE.py`
   - Verifica consistência do sistema
   - Valida estado atual

2. **Validação de Transições:**
   - Verifica se todas as transições FSM são válidas
   - Valida Pivot Protection
   - Bloqueia transições não autorizadas

3. **Validação Pós-Execução:**
   - Verifica se ações foram executadas corretamente
   - Valida consistência final
   - Gera relatório

### Ações Executadas

1. **Registro de Intenção:**
   - Para cada módulo, registra intenção no audit trail
   - Atualiza status para ACTIVE
   - Documenta ação planejada

2. **Registro de Conclusão:**
   - Após validação, registra conclusão
   - Atualiza status para COMPLETED
   - Adiciona metadados de testes

3. **Tags de Compliance:**
   - Adiciona tags de compliance conforme especificado
   - Documenta frameworks aplicáveis

---

## 📊 ESTRUTURA DO TEMPLATE

### Seções Obrigatórias

1. **Objetivo do Plano** - Descrição clara do que será feito
2. **Contexto e Validação Prévia** - Status do sistema antes de iniciar
3. **Checklist de Ações** - Lista completa de ações a executar
4. **Resumo Executivo** - Estatísticas e resultados

### Seções Opcionais

- **Problemas e Resoluções** - Se houver problemas
- **Observações** - Notas adicionais
- **Aprovação** - Assinaturas e aprovações

---

## 🛡️ PROTEÇÕES AUTOMÁTICAS

### Pivot Protection

- Módulos INACTIVE não podem ser modificados sem reativação explícita
- Processador valida e bloqueia automaticamente

### FSM Validation

- Todas as transições são validadas antes de execução
- Transições não autorizadas são bloqueadas

### Audit Trail

- Todas as ações são registradas automaticamente
- Rastreabilidade completa garantida

---

## 📋 EXEMPLO DE USO

### Exemplo 1: Atualizar Módulo Único

```markdown
## 📝 CHECKLIST DE AÇÕES

### FASE 2: EXECUÇÃO

#### 2.1 Registro de Intenção

- [x] **MOD-001:** Intenção registrada
  ```python
  orchestrator.log_event(
      mod_id="MOD-001",
      action_desc="Implementação de validação CVA",
      status_type="active",
      actor="AIC_Agent"
  )
  ```
```

### Exemplo 2: Múltiplos Módulos

```markdown
| ID | Nome do Módulo | Status Atual | Ação Planejada | Prioridade |
|----|----------------|--------------|----------------|------------|
| MOD-001 | quantum_firewall | ACTIVE | Adicionar validação CVA | ALTA |
| MOD-002 | risk_engine | ACTIVE | Implementar circuit breakers | ALTA |
```

---

## ✅ CHECKLIST DE QUALIDADE

Antes de enviar template, verifique:

- [ ] Objetivo claramente definido
- [ ] Módulos identificados corretamente (IDs válidos)
- [ ] Transições FSM validadas
- [ ] Checklist completo
- [ ] Testes planejados
- [ ] Compliance considerado (se aplicável)
- [ ] Validação prévia executada
- [ ] Validação final planejada

---

## 🚨 EM CASO DE ERRO

Se o processador retornar erro:

1. **Leia a mensagem de erro** cuidadosamente
2. **Corrija o template** conforme indicado
3. **Re-execute validação** (dry-run)
4. **Só execute** quando validação passar

---

## 📚 REFERÊNCIAS

- [📄 TEMPLATE_PLANO_ACAO_GOVERNANCA.md](TEMPLATE_PLANO_ACAO_GOVERNANCA.md) - Template base
- [📄 PROCESSAR_TEMPLATE_PLANO_ACAO.py](PROCESSAR_TEMPLATE_PLANO_ACAO.py) - Processador automático
- [📄 PROTOCOLO_GOVERNANCA_VISUAL.md](PROTOCOLO_GOVERNANCA_VISUAL.md) - Protocolo de governança
- [📄 PROTOCOLO_ANTI_ERRO.md](PROTOCOLO_ANTI_ERRO.md) - Protocolo anti-erro

---

**Última atualização:** 2025-12-25  
**Versão:** 1.0

