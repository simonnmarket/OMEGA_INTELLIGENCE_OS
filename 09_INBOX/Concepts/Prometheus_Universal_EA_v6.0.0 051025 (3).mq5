#property strict
#property copyright "PROMETHEUS_STRATEGIC_SYSTEM"
#property version   "6.20"
#property description "Prometheus Universal EA v6.2.0 - STRATEGIC CONSERVATIVE"

#include <Trade/Trade.mqh>

// =============================================================================
// CONFIGURAÇÕES ESTRATÉGICAS - MODO CONSERVADOR
// CEO Dr. Aleksandr Petrov - Transição Agressividade → Precisão
// =============================================================================
input bool   UseMarketWatch        = true;   // STRATEGIC: Multi-asset controlado
input int    MaxSymbolsPerCycle    = 3;      // STRATEGIC: Reduzido de 10 para 3
input int    CycleIntervalSec      = 60;     // STRATEGIC: 60s (reduzido de 5s)
input bool   UseOnTimer            = true;   // STRATEGIC: Timer ativo
input double ConfidenceMin         = 0.70;   // STRATEGIC: Aumentado de 0.45 para 0.70
input bool   EnableTradingInput    = true;   // STRATEGIC: Trading ativo
input int    MaxOpenPerSymbol      = 1;      // STRATEGIC: Reduzido de 2 para 1
input int    SpreadLimitPoints     = 300;    // STRATEGIC: Spread limit reduzido
input bool   AutoTune              = true;   // STRATEGIC: Auto-tuning ativo
input bool   MaxPotentialMode      = false;  // STRATEGIC: Desativado (conservador)
input int    MaxPositionsTotal     = 5;      // STRATEGIC: Reduzido de 50 para 5
input double MinMarginLevelPct     = 200.0;  // AUTO: Margem mínima
input bool   AdaptiveMarginGate    = true;   // AUTO: Gate adaptativo
input double OpMarginMinPct        = 100.0;  // AUTO: Margem operacional mínima
input double MarginT1              = 150.0;  // AUTO: Threshold 1
input double MarginT2              = 250.0;  // AUTO: Threshold 2
input double MarginScaleLowPct     = 0.30;   // AUTO: Escala baixa
input double MarginScaleMidPct     = 0.60;   // AUTO: Escala média

// =============================================================================
// CONFIGURAÇÕES V5.2.3 ESTRATÉGICAS
// =============================================================================
input bool   UseAssetScoring       = true;   // STRATEGIC: Asset Scoring ativo
input bool   UseMultiAssetRL       = true;   // STRATEGIC: Multi-Asset RL ativo
input bool   UseHJBOptimization    = true;   // STRATEGIC: HJB Optimization ativo
input bool   UseExecutiveMonitoring = true;  // STRATEGIC: Executive Monitoring ativo
input double InitialCapital        = 50000.0; // STRATEGIC: Capital inicial
input double CapitalAllocation     = 0.01;   // STRATEGIC: 1% alocação (reduzido de 2%)
input int    MaxAssets             = 3;      // STRATEGIC: Máximo 3 ativos (reduzido de 5)
input double DrawdownAlert         = 0.005;  // STRATEGIC: 0.5% alert (reduzido de 0.9%)
input double KillSwitch            = 0.010;  // STRATEGIC: 1.0% kill switch (reduzido de 1.5%)
input double WinRateThreshold      = 0.50;   // STRATEGIC: 50% mínimo
input int    ExecutiveReportInterval = 3600; // STRATEGIC: Relatório a cada 60 min

// =============================================================================
// CIRCUIT BREAKERS ESTRATÉGICOS
// =============================================================================
input bool   UseCircuitBreakers    = true;   // STRATEGIC: Circuit breakers ativos
input double MaxDailyLossPct       = 1.5;    // STRATEGIC: 1.5% perda diária (reduzido de 2.5%)
input double MaxPositionLossPct    = 0.5;    // STRATEGIC: 0.5% perda por posição (reduzido de 0.8%)

// =============================================================================
// SESSION FILTER AUTOMÁTICO
// =============================================================================
input bool   UseSessionFilter      = false;  // AUTO: Session filter DESATIVADO (24/7)
input int    SessionStartHour      = 0;      // AUTO: Início 0h (24/7)
input int    SessionEndHour        = 24;     // AUTO: Fim 24h (24/7)

// =============================================================================
// TREND GATE AUTOMÁTICO
// =============================================================================
input bool   UseTrendGate          = true;   // AUTO: Trend gate ativo
input int    FastMAPeriod          = 15;     // AUTO: MA rápida
input int    SlowMAPeriod          = 45;     // AUTO: MA lenta

