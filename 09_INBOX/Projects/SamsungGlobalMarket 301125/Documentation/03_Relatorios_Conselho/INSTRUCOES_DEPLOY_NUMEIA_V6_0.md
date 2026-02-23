# 🚀 INSTRUÇÕES DE DEPLOY - NUMEIA v6.0 TACTICAL WAR ROOM

**Data:** 06-11-2025 14:00 CET  
**Versão:** 6.00 COMPLETA  
**Status:** PRONTO PARA DEPLOY  
**Filosofia:** "Agressão ao Mercado - Testar TUDO"

---

## ✅ ARQUIVOS CRIADOS (COMPLETOS)

```
SamsungGlobalMarket/
├─ Experts/
│  └─ Numeia_v6_0_Tactical_EA.mq5        [NOVO - EA COMPLETO]
│
├─ Server/
│  └─ Numeia_v6_0_Tactical_Server.py     [NOVO - SERVIDOR COMPLETO]
│
└─ Core/Strategies/Tactical/
   └─ MomentumScanner_Aggressive.py      [CRIADO ANTERIORMENTE]
```

---

## 📋 FASE 1: COMPILAR EA (5 MINUTOS)

### PASSO 1: Abrir MetaEditor

1. No MT5, pressione `F4` (abre MetaEditor)
2. No MetaEditor, menu **File → Open**
3. Navegar até: `C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Experts\`
4. Abrir: `Numeia_v6_0_Tactical_EA.mq5`

### PASSO 2: Compilar

1. Pressionar `F7` (Compile)
2. **VERIFICAR:** Aba "Errors" deve mostrar:
   ```
   0 error(s), 0 warning(s)
   Succeeded
   ```
3. Se houver erros, **PARAR** e reportar

### PASSO 3: Verificar Arquivo Compilado

1. Arquivo compilado deve estar em:
   ```
   C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\<ID>\MQL5\Experts\Numeia_v6_0_Tactical_EA.ex5
   ```

---

## 📋 FASE 2: PREPARAR SERVIDOR PYTHON (10 MINUTOS)

### PASSO 1: Instalar Dependências

Abrir PowerShell e executar:

```powershell
# Ativar ambiente virtual
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\venv\Scripts\Activate.ps1

# Instalar MetaTrader5 Python (se ainda não instalado)
pip install MetaTrader5

# Verificar instalação
python -c "import MetaTrader5 as mt5; print('MT5 OK' if mt5.initialize() else 'MT5 ERRO'); mt5.shutdown()"
```

**Resultado esperado:** `MT5 OK`

### PASSO 2: Testar Servidor (Teste Rápido)

```powershell
# No mesmo PowerShell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server

# Executar servidor (Ctrl+C para parar após 30s)
python Numeia_v6_0_Tactical_Server.py
```

**Verificar logs:**
- ✅ "NUMEIA v6.0 - TACTICAL WAR ROOM SERVER"
- ✅ "Momentum Scanner carregado"
- ✅ "Universo: X ativos"
- ✅ "Iniciando servidor tático"

Se aparecer tudo OK, pressionar `Ctrl+C` para parar.

---

## 📋 FASE 3: PRIMEIRO CICLO DE TESTE (30 MINUTOS)

### CONFIGURAÇÃO:

1. **MT5 aberto** (conta DEMO Hantec)
2. **Servidor parado** (iniciaremos juntos)
3. **EA anexado** (faremos agora)

### PASSO 1: Anexar EA no MT5

1. No MT5, abrir gráfico de **qualquer símbolo** (ex: XAUUSD, M15)
2. No Navigator (Ctrl+N), expandir **Expert Advisors**
3. Arrastar `Numeia_v6_0_Tactical_EA` para o gráfico
4. Na janela de configuração:
   ```
   InpCheckInterval = 60         (verifica sinais a cada 60s)
   InpMaxPositions = 20          (até 20 posições simultâneas)
   InpRiskPerTrade = 2.0         (2% risco por trade)
   InpMinConfidence = 0.50       (executar se confidence ≥ 50%)
   InpMaxDrawdown = 25.0         (kill-switch se DD > 25%)
   ```
5. Marcar: **Allow algo trading** ✅
6. Clicar **OK**

**VERIFICAR LOG DO MT5:**
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

### PASSO 2: Iniciar Servidor

No PowerShell (com venv ativado):

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server
python Numeia_v6_0_Tactical_Server.py
```

### PASSO 3: Acompanhar Primeiro Ciclo

**O que deve acontecer (próximos 5-10 minutos):**

1. **Servidor:**
   ```
   🔍 CICLO DE SCAN #1
   📊 Buscando dados de mercado...
      ✅ US500 (MT5): 180 dias
      ✅ XAUUSD (MT5): 180 dias
      ... (outros ativos)
   
   🚀 Executando Momentum Scanner...
      ✅ Momentum Scanner: 10 sinais
   
   🔗 Consolidando sinais...
      ✅ 10 sinais consolidados
   
   ✅ Sinais salvos: TacticalSignals.json
      Total: 10 sinais
   
   📋 RESUMO DE SINAIS:
      XAUUSD: BUY @ 4065.00 (conf: 0.85)
      US500: BUY @ 5000.00 (conf: 0.75)
      ... (top 5)
   ```

