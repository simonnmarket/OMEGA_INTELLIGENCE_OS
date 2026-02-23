# 📊 ALTERAÇÃO: STOP LOSS EM PONTOS

**Data:** 29 de Novembro de 2025  
**Versão:** 6.0 (Atualizada)

---

## ✅ MUDANÇA APLICADA

O sistema agora usa **Stop Loss em PONTOS** ao invés de ATR/pips.

### **Por quê?**

- ✅ **Mais seguro:** Controle preciso e direto
- ✅ **Mais fácil:** Ajuste simples de um número
- ✅ **Mais previsível:** Não depende da volatilidade (ATR)
- ✅ **Mais confiável:** Evita cálculos complexos

---

## 🔧 CONFIGURAÇÃO

### **Antes (ATR):**
```python
SL_ATR_MULT = 2.3  # SL = ATR * 2.3 (variável)
```

### **Agora (PONTOS):**
```python
SL_POINTS = 300    # SL = 300 pontos (fixo e controlável)
USE_ATR_SL = False # Usa pontos ao invés de ATR
```

---

## 📋 COMO FUNCIONA

### **Cálculo do SL:**
```python
sl_distance_price = SL_POINTS * tick_size
sl_price = tick.bid - sl_distance_price
```

### **Exemplo:**
- **SL_POINTS = 300**
- **tick_size = 0.001** (para XAGUSD)
- **SL em preço = 300 * 0.001 = 0.300**
- **Se preço de entrada = 53.455**
- **SL = 53.455 - 0.300 = 53.155**

---

## ⚙️ COMO ALTERAR O SL

### **Edite no início do arquivo:**
```python
SL_POINTS = 300  # Altere este valor
```

### **Exemplos:**
- **SL menor (mais apertado):** `SL_POINTS = 200`
- **SL médio:** `SL_POINTS = 300`
- **SL maior (mais largo):** `SL_POINTS = 500`

---

## 🔄 COMPARAÇÃO

| Método | Vantagem | Desvantagem |
|--------|----------|-------------|
| **ATR** | Adapta à volatilidade | Imprevisível, varia muito |
| **PONTOS** | Fixo, controlável | Não adapta à volatilidade |

**Escolhemos PONTOS porque é mais seguro e fácil de controlar!**

---

## 📊 IMPACTO NO CÁLCULO DE LOTE

O cálculo de lote também foi ajustado para usar pontos:

```python
def calcular_lote(self, symbol, sl_points):
    # Calcula lote baseado em SL em pontos
    sl_distance = sl_points * tick_size
    # ... resto do cálculo
```

---

## ⚠️ IMPORTANTE

- **USE_ATR_SL = False:** Sistema usa pontos (padrão)
- **USE_ATR_SL = True:** Sistema usa ATR (modo antigo)
- **SL_POINTS:** Valor em pontos (não pips!)

---

## 🎯 RECOMENDAÇÕES

### **Para XAG (Prata):**
- **SL conservador:** 200-300 pontos
- **SL médio:** 300-400 pontos
- **SL agressivo:** 400-500 pontos

### **Ajuste conforme:**
- Volatilidade do mercado
- Seu perfil de risco
- Resultados observados

---

**Sistema agora mais seguro e fácil de controlar!**