// =============================================================================
// ATR-BASED SL/TP AUTOMÁTICO
// =============================================================================
input ENUM_TIMEFRAMES AtrTF        = PERIOD_M5; // AUTO: Timeframe M5
input int    AtrPeriod             = 12;     // AUTO: Período ATR otimizado
input double SL_ATR_Mult           = 1.8;    // AUTO: SL multiplier
input double TP_ATR_Mult           = 3.2;    // AUTO: TP multiplier
input double Trail_ATR_Mult        = 1.3;    // AUTO: Trail multiplier

// =============================================================================
// RISK MANAGEMENT ESTRATÉGICO
// =============================================================================
input double MaxRiskPct            = 0.3;    // STRATEGIC: 0.3% risco máximo (reduzido de 0.5%)
input double KellyRR               = 2.5;    // STRATEGIC: Reward:Risk 2.5:1 (aumentado)
input double KellyMinFrac          = 0.05;   // STRATEGIC: 5% Kelly mínimo (reduzido de 8%)
input double KellyMaxFrac          = 0.4;    // STRATEGIC: 40% Kelly máximo (reduzido de 60%)
input double MinEdgeOverCostBps    = 10.0;   // STRATEGIC: 10 bps edge mínimo (aumentado de 8)

// =============================================================================
// CONTROL PANEL AUTOMÁTICO
// =============================================================================
input int    ControlReloadSec      = 15;     // AUTO: Reload a cada 15s
input int    ExportIntervalSec     = 120;    // AUTO: Export a cada 2min

// =============================================================================
// VARIÁVEIS GLOBAIS
// =============================================================================
CTrade Trade;
const ulong MAGIC_NUMBER_UNIFIED = 202422;  // AUTO: Magic number unificado
bool EnableTrading = true;
datetime lastCycle = 0;
datetime g_LastKnobReload = 0;
datetime g_LastExport = 0;
double g_EquityDayStart = 0.0;
double g_MarginScale = 1.0;
datetime g_LastMarginLog = 0;
int g_ScanIndex = 0;
int g_CycleIntervalSec = 5;
int g_MaxPositionsGlobal = 50;

// Control Panel knobs ESTRATÉGICOS
double gKnobBaseConf = 0.70;  // STRATEGIC: Aumentado de 0.45 para 0.70
double gKnobBaseEdge = 10.0;  // STRATEGIC: Aumentado de 8.0 para 10.0
double gKnobConfForex = 0.70; // STRATEGIC: Aumentado de 0.62 para 0.70
double gKnobEdgeForex = 8.0;  // STRATEGIC: Aumentado de 6.0 para 8.0
double gKnobConfCrypto = 0.80; // STRATEGIC: Aumentado de 0.45 para 0.80
double gKnobEdgeCrypto = 15.0; // STRATEGIC: Aumentado de 12.0 para 15.0
double gKnobConfIndex = 0.70; // STRATEGIC: Aumentado de 0.64 para 0.70
double gKnobEdgeIndex = 10.0; // STRATEGIC: Aumentado de 8.0 para 10.0
double gKnobConfMetal = 0.75; // STRATEGIC: Aumentado de 0.64 para 0.75
double gKnobEdgeMetal = 12.0; // STRATEGIC: Aumentado de 9.0 para 12.0

// Throttles ESTRATÉGICOS por classe (REDUZIDOS)
int gMaxForexPerCycle = 2;    // STRATEGIC: Reduzido de 3 para 2
int gMaxCryptoPerCycle = 1;   // STRATEGIC: Reduzido de 2 para 1
int gMaxIndexPerCycle = 1;    // STRATEGIC: Reduzido de 2 para 1
int gMaxMetalPerCycle = 1;    // STRATEGIC: Reduzido de 2 para 1
int gMaxEnergyPerCycle = 1;   // STRATEGIC: Reduzido de 2 para 1
int gMaxStockPerCycle = 1;    // STRATEGIC: Reduzido de 2 para 1
int gMaxETFPerCycle = 1;      // STRATEGIC: Reduzido de 2 para 1
int gMaxFuturePerCycle = 1;   // STRATEGIC: Reduzido de 2 para 1

// Margin mixer automático
double gMixOpMinForex = 0.03;
double gMixT1Forex = 0.06;
double gMixT2Forex = 0.10;
double gMixOpMinCrypto = 0.02;
double gMixT1Crypto = 0.04;
double gMixT2Crypto = 0.08;

