# 🔴 RELATÓRIO: PROBLEMA "INVALID STOPS" - MT5

**Data:** 2025-12-20 23:01  
**Erro:** 10016 - Invalid stops  
**Status:** ❌ **CRÍTICO - BLOQUEANDO EXECUÇÃO DE ORDENS**

---

## 📊 ANÁLISE DO PROBLEMA

### Erros Observados:

**Tentativa 1 - BTCUSD:**
- Preço: 88217.55
- SL: 88215.55 (diferença: 2.00 = ~2 pontos)
- TP: 88221.55 (diferença: 4.00 = ~4 pontos)
- **Resultado:** ❌ Rejeitado - Invalid stops

**Tentativa 2 - ETHUSD:**
- Preço: 2978.867
- SL: 2978.667 (diferença: 0.2 = ~200 pontos se point=0.001)
- TP: 2979.267 (diferença: 0.4 = ~400 pontos se point=0.001)
- **Resultado:** ❌ Rejeitado - Invalid stops

---

## 🔍 CAUSA RAIZ

### Problema Identificado:

1. **Código não está usando `stops_level` corretamente**
   - O `stops_level` do símbolo não está sendo respeitado
   - Valores padrão (100/200 pontos) são muito pequenos para crypto
   - Crypto pode ter `stops_level` de 1000+ pontos

2. **Cálculo de distância está incorreto**
   - Para BTCUSD: point pode ser 0.01 ou 0.1
   - Para ETHUSD: point pode ser 0.001
   - Cálculo atual não considera o `point` corretamente

3. **Falta validação antes de enviar**
   - Não verifica se SL/TP respeitam `stops_level`
   - Não loga o `stops_level` real do símbolo

---

## 🎯 SOLUÇÃO DEFINITIVA

### Opção 1: REMOVER SL/TP TEMPORARIAMENTE (RÁPIDO)
- Enviar ordens SEM Stop Loss e Take Profit
- Adicionar SL/TP depois que ordem for executada
- **Vantagem:** Funciona imediatamente
- **Desvantagem:** Sem proteção inicial

### Opção 2: CALCULAR CORRETAMENTE (RECOMENDADO)
- Obter `stops_level` do símbolo
- Calcular SL/TP baseado em `stops_level * point`
- Validar antes de enviar
- **Vantagem:** Correto e seguro
- **Desvantagem:** Requer ajuste no código

### Opção 3: USAR VALORES FIXOS CONSERVADORES
- SL: 1% do preço
- TP: 2% do preço
- **Vantagem:** Simples
- **Desvantagem:** Pode ser muito largo para alguns símbolos

---

## 🚀 IMPLEMENTAÇÃO RECOMENDADA

**SOLUÇÃO HÍBRIDA:**
1. Obter `stops_level` do símbolo
2. Se `stops_level > 0`: usar `stops_level * 2` para SL, `stops_level * 3` para TP
3. Se `stops_level = 0`: usar 1% do preço para SL, 2% para TP
4. Validar distância mínima antes de enviar
5. Se não passar validação: enviar SEM SL/TP e adicionar depois

---

## 📋 CHECKLIST DE CORREÇÃO

- [ ] Obter `stops_level` do símbolo corretamente
- [ ] Calcular SL/TP baseado em `stops_level` e `point`
- [ ] Validar distância mínima antes de enviar
- [ ] Adicionar logs detalhados
- [ ] Fallback: enviar sem SL/TP se cálculo falhar
- [ ] Testar com BTCUSD e ETHUSD

---

## ⚡ AÇÃO IMEDIATA

**RECOMENDAÇÃO:** Implementar Opção 1 (remover SL/TP temporariamente) para desbloquear execução, depois implementar Opção 2 (cálculo correto).

**TEMPO ESTIMADO:** 5 minutos para Opção 1, 15 minutos para Opção 2 completa.

---

**Status:** 🔴 **AGUARDANDO DECISÃO PARA IMPLEMENTAÇÃO**

