# 🚀 GO LIVE - NUMEIA v6.0 TACTICAL - DEPLOY IMEDIATO

**Data:** 06-11-2025 14:20 CET  
**Comando CEO:** "Deploy AGORA"  
**Status:** INICIANDO DEPLOY  
**Filosofia:** "Capturar oportunidades HOJE, não amanhã"

---

## ⚡ SEQUÊNCIA DE DEPLOY (15 MINUTOS)

### PASSO 1: COMPILAR EA (3 MIN)

**CEO, EXECUTAR AGORA:**

1. Abrir **MetaEditor** (F4 no MT5)
2. Menu: **File → Open**
3. Navegar para:
   ```
   C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Experts\Numeia_v6_0_Tactical_EA.mq5
   ```
4. Pressionar **F7** (Compile)
5. **VERIFICAR:** Aba "Errors" deve mostrar:
   ```
   0 error(s), 0 warning(s)
   Succeeded
   ```

**SE HOUVER ERRO:** Reportar imediatamente, **NÃO CONTINUAR**.

**SE SUCESSO:** Prosseguir para Passo 2.

---

### PASSO 2: PREPARAR MT5 (2 MIN)

1. No MT5, abrir gráfico **XAUUSD M15** (ou qualquer símbolo)
2. Verificar que **AutoTrading** está **ATIVADO** (botão verde no topo)
   - Se estiver vermelho, clicar para ativar
3. Verificar conta: **DEMO Hantec**

---

### PASSO 3: ANEXAR EA (2 MIN)

1. No **Navigator** (Ctrl+N), expandir **Expert Advisors**
2. Arrastar **Numeia_v6_0_Tactical_EA** para o gráfico
3. Na janela de configuração, **MANTER PADRÕES**:
   ```
   InpCheckInterval = 60         ✅
   InpMaxPositions = 20          ✅
   InpRiskPerTrade = 2.0         ✅
   InpMinConfidence = 0.50       ✅
   InpMaxDrawdown = 25.0         ✅
   InpMaxDailyLoss = 5.0         ✅
   ```
4. Marcar: **Allow algo trading** ✅
5. Clicar **OK**

**VERIFICAR LOG MT5:**
```
========================================
NUMEIA v6.0 - TACTICAL WAR ROOM
AGRESSÃO TOTAL - TESTE DE MÚLTIPLAS ESTRATÉGIAS
========================================
Versão: 6.00
Magic Number: 60000
Risco por trade: 2.0%
Max posições: 20
Min confidence: 0.5
========================================
Balanço Inicial: $XXXXX
Arquivo de sinais: TacticalSignals.json
========================================

⏳ Aguardando sinais do servidor Python...
```

**SE APARECER ESTE LOG:** ✅ EA funcionando, prosseguir.

---

### PASSO 4: INICIAR SERVIDOR (5 MIN)

**CEO, EXECUTAR AGORA:**

1. Abrir **PowerShell** (como Administrador)
2. Executar:
   ```powershell
   cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
   .\venv\Scripts\Activate.ps1
   cd Server
   python Numeia_v6_0_Tactical_Server.py
   ```

**VERIFICAR LOGS:**
```
================================================================================
NUMEIA v6.0 - TACTICAL WAR ROOM SERVER
================================================================================
MT5 Path: C:\Users\Lenovo\AppData\Roaming\MetaQuotes\...
Signals File: TacticalSignals.json
================================================================================
✅ Momentum Scanner carregado
✅ Universo: 13 ativos
================================================================================

🚀 INICIANDO SERVIDOR TÁTICO NUMEIA v6.0
================================================================================
📡 Aguardando ciclo de scan...
   Intervalo: 300s (5.0 minutos)
================================================================================
```

**SE APARECER ESTE LOG:** ✅ Servidor funcionando.

**AGUARDAR 2 MINUTOS** para primeiro ciclo de scan...

---

### PASSO 5: VERIFICAR PRIMEIRO CICLO (3 MIN)

**NO POWERSHELL (Servidor), DEVE APARECER:**
```
================================================================================
🔍 CICLO DE SCAN #1
================================================================================
📊 Buscando dados de mercado...
   ✅ US500 (MT5): 180 dias
   ✅ XAUUSD (MT5): 180 dias
   ✅ EURUSD (MT5): 180 dias
   ... (outros ativos)

✅ Total: X símbolos com dados

🚀 Executando Momentum Scanner...
   ✅ Momentum Scanner: Y sinais

🔗 Consolidando sinais...
   ✅ Z sinais consolidados

✅ Sinais salvos: TacticalSignals.json
   Total: Z sinais

📋 RESUMO DE SINAIS:
   XAUUSD: BUY @ 4065.00 (conf: 0.85)
   US500: BUY @ 5000.00 (conf: 0.75)
   ... (top 5)
================================================================================
```