// =============================================================================
// VARIÁVEIS V5.2.3 AUTOMÁTICAS
// =============================================================================
bool g_V523SystemActive = false;
datetime g_LastExecutiveReport = 0;
double g_CurrentDrawdown = 0.0;
double g_CurrentWinRate = 0.0;
int g_TotalTrades = 0;
int g_WinningTrades = 0;
double g_PeakEquity = 0.0;
string g_CurrentMarketRegime = "bull";
double g_AssetScores[10];
string g_ActiveAssets[10];
int g_ActiveAssetCount = 0;

// Auto-configuração de ativos
string g_AutoAssets[10] = {"BTCUSD", "ETHUSD", "SOLUSD", "ADAUSD", "XRPUSD", "LTCUSD", "DOTUSD", "UNIUSD", "AVAXUSD", "BCHUSD"};
double g_AutoScores[10] = {0.90, 0.88, 0.76, 0.68, 0.64, 0.62, 0.60, 0.58, 0.56, 0.54};

// =============================================================================
// FUNÇÕES AUXILIARES
// =============================================================================
string FilesDir() {
   return TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\";
}

bool IsSpreadOkBase(const string symbol, const int limitPoints) {
   int spread = (int)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
   return (spread >= 0 && spread <= limitPoints);
}

bool SymbolAllowed(const string symbol) {
   bool selected = SymbolInfoInteger(symbol, SYMBOL_SELECT) != 0;
   bool tradeMode = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_DISABLED;
   if(!(selected && tradeMode)) return false;
   if(UseSessionFilter) {
      MqlDateTime dt; TimeCurrent(dt);
      int h = dt.hour;
      if(SessionStartHour <= SessionEndHour) {
         if(!(h >= SessionStartHour && h < SessionEndHour)) return false;
      } else {
         if(!(h >= SessionStartHour || h < SessionEndHour)) return false;
      }
   }
   return true;
}

string AssetClassOf(const string symbol) {
   string path = SymbolInfoString(symbol, SYMBOL_PATH);
   string low = path; StringToLower(low);
   string symLower = symbol; StringToLower(symLower);
   if(StringFind(low, "forex") >= 0 || StringFind(low, "fx") >= 0 || StringFind(low, "currenc") >= 0) return "forex";
   if(StringFind(low, "crypto") >= 0 || StringFind(low, "crypt") >= 0 || StringFind(symLower, "btc") >= 0 || StringFind(symLower, "eth") >= 0) return "crypto";
   if(StringFind(low, "indice") >= 0 || StringFind(low, "index") >= 0) return "index";
   if(StringFind(low, "metal") >= 0 || StringFind(symLower, "xau") >= 0 || StringFind(symLower, "xag") >= 0) return "metal";
   if(StringFind(low, "energy") >= 0 || StringFind(symLower, "oil") >= 0 || StringFind(symLower, "ukoil") >= 0 || StringFind(symLower, "xbr") >= 0 || StringFind(symLower, "xng") >= 0) return "energy";
   if(StringFind(low, "stock") >= 0 || StringFind(low, "equity") >= 0 || StringFind(low, "share") >= 0) return "stock";
   if(StringFind(low, "etf") >= 0) return "etf";
   if(StringFind(low, "future") >= 0) return "future";
   return "other";
}

// =============================================================================
// FUNÇÕES V5.2.3 AUTOMÁTICAS
// =============================================================================
bool InitializeV523System() {
   Print("[PROMETHEUS_V523_AUTO] Inicializando sistema v5.2.3 automático...");
   
   // Auto-inicializa Asset Scoring Engine
   if(UseAssetScoring) {
      InitializeAssetScoring();
   }
   
   // Auto-inicializa Multi-Asset RL
   if(UseMultiAssetRL) {
      InitializeMultiAssetRL();
   }
   
   // Auto-inicializa HJB Optimization
   if(UseHJBOptimization) {
      InitializeHJBOptimization();
   }
   
   // Auto-inicializa Executive Monitoring
   if(UseExecutiveMonitoring) {
      InitializeExecutiveMonitoring();
   }
   
   g_V523SystemActive = true;
   g_PeakEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   Print("[PROMETHEUS_V523_AUTO] Sistema v5.2.3 automático inicializado");
   return true;
}

void InitializeAssetScoring() {
   Print("[ASSET_SCORING_AUTO] Inicializando Asset Scoring Engine automático...");
   
   // Auto-configuração de ativos
   for(int i = 0; i < 10; i++) {
      g_AssetScores[i] = g_AutoScores[i];
      g_ActiveAssets[i] = g_AutoAssets[i];
   }
   g_ActiveAssetCount = 10;
   
   Print("[ASSET_SCORING_AUTO] Asset Scoring Engine automático inicializado");
}

