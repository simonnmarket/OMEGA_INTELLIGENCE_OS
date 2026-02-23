# 📊 DIFERENÇAS: SILVER V3.0 vs SILVER QUANTUM V6.0

**Data:** 29 de Novembro de 2025

---

## 🔄 COMPARAÇÃO GERAL

| Característica | V3.0 Escalonado | V6.0 Quantum |
|----------------|----------------|--------------|
| **Magic Number** | 99992 | 20251129 |
| **Estratégia Base** | MA Crossover Multi-Timeframe | MA Crossover + ATR-Risk |
| **Cálculo de SL** | Fixo (30 pips) | Dinâmico (ATR * 2.3) |
| **Cálculo de Volume** | Escalonado fixo (0.10 - 50.00) | Baseado em risco % equity |
| **Biblioteca Técnica** | NumPy manual | TA-Lib |
| **Gestão de Risco** | Filtros múltiplos | Risco % por trade + total |
| **Break-Even** | Fixo (20 pips) | Dinâmico (1 ATR) |
| **Trailing Stop** | Fixo (15 pips) | Dinâmico (1 ATR) |
| **Fechamento** | TPs parciais | Fecha tudo se tendência reverter |

---

## 🎯 ESTRATÉGIA V3.0

### **Sinal de Entrada:**
- MA20 > MA50 em D1, H4, H1
- 10 filtros de validação
- Execução no M1

### **Gestão de Risco:**
- SL: 30 pips (fixo)
- TP: 60 pips (fixo)
- TPs Parciais: 20/35/50 pips
- Volume: 0.10 - 50.00 (escalonado)

### **Características:**
- ✅ Múltiplas entradas escalonadas
- ✅ TPs parciais (25% cada)
- ✅ Filtros rigorosos
- ⚠️ SL/TP fixos (não adapta à volatilidade)

---

## 🚀 ESTRATÉGIA V6.0

### **Sinal de Entrada:**
- MA20 > MA50 em D1, H4, H1
- **+ Inclinação positiva da SMA50**
- **+ Preço acima das duas MAs**

### **Gestão de Risco:**
- **SL: ATR * 2.3** (dinâmico)
- **Volume: Baseado em 1% do equity**
- **Risco Total: Máximo 20% do equity**
- **BE: 1 ATR de lucro**
- **Trailing: 1 ATR de distância**

### **Características:**
- ✅ SL/TP adaptativos (ATR)
- ✅ Volume baseado em risco real
- ✅ Limite de risco total (20%)
- ✅ Fecha tudo se tendência reverter
- ✅ Usa TA-Lib (cálculos precisos)

---

## 📊 PRINCIPAIS DIFERENÇAS

### **1. Cálculo de Stop Loss**

**V3.0:**
```python
sl_price = entry_price - (30 * pip_value)  # Fixo
```

**V6.0:**
```python
atr = get_atr_h4(symbol, 14)
sl_price = tick.bid - (atr * 2.3)  # Dinâmico
```

### **2. Cálculo de Volume**

**V3.0:**
```python
volume = 0.10 + (num_entradas * 0.10)  # Escalonado fixo
```

**V6.0:**
```python
risk_money = equity * 0.01  # 1% do equity
lots = risk_money / loss_per_lot  # Baseado em risco
```

### **3. Break-Even**

**V3.0:**
```python
if profit >= 20 pips:
    move_sl_to_entry + 5 points
```

**V6.0:**
```python
if profit >= (atr * 1.0):  # 1 ATR
    move_sl_to_entry + 2 ticks
```

### **4. Trailing Stop**

**V3.0:**
```python
trail_distance = 15 pips  # Fixo
```

**V6.0:**
```python
trail_distance = atr * 1.0  # Dinâmico
trail_start = atr * 1.5  # Só começa após 1.5 ATR
```

### **5. Filtro de Tendência**

**V3.0:**
- MA20 > MA50 em D1, H4, H1

**V6.0:**
- MA20 > MA50 em D1, H4, H1
- **+ SMA50 subindo (inclinação positiva)**
- **+ Preço acima de MA20 e MA50**

### **6. Fechamento de Posições**

**V3.0:**
- TPs parciais (25% cada)
- Mantém posições até TP final

**V6.0:**
- **Fecha TODAS as posições se tendência reverter**
- Não usa TPs parciais

---

## 🎓 VANTAGENS DE CADA VERSÃO

### **V3.0 Escalonado:**
- ✅ Múltiplas entradas escalonadas
- ✅ TPs parciais (protege lucros)
- ✅ Filtros muito rigorosos
- ✅ Ideal para tendências grandes (500-1600 pontos)

### **V6.0 Quantum:**
- ✅ SL/TP adaptativos (ATR)
- ✅ Volume baseado em risco real
- ✅ Limite de risco total (20%)
- ✅ Fecha tudo se tendência reverter (proteção)
- ✅ Ideal para mercados voláteis

---

## 🔧 DEPENDÊNCIAS

### **V3.0:**
```bash
pip install MetaTrader5 numpy
```

### **V6.0:**
```bash
pip install MetaTrader5 pandas talib
```

**NOTA:** TA-Lib pode precisar de binários do Windows:
- Baixar de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

---

## 📋 QUANDO USAR CADA VERSÃO

### **Use V3.0 se:**
- Quer múltiplas entradas escalonadas
- Quer TPs parciais (protege lucros gradualmente)
- Prefere SL/TP fixos (mais previsível)
- Quer capturar tendências muito grandes

### **Use V6.0 se:**
- Quer SL/TP adaptativos (ATR)
- Quer volume baseado em risco real
- Quer limite de risco total (20%)
- Quer fechar tudo se tendência reverter
- Prefere cálculos técnicos precisos (TA-Lib)

---

## ⚠️ IMPORTANTE

- **Magic Numbers diferentes:** Não executar ambos simultaneamente
- **Estratégias diferentes:** Escolher uma versão por vez
- **Dependências diferentes:** V6.0 precisa de TA-Lib

---

**Escolha a versão que melhor se adapta ao seu perfil de risco e objetivos!**

