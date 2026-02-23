# RELATÓRIO MOMENTUM STRATEGY ANALYSIS
## DIRETIVA F2-T2-PARALLEL (TRILHA B): ESTRATÉGIA #2

**Data do Relatório:** 04-11-2025 00:01 CET  
**Período Testado:** 2018-01-01 a 2023-12-31 (6 anos)  
**Capital Inicial:** EUR 30,000.00  
**Estratégia:** Crypto Momentum (Jegadeesh & Titman 1993)

---

## 📊 RESULTADOS FINANCEIROS

### Performance Geral
```
Capital Inicial:      EUR    30,000.00
Capital Final:        EUR   118,493.80
P&L Líquido:          EUR    88,493.80
Retorno Total:                 294.98%
Retorno Anualizado:             25.75%
```

### Métricas de Trading
```
Total de Trades:                  100
Trades Vencedores:                 39
Trades Perdedores:                 61
Win Rate:                       39.00%
Average Win:          EUR      2837.21
Average Loss:         EUR       359.08
```

### Métricas de Risco
```
Sharpe Ratio:                    0.36
Máximo Drawdown:                19.25%
Profit Factor:                   5.05
```

---

## 📈 ANÁLISE DE REGIME (ANO A ANO)


### 2018
```
Trades: 10
Wins/Losses: 1/9
Win Rate: 10.00%
P&L: EUR -2,810.61
```

### 2019
```
Trades: 9
Wins/Losses: 6/3
Win Rate: 66.67%
P&L: EUR 12,333.17
```

### 2020
```
Trades: 21
Wins/Losses: 6/15
Win Rate: 28.57%
P&L: EUR -2,468.11
```

### 2021
```
Trades: 17
Wins/Losses: 12/5
Win Rate: 70.59%
P&L: EUR 86,494.00
```

### 2022
```
Trades: 19
Wins/Losses: 4/15
Win Rate: 21.05%
P&L: EUR -2,848.49
```

### 2023
```
Trades: 24
Wins/Losses: 10/14
Win Rate: 41.67%
P&L: EUR -1,952.81
```


---

## 🔬 TESTE DE HIPÓTESE ESTATÍSTICA

### Teste Binomial
```
Sample Size (n):           100
Trades Vencedores (k):     39
Win Rate Observado:        39.00%
p-value:                   0.989511
Intervalo Confiança 95%:   [30.00%, 49.00%]
```

### Conclusão Estatística
**A estratégia NÃO mostra um edge estatisticamente significativo (p >= 0.05)**

---

## 🎯 LÓGICA DA ESTRATÉGIA

### Entry (BUY)
- Retorno 3M > 10%
- AND Volume > MA 20 dias
- = Tendência forte confirmada

### Exit (SELL)
- Retorno 3M < 0%
- = Momentum acabou

### Diferença vs Mean Reversion
- **Mean Reversion:** Compra quedas, vende recuperações
- **Momentum:** Compra tendências, vende quando acabam
- **Perfis OPOSTOS:** Hedge natural

---

**Assinatura:**  
Agente IA Cursor (AIC)  
Data: 04-11-2025 00:01 CET  
Status: Trilha B - Momentum Analysis Completa