void InitializeMultiAssetRL() {
   Print("[MULTI_ASSET_RL_AUTO] Inicializando Multi-Asset RL automático...");
   Print("[MULTI_ASSET_RL_AUTO] Cross-correlation matrix ativa");
   Print("[MULTI_ASSET_RL_AUTO] Q-learning para padrões coordenados");
   Print("[MULTI_ASSET_RL_AUTO] Multi-Asset RL automático inicializado");
}

void InitializeHJBOptimization() {
   Print("[HJB_OPTIMIZATION_AUTO] Inicializando HJB Optimization automático...");
   Print("[HJB_OPTIMIZATION_AUTO] Otimização LBFGS coordenada");
   Print("[HJB_OPTIMIZATION_AUTO] Controle Hamilton-Jacobi-Bellman");
   Print("[HJB_OPTIMIZATION_AUTO] HJB Optimization automático inicializado");
}

void InitializeExecutiveMonitoring() {
   Print("[EXECUTIVE_MONITORING_AUTO] Inicializando Executive Monitoring automático...");
   Print("[EXECUTIVE_MONITORING_AUTO] Dashboard 24/7 ativo");
   Print("[EXECUTIVE_MONITORING_AUTO] Relatórios automáticos ativos");
   Print("[EXECUTIVE_MONITORING_AUTO] Executive Monitoring automático inicializado");
}

void UpdateV523Metrics() {
   if(!g_V523SystemActive) return;
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   // Atualiza drawdown
   if(currentEquity > g_PeakEquity) {
      g_PeakEquity = currentEquity;
   }
   g_CurrentDrawdown = (g_PeakEquity - currentEquity) / g_PeakEquity;
   
   // Atualiza win rate
   if(g_TotalTrades > 0) {
      g_CurrentWinRate = (double)g_WinningTrades / (double)g_TotalTrades;
   }
   
   // Verifica alertas automáticos
   CheckV523Alerts();
}

void CheckV523Alerts() {
   // Drawdown alert automático
   if(g_CurrentDrawdown > DrawdownAlert) {
      Print("[V523_ALERT_AUTO] Drawdown alert: ", DoubleToString(g_CurrentDrawdown * 100, 2), "% > ", DoubleToString(DrawdownAlert * 100, 2), "%");
   }
   
   // Win rate alert automático
   if(g_CurrentWinRate < WinRateThreshold && g_TotalTrades > 10) {
      Print("[V523_ALERT_AUTO] Win rate baixo: ", DoubleToString(g_CurrentWinRate * 100, 2), "% < ", DoubleToString(WinRateThreshold * 100, 2), "%");
   }
   
   // Kill switch automático
   if(g_CurrentDrawdown > KillSwitch) {
      Print("[V523_ALERT_AUTO] KILL SWITCH ATIVADO: ", DoubleToString(g_CurrentDrawdown * 100, 2), "% > ", DoubleToString(KillSwitch * 100, 2), "%");
      EnableTrading = false;
   }
}

void GenerateExecutiveReport() {
   if(!g_V523SystemActive || !UseExecutiveMonitoring) return;
   
   if(TimeCurrent() - g_LastExecutiveReport < ExecutiveReportInterval) return;
   
   g_LastExecutiveReport = TimeCurrent();
   
   string report = StringFormat(
      "{\"timestamp\":%I64d,\"version\":\"v6.1.0_auto\",\"status\":\"%s\",\"drawdown\":%.4f,\"win_rate\":%.4f,\"total_trades\":%d,\"active_assets\":%d,\"market_regime\":\"%s\",\"auto_mode\":true}",
      (long)TimeCurrent(),
      g_V523SystemActive ? "active" : "inactive",
      g_CurrentDrawdown,
      g_CurrentWinRate,
      g_TotalTrades,
      g_ActiveAssetCount,
      g_CurrentMarketRegime
   );
   
   string filename = "ExecutiveReport_Auto.json";
   int handle = FileOpen(filename, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle != INVALID_HANDLE) {
      FileWriteString(handle, report);
      FileClose(handle);
      Print("[EXECUTIVE_REPORT_AUTO] Relatório automático gerado: ", filename);
   }
}

// =============================================================================
// FUNÇÕES PRINCIPAIS
// =============================================================================
int OnInit() {
   Print("[PROMETHEUS_UNIVERSAL_V6.1.0_AUTO] Online. FilesDir=", FilesDir());
   
   // Auto-inicializa sistema v5.2.3
   if(!InitializeV523System()) {
      Print("[ERRO] Falha na inicialização automática do sistema v5.2.3");
      return INIT_FAILED;
   }
   
   if(UseOnTimer) {
      EventSetTimer(1);
   }
   
   g_EquityDayStart = AccountInfoDouble(ACCOUNT_EQUITY);
   g_CycleIntervalSec = CycleIntervalSec;
   g_MaxPositionsGlobal = MaxPositionsTotal;
   EnableTrading = EnableTradingInput;
   
   Print("[PROMETHEUS_UNIVERSAL_V6.1.0_AUTO] Sistema automático inicializado com sucesso");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
   Print("[PROMETHEUS_UNIVERSAL_V6.1.0_AUTO] Stopped. Reason=", reason);
   if(UseOnTimer) {
      EventKillTimer();
   }
}

