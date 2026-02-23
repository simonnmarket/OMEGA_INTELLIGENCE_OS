# 🥈 SILVER QUANTUM REAL V6.0

**Versão:** 6.0  
**Data:** 29 de Novembro de 2025  
**Status:** ✅ **IMPLEMENTADO**

---

## 🎯 OBJETIVO

Sistema de trading autônomo **especializado em prata (XAG)** com gestão de risco baseada em **ATR (Average True Range)** e sizing dinâmico baseado em **% do equity**.

---

## 📊 SÍMBOLOS OPERADOS

- **XAGUSD** (Prata/USD)
- **XAGAUD** (Prata/AUD)
- **XAGEUR** (Prata/EUR)
- **XAGGBP** (Prata/GBP)

---

## 🔑 CARACTERÍSTICAS DO SISTEMA

### **Configuração Específica**

- **Magic Number:** `20251129` (isolado)
- **Estratégia:** MA Crossover Multi-Timeframe + ATR-Risk
- **Biblioteca Técnica:** TA-Lib

### **Gestão de Risco (ATR-Based)**

- **Risco por Trade:** 1% do equity
- **Risco Total Máximo:** 20% do equity
- **Stop Loss:** ATR * 2.3 (dinâmico)
- **Break-Even:** 1 ATR de lucro
- **Trailing Stop:** 1 ATR de distância (inicia após 1.5 ATR)

### **Limites Operacionais**

- **Máximo de Posições:** 25 por símbolo
- **Máximo de Lotes:** 5.0 por símbolo
- **Intervalo Mínimo:** 5 minutos entre entradas

---

## 📈 ESTRATÉGIA

### **Sinal de Entrada (BUY)**

**Condições obrigatórias:**
1. **MA20 > MA50** em D1, H4, H1
2. **SMA50 subindo** (inclinação positiva)
3. **Preço acima** de MA20 e MA50

**Só entra se TODAS as condições forem atendidas!**

### **Gestão de Posições**

1. **Break-Even:** Move SL para entrada + 2 ticks quando lucro >= 1 ATR
2. **Trailing Stop:** Move SL seguindo preço (1 ATR de distância) após 1.5 ATR de lucro
3. **Reversão:** Fecha TODAS as posições se tendência reverter

---

## 🚀 COMO EXECUTAR

### **Método 1: PowerShell (Recomendado)**

```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
.\EXECUTAR_QUANTUM_V6.ps1
```

### **Método 2: Atalho Windows**

Duplo clique em: `EXECUTAR_QUANTUM_V6.bat`

### **Método 3: Direto**

```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
python silver_quantum_real_v6.0.py
```

---

## 📦 INSTALAÇÃO DE DEPENDÊNCIAS

### **Instalar Tudo:**

```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
.\INSTALAR_DEPENDENCIAS_V6.ps1
```

### **Ou Manualmente:**

```powershell
pip install MetaTrader5
pip install pandas
pip install TA-Lib
```

**⚠️ IMPORTANTE:** TA-Lib pode precisar de binários do Windows.  
Veja `INSTALAR_TA_LIB.md` para instruções detalhadas.

---

## 🔍 DIFERENÇAS vs V3.0

| Característica | V3.0 | V6.0 |
|----------------|------|------|
| **SL/TP** | Fixo (30/60 pips) | Dinâmico (ATR) |
| **Volume** | Escalonado fixo | Baseado em risco % |
| **Risco Total** | Sem limite | Máximo 20% equity |
| **Fechamento** | TPs parciais | Fecha tudo se reverter |
| **Biblioteca** | NumPy | TA-Lib |

**Veja `DIFERENCAS_V3_VS_V6.md` para comparação completa.**

---

## 📋 CHECKLIST ANTES DE EXECUTAR

- [ ] MetaTrader 5 está aberto e conectado
- [ ] Símbolos XAG estão no Market Watch
- [ ] TA-Lib está instalado (`python -c "import talib"`)
- [ ] Conta tem fundos suficientes
- [ ] Trading está habilitado na conta

---

## ⚙️ CONFIGURAÇÕES AVANÇÁVEIS

Edite as constantes no início do arquivo `silver_quantum_real_v6.0.py`:

```python
RISK_PER_TRADE = 0.01       # 1% do equity por trade
MAX_TOTAL_RISK = 0.20       # 20% do equity total
SL_ATR_MULT = 2.3           # Multiplicador do ATR para SL
BE_ATR_MULT = 1.0           # Multiplicador do ATR para BE
TRAIL_START_ATR_MULT = 1.5  # Multiplicador do ATR para iniciar trailing
TRAIL_STEP_ATR_MULT = 1.0    # Multiplicador do ATR para distância do trailing
MAX_POS_PER_SYMBOL = 25     # Máximo de posições por símbolo
MAX_LOT_PER_SYMBOL = 5.0    # Máximo de lotes por símbolo
```

---

## 🛡️ PROTEÇÕES

1. **Risco por Trade:** Máximo 1% do equity
2. **Risco Total:** Máximo 20% do equity
3. **Limite de Posições:** 25 por símbolo
4. **Limite de Lotes:** 5.0 por símbolo
5. **Intervalo Mínimo:** 5 minutos entre entradas
6. **Reversão:** Fecha tudo se tendência reverter

---

## 📝 LOGS

O sistema imprime no console:
- Entradas de posições
- Atualizações de SL (BE/Trailing)
- Fechamentos por reversão
- Erros e falhas

---

## ⚠️ IMPORTANTE

- **Magic Number:** `20251129` (não modificar)
- **Não executar simultaneamente** com V3.0 (Magic Numbers diferentes)
- **TA-Lib obrigatório** para funcionar
- **Fecha tudo** se tendência reverter (proteção)

---

**Sistema desenvolvido para operação especializada em Prata (XAG) com gestão de risco baseada em ATR**

