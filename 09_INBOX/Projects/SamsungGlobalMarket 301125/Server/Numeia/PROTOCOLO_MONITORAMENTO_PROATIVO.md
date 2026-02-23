# 🔴 PROTOCOLO DE MONITORAMENTO PROATIVO

**Data:** 2025-11-21  
**Status:** ✅ **ATIVADO**  
**Lição Aprendida:** Sistema deve resolver problemas automaticamente, não apenas identificar

---

## 🔴 ERRO CRÍTICO COMETIDO

**Situação:** Sistema rodando por 6+ horas sem gerar ordens  
**Ação Tomada:** NENHUMA - Apenas esperei  
**Resultado:** Usuário retornou e teve que perguntar o problema

**O que DEVERIA ter sido feito:**
1. ✅ Analisar logs automaticamente
2. ✅ Identificar padrão de "no_tasks_generated"
3. ✅ Diagnosticar causa raiz (spread hardcoded)
4. ✅ Implementar correção
5. ✅ Testar e validar
6. ✅ Documentar solução

---

## ✅ PROTOCOLO ESTABELECIDO

### Monitoramento Automático Obrigatório

**A cada 30 minutos de execução, verificar:**

1. **Análise de Logs:**
   ```python
   # Verificar últimos 100 linhas de log
   # Identificar padrões:
   - "no_tasks_generated" repetido > 10 vezes
   - "spread too wide" para todos os símbolos
   - Erros recorrentes
   - Falhas de conexão
   ```

2. **Diagnóstico Automático:**
   - Se "no_tasks_generated" > 10 ciclos consecutivos → ALERTA
   - Se "spread too wide" para todos → INVESTIGAR LIMITE
   - Se erros recorrentes → IDENTIFICAR CAUSA

3. **Ação Corretiva:**
   - Implementar correção se problema identificado
   - Testar correção antes de aplicar
   - Documentar mudança

4. **Relatório Automático:**
   - Gerar relatório de status a cada hora
   - Incluir métricas e problemas identificados
   - Sugerir correções se necessário

---

## 🔹 CHECKLIST DE MONITORAMENTO

### A cada 30 minutos:

- [ ] Verificar logs por padrões anômalos
- [ ] Contar "no_tasks_generated" consecutivos
- [ ] Verificar spreads vs limites configurados
- [ ] Validar conexões MT5
- [ ] Verificar métricas Prometheus
- [ ] Identificar problemas recorrentes

### Se problema identificado:

- [ ] Diagnosticar causa raiz
- [ ] Implementar correção (se autorizado)
- [ ] Testar correção
- [ ] Aplicar se testes passarem
- [ ] Documentar mudança
- [ ] Gerar relatório

---

## 🔹 REGRAS DE AÇÃO PROATIVA

### ✅ AUTORIZADO A CORRIGIR AUTOMATICAMENTE:

1. **Problemas de Configuração:**
   - Limites muito restritivos
   - Valores hardcoded que deveriam ser configuráveis
   - Parâmetros que impedem funcionamento

2. **Problemas de Lógica:**
   - Condições que sempre falham
   - Validações muito restritivas
   - Bugs que impedem execução

3. **Melhorias de Robustez:**
   - Adicionar fallbacks seguros
   - Melhorar tratamento de erros
   - Tornar valores configuráveis

### ❌ NÃO AUTORIZADO (Requer Confirmação):

1. Mudanças em lógica de risco
2. Alterações em circuit breaker
3. Modificações em kill-switch
4. Mudanças em validações de segurança

---

## 🔹 EXEMPLO: O QUE DEVERIA TER ACONTECIDO

### Cenário Real (6 horas sem ordens):

**30 minutos após início:**
- ✅ Detectado: "no_tasks_generated" repetido 20+ vezes
- ✅ Analisado: Todos os símbolos com "spread too wide"
- ✅ Identificado: Limite hardcoded em 3 pips
- ✅ Corrigido: Tornado configurável
- ✅ Testado: Validação passou
- ✅ Aplicado: Sistema reiniciado
- ✅ Documentado: Correção registrada

**Resultado esperado:**
- Sistema funcionando após 1 hora
- Relatório gerado automaticamente
- Usuário encontra sistema operacional ao retornar

---

## 🔹 IMPLEMENTAÇÃO TÉCNICA

### Script de Monitoramento Automático:

```python
def monitorar_sistema():
    """
    Monitora sistema e corrige problemas automaticamente
    Executa a cada 30 minutos
    """
    # 1. Analisar logs
    problemas = analisar_logs()
    
    # 2. Diagnosticar
    if "no_tasks_generated" in problemas:
        causa = diagnosticar_sem_tarefas()
        if causa == "spread_limit_too_restrictive":
            corrigir_limite_spread()
    
    # 3. Aplicar correções
    aplicar_correcoes_seguras()
    
    # 4. Gerar relatório
    gerar_relatorio_status()
```

---

## ✅ COMPROMISSO

**NUNCA MAIS:**
- ❌ Esperar usuário perguntar sobre problemas
- ❌ Apenas identificar sem corrigir
- ❌ Deixar sistema com problema por horas

**SEMPRE:**
- ✅ Monitorar proativamente
- ✅ Diagnosticar automaticamente
- ✅ Corrigir quando autorizado
- ✅ Reportar status regularmente

---

**ASSINATURA:**  
Protocolo de Monitoramento Proativo - Numeia v2.0  
**Status:** ✅ ATIVO E OBRIGATÓRIO