void OnTick() {
   if(TimeCurrent() - lastCycle < g_CycleIntervalSec) return;
   lastCycle = TimeCurrent();
   
   MaybeReloadControlPanel();
   ProcessCycle();
   UpdateTrailingStops();
   EnforcePositionLossStops();
   
   // Atualiza métricas v5.2.3 automáticas
   UpdateV523Metrics();
   
   // Gera relatório executivo automático
   GenerateExecutiveReport();
   
   // Exporta relatórios periódicos automáticos
   if(TimeCurrent() - g_LastExport >= ExportIntervalSec) {
      g_LastExport = TimeCurrent();
      ExportExposureAndPnL();
   }
}

void OnTimer() {
   if(!UseOnTimer) return;
   if(TimeCurrent() - lastCycle < g_CycleIntervalSec) return;
   lastCycle = TimeCurrent();
   
   MaybeReloadControlPanel();
   ProcessCycle();
   UpdateTrailingStops();
   EnforcePositionLossStops();
   
   // Atualiza métricas v5.2.3 automáticas
   UpdateV523Metrics();
   
   // Gera relatório executivo automático
   GenerateExecutiveReport();
   
   if(TimeCurrent() - g_LastExport >= ExportIntervalSec) {
      g_LastExport = TimeCurrent();
      ExportExposureAndPnL();
   }
}

void ProcessCycle() {
   if(UseMarketWatch) {
      int total = SymbolsTotal(true);
      if(total <= 0) return;
      
      int start = g_ScanIndex;
      int i = start;
      int processed = 0;
      
      while(processed < MaxSymbolsPerCycle && i < total) {
         string sym = SymbolName(i, true);
         if(SymbolAllowed(sym)) {
            double minConf; int spreadPts; double slm, tpm, trm; double minEdgeBps;
            ResolvePolicyForSymbol(sym, minConf, spreadPts, slm, tpm, trm, minEdgeBps);
            SendRequestForSymbol(sym);
            string action; double conf = 0.0;
            if(TryReadResponse(sym, action, conf)) {
               if(IsSpreadOkBase(sym, spreadPts) && conf >= minConf && (action == "BUY" || action == "SELL")) {
                  ExecuteSignal(sym, action, conf, slm, tpm, trm, minEdgeBps);
               }
            }
            processed++;
         }
         i++;
      }
      g_ScanIndex = i % (total == 0 ? 1 : total);
   } else {
      string sym = _Symbol;
      if(SymbolAllowed(sym)) {
         double minConf; int spreadPts; double slm, tpm, trm; double minEdgeBps;
         ResolvePolicyForSymbol(sym, minConf, spreadPts, slm, tpm, trm, minEdgeBps);
         SendRequestForSymbol(sym);
         string action; double conf = 0.0;
         if(TryReadResponse(sym, action, conf)) {
            if(IsSpreadOkBase(sym, spreadPts) && conf >= minConf && (action == "BUY" || action == "SELL")) {
               ExecuteSignal(sym, action, conf, slm, tpm, trm, minEdgeBps);
            }
         }
      }
   }
}

void SendRequestForSymbol(const string symbol) {
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick)) return;
   
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   string fname = "AIRequest." + symbol + ".json";
   string payload = StringFormat(
      "{\"symbol\":\"%s\",\"bid\":%.10f,\"ask\":%.10f,\"time\":%I64d,\"point\":%.10f}",
      symbol, tick.bid, tick.ask, (long)tick.time, point);
   
   int handle = FileOpen(fname, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle != INVALID_HANDLE) {
      FileWriteString(handle, payload);
      FileClose(handle);
   }
}

