# 🚀 INSTRUÇÕES DE EXECUÇÃO - NUMEIA v5.0 (DEMO)

**Data:** 05-11-2025  
**Broker:** Hantec Markets MU  
**Conta:** Demo (USD 100,000)  
**Plataforma:** MetaTrader 5  
**Portfolio:** 80% ACWI + 15% AGG + 5% CASH  
**Executor:** CEO + ASC-AQ

---

## 📋 CHECKLIST PRÉ-EXECUÇÃO (5 MINUTOS)

### ✅ PASSO 1: Verificar MT5

**Ação:**
1. Abrir MetaTrader 5
2. Conectar à conta demo Hantec
3. Verificar saldo disponível
4. Confirmar símbolos no Market Watch:
   - `ACWI` (deve aparecer)
   - `AGG` (deve aparecer)

**Status:** [ ] CONCLUÍDO

---

### ✅ PASSO 2: Compilar e Anexar EA

**Ação:**
1. Abrir MetaEditor (F4 no MT5)
2. Abrir arquivo: `Numeia_v5_0_Passive_Portfolio_EA.mq5`
3. Compilar (F7)
4. Verificar: **0 errors, 0 warnings**
5. Voltar ao MT5
6. Arrastar EA para gráfico de ACWI
7. Configurar inputs:
   ```
   Symbol 1: ACWI
   Weight 1: 80%
   Symbol 2: AGG
   Weight 2: 15%
   Cash: 5%
   Rebalance Days: 90
   Max Drawdown: 30%
   ```
8. Clicar OK

**Status:** [ ] CONCLUÍDO

---

### ✅ PASSO 3: Executar Controlador Python

**Ação:**
1. Abrir terminal/PowerShell
2. Navegar para pasta:
   ```
   cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Core\Implementation
   ```
3. Executar:
   ```
   python Numeia_v5_0_Controller.py
   ```
4. Escolher opção **1** (Inicializar Portfolio)
5. Aguardar execução no MT5

**Status:** [ ] CONCLUÍDO

---

## 📊 EXECUÇÃO (GO-LIVE DEMO)

### PASSO 4: Inicialização do Portfolio

**O QUE VAI ACONTECER:**

1. **Python envia comando** → `NumeiaCommand.json`
2. **EA lê comando** → Processa INITIALIZE
3. **EA calcula valores:**
   ```
   Saldo Demo: USD 100,000
   ACWI Target: USD 80,000 (80%)
   AGG Target: USD 15,000 (15%)
   CASH: USD 5,000 (5%)
   ```
4. **EA executa ordens:**
   - BUY ACWI (valor USD 80k)
   - BUY AGG (valor USD 15k)
5. **Confirmação no terminal MT5**

**TEMPO:** 1-2 minutos

**VERIFICAÇÃO:**
- Abrir "Toolbox" → "Trade" no MT5
- Ver 2 posições abertas (ACWI, AGG)
- Verificar valores aproximados

---

### PASSO 5: Monitoramento Inicial (7 DIAS)

**OBJETIVO:** Validar que o sistema funciona como esperado

**AÇÕES:**

**Diariamente (5 minutos):**
1. Abrir MT5
2. Verificar posições ativas
3. Anotar:
   - Balance atual
   - Equity atual
   - Profit/Loss
   - Desvio de pesos

**Via Python (automático):**
1. Executar: `python Numeia_v5_0_Controller.py`
2. Opção **3** (Ver Status)
3. Revisar métricas

**ALERTAS:**
- ❌ Se Drawdown > 20%: Investigar causa
- ❌ Se EA parou: Reiniciar
- ❌ Se pesos desviaram > 10%: Rebalancear

---

### PASSO 6: Rebalanceamento Teste (DIA 7-14)

**OBJETIVO:** Testar mecânica de rebalanceamento

**AÇÃO:**
1. Executar controlador Python
2. Escolher opção **2** (Forçar Rebalanceamento)
3. Observar ajustes no MT5
4. Confirmar que pesos voltam a 80-15-5

**VERIFICAÇÃO:**
- Posições ajustadas?
- Valores corretos?
- Custos registrados?

---

## 📊 MÉTRICAS DE VALIDAÇÃO (7-14 DIAS)

### CRITÉRIOS DE SUCESSO:

