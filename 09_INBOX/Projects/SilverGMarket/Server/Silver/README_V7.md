# 🥈 SILVER QUANTUM REAL V7.0 – HÍBRIDO

**Versão:** 7.0 Híbrido  
**Data:** 29 de Novembro de 2025  
**Status:** ✅ **INTEGRAÇÃO COMPLETA V6.0 + V8.0**

---

## 🎯 OBJETIVO

Sistema de trading autônomo **híbrido** que combina:
- **Trend Following** (V6.0) - Seguir tendências fortes
- **Mean Reversion** (V8.0) - Comprar quando barato
- **Filtros Avançados** - Ambos os sistemas

---

## 🔑 CARACTERÍSTICAS INTEGRADAS

### **Do V6.0:**
- ✅ Gestão avançada (Break-Even + Trailing Stop)
- ✅ SL em pontos (300) - mais seguro
- ✅ Código completo e testado
- ✅ Filtro multi-timeframe (D1, H4, H1)

### **Do V8.0:**
- ✅ Filtro macro SMA200 H4 (mais conservador)
- ✅ Filtro de regime (evita BB Walk)
- ✅ Opção Mean Reversion (Bollinger Bands)
- ✅ Risco total 15% (mais conservador)

### **Melhorias:**
- ✅ Max posições: 8 (meio termo entre 25 e 3)
- ✅ Magic Number: 20251201 (novo)
- ✅ 3 modos de estratégia (TREND, MEAN_REVERSION, HYBRID)

---

## ⚙️ CONFIGURAÇÃO

### **Modos de Estratégia:**

```python
STRATEGY_MODE = "TREND"          # Apenas Trend Following (V6.0)
STRATEGY_MODE = "MEAN_REVERSION"  # Apenas Mean Reversion (V8.0)
STRATEGY_MODE = "HYBRID"          # Ambos devem confirmar (mais restritivo)
```

### **Parâmetros Principais:**

```python
SL_POINTS = 300                   # Stop Loss em pontos
MAX_POS_PER_SYMBOL = 8           # Máximo de posições por símbolo
MAX_TOTAL_RISK = 0.15            # 15% do equity (mais conservador)
RISK_PER_TRADE = 0.01            # 1% do equity por trade
```

---

## 📊 COMO FUNCIONA

### **Filtros Obrigatórios (Todos os Modos):**
1. **Filtro Macro H4:** Preço acima da SMA200 H4 e SMA200 subindo
2. **Intervalo Mínimo:** 5 minutos entre entradas
3. **Limite de Posições:** Máximo 8 por símbolo
4. **Risco Total:** Máximo 15% do equity

### **Modo TREND:**
- **Sinal:** MA20 > MA50 em D1, H4, H1 + inclinação positiva
- **TP:** Trailing Stop (sem TP fixo)
- **Filosofia:** Seguir tendência forte

### **Modo MEAN_REVERSION:**
- **Sinal:** Preço toca banda inferior BB + filtro de regime
- **TP:** Middle Band da BB
- **Filosofia:** Comprar quando barato (oversold)

### **Modo HYBRID:**
- **Sinal:** Ambos devem confirmar (mais restritivo)
- **TP:** Middle Band da BB (se Mean Reversion confirmar)
- **Filosofia:** Máxima segurança (dupla confirmação)

---

## 🚀 COMO EXECUTAR

### **Método 1: PowerShell**
```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
.\EXECUTAR_QUANTUM_V7.ps1
```

### **Método 2: Atalho Windows**
Duplo clique em: `EXECUTAR_QUANTUM_V7.bat`

### **Método 3: Direto**
```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
python silver_quantum_real_v7.0_hibrido.py
```

---

## 🎯 QUAL MODO USAR?

### **Use TREND se:**
- Mercado em tendência clara
- Quer capturar movimentos grandes
- Prefere gestão automática (trailing)

### **Use MEAN_REVERSION se:**
- Mercado lateral/range-bound
- Quer comprar quando barato
- Prefere TP fixo (middle band)

### **Use HYBRID se:**
- Quer máxima segurança
- Ambos os sinais devem confirmar
- Menos entradas, mas mais qualidade

---

## 📋 CHECKLIST ANTES DE EXECUTAR

- [ ] MetaTrader 5 está aberto e conectado
- [ ] Símbolos XAG estão no Market Watch
- [ ] TA-Lib está instalado
- [ ] Estratégia escolhida (TREND/MEAN_REVERSION/HYBRID)
- [ ] Conta tem fundos suficientes
- [ ] Trading está habilitado na conta

---

## 🛡️ PROTEÇÕES

1. **Filtro Macro:** SMA200 H4 (obrigatório)
2. **Risco por Trade:** Máximo 1% do equity
3. **Risco Total:** Máximo 15% do equity
4. **Limite de Posições:** 8 por símbolo
5. **Break-Even:** Automático (1 ATR)
6. **Trailing Stop:** Automático (1 ATR)
7. **Fechamento:** Automático se tendência macro reverter

---

## 📝 LOGS

O sistema imprime:
- Entradas de posições (com estratégia usada)
- Atualizações de SL (BE/Trailing)
- Fechamentos por reversão
- Erros e falhas

---

## ⚠️ IMPORTANTE

- **Magic Number:** `20251201` (não modificar)
- **Não executar simultaneamente** com V6.0 ou V8.0
- **TA-Lib obrigatório** para funcionar
- **Filtro Macro obrigatório** (SMA200 H4)

---

**Sistema híbrido desenvolvido integrando o melhor de V6.0 e V8.0**