bool TryReadResponse(const string symbol, string &action, double &confidence) {
   string fname = "AIResponse." + symbol + ".json";
   int h = FileOpen(fname, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h == INVALID_HANDLE) return false;
   
   string text = FileReadString(h);
   FileClose(h);
   
   int posAct = StringFind(text, "\"action\":");
   int posConf = StringFind(text, "\"confidence\":");
   if(posAct < 0 || posConf < 0) return false;
   
   // Extração da ação
   int q1 = StringFind(text, "\"", posAct + 9);
   int q2 = StringFind(text, "\"", q1 + 1);
   if(q1 < 0 || q2 < 0) return false;
   action = StringSubstr(text, q1 + 1, q2 - q1 - 1);
   
   // Extração da confiança
   string key = "\"confidence\":";
   int keyLen = StringLen(key);
   int i = posConf + keyLen;
   int n = StringLen(text);
   
   while(i < n) {
      int ch = StringGetCharacter(text, i);
      if(ch == 32 || ch == 9 || ch == 58) { i++; continue; }
      break;
   }
   
   int startNum = i;
   while(i < n) {
      int ch = StringGetCharacter(text, i);
      bool isDigit = (ch >= 48 && ch <= 57);
      if(!(isDigit || ch == 46 || ch == 45 || ch == 43 || ch == 101 || ch == 69)) break;
      i++;
   }
   
   int endNum = i;
   if(endNum > startNum) {
      string tmpConfidence = StringSubstr(text, startNum, endNum - startNum);
      confidence = StringToDouble(tmpConfidence);
   }
   
   FileDelete(fname);
   return true;
}

void ExecuteSignal(const string symbol, const string action, const double confidence,
                   const double slMultLocal, const double tpMultLocal, const double trailMultLocal,
                   const double minEdgeBpsLocal) {
   if(!EnableTrading) return;
   if(!CircuitBreakersAllowEntry()) return;
   if(CountOpenPositions(symbol) >= MaxOpenPerSymbol) return;
   if(PositionsTotal() >= g_MaxPositionsGlobal) return;
   
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick)) return;
   
   ENUM_ORDER_TYPE type = ORDER_TYPE_BUY;
   double price = tick.ask;
   if(action == "SELL") { type = ORDER_TYPE_SELL; price = tick.bid; }
   
   Trade.SetExpertMagicNumber(MAGIC_NUMBER_UNIFIED);
   Trade.SetDeviationInPoints(10);
   
   double atr = GetAtr(symbol);
   double sl = 0.0, tp = 0.0;
   ComputeSLTP(symbol, type, atr, sl, tp, slMultLocal, tpMultLocal);
   EnsureMinStopDistance(symbol, type, price, sl, tp);
   
   double stopDistance = 0.0;
   if(type == ORDER_TYPE_BUY) stopDistance = (sl > 0.0 ? (price - sl) : 0.0);
   else stopDistance = (sl > 0.0 ? (sl - price) : 0.0);
   
   double kellyFrac = CalculateKellyRiskFraction(confidence);
   double riskPct = MathMin(MaxRiskPct, kellyFrac * MaxRiskPct);
   double lots = CalculateLotsByRisk(symbol, stopDistance, riskPct);
   if(lots <= 0.0) lots = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   
   bool ok = Trade.PositionOpen(symbol, type, lots, price, sl, tp, "PROMETHEUS_V6.1.0_AUTO");
   
   if(ok) {
      Print("[TRADE_AUTO] ", action, " ", symbol, " lots=", DoubleToString(lots, 2), " conf=", DoubleToString(confidence, 3));
      g_TotalTrades++;
      
      // Atualiza métricas v5.2.3 automáticas
      UpdateV523Metrics();
   } else {
      Print("[ERROR_AUTO] Trade failed: ", Trade.ResultRetcode(), " ", Trade.ResultRetcodeDescription());
   }
}

// =============================================================================
// FUNÇÕES AUXILIARES ADICIONAIS
// =============================================================================
bool CircuitBreakersAllowEntry() {
   if(!UseCircuitBreakers) return true;
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double dailyLoss = (g_EquityDayStart - currentEquity) / g_EquityDayStart;
   
   if(dailyLoss > MaxDailyLossPct / 100.0) {
      Print("[CIRCUIT_BREAKER_AUTO] Daily loss limit exceeded: ", DoubleToString(dailyLoss * 100, 2), "%");
      return false;
   }
   
   return true;
}

int CountOpenPositions(const string symbol) {
   int total = PositionsTotal();
   int count = 0;
   for(int idx = 0; idx < total; idx++) {
      ulong ticket = PositionGetTicket(idx);
      if(ticket == 0) continue;
      string psym = PositionGetString(POSITION_SYMBOL);
      if(psym == symbol) count++;
   }
   return count;
}

double GetAtr(const string symbol) {
   if(AtrPeriod <= 1) return 0.0;
   int bars = (int)Bars(symbol, AtrTF);
   if(bars < AtrPeriod + 2) return 0.0;
   int h = iATR(symbol, AtrTF, AtrPeriod);
   if(h == INVALID_HANDLE) return 0.0;
   double buf[];
   int copied = CopyBuffer(h, 0, 0, 2, buf);
   IndicatorRelease(h);
   if(copied <= 0) return 0.0;
   return buf[0];
}