| Critério | Target | Método de Verificação |
|----------|--------|----------------------|
| **Posições Abertas** | 2 (ACWI + AGG) | MT5 Toolbox → Trade |
| **Pesos Iniciais** | 80-15-5 | Calcular manualmente |
| **Rebalanceamento** | Funciona | Teste manual dia 7 |
| **EA Estável** | Sem crashes | Verificar logs MT5 |
| **Python Conecta** | SIM | Comando aceito |

### SE TUDO VALIDADO:

**DECISÃO GO/NO-GO PARA REAL:**

✅ **GO:** Se TODOS os critérios passaram
- Abrir conta real Hantec (ou IB)
- Depositar EUR 30,000
- Executar EXATAMENTE o mesmo setup
- Monitorar por 90 dias
- Primeiro rebalanceamento real

❌ **NO-GO:** Se QUALQUER critério falhou
- Investigar causa
- Corrigir bugs
- Re-testar em demo
- NÃO ir para real

---

## 🎯 TIMELINE COMPLETA

```
DIA 0 (HOJE - 05-NOV):
  ✅ CEO confirma broker (Hantec MU)
  ✅ ASC-AQ cria EA v5.0
  ✅ ASC-AQ cria Controller Python
  ✅ Instruções geradas

DIA 1 (06-NOV):
  [ ] CEO compila EA
  [ ] CEO anexa EA ao gráfico
  [ ] CEO executa Python controller
  [ ] Portfolio inicializado em DEMO
  🚀 GO-LIVE DEMO

DIA 2-7:
  [ ] Monitoramento diário (5 min/dia)
  [ ] Verificar estabilidade
  [ ] Anotar métricas

DIA 7-14:
  [ ] Teste de rebalanceamento
  [ ] Validação completa
  [ ] Decisão GO/NO-GO para REAL

DIA 15+ (SE APROVADO):
  [ ] Abrir conta REAL
  [ ] Depositar EUR 30k
  [ ] Replicar setup
  🚀 GO-LIVE REAL
```

---

## 🛠️ TROUBLESHOOTING

### PROBLEMA 1: EA não compila

**Solução:**
- Verificar se `#include <Trade\Trade.mqh>` está disponível
- Verificar versão MT5 (build > 3000)
- Ver erros no MetaEditor

### PROBLEMA 2: Python não encontra pasta Common

**Solução:**
- Verificar caminho: `%APPDATA%\MetaQuotes\Terminal\Common\Files`
- Ajustar manualmente no script

### PROBLEMA 3: Símbolos não encontrados

**Solução:**
- Verificar nomenclatura exata no Market Watch
- Adicionar símbolos manualmente
- Confirmar que Hantec oferece esses ETFs

### PROBLEMA 4: Ordens não executam

**Solução:**
- Verificar AutoTrading está habilitado (MT5)
- Verificar saldo demo suficiente
- Verificar logs do EA (Experts → log)

---

## 📝 PRÓXIMO RELATÓRIO

**Tipo:** Status Inicial Demo  
**Quando:** Após DIA 1 (primeira execução)  
**Formato:**
```
Portfolio Demo - Status Inicial
- ACWI: X shares, USD Y
- AGG: X shares, USD Y
- CASH: USD Y
- Total: USD 100,000
- Status: ✅ Operacional
```

---

## 🔐 ASSINATURA

**Criado por:** ASC-AQ  
**Data:** 05-11-2025 23:45 CET  
**Protocolo:** ASC-AQ v1.0.0  
**Status:** PRONTO PARA EXECUÇÃO DEMO

---

## 💬 PRÓXIMA AÇÃO (VOCÊ)

**AMANHÃ PELA MANHÃ (06-NOV):**

1. ⏰ Abrir MT5
2. 📝 Compilar EA v5.0
3. 📊 Anexar ao gráfico ACWI
4. 🐍 Executar Python controller
5. 🚀 Inicializar portfolio (opção 1)

**TEMPO TOTAL:** 15-20 minutos

**DEPOIS:** Observar por 7 dias

---

**TUDO PRONTO PARA TESTE EM DEMO!** ✅

**Amanhã começamos a validação.** 🚀

**Boa noite, CEO!** 😴

---

*Próxima ação: 06-NOV-2025 pela manhã*  
*GO-LIVE DEMO incoming...*  
*"Executar e Monitorar. Não otimizar. Não interferir."*