2. **EA (logs MT5 - verificar após 60s):**
   ```
   ========================================
   📥 NOVOS SINAIS RECEBIDOS: 10
   ========================================
   
   📊 SINAL #1/10
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
   ```

3. **Verificar Posições Abertas:**
   - No MT5, aba **Trade** (Ctrl+T)
   - Deve aparecer posições abertas com comentário: `Numeia_v6.0`

---

## 📋 FASE 4: VALIDAÇÃO (1 HORA)

### CHECKLIST DE VALIDAÇÃO:

**SERVIDOR:**
- [ ] Conectou ao MT5? (logs mostram "MT5 OK")
- [ ] Baixou dados dos ativos? (logs mostram quantidade de dias)
- [ ] Gerou sinais? (logs mostram "X sinais consolidados")
- [ ] Salvou TacticalSignals.json? (verificar em `%APPDATA%\MetaQuotes\Terminal\Common\Files\`)

**EA:**
- [ ] Leu arquivo de sinais? (logs mostram "NOVOS SINAIS RECEBIDOS")
- [ ] Processou sinais? (logs mostram detalhes de cada sinal)
- [ ] Executou trades? (logs mostram "TRADE EXECUTADO" com tickets)
- [ ] Posições aparecem na aba Trade? (verificar visualmente)

**FUNCIONALIDADES:**
- [ ] SL e TP foram definidos corretamente?
- [ ] Volume calculado está razoável (não muito grande/pequeno)?
- [ ] Múltiplos símbolos foram tradados?

---

## 📋 FASE 5: MONITORAMENTO CONTÍNUO

### COMANDOS ÚTEIS:

**Ver logs do servidor em tempo real:**
```powershell
Get-Content C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia_v6_0_Tactical.log -Wait -Tail 50
```

**Ver arquivo de sinais atual:**
```powershell
Get-Content "$env:APPDATA\MetaQuotes\Terminal\Common\Files\TacticalSignals.json" | ConvertFrom-Json | Format-List
```

**Parar servidor:**
```
Ctrl+C no PowerShell onde está rodando
```

**Remover EA do gráfico:**
```
Clicar com botão direito no nome do EA no gráfico → Delete
```

---

## 🚨 TROUBLESHOOTING

### PROBLEMA 1: EA não lê sinais

**SINTOMA:** EA mostra "Aguardando sinais..." mas servidor já gerou.

**SOLUÇÃO:**
1. Verificar se arquivo existe:
   ```powershell
   Test-Path "$env:APPDATA\MetaQuotes\Terminal\Common\Files\TacticalSignals.json"
   ```
2. Se não existir, verificar logs do servidor (pode ter erro ao salvar)
3. Se existir, aguardar até próximo timer (60s)

### PROBLEMA 2: Servidor não conecta ao MT5

**SINTOMA:** Logs mostram "MT5 não conectado - usando yfinance"

**SOLUÇÃO:**
1. Verificar se MT5 está aberto
2. Executar teste:
   ```python
   python -c "import MetaTrader5 as mt5; print(mt5.initialize()); mt5.shutdown()"
   ```
3. Se retornar `False`, fechar e reabrir MT5

### PROBLEMA 3: Nenhum trade executado

**SINTOMA:** EA lê sinais mas não executa trades.

**POSSÍVEIS CAUSAS:**
- Confidence < 0.50 (verificar nos logs: "IGNORADO: Confidence < 0.5")
- Limite de posições atingido (verificar: "LIMITE DE POSIÇÕES ATINGIDO")
- Símbolo não disponível (verificar: "Símbolo não disponível")
- Ordem rejeitada pelo broker (verificar logs de erro do trade)

---

## ✅ CRITÉRIOS DE SUCESSO

### SUCESSO TÉCNICO:
- ✅ EA e Servidor comunicam via arquivo JSON
- ✅ Múltiplos ativos são tradados
- ✅ SL/TP funcionam corretamente
- ✅ Gestão de risco por posição operacional

### SUCESSO OPERACIONAL (Avaliar após 24-48h):
- ✅ Sistema roda sem intervenção manual
- ✅ Sinais são gerados regularmente (a cada 5 min)
- ✅ Posições são abertas/fechadas automaticamente

### SUCESSO FINANCEIRO (Avaliar após 7 dias):
- 📊 Sharpe > 0.3?
- 📊 Win Rate > 50%?
- 📊 Max DD < 25%?

---

## 🎯 PRÓXIMOS PASSOS

**SE TUDO FUNCIONAR (HOJE):**
1. ✅ Deixar rodando por 24h
2. ✅ Monitorar logs e performance
3. ✅ Avaliar primeiro ciclo completo

**AMANHÃ (07-NOV):**
1. Análise de performance do Momentum Scanner
2. Implementar Breakout Hunter (estratégia #2)
3. Backtest de ambas as estratégias

**SEMANA 1 (06-12 NOV):**
1. Adicionar 3 estratégias (VIX Detector, Mean Reversion, Correlation Breakdown)
2. Testar todas em paralelo
3. Descartar as que falharem

---

## 📞 COMANDO PARA MIM

**CEO, ESTAMOS PRONTOS PARA DEPLOY!**

Aguardo seu comando para iniciarmos a FASE 1 (Compilar EA).

Confirme quando estiver com o MT5 aberto e pronto para começar.

**COMANDO:** "Iniciar deploy Numeia v6.0"

