# 📋 GUIA DE USO - TEMPLATE YAML DE PLANO DE AÇÃO

## 🎯 VANTAGENS DO FORMATO YAML

✅ **Fácil de editar** - Formato legível e estruturado  
✅ **Validação automática** - Estrutura validada pelo processador  
✅ **Processamento inteligente** - Atualização automática do sistema  
✅ **Versionamento** - Fácil de rastrear mudanças no Git  

---

## 📝 COMO USAR

### Passo 1: Copiar Template Base

```bash
cp TEMPLATE_PLANO_ACAO.yaml PLANO_[NOME]_[DATA].yaml
```

### Passo 2: Preencher Template

Edite o arquivo YAML com suas informações:

```yaml
metadata:
  document_id: "PLAN-AURORA-5.1-20251225"
  date: "2025-12-25"
  status: "DRAFT"
  responsible: "Seu_Nome"

objetivo:
  descricao: |
    [Sua descrição aqui]
  
modulos_afetados:
  lista:
    - id: "MOD-001"
      nome: "quantum_firewall"
      status_atual: "BACKLOG"
      acao_planejada: "Implementar validação CVA"
      prioridade: "ALTA"
```

### Passo 3: Processar Template

**Dry Run (apenas validar):**
```bash
python PROCESSAR_TEMPLATE_YAML.py PLANO_[NOME]_[DATA].yaml --dry-run
```

**Execução Real:**
```bash
python PROCESSAR_TEMPLATE_YAML.py PLANO_[NOME]_[DATA].yaml
```

**Executar fase específica:**
```bash
# Apenas registro de intenção
python PROCESSAR_TEMPLATE_YAML.py PLANO.yaml --fase intencao

# Apenas registro de conclusão
python PROCESSAR_TEMPLATE_YAML.py PLANO.yaml --fase conclusao

# Apenas tags de compliance
python PROCESSAR_TEMPLATE_YAML.py PLANO.yaml --fase compliance

# Tudo (padrão)
python PROCESSAR_TEMPLATE_YAML.py PLANO.yaml --fase tudo
```

---

## 📊 ESTRUTURA DO TEMPLATE

### Seções Principais

1. **metadata** - Informações do documento
2. **objetivo** - Objetivo e justificativa
3. **validacao_previa** - Validações obrigatórias
4. **modulos_afetados** - Lista de módulos a trabalhar
5. **validacao_transicoes** - Validação FSM
6. **registro_intencao** - Ações a registrar antes
7. **alteracoes** - Alterações planejadas
8. **testes** - Testes obrigatórios
9. **registro_conclusao** - Ações a registrar depois
10. **compliance** - Tags de compliance
11. **validacao_final** - Validações pós-execução
12. **resumo_executivo** - Estatísticas
13. **problemas** - Problemas encontrados
14. **aprovacao** - Assinaturas

---

## 🔍 EXEMPLO DE PREENCHIMENTO

### Módulo Único

```yaml
modulos_afetados:
  lista:
    - id: "MOD-001"
      nome: "quantum_firewall"
      status_atual: "BACKLOG"
      acao_planejada: "Implementar validação CVA"
      prioridade: "ALTA"
      arquivos_afetados:
        - "00-Governanca/quantum_firewall.py"
      tipo_alteracao: "CÓDIGO"
      compliance_tags:
        - "Basel III"

registro_intencao:
  - modulo_id: "MOD-001"
    action_desc: "Implementação de validação CVA"
    status_type: "active"
    actor: "AIC_Agent"
    regulatory_context:
      - "Basel III"
```

### Múltiplos Módulos

```yaml
modulos_afetados:
  lista:
    - id: "MOD-001"
      nome: "quantum_firewall"
      status_atual: "BACKLOG"
      acao_planejada: "Implementar validação CVA"
      prioridade: "ALTA"
    
    - id: "MOD-002"
      nome: "risk_engine"
      status_atual: "ACTIVE"
      acao_planejada: "Adicionar circuit breakers"
      prioridade: "ALTA"
```

---

## 🛡️ VALIDAÇÕES AUTOMÁTICAS

O processador valida automaticamente:

1. ✅ **Estrutura do template** - Campos obrigatórios presentes
2. ✅ **IDs de módulos** - Formato MOD-XXX válido
3. ✅ **Transições FSM** - Transições permitidas
4. ✅ **Pivot Protection** - Módulos INACTIVE bloqueados
5. ✅ **Existência de módulos** - Módulos existem no sistema

---

## 📈 O QUE O PROCESSADOR FAZ

### Ao Processar Template

1. **Valida pré-execução:**
   - Executa `PROTOCOLO_FONTE_VERDADE.py`
   - Verifica consistência do sistema

2. **Valida template:**
   - Verifica estrutura YAML
   - Valida campos obrigatórios
   - Valida IDs de módulos

3. **Valida transições:**
   - Verifica se transições FSM são válidas
   - Bloqueia transições não autorizadas

4. **Executa ações:**
   - Registra intenção (se especificado)
   - Registra conclusão (se especificado)
   - Adiciona tags de compliance (se especificado)

5. **Atualiza template:**
   - Marca ações como executadas
   - Adiciona timestamps
   - Registra resultados

6. **Gera relatório:**
   - Relatório JSON completo
   - Estatísticas de execução
   - Lista de erros (se houver)

---

## 📋 CHECKLIST DE QUALIDADE

Antes de processar, verifique:

- [ ] Template YAML válido (sem erros de sintaxe)
- [ ] Todos os campos obrigatórios preenchidos
- [ ] IDs de módulos corretos (MOD-XXX)
- [ ] Status atuais corretos
- [ ] Ações descritas claramente
- [ ] Transições FSM válidas
- [ ] Compliance tags corretas (se aplicável)

---

## 🚨 EM CASO DE ERRO

Se o processador retornar erro:

1. **Leia a mensagem de erro** cuidadosamente
2. **Corrija o template YAML** conforme indicado
3. **Valide sintaxe YAML** (use validador online se necessário)
4. **Re-execute validação** (dry-run)
5. **Só execute** quando validação passar

---

## 📚 ARQUIVOS RELACIONADOS

- **`TEMPLATE_PLANO_ACAO.yaml`** - Template base (vazio)
- **`EXEMPLO_TEMPLATE_PREENCHIDO.yaml`** - Exemplo completo
- **`PROCESSAR_TEMPLATE_YAML.py`** - Processador automático
- **`TEMPLATE_PLANO_ACAO_GOVERNANCA.md`** - Versão Markdown (alternativa)

---

## 💡 DICAS

1. **Use o exemplo** como referência (`EXEMPLO_TEMPLATE_PREENCHIDO.yaml`)
2. **Sempre faça dry-run primeiro** para validar
3. **Mantenha IDs consistentes** entre seções
4. **Use YAML válido** - respeite indentação (espaços, não tabs)
5. **Comente se necessário** - YAML suporta comentários com `#`

---

**Última atualização:** 2025-12-25  
**Versão:** 1.0

