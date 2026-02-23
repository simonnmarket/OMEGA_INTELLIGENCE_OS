# ⚡ INSTRUÇÕES RÁPIDAS - GO-LIVE DEMO NUMEIA v5.0

**Data:** 06-11-2025  
**Broker:** Hantec Markets MU (Demo)  
**Portfolio:** 80% SPX500 + 15% XAUUSD (Gold) + 5% CASH  
**Tempo Total:** 10 minutos

---

## 🚀 EXECUÇÃO EM 4 PASSOS SIMPLES

### PASSO 1: COMPILAR EA (2 minutos)

1. Abrir **MetaEditor** (F4 no MT5)
2. Navegar: `Experts` → `Numeia_v5_0_Passive_Portfolio_EA.mq5`
3. Apertar **F7** (Compile)
4. Verificar: **0 errors, 0 warnings** ✅
5. Fechar MetaEditor

---

### PASSO 2: ANEXAR EA AO GRÁFICO (2 minutos)

1. No MT5, abrir gráfico de **SPX500** (ou qualquer símbolo)
2. No **Navigator** (Ctrl+N), expandir "Expert Advisors"
3. Arrastar `Numeia_v5_0_Passive_Portfolio_EA` para o gráfico
4. Na janela de configuração:
   ```
   Symbol 1: SPX500
   Weight 1: 80
   Symbol 2: XAUUSD
   Weight 2: 15
   Cash: 5
   Rebalance Days: 90
   Max Drawdown: 30
   ```
5. Verificar: **AutoTrading está ON** (botão verde no MT5) ✅
6. Clicar **OK**
7. Ver no canto superior direito do gráfico: 😊 (EA ativo)

---

### PASSO 3: EXECUTAR CONTROLADOR PYTHON (2 minutos)

1. Abrir **PowerShell** ou **CMD**
2. Navegar para pasta:
   ```
   cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Core\Implementation
   ```
3. Executar:
   ```
   python Numeia_v5_0_Controller.py
   ```
4. Ver menu aparecer
5. Escolher opção **1** (Inicializar Portfolio)
6. Apertar Enter
7. Ver mensagem: "✅ Comando enviado ao EA"

---

### PASSO 4: VERIFICAR EXECUÇÃO (4 minutos)

1. **Voltar ao MT5**
2. Abrir **Toolbox** (Ctrl+T) → aba **Trade**
3. **AGUARDAR 30-60 segundos**
4. Verificar se apareceram 2 posições:
   - `SPX500` (tipo: BUY, volume: ~80% do saldo)
   - `XAUUSD` (tipo: BUY, volume: ~15% do saldo)

5. Abrir aba **Experts** no Toolbox
6. Ver logs:
   ```
   ✅ Portfolio inicializado com sucesso
   Comprando SPX500: X lotes
   ✅ Compra executada: SPX500
   Comprando XAUUSD: X lotes
   ✅ Compra executada: XAUUSD
   ```

---

## ✅ CONFIRMAÇÃO DE SUCESSO

**SE VOCÊ VIU:**
- ✅ 2 posições abertas (SPX500 + XAUUSD)
- ✅ Logs "Compra executada"
- ✅ EA com 😊 no gráfico

**ENTÃO:**
🎉 **GO-LIVE DEMO CONCLUÍDO COM SUCESSO!**

---

## 📊 PRÓXIMOS 7 DIAS (OBSERVAÇÃO)

**O QUE FAZER:**

**Diariamente (5 minutos):**
1. Abrir MT5
2. Ver posições (Toolbox → Trade)
3. Anotar:
   - Balance
   - Equity
   - Profit/Loss

**NÃO FAZER:**
- ❌ NÃO fechar posições manualmente
- ❌ NÃO ajustar pesos
- ❌ NÃO adicionar estratégias
- ❌ NÃO otimizar parâmetros

**APENAS:** Observar

---

## 🔄 DIA 7: TESTE DE REBALANCEAMENTO

**Ação:**
1. Executar `python Numeia_v5_0_Controller.py`
2. Escolher opção **2** (Forçar Rebalanceamento)
3. Observar ajustes no MT5
4. Confirmar pesos voltam a 80-15-5

---

## 🎯 DIA 14: DECISÃO GO/NO-GO

**Critérios:**
```
✅ EA funcionou sem crashes
✅ Posições mantidas corretamente
✅ Rebalanceamento funcionou
✅ Logs claros
✅ Python conecta OK

SE TODOS ✅ → GO para implementar em REAL
SE ALGUM ❌ → Corrigir bugs
```

---

## 🚨 TROUBLESHOOTING RÁPIDO

### ERRO: "Símbolo SPX500 não encontrado"

**Solução:**
1. Abrir MT5 → Market Watch (Ctrl+M)
2. Clicar direito → Symbols
3. Procurar: S&P 500, SP500, ou SPX
4. Anotar nome EXATO
5. Mudar no EA: `InpSymbol1 = "[nome exato]"`

### ERRO: "AutoTrading is disabled"

**Solução:**
1. Clicar no botão "AutoTrading" no MT5 (fica verde)
2. Tools → Options → Expert Advisors → Marcar "Allow automated trading"

### ERRO: Python não encontra pasta Common

**Solução:**
1. Verificar caminho: `%APPDATA%\MetaQuotes\Terminal\Common\Files`
2. Se diferente, ajustar no script Python

---

## 📝 APÓS GO-LIVE

**Reportar ao CEO:**
```
✅ Portfolio inicializado
Posições:
  - SPX500: X lotes, USD Y
  - XAUUSD: X lotes, USD Y
  - CASH: USD Y
Total: USD [saldo demo]
Status: Operacional
```

---

## ✅ CHECKLIST FINAL

```
[ ] MT5 conectado (Hantec Demo)
[ ] EA compilado (0 errors)
[ ] EA anexado ao gráfico
[ ] AutoTrading ON
[ ] Python controller executado
[ ] Comando INITIALIZE enviado
[ ] 2 posições abertas
[ ] Logs confirmam sucesso
```

---

**PRONTO PARA EXECUTAR AMANHÃ!** 🚀

---

*Numeia v5.0 - Hantec Edition*  
*"Executar e Monitorar. Não otimizar. Não interferir."*  
*Portfolio: 80% SPX500 + 15% Gold + 5% Cash*