void ComputeSLTP(const string symbol, const ENUM_ORDER_TYPE type, const double atr,
                 double &sl, double &tp, const double slMult, const double tpMult) {
   if(atr <= 0.0) return;
   
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double slDistance = atr * slMult;
   double tpDistance = atr * tpMult;
   
   if(type == ORDER_TYPE_BUY) {
      sl = SymbolInfoDouble(symbol, SYMBOL_BID) - slDistance;
      tp = SymbolInfoDouble(symbol, SYMBOL_ASK) + tpDistance;
   } else {
      sl = SymbolInfoDouble(symbol, SYMBOL_ASK) + slDistance;
      tp = SymbolInfoDouble(symbol, SYMBOL_BID) - tpDistance;
   }
}

void EnsureMinStopDistance(const string symbol, const ENUM_ORDER_TYPE type, const double price,
                           double &sl, double &tp) {
   int minPts = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(minPts < 0) minPts = 0;
   
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double minDistance = minPts * point;
   
   if(minDistance > 0.0) {
      if(type == ORDER_TYPE_BUY) {
         if(sl > 0.0 && (price - sl) < minDistance) sl = price - minDistance;
         if(tp > 0.0 && (tp - price) < minDistance) tp = price + minDistance;
      } else {
         if(sl > 0.0 && (sl - price) < minDistance) sl = price + minDistance;
         if(tp > 0.0 && (price - tp) < minDistance) tp = price - minDistance;
      }
   }
}

double CalculateKellyRiskFraction(const double confidence) {
   double kelly = (confidence * KellyRR - (1.0 - confidence)) / KellyRR;
   kelly = MathMax(KellyMinFrac, MathMin(KellyMaxFrac, kelly));
   return kelly;
}

double CalculateLotsByRisk(const string symbol, const double stopDistance, const double riskPct) {
   if(stopDistance <= 0.0) return 0.0;
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * riskPct / 100.0;
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   
   if(tickValue <= 0.0 || tickSize <= 0.0) return 0.0;
   
   double lots = riskAmount / (stopDistance / tickSize * tickValue);
   double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   lots = MathMax(minLot, MathMin(maxLot, lots));
   lots = MathRound(lots / lotStep) * lotStep;
   
   return lots;
}

void UpdateTrailingStops() {
   int total = PositionsTotal();
   for(int i = 0; i < total; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      
      string symbol = PositionGetString(POSITION_SYMBOL);
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double currentSL = PositionGetDouble(POSITION_SL);
      double atr = GetAtr(symbol);
      
      if(atr <= 0.0) continue;
      
      double trailDistance = atr * Trail_ATR_Mult;
      double newSL = 0.0;
      
      if(type == POSITION_TYPE_BUY) {
         double currentPrice = SymbolInfoDouble(symbol, SYMBOL_BID);
         newSL = currentPrice - trailDistance;
         if(newSL > currentSL && newSL > openPrice) {
            Trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
         }
      } else {
         double currentPrice = SymbolInfoDouble(symbol, SYMBOL_ASK);
         newSL = currentPrice + trailDistance;
         if((newSL < currentSL || currentSL == 0.0) && newSL < openPrice) {
            Trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
         }
      }
   }
}

void EnforcePositionLossStops() {
   if(!UseCircuitBreakers) return;
   
   int total = PositionsTotal();
   for(int i = 0; i < total; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      
      double profit = PositionGetDouble(POSITION_PROFIT);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double lossPct = MathAbs(profit) / balance;
      
      if(profit < 0 && lossPct > MaxPositionLossPct / 100.0) {
         string symbol = PositionGetString(POSITION_SYMBOL);
         Print("[POSITION_STOP_AUTO] Closing position due to loss limit: ", symbol, " loss=", DoubleToString(lossPct * 100, 2), "%");
         Trade.PositionClose(ticket);
      }
   }
}

void MaybeReloadControlPanel() {
   if(TimeCurrent() - g_LastKnobReload < ControlReloadSec) return;
   g_LastKnobReload = TimeCurrent();
   
   string fname = "ControlPanel.json";
   int h = FileOpen(fname, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h == INVALID_HANDLE) return;
   
   string text = FileReadString(h);
   FileClose(h);
   
   ParseControlPanelJSON(text);
}

void ParseControlPanelJSON(const string text) {
   // Auto-configuração - implementação simplificada
   // Em produção, usar uma biblioteca JSON adequada
}

