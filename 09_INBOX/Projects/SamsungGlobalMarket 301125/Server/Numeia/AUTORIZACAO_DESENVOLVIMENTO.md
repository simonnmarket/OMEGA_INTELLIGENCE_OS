# Autorização de Desenvolvimento - Numeia v2.0

**Data:** 2025-11-21  
**Status:** ✅ **ATIVO**  
**Autorização:** Desenvolvimento contínuo durante ausência do desenvolvedor

---

## 🔹 AUTORIZAÇÃO VIGENTE

**Autorizado a:**
- ✅ Aprovar e implementar novas integrações
- ✅ Desenvolver funcionalidades que mantêm a excelência do sistema
- ✅ Corrigir bugs e melhorar performance
- ✅ Adicionar documentação técnica

**CONDIÇÕES OBRIGATÓRIAS:**

### ✅ APROVAÇÃO AUTOMÁTICA (Cumpre TODOS os critérios)

1. **Mantém Excelência Institucional**
   - ✅ Padrão TIER-0
   - ✅ Conformidade com MetaQuotes MQL5 (quando aplicável)
   - ✅ Validação com Pydantic
   - ✅ Logging JSON estruturado
   - ✅ Métricas Prometheus

2. **Sem Degradação de Qualidade**
   - ✅ Nenhum placeholder ("TODO", "FIXME" sem implementação)
   - ✅ Nenhum código comentado ou desabilitado
   - ✅ Nenhuma simplificação que reduza funcionalidade
   - ✅ Mantém complexidade necessária (não simplifica artificialmente)

3. **Proteção de Protocolos**
   - ✅ Mantém todas as regras fundamentais (Rules & Memories)
   - ✅ Preserva arquitetura de memória quádrupla
   - ✅ Mantém circuit breaker e kill-switch
   - ✅ Preserva validações de risco

4. **Consistência Completa**
   - ✅ Nomenclatura PascalCase para módulos
   - ✅ Checksum SHA3-256 quando aplicável
   - ✅ ISO 8601 para timestamps
   - ✅ Documentação inline completa

---

## ❌ REJEIÇÃO AUTOMÁTICA (Qualquer violação)

### NÃO APROVAR se:

1. **Coloca Protocolos em Risco**
   - ❌ Remove validações de segurança
   - ❌ Desabilita circuit breaker
   - ❌ Remove checksums ou validações
   - ❌ Ignora limites de risco configurados

2. **Downgrade ao Sistema**
   - ❌ Remove funcionalidades existentes
   - ❌ Simplifica lógica complexa necessária
   - ❌ Substitui código robusto por versão simplificada
   - ❌ Remove tratamento de erros

3. **Placeholders ou Inconsistências**
   - ❌ Código com "TODO", "FIXME" sem implementação real
   - ❌ Funções vazias ou retornando valores fixos
   - ❌ Hardcoded values onde deveria ser configurável
   - ❌ Validações comentadas ou desabilitadas

4. **Não Mantém Excelência**
   - ❌ Código sem documentação
   - ❌ Sem tratamento de erros adequado
   - ❌ Sem logging estruturado
   - ❌ Sem validação Pydantic (quando aplicável)

---

## 🔹 CRITÉRIOS DE QUALIDADE OBRIGATÓRIOS

### 1. Código Python (Numeia v2.0)

✅ **OBRIGATÓRIO:**
- Type hints completos
- Docstrings em todas as funções/classes
- Validação Pydantic para configs
- Logging JSON estruturado
- Tratamento de exceções robusto
- Testes unitários quando aplicável

### 2. Estrutura de Arquivos

✅ **OBRIGATÓRIO:**
- Nomes em PascalCase para módulos
- Include guards em arquivos MQL5 (quando aplicável)
- Organização hierárquica respeitada
- Nenhum arquivo solto no root

### 3. Configuração

✅ **OBRIGATÓRIO:**
- Validação com Pydantic
- Campos obrigatórios documentados
- Valores padrão seguros
- Sem valores hardcoded

### 4. Monitoramento

✅ **OBRIGATÓRIO:**
- Métricas Prometheus
- Logging JSON para análise forense
- Health checks implementados
- Circuit breaker funcional

---

## 🔹 PROTOCOLOS QUE DEVEM SER PRESERVADOS

### 1. PROTOCOLO PROMETHEUS v3.0.0
- ✅ Arquitetura de memória quádrupla
- ✅ Axiomas fundamentais
- ✅ Meta-aprendizagem recursiva
- ✅ World Model e simulação

### 2. PROTOCOLO OMEGA (TIER-0)
- ✅ Blindagem institucional
- ✅ Checksums SHA3-256
- ✅ Fail-safe automático
- ✅ Logging ISO 8601

### 3. PROTOCOLO ASC-AQ
- ✅ Falsificação ativa
- ✅ Análise de regime obrigatória
- ✅ Concretude matemática (sem placeholders)
- ✅ Análise de sistema completo

