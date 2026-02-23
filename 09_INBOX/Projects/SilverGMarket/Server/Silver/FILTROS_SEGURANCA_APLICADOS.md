# 🛡️ FILTROS DE SEGURANÇA APLICADOS

**Data:** 28 de Novembro de 2025  
**Problema:** Sistema iniciando com saldo negativo (quase 100 negativo)  
**Solução:** Filtros rigorosos antes de abrir qualquer posição

---

## ❌ PROBLEMA IDENTIFICADO

### Situação:
- ❌ Sistema iniciando com quase **100 negativo**
- ❌ Entradas sem validação adequada
- ❌ Sem verificação de condições de mercado
- ❌ Sem bloqueio quando há perdas acumuladas

---

## ✅ FILTROS IMPLEMENTADOS

### 1. **BLOQUEIO POR PnL TOTAL** 🔴 CRÍTICO
```python
if pnl_total < -50.0:
    BLOQUEAR novas entradas
```
**Objetivo:** Se o sistema já está com -50 negativo, para de abrir novas posições.

---

### 2. **FILTRO DE SPREAD** 📊
```python
- Spread máximo: 50 pips (absoluto)
- Spread máximo: 0.5% do preço (percentual)
```
**Objetivo:** Não operar quando spread está muito alto (custo de entrada alto).

---

### 3. **FILTRO DE VOLATILIDADE (ATR)** 📈
```python
- ATR mínimo: 30% do spread (mercado muito calmo = não operar)
- ATR máximo: 300% do spread (mercado muito volátil = não operar)
```
**Objetivo:** Operar apenas em mercados com volatilidade adequada.

---

### 4. **FILTRO DE HORÁRIO** ⏰
```python
Evitar trading:
- 22:00 - 01:00 (baixa liquidez, rollover)
```
**Objetivo:** Não operar em horários de baixa liquidez.

---

### 5. **FILTRO DE DISTÂNCIA DA MA20** 📍
```python
- Mínimo: 5 pips da MA20 (evita entrada muito prematura)
- Máximo: 100 pips da MA20 (evita entrada muito tardia)
```
**Objetivo:** Entrar em momento adequado, nem muito cedo nem muito tarde.

---

### 6. **BLOQUEIO POR POSIÇÕES NEGATIVAS NO SÍMBOLO** 🚫
```python
Se PnL do símbolo < -20.0:
    Não abre mais posições neste símbolo
```
**Objetivo:** Se um símbolo já está dando prejuízo, para de abrir novas posições nele.

---

## 📋 VALIDAÇÕES EM ORDEM

### Antes de abrir qualquer posição:

1. ✅ **PnL Total < -50?** → BLOQUEAR
2. ✅ **Horário adequado?** → BLOQUEAR se não
3. ✅ **Spread aceitável?** → BLOQUEAR se não
4. ✅ **Volatilidade adequada?** → BLOQUEAR se não
5. ✅ **Distância da MA20 adequada?** → BLOQUEAR se não
6. ✅ **Símbolo já em negativo?** → BLOQUEAR se sim

**Só executa se TODAS passarem!**

---

## 🎯 CONFIGURAÇÕES

### Valores Configuráveis:
```python
'spread_max_pips': 50,              # Spread máximo em pips
'spread_max_percent': 0.5,          # Spread máximo em %
'atr_min_multiplier': 0.3,           # ATR mínimo (30% do spread)
'atr_max_multiplier': 3.0,          # ATR máximo (300% do spread)
'max_loss_before_block': -50.0,      # Bloquear se PnL < -50
'min_distance_from_ma_pips': 5,      # Mínimo 5 pips da MA20
'max_distance_from_ma_pips': 100,    # Máximo 100 pips da MA20
'avoid_trading_hours': [(22, 0), (0, 1)],  # Evitar 22:00-01:00
```

---

## 📊 LOGS DE BLOQUEIO

### Quando uma entrada é bloqueada:
```json
{
  "event": "trade_blocked_filter",
  "symbol": "XAGUSD",
  "reason": "PnL_TOTAL_NEGATIVO: -52.30 < -50.00",
  "pnl_total": -52.30
}
```

### Motivos possíveis:
- `PnL_TOTAL_NEGATIVO`: Sistema com perdas acumuladas
- `HORARIO_INADEQUADO`: Fora do horário de trading
- `SPREAD_ALTO_PIPS`: Spread muito alto
- `SPREAD_ALTO_PERCENT`: Spread muito alto em %
- `MERCADO_MUITO_CALMO`: ATR muito baixo
- `MERCADO_MUITO_VOLATIL`: ATR muito alto
- `MUITO_PERTO_MA20`: Entrada muito prematura
- `MUITO_LONGE_MA20`: Entrada muito tardia
- `POSICOES_NEGATIVAS_SYMBOL`: Símbolo já em negativo

---

## ✅ BENEFÍCIOS ESPERADOS

### 1. **Proteção de Capital** ✅
- Sistema para quando perdas acumulam
- Não continua abrindo posições em perda

### 2. **Melhor Qualidade de Entradas** ✅
- Só entra em condições adequadas
- Spread, volatilidade e timing validados

### 3. **Redução de Perdas Iniciais** ✅
- Não inicia com saldo negativo
- Filtros previnem entradas ruins

### 4. **Gestão de Risco por Símbolo** ✅
- Para de operar símbolo que está dando prejuízo
- Protege contra perdas concentradas

---

## ⚠️ IMPORTANTE

### O que mudou:
- ✅ Filtros rigorosos antes de abrir posição
- ✅ Bloqueio automático quando perdas acumulam
- ✅ Validação de spread, volatilidade e timing
- ✅ Proteção por símbolo

### O que NÃO mudou:
- ✅ Análise multi-timeframe (D1 + H4 + H1)
- ✅ Execução no M1
- ✅ Volume escalonado
- ✅ SL/TP (30/60 pips)

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Sistema já está protegido
2. ⏳ Monitorar se perdas iniciais diminuíram
3. ⏳ Ajustar valores se necessário
4. ⏳ Verificar se bloqueios estão funcionando

---

**Filtros de segurança ativos e operacionais!**