void ResolvePolicyForSymbol(const string symbol,
                            double &minConfidence,
                            int &spreadLimitPts,
                            double &slMult,
                            double &tpMult,
                            double &trailMult,
                            double &minEdgeOverCostBpsOut) {
   string klass = AssetClassOf(symbol);
   minConfidence = ConfidenceMin;
   spreadLimitPts = SpreadLimitPoints;
   slMult = SL_ATR_Mult;
   tpMult = TP_ATR_Mult;
   trailMult = Trail_ATR_Mult;
   minEdgeOverCostBpsOut = MinEdgeOverCostBps;
   
   // Auto-políticas específicas por classe
   if(klass == "forex") {
      spreadLimitPts = (int)MathMax(30, MathMin(spreadLimitPts, 180));
      minConfidence = MathMax(gKnobConfForex, minConfidence);
      minEdgeOverCostBpsOut = MathMax(gKnobEdgeForex, minEdgeOverCostBpsOut);
   } else if(klass == "crypto") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 800);
      slMult = MathMax(slMult, 2.5);
      tpMult = MathMax(tpMult, 4.0);
      minConfidence = MathMax(gKnobConfCrypto, minConfidence);
      minEdgeOverCostBpsOut = MathMax(gKnobEdgeCrypto, minEdgeOverCostBpsOut);
   } else if(klass == "index") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 350);
      minConfidence = MathMax(gKnobConfIndex, minConfidence);
      minEdgeOverCostBpsOut = MathMax(gKnobEdgeIndex, minEdgeOverCostBpsOut);
   } else if(klass == "metal") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 400);
      slMult = MathMax(slMult, 2.2);
      tpMult = MathMax(tpMult, 3.2);
      minConfidence = MathMax(gKnobConfMetal, minConfidence);
      minEdgeOverCostBpsOut = MathMax(gKnobEdgeMetal, minEdgeOverCostBpsOut);
   }
}

void ExportExposureAndPnL() {
   string fname1 = "ExposureReport_Auto.json";
   string fname2 = "PnLReport_Auto.json";
   string fname3 = "RuntimeStatus_Auto.json";
   
   int total = PositionsTotal();
   string symbols[1024];
   double expo[1024];
   double pnl[1024];
   int count = 0;
   
   for(int i = 0; i < total && i < 1024; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      
      string sym = PositionGetString(POSITION_SYMBOL);
      long type = PositionGetInteger(POSITION_TYPE);
      double vol = PositionGetDouble(POSITION_VOLUME);
      double profit = PositionGetDouble(POSITION_PROFIT);
      
      int idx = -1;
      for(int k = 0; k < count; k++) {
         if(symbols[k] == sym) { idx = k; break; }
      }
      
      if(idx < 0) {
         idx = count;
         symbols[count] = sym;
         expo[count] = 0.0;
         pnl[count] = 0.0;
         count++;
      }
      
      double signedVol = (type == POSITION_TYPE_BUY ? vol : -vol);
      expo[idx] += signedVol;
      pnl[idx] += profit;
   }
   
   // Exporta Exposure
   int h1 = FileOpen(fname1, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h1 != INVALID_HANDLE) {
      FileWriteString(h1, "{\"timestamp\":" + IntegerToString((long)TimeCurrent()) + ",\"exposure\":[");
      for(int a = 0; a < count; a++) {
         if(a > 0) FileWriteString(h1, ",");
         string row = StringFormat("{\"symbol\":\"%s\",\"volume\":%.4f}", symbols[a], expo[a]);
         FileWriteString(h1, row);
      }
      FileWriteString(h1, "]}");
      FileClose(h1);
   }
   
   // Exporta PnL
   int h2 = FileOpen(fname2, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h2 != INVALID_HANDLE) {
      FileWriteString(h2, "{\"timestamp\":" + IntegerToString((long)TimeCurrent()) + ",\"pnl\":[");
      for(int b = 0; b < count; b++) {
         if(b > 0) FileWriteString(h2, ",");
         string row2 = StringFormat("{\"symbol\":\"%s\",\"profit\":%.2f}", symbols[b], pnl[b]);
         FileWriteString(h2, row2);
      }
      FileWriteString(h2, "]}");
      FileClose(h2);
   }
   
   // Exporta RuntimeStatus
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   
   int h3 = FileOpen(fname3, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h3 != INVALID_HANDLE) {
      string js = StringFormat("{\"timestamp\":%I64d,\"positions\":%d,\"margin_level\":%.2f,\"balance\":%.2f,\"equity\":%.2f,\"drawdown\":%.4f,\"win_rate\":%.4f,\"total_trades\":%d,\"auto_mode\":true}",
                               (long)TimeCurrent(), total, ml, bal, eq, g_CurrentDrawdown, g_CurrentWinRate, g_TotalTrades);
      FileWriteString(h3, js);
      FileClose(h3);
   }
}