**NO MT5 (EA), APÓS ~60 SEGUNDOS, DEVE APARECER:**
```
========================================
📥 NOVOS SINAIS RECEBIDOS: Z
========================================

📊 SINAL #1/Z
   Symbol: XAUUSD
   Action: BUY
   Entry: 4065.00
   SL: 3943.05 | TP: 4390.20
   Confidence: 0.85
   Strategy: momentum
   Reason: Momentum 3M: 15.2%, 6M: 22.5%

✅ TRADE EXECUTADO
   Volume: 0.01
   SL: 3943.05 | TP: 4390.20
   Ticket: 123456789

... (outros sinais)
========================================
```

**VERIFICAR ABA "TRADE" DO MT5:**
- Devem aparecer posições abertas com comentário: `Numeia_v6.0`

---

## ✅ CRITÉRIOS DE SUCESSO (CHECKLIST)

Marcar conforme executa:

**SERVIDOR:**
- [ ] Servidor iniciou sem erros
- [ ] Conectou ao MT5 (ou usou yfinance fallback)
- [ ] Baixou dados dos ativos
- [ ] Gerou sinais do Momentum Scanner
- [ ] Salvou `TacticalSignals.json`

**EA:**
- [ ] EA compilou sem erros
- [ ] EA anexado ao gráfico
- [ ] Log mostra "Aguardando sinais..."
- [ ] EA leu arquivo de sinais (após ~60s)
- [ ] EA executou trades
- [ ] Posições aparecem na aba Trade

**OPERACIONAL:**
- [ ] SL e TP estão definidos
- [ ] Volume calculado está razoável
- [ ] Múltiplos símbolos foram tradados

---

## 🚨 TROUBLESHOOTING RÁPIDO

### PROBLEMA 1: Servidor não conecta ao MT5
**SINTOMA:** Logs mostram "MT5 não conectado - usando yfinance"

**SOLUÇÃO:** 
- Isso é **NORMAL** e está **OK**!
- Servidor usa yfinance como fallback
- Sistema funciona normalmente

### PROBLEMA 2: EA não lê sinais
**SINTOMA:** EA mostra "Aguardando sinais..." por > 5 minutos

**SOLUÇÃO:**
1. Verificar se arquivo existe:
   ```powershell
   Test-Path "$env:APPDATA\MetaQuotes\Terminal\Common\Files\TacticalSignals.json"
   ```
2. Se não existir, aguardar próximo ciclo do servidor (5 min)
3. Se existir mas EA não lê, aguardar próximo timer do EA (60s)

### PROBLEMA 3: Nenhum trade executado
**SINTOMA:** EA lê sinais mas não abre posições

**VERIFICAR:**
- Confidence dos sinais >= 0.50?
- Símbolos estão disponíveis no Market Watch?
- AutoTrading está ativado (botão verde)?
- Conta tem saldo suficiente?

---

## 📊 MONITORAMENTO CONTÍNUO

**DEIXAR RODANDO:**
- PowerShell com servidor (não fechar)
- MT5 com EA anexado (não remover)

**VERIFICAR A CADA 10 MINUTOS:**
- Logs do servidor (novos ciclos de scan)
- Logs do EA (novos sinais)
- Aba Trade do MT5 (posições abertas/fechadas)

**COMANDOS ÚTEIS:**
```powershell
# Ver últimos logs do servidor
Get-Content C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia_v6_0_Tactical.log -Wait -Tail 20

# Ver arquivo de sinais atual
Get-Content "$env:APPDATA\MetaQuotes\Terminal\Common\Files\TacticalSignals.json"
```

---

## 🎯 PRÓXIMOS PASSOS (APÓS DEPLOY)

**HOJE (Próximas 6 horas):**
1. Monitorar operações
2. Coletar dados de performance
3. Verificar se SL/TP estão funcionando

**AMANHÃ (07-NOV):**
1. Análise de performance do primeiro dia
2. Fix backtest (em paralelo)
3. Comparar paper trading vs backtest
4. Implementar estratégia #2 (Breakout Hunter)

**SEMANA 1 (06-12 NOV):**
1. Adicionar 3-5 estratégias táticas
2. Testar todas em paralelo
3. Descartar as que falharem
4. Manter as que funcionarem

---

## ✅ SISTEMA GO LIVE!

**TUDO PRONTO PARA DEPLOY!**

CEO, assim que executar os 5 passos acima, o sistema estará **OPERACIONAL**.

**Tempo estimado:** 15 minutos  
**Próximo checkpoint:** 30 minutos (verificar primeiro ciclo completo)

🚀 **VAMOS PARA O MERCADO!** 🚀