### 4. MQL5 COMPATIBILITY
- ✅ 100% padrão MetaQuotes
- ✅ Nomenclatura conforme regras
- ✅ Sem variáveis globais desnecessárias
- ✅ Validação rigorosa

---

## 🔹 EXEMPLOS DE APROVAÇÃO/REJEIÇÃO

### ✅ APROVADO - Exemplo 1: Nova Função de Validação

```python
def validate_spread(symbol: str, max_spread_pips: float) -> bool:
    """
    Valida se o spread está dentro do limite aceitável.
    
    Args:
        symbol: Nome do símbolo (ex: 'EURUSD')
        max_spread_pips: Spread máximo aceitável em pips
        
    Returns:
        True se spread aceitável, False caso contrário
        
    Raises:
        ValueError: Se símbolo inválido
        ConnectionError: Se MT5 não conectado
    """
    if not symbol or not symbol.strip():
        raise ValueError(f"Symbol inválido: {symbol}")
    
    if not mt5.initialize():
        raise ConnectionError("MT5 não conectado")
    
    try:
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(json.dumps({"event": "symbol_not_found", "symbol": symbol}))
            return False
            
        spread = (tick.ask - tick.bid) / mt5.symbol_info(symbol).point
        is_valid = spread <= max_spread_pips
        
        logger.info(json.dumps({
            "event": "spread_validation",
            "symbol": symbol,
            "spread_pips": spread,
            "max_spread_pips": max_spread_pips,
            "valid": is_valid
        }))
        
        return is_valid
    except Exception as e:
        logger.error(json.dumps({"event": "spread_validation_error", "error": str(e)}))
        raise
```

**Por que é aprovado:**
- ✅ Type hints completos
- ✅ Docstring completa
- ✅ Tratamento de erros robusto
- ✅ Logging JSON estruturado
- ✅ Validações adequadas
- ✅ Sem placeholders

### ❌ REJEITADO - Exemplo 1: Código Simplificado com Placeholder

```python
def validate_spread(symbol: str, max_spread: float) -> bool:
    # TODO: Implementar validação real
    return True  # Placeholder
```

**Por que é rejeitado:**
- ❌ Placeholder sem implementação
- ❌ Sem validação real
- ❌ Retorna sempre True (perigoso)

### ❌ REJEITADO - Exemplo 2: Remoção de Validação

```python
def calculate_position_size(symbol: str, risk_pct: float) -> float:
    # Removida validação de risco para simplificar
    balance = mt5.account_info().balance
    return balance * risk_pct
```

**Por que é rejeitado:**
- ❌ Remove validações de segurança
- ❌ Sem limites de risco
- ❌ Pode causar overexposure

---

## 🔹 CHECKLIST OBRIGATÓRIO ANTES DE APROVAR

Antes de qualquer mudança, verificar:

- [ ] Mantém excelência institucional (TIER-0)
- [ ] Não degrada qualidade existente
- [ ] Preserva todos os protocolos
- [ ] Sem placeholders ou TODOs não implementados
- [ ] Código completo e funcional
- [ ] Documentação adequada
- [ ] Tratamento de erros robusto
- [ ] Logging estruturado (JSON)
- [ ] Validação Pydantic (quando aplicável)
- [ ] Testes quando necessário
- [ ] Nomenclatura consistente
- [ ] Sem hardcoded values perigosos

**Se TODAS as caixas estiverem marcadas:** ✅ **APROVAR**  
**Se QUALQUER caixa não estiver marcada:** ❌ **REJEITAR**

---

## 🔹 NOTAS IMPORTANTES

1. **Excellence is Non-Negotiable:**
   - Qualquer código adicionado deve manter ou elevar o padrão
   - Nunca simplificar se isso reduzir robustez

2. **Security First:**
   - Validações de risco são sagradas
   - Circuit breaker não pode ser desabilitado
   - Kill-switch deve sempre funcionar

3. **Consistency is Key:**
   - Mesmo padrão em todo o código
   - Mesma estrutura de logging
   - Mesma abordagem de validação

4. **No Shortcuts:**
   - Sem placeholders
   - Sem código temporário
   - Sem validações desabilitadas
   - Sem simplificações perigosas

---

**ASSINATURA:**  
Sistema de Autorização Automática - Numeia v2.0  
Timestamp: 2025-11-21T13:07:00+0100  
**Status:** ✅ OPERACIONAL

---

## 🔹 CONTATO EM CASO DE DÚVIDA

Se houver dúvida sobre aprovar ou rejeitar:
- ❌ **Em dúvida, REJEITAR**
- ✅ Apenas aprovar se 100% certo que cumpre TODOS os critérios
- ✅ Priorizar segurança e qualidade sobre velocidade

**Princípio:** "Better safe than sorry" - melhor rejeitar e esperar confirmação do que aprovar algo que pode comprometer o sistema.

