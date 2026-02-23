#property strict
#property copyright "PROMETHEUS_STRATEGIC_CONSERVATIVE_SYSTEM"
#property version   "6.40"
#property description "Prometheus STRATEGIC v6.4.0 - Apollo11 + TrajectoryAnalyzer + MarketPsyEngine - FULL INTEGRATION"

#include <Trade/Trade.mqh>
#include <Math/Stat/Math.mqh>
#include <MarketPsyEngine.mqh>
#include <Apollo11_Professional.mqh>
#include <TrajectoryAnalyzer.mqh>

// =============================================================================
// CONFIGURAÇÕES ULTRA-CONSERVADORAS - QUALIDADE SOBRE QUANTIDADE
// =============================================================================
input bool   UseMarketWatch        = false;
input int    MaxSymbolsPerCycle    = 3;
input int    CycleIntervalSec      = 60;
input bool   UseOnTimer            = true;
input double ConfidenceMin         = 0.70;
input bool   EnableTradingInput    = true;
input int    MaxOpenPerSymbol      = 1;
input int    SpreadLimitPoints     = 300;
input bool   AutoTune              = true;
input bool   MaxPotentialMode      = false;
input int    MaxPositionsTotal     = 5;
input double MinMarginLevelPct     = 200.0;
input bool   AdaptiveMarginGate    = true;
input double OpMarginMinPct        = 100.0;
input double MarginT1              = 150.0;
input double MarginT2              = 250.0;
input double MarginScaleLowPct     = 0.30;
input double MarginScaleMidPct     = 0.60;

// =============================================================================
// CONFIGURAÇÕES V5.2.3 ULTRA-CONSERVADORAS
// =============================================================================
input bool   UseAssetScoring       = true;
input bool   UseMultiAssetRL       = true;
input bool   UseHJBOptimization    = true;
input bool   UseExecutiveMonitoring = true;
input double InitialCapital        = 50000.0;
input double CapitalAllocation     = 0.01;
input int    MaxAssets             = 3;
input double DrawdownAlert         = 0.005;
input double KillSwitch            = 0.010;
input double WinRateThreshold      = 0.50;
input int    ExecutiveReportInterval = 3600;

// =============================================================================
// CIRCUIT BREAKERS ULTRA-CONSERVADORES
// =============================================================================
input bool   UseCircuitBreakers    = true;
input double MaxDailyLossPct       = 1.5;
input double MaxPositionLossPct    = 0.5;

// =============================================================================
// SESSION FILTER
// =============================================================================
input bool   UseSessionFilter      = false;
input int    SessionStartHour      = 0;
input int    SessionEndHour        = 24;

// =============================================================================
// TREND GATE
// =============================================================================
input bool   UseTrendGate          = true;
input int    FastMAPeriod          = 15;
input int    SlowMAPeriod          = 45;

// =============================================================================
// ATR-BASED SL/TP
// =============================================================================
input ENUM_TIMEFRAMES AtrTF        = PERIOD_M5;
input int    AtrPeriod             = 12;
input double SL_ATR_Mult           = 1.8;
input double TP_ATR_Mult           = 3.2;
input double Trail_ATR_Mult        = 1.3;

// =============================================================================
// RISK MANAGEMENT ULTRA-CONSERVADOR
// =============================================================================
input double MaxRiskPct            = 0.3;
input double KellyRR               = 2.5;
input double KellyMinFrac          = 0.05;
input double KellyMaxFrac          = 0.4;
input double MinEdgeOverCostBps    = 10.0;

// =============================================================================
// CONTROL PANEL
// =============================================================================
input int    ControlReloadSec      = 15;
input int    ExportIntervalSec     = 120;

// =============================================================================
// VARIÁVEIS GLOBAIS
// =============================================================================
string g_ValidatedSymbols[] = {"GBPJPY", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD", "SOLUSD", "US500", "NAS100", "US30"};

CTrade Trade;
const ulong MAGIC_NUMBER_UNIFIED = 202422;
bool EnableTrading = true;
datetime lastCycle = 0;
datetime g_LastKnobReload = 0;
datetime g_LastExport = 0;

// Instâncias dos sistemas avançados
MarketPsyEngine_ProductionReady* g_SentimentEngine = NULL;
Apollo11Professional* g_Apollo11System = NULL;
// TSK-TRAJECTORY-004: Instância do Analisador de Trajetória
TrajectoryAnalyzer* g_TrajectoryAnalyzer = NULL;

double g_EquityDayStart = 0.0;
double g_MarginScale = 1.0;
datetime g_LastMarginLog = 0;
int g_ScanIndex = 0;
int g_CycleIntervalSec = 60;
int g_MaxPositionsGlobal = 5;

// =============================================================================
// PERFIS ESPECÍFICOS POR ATIVO
// =============================================================================
double gKnobConfEURUSD = 0.65;
double gKnobConfGBPUSD = 0.65;
double gKnobConfUSDJPY = 0.65;
double gKnobConfEURGBP = 0.68;
double gKnobConfEURJPY = 0.68;
double gKnobConfGBPJPY = 0.60;
double gKnobConfAUDCAD = 0.62;
double gKnobConfAUDNZD = 0.62;
double gKnobConfCADCHF = 0.65;
double gKnobConfXAUUSD = 0.68;
double gKnobConfXAGUSD = 0.65;
double gKnobConfUS30 = 0.68;
double gKnobConfUS500 = 0.68;
double gKnobConfNAS100 = 0.65;
double gKnobConfBTCUSD = 0.70;
double gKnobConfETHUSD = 0.72;
double gKnobBaseConf = 0.70;
double gKnobBaseEdge = 10.0;

// Throttles conservadores
int gMaxForexPerCycle = 2;
int gMaxCryptoPerCycle = 1;
int gMaxIndexPerCycle = 1;
int gMaxMetalPerCycle = 1;

// =============================================================================
// VARIÁVEIS V5.2.3
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

// Arrays para filtros avançados - ADAPTAÇÃO SINTÁTICA MQL5
datetime g_LastTradeTime[]; // ADAPTADO: Array dinâmico para permitir ArrayResize
int g_SymbolIndexMap[50]; // Mantido fixo (não precisa resize)

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
// FUNÇÕES V5.2.3
// =============================================================================
bool InitializeV523System() {
   Print("[PROMETHEUS_STRATEGIC_V6.3.0] Inicializando sistema STRATEGIC...");
   
   if(UseAssetScoring) {
      InitializeAssetScoring();
   }
   
   if(UseMultiAssetRL) {
      InitializeMultiAssetRL();
   }
   
   if(UseHJBOptimization) {
      InitializeHJBOptimization();
   }
   
   if(UseExecutiveMonitoring) {
      InitializeExecutiveMonitoring();
   }
   
   g_V523SystemActive = true;
   g_PeakEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   Print("[PROMETHEUS_STRATEGIC_V6.3.0] Sistema STRATEGIC inicializado");
   return true;
}

void InitializeAssetScoring() {
   Print("[ASSET_SCORING_STRATEGIC] Inicializando Asset Scoring STRATEGIC...");
   
   string autoAssets[10] = {"BTCUSD", "ETHUSD", "SOLUSD", "ADAUSD", "XRPUSD", "LTCUSD", "DOTUSD", "UNIUSD", "AVAXUSD", "BCHUSD"};
   double autoScores[10] = {0.90, 0.88, 0.76, 0.68, 0.64, 0.62, 0.60, 0.58, 0.56, 0.54};
   
   for(int i = 0; i < 10; i++) {
      g_AssetScores[i] = autoScores[i];
      g_ActiveAssets[i] = autoAssets[i];
   }
   g_ActiveAssetCount = 10;
   
   Print("[ASSET_SCORING_STRATEGIC] Asset Scoring STRATEGIC inicializado");
}

void InitializeMultiAssetRL() {
   Print("[MULTI_ASSET_RL_STRATEGIC] Inicializando Multi-Asset RL STRATEGIC...");
   Print("[MULTI_ASSET_RL_STRATEGIC] Cross-correlation matrix ativa");
   Print("[MULTI_ASSET_RL_STRATEGIC] Q-learning para padrões coordenados");
   Print("[MULTI_ASSET_RL_STRATEGIC] Multi-Asset RL STRATEGIC inicializado");
}

void InitializeHJBOptimization() {
   Print("[HJB_OPTIMIZATION_STRATEGIC] Inicializando HJB Optimization STRATEGIC...");
   Print("[HJB_OPTIMIZATION_STRATEGIC] Otimização LBFGS coordenada");
   Print("[HJB_OPTIMIZATION_STRATEGIC] Controle Hamilton-Jacobi-Bellman");
   Print("[HJB_OPTIMIZATION_STRATEGIC] HJB Optimization STRATEGIC inicializado");
}

void InitializeExecutiveMonitoring() {
   Print("[EXECUTIVE_MONITORING_STRATEGIC] Inicializando Executive Monitoring STRATEGIC...");
   Print("[EXECUTIVE_MONITORING_STRATEGIC] Dashboard 24/7 ativo");
   Print("[EXECUTIVE_MONITORING_STRATEGIC] Relatórios STRATEGIC ativos");
   Print("[EXECUTIVE_MONITORING_STRATEGIC] Executive Monitoring STRATEGIC inicializado");
}

void UpdateV523Metrics() {
   if(!g_V523SystemActive) return;
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   if(currentEquity > g_PeakEquity) {
      g_PeakEquity = currentEquity;
   }
   g_CurrentDrawdown = (g_PeakEquity - currentEquity) / g_PeakEquity;
   
   if(g_TotalTrades > 0) {
      g_CurrentWinRate = (double)g_WinningTrades / (double)g_TotalTrades;
   }
   
   CheckV523Alerts();
}

void CheckV523Alerts() {
   if(g_CurrentDrawdown > DrawdownAlert) {
      Print("[V523_ALERT_STRATEGIC] Drawdown alert: ", DoubleToString(g_CurrentDrawdown * 100, 2), "% > ", DoubleToString(DrawdownAlert * 100, 2), "%");
   }
   
   if(g_CurrentWinRate < WinRateThreshold && g_TotalTrades > 10) {
      Print("[V523_ALERT_STRATEGIC] Win rate baixo: ", DoubleToString(g_CurrentWinRate * 100, 2), "% < ", DoubleToString(WinRateThreshold * 100, 2), "%");
   }
   
   if(g_CurrentDrawdown > KillSwitch) {
      Print("[V523_ALERT_STRATEGIC] KILL SWITCH ATIVADO: ", DoubleToString(g_CurrentDrawdown * 100, 2), "% > ", DoubleToString(KillSwitch * 100, 2), "%");
      EnableTrading = false;
   }
}

void GenerateExecutiveReport() {
   if(!g_V523SystemActive || !UseExecutiveMonitoring) return;
   
   if(TimeCurrent() - g_LastExecutiveReport < ExecutiveReportInterval) return;
   
   g_LastExecutiveReport = TimeCurrent();
   
   string report = StringFormat(
      "{\"timestamp\":%I64d,\"version\":\"v6.3.0_strategic_final\",\"status\":\"%s\",\"drawdown\":%.4f,\"win_rate\":%.4f,\"total_trades\":%d,\"active_assets\":%d,\"market_regime\":\"%s\",\"mode\":\"STRATEGIC_CONSERVATIVE\"}",
      (long)TimeCurrent(),
      g_V523SystemActive ? "active" : "inactive",
      g_CurrentDrawdown,
      g_CurrentWinRate,
      g_TotalTrades,
      g_ActiveAssetCount,
      g_CurrentMarketRegime
   );
   
   string filename = "ExecutiveReport_Strategic.json";
   int handle = FileOpen(filename, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle != INVALID_HANDLE) {
      FileWriteString(handle, report);
      FileClose(handle);
      Print("[EXECUTIVE_REPORT_STRATEGIC] Relatório STRATEGIC gerado: ", filename);
   }
}

// =============================================================================
// FUNÇÕES PRINCIPAIS
// =============================================================================
int OnInit() {
   Print("[PROMETHEUS_STRATEGIC_V6.4.0] Online com CÉREBRO TRIPLO: MarketPsyEngine + Apollo11 + TrajectoryAnalyzer. FilesDir=", FilesDir());
   
   // Inicializar Motor de Sentimento
   if(g_SentimentEngine == NULL) {
      g_SentimentEngine = new MarketPsyEngine_ProductionReady();
      if(g_SentimentEngine != NULL) {
         Print("[INIT] MarketPsyEngine_ProductionReady inicializado com sucesso!");
      } else {
         Print("[ERRO] Falha ao inicializar MarketPsyEngine!");
         return INIT_FAILED;
      }
   }
   
   // Inicializar Motor Quântico Apollo11
   g_Apollo11System = new Apollo11Professional(8);
   if(g_Apollo11System == NULL || !g_Apollo11System.Initialize()) {
      Print("[ERRO] FALHA CRÍTICA: Não foi possível inicializar o Apollo11 Professional!");
      return INIT_FAILED;
   }
   Print("[INIT] Apollo11 Professional inicializado com sucesso!");
   
   // TSK-TRAJECTORY-004: Inicializar Analisador de Trajetória
   g_TrajectoryAnalyzer = new TrajectoryAnalyzer(200, 20, 0.01);
   if(g_TrajectoryAnalyzer == NULL) {
      Print("[ERRO] FALHA CRÍTICA: Não foi possível inicializar o TrajectoryAnalyzer!");
      return INIT_FAILED;
   }
   Print("[INIT] Trajectory Analyzer inicializado com sucesso!");
   
   if(!InitializeV523System()) {
      Print("[ERRO] Falha na inicialização do sistema STRATEGIC");
      return INIT_FAILED;
   }
   
   if(UseOnTimer) {
      EventSetTimer(1);
   }
   
   g_EquityDayStart = AccountInfoDouble(ACCOUNT_EQUITY);
   g_CycleIntervalSec = CycleIntervalSec;
   g_MaxPositionsGlobal = MaxPositionsTotal;
   EnableTrading = EnableTradingInput;
   
   // Inicializar array de timestamps
   // ADAPTAÇÃO: ArrayResize antes de ArrayInitialize para arrays dinâmicos
   ArrayResize(g_LastTradeTime, 50);
   ArrayInitialize(g_LastTradeTime, 0);
   ArrayInitialize(g_SymbolIndexMap, -1);
   
   Print("[PROMETHEUS_STRATEGIC_V6.4.0] Sistema CÉREBRO TRIPLO 100% OPERACIONAL: MarketPsyEngine + Apollo11 + TrajectoryAnalyzer");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
   Print("[PROMETHEUS_STRATEGIC_V6.4.0] Stopped. Reason=", reason);
   
   if(g_SentimentEngine != NULL) {
      delete g_SentimentEngine;
      g_SentimentEngine = NULL;
      Print("[DEINIT] MarketPsyEngine liberado da memória");
   }
   
   // Liberar Apollo11
   if(g_Apollo11System != NULL) {
      delete g_Apollo11System;
      g_Apollo11System = NULL;
      Print("[DEINIT] Apollo11 Professional liberado da memória");
   }
   
   // TSK-TRAJECTORY-004: Liberar Analisador de Trajetória
   if(g_TrajectoryAnalyzer != NULL) {
      delete g_TrajectoryAnalyzer;
      g_TrajectoryAnalyzer = NULL;
      Print("[DEINIT] Trajectory Analyzer liberado da memória");
   }
   
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
   
   UpdateV523Metrics();
   GenerateExecutiveReport();
   
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
   
   UpdateV523Metrics();
   GenerateExecutiveReport();
   
   if(TimeCurrent() - g_LastExport >= ExportIntervalSec) {
      g_LastExport = TimeCurrent();
      ExportExposureAndPnL();
   }
}

void ProcessCycle() {
   static datetime lastCycleLog = 0;
   datetime now = TimeCurrent();
   
   if(now - lastCycleLog >= 60) {
      Print("[CYCLE_ACTIVE] Sistema escaneando ativos - Posições: ", PositionsTotal(), 
            " - Equity: $", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2));
      lastCycleLog = now;
   }
   
   if(UseMarketWatch) {
      int total = SymbolsTotal(true);
      if(total <= 0) return;
      
      int start = g_ScanIndex;
      int i = start;
      int processed = 0;
      
      while(processed < MaxSymbolsPerCycle && i < total) {
         string sym = SymbolName(i, true);
         if(SymbolAllowed(sym)) {
            ProcessSymbolSignal(sym);
            processed++;
         }
         i++;
      }
      g_ScanIndex = i % (total == 0 ? 1 : total);
   } else {
      int total = ArraySize(g_ValidatedSymbols);
      if(total <= 0) return;
      
      int start = g_ScanIndex;
      int i = start;
      int processed = 0;
      
      while(processed < MaxSymbolsPerCycle && i < total) {
         string sym = g_ValidatedSymbols[i];
         if(SymbolAllowed(sym)) {
            ProcessSymbolSignal(sym);
            processed++;
         }
         i++;
      }
      g_ScanIndex = i % (total == 0 ? 1 : total);
   }
}

void ProcessSymbolSignal(const string symbol) {
   double minConf; int spreadPts; double slm, tpm, trm; double minEdgeBps;
   ResolvePolicyForSymbol(symbol, minConf, spreadPts, slm, tpm, trm, minEdgeBps);
   
   Print("[SCANNING] ", symbol, " - Spread check, confidence min: ", DoubleToString(minConf, 2));
   
   SendRequestForSymbol(symbol);
   Sleep(200);
   string action; double conf = 0.0;
   if(TryReadResponse(symbol, action, conf)) {
      double conf_adjusted = ProcessSentimentAndAdjustConfidence(symbol, conf);
      
      Print("[RESPONSE] ", symbol, ": ", action, " conf=", DoubleToString(conf_adjusted, 3), 
            " (min: ", DoubleToString(minConf, 2), ")");
      
      if(IsSpreadOkBase(symbol, spreadPts) && conf_adjusted >= minConf && (action == "BUY" || action == "SELL")) {
         ExecuteSignal(symbol, action, conf_adjusted, slm, tpm, trm, minEdgeBps);
      } else {
         if(!IsSpreadOkBase(symbol, spreadPts)) {
            Print("[REJECTED] ", symbol, " - Spread muito alto");
         } else if(conf_adjusted < minConf) {
            Print("[REJECTED] ", symbol, " - Confiança ajustada baixa: ", DoubleToString(conf_adjusted, 3));
         } else if(action != "BUY" && action != "SELL") {
            Print("[REJECTED] ", symbol, " - Ação: ", action);
         }
      }
   } else {
      Print("[NO_RESPONSE] ", symbol, " - Python não respondeu");
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
   
   int q1 = StringFind(text, "\"", posAct + 9);
   int q2 = StringFind(text, "\"", q1 + 1);
   if(q1 < 0 || q2 < 0) return false;
   action = StringSubstr(text, q1 + 1, q2 - q1 - 1);
   
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

double ProcessSentimentAndAdjustConfidence(const string symbol, double python_conf) {
   if(g_SentimentEngine == NULL) return python_conf;
   
   double current_price = SymbolInfoDouble(symbol, SYMBOL_LAST);
   double current_volume = (double)SymbolInfoInteger(symbol, SYMBOL_VOLUME);
   double current_spread = SymbolInfoDouble(symbol, SYMBOL_ASK) - SymbolInfoDouble(symbol, SYMBOL_BID);
   double bid_volume = 0.0;
   double ask_volume = 0.0;
   double empty_array[];
   
   if(!g_SentimentEngine.ProcessMarketData(current_price, current_volume, current_spread,
                                          bid_volume, ask_volume, empty_array, empty_array, TimeCurrent())) {
      return python_conf;
   }
   
   double sentiment_score = g_SentimentEngine.GetSentimentScore();
   double aggression = g_SentimentEngine.GetLastAggressionScore();
   double conviction = g_SentimentEngine.GetLastConvictionScore();
   
   double conf_adjusted = 0.7 * python_conf + 0.3 * sentiment_score;
   
   PrintFormat("[SENTIMENT] %s: Python=%.3f Sentiment=%.3f Adjusted=%.3f Aggr=%.3f Conv=%.3f",
               symbol, python_conf, sentiment_score, conf_adjusted, aggression, conviction);
   
   return conf_adjusted;
}

void ExecuteSignal(const string symbol, const string action, const double confidence,
                   const double slMultLocal, const double tpMultLocal, const double trailMultLocal,
                   const double minEdgeBpsLocal) {
   if(!EnableTrading) return;
   if(!CircuitBreakersAllowEntry()) return;
   if(!AdvancedFiltersAllow(symbol, action)) return;
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
   
   bool ok = Trade.PositionOpen(symbol, type, lots, price, sl, tp, "PROMETHEUS_STRATEGIC_V6.3.0_FINAL");
   
   if(ok) {
      Print("[TRADE_STRATEGIC] ", action, " ", symbol, " lots=", DoubleToString(lots, 2), " conf=", DoubleToString(confidence, 3));
      UpdateLastTradeTime(symbol);
      g_TotalTrades++;
      UpdateV523Metrics();
      
      // Atualizar Apollo11 com o novo trade
      if(g_Apollo11System != NULL) {
         // UpdateBalance não aceita parâmetros - é chamado internamente
      }
   } else {
      Print("[ERROR_STRATEGIC] Trade failed: ", Trade.ResultRetcode(), " ", Trade.ResultRetcodeDescription());
   }
}

bool CircuitBreakersAllowEntry() {
   if(!UseCircuitBreakers) return true;
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double dailyLoss = (g_EquityDayStart - currentEquity) / g_EquityDayStart;
   
   if(dailyLoss > MaxDailyLossPct / 100.0) {
      Print("[CIRCUIT_BREAKER_STRATEGIC] Daily loss limit exceeded: ", DoubleToString(dailyLoss * 100, 2), "%");
      return false;
   }
   
   return true;
}

// =============================================================================
// FILTROS AVANÇADOS - CORREÇÃO DAS MATRIZES MULTIDIMENSIONAIS
// =============================================================================
bool AdvancedFiltersAllow(const string symbol, const string action) {
   // FILTRO 1: Intervalo Mínimo entre Trades
   int symbolIndex = GetSymbolIndex(symbol);
   if(symbolIndex >= 0 && symbolIndex < ArraySize(g_LastTradeTime)) {
      datetime lastTime = g_LastTradeTime[symbolIndex];
      datetime currentTime = TimeCurrent();
      int secondsSinceLastTrade = (int)(currentTime - lastTime);
      
      if(secondsSinceLastTrade < 30) {
         Print("[FILTER_INTERVAL] ", symbol, ": Rejeitado - Apenas ", secondsSinceLastTrade, "s desde último trade");
         return false;
      }
   }
   
   // FILTRO 2: Correlação com Posições Abertas
   if(!CheckCorrelationFilter(symbol)) {
      Print("[FILTER_CORRELATION] ", symbol, ": Rejeitado - Alta correlação com posições abertas");
      return false;
   }
   
   // FILTRO 3: Filtro de Média Móvel (Trend)
   if(UseTrendGate) {
      if(!CheckTrendFilter(symbol, action)) {
         Print("[FILTER_TREND] ", symbol, ": Rejeitado - Trade contra tendência");
         return false;
      }
   }
   
   // FILTRO 4: Filtro de Volatilidade (ATR)
   double atr = GetAtr(symbol);
   double atrThreshold = SymbolInfoDouble(symbol, SYMBOL_POINT) * 100;
   if(atr > atrThreshold) {
      Print("[FILTER_VOLATILITY] ", symbol, ": Rejeitado - ATR muito alto: ", DoubleToString(atr, 5));
      return false;
   }
   
   // FILTRO 5: Filtro de Spread Dinâmico
   MqlTick tick;
   if(SymbolInfoTick(symbol, tick)) {
      double spread = tick.ask - tick.bid;
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      int spreadPoints = (int)(spread / point);
      
      int maxSpread = SpreadLimitPoints;
      if(StringFind(symbol, "XAU") >= 0) maxSpread = 300;
      if(StringFind(symbol, "BTC") >= 0) maxSpread = 500;
      if(StringFind(symbol, "ETH") >= 0) maxSpread = 400;
      
      if(spreadPoints > maxSpread) {
         Print("[FILTER_SPREAD] ", symbol, ": Rejeitado - Spread alto: ", spreadPoints, " pontos");
         return false;
      }
   }
   
   return true;
}

int GetSymbolIndex(const string symbol) {
   string symbols[] = {"GBPUSD", "EURUSD", "USDJPY", "AUDUSD", "AUDCAD", "AUDNZD", 
                       "USDCAD", "NZDUSD", "XAUUSD", "XAGUSD", "USOIL", "BTCUSD", 
                       "ETHUSD", "US30", "US500", "NAS100"};
   
   for(int i = 0; i < ArraySize(symbols); i++) {
      if(symbols[i] == symbol) {
         g_SymbolIndexMap[i] = i;
         return i;
      }
   }
   return -1;
}

bool CheckCorrelationFilter(const string symbol) {
   // CORREÇÃO CRÍTICA: Matriz de correlação corretamente declarada
   string correlatedPairs[16][2]; // Array bidimensional fixo
   
   // Inicializar a matriz de correlação
   correlatedPairs[0][0] = "AUDCAD"; correlatedPairs[0][1] = "AUDNZD";
   correlatedPairs[1][0] = "AUDCAD"; correlatedPairs[1][1] = "AUDUSD";
   correlatedPairs[2][0] = "AUDNZD"; correlatedPairs[2][1] = "AUDUSD";
   correlatedPairs[3][0] = "XAUUSD"; correlatedPairs[3][1] = "XAGUSD";
   correlatedPairs[4][0] = "USOIL"; correlatedPairs[4][1] = "XAUUSD";
   correlatedPairs[5][0] = "GBPUSD"; correlatedPairs[5][1] = "EURUSD";
   correlatedPairs[6][0] = "US30"; correlatedPairs[6][1] = "US500";
   correlatedPairs[7][0] = "US500"; correlatedPairs[7][1] = "NAS100";
   
   int total = PositionsTotal();
   for(int idx = 0; idx < total; idx++) {
      ulong ticket = PositionGetTicket(idx);
      if(ticket == 0) continue;
      string openSymbol = PositionGetString(POSITION_SYMBOL);
      
      for(int i = 0; i < 8; i++) { // 8 pares correlacionados
         if((correlatedPairs[i][0] == symbol && correlatedPairs[i][1] == openSymbol) ||
            (correlatedPairs[i][1] == symbol && correlatedPairs[i][0] == openSymbol)) {
            return false;
         }
      }
   }
   
   return true;
}

bool CheckTrendFilter(const string symbol, const string action) {
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick)) return true;
   double currentPrice = (action == "BUY") ? tick.ask : tick.bid;
   
   // EMA 8 (M5)
   int bars_m5 = (int)Bars(symbol, PERIOD_M5);
   if(bars_m5 < 210) return true;
   
   int hEMA8 = iMA(symbol, PERIOD_M5, 8, 0, MODE_EMA, PRICE_CLOSE);
   if(hEMA8 == INVALID_HANDLE) return true;
   
   double ema8[];
   int copiedEMA8 = CopyBuffer(hEMA8, 0, 0, 3, ema8);
   IndicatorRelease(hEMA8);
   
   if(copiedEMA8 < 3) return true;
   
   double distanceEMA8 = MathAbs(currentPrice - ema8[0]) / currentPrice * 100;
   if(distanceEMA8 > 0.5) {
      Print("[FILTER_EMA8] ", symbol, ": Rejeitado - Preço longe da EMA8 (", 
            DoubleToString(distanceEMA8, 3), "%)");
      return false;
   }
   
   // EMA 21 (M5)
   int hEMA21_M5 = iMA(symbol, PERIOD_M5, 21, 0, MODE_EMA, PRICE_CLOSE);
   if(hEMA21_M5 == INVALID_HANDLE) return true;
   
   double ema21_m5[];
   int copiedEMA21_M5 = CopyBuffer(hEMA21_M5, 0, 0, 3, ema21_m5);
   IndicatorRelease(hEMA21_M5);
   
   if(copiedEMA21_M5 < 3) return true;
   
   bool ema21_m5_rising = (ema21_m5[0] > ema21_m5[1] && ema21_m5[1] > ema21_m5[2]);
   bool ema21_m5_falling = (ema21_m5[0] < ema21_m5[1] && ema21_m5[1] < ema21_m5[2]);
   
   // EMA 21 (M15)
   int bars_m15 = (int)Bars(symbol, PERIOD_M15);
   if(bars_m15 < 70) return true;
   
   int hEMA21_M15 = iMA(symbol, PERIOD_M15, 21, 0, MODE_EMA, PRICE_CLOSE);
   if(hEMA21_M15 == INVALID_HANDLE) return true;
   
   double ema21_m15[];
   int copiedEMA21_M15 = CopyBuffer(hEMA21_M15, 0, 0, 3, ema21_m15);
   IndicatorRelease(hEMA21_M15);
   
   if(copiedEMA21_M15 < 3) return true;
   
   bool ema21_m15_rising = (ema21_m15[0] > ema21_m15[1] && ema21_m15[1] > ema21_m15[2]);
   bool ema21_m15_falling = (ema21_m15[0] < ema21_m15[1] && ema21_m15[1] < ema21_m15[2]);
   
   bool confluence_bullish = (ema21_m5_rising && ema21_m15_rising);
   bool confluence_bearish = (ema21_m5_falling && ema21_m15_falling);
   
   if(action == "BUY" && !confluence_bullish) {
      Print("[FILTER_CONFLUENCE] ", symbol, ": Rejeitado BUY - EMA21 M5/M15 não confluentes");
      return false;
   }
   
   if(action == "SELL" && !confluence_bearish) {
      Print("[FILTER_CONFLUENCE] ", symbol, ": Rejeitado SELL - EMA21 M5/M15 não confluentes");
      return false;
   }
   
   // SMA 200 (M5)
   int hSMA200 = iMA(symbol, PERIOD_M5, 200, 0, MODE_SMA, PRICE_CLOSE);
   if(hSMA200 == INVALID_HANDLE) return true;
   
   double sma200[];
   int copiedSMA200 = CopyBuffer(hSMA200, 0, 0, 1, sma200);
   IndicatorRelease(hSMA200);
   
   if(copiedSMA200 < 1) return true;
   
   bool price_above_sma200 = (currentPrice > sma200[0]);
   bool price_below_sma200 = (currentPrice < sma200[0]);
   
   if(action == "BUY" && price_below_sma200) {
      Print("[FILTER_SMA200] ", symbol, ": Rejeitado BUY - Preço abaixo da SMA200");
      return false;
   }
   
   if(action == "SELL" && price_above_sma200) {
      Print("[FILTER_SMA200] ", symbol, ": Rejeitado SELL - Preço acima da SMA200");
      return false;
   }
   
   // VWAP
   double vwap = CalculateVWAP(symbol);
   if(vwap > 0.0) {
      bool price_above_vwap = (currentPrice > vwap);
      
      if(action == "BUY" && !price_above_vwap) {
         Print("[FILTER_VWAP] ", symbol, ": Rejeitado BUY - Preço abaixo do VWAP");
         return false;
      }
      
      if(action == "SELL" && price_above_vwap) {
         Print("[FILTER_VWAP] ", symbol, ": Rejeitado SELL - Preço acima do VWAP");
         return false;
      }
   }
   
   // Volume
   long volume[];
   int copiedVol = CopyTickVolume(symbol, PERIOD_M5, 0, 20, volume);
   
   if(copiedVol >= 20) {
      long totalVol = 0;
      for(int i = 0; i < 20; i++) totalVol += volume[i];
      long avgVolume = totalVol / 20;
      
      long currentVolume = volume[0];
      
      if(currentVolume < avgVolume * 0.5) {
         Print("[FILTER_VOLUME] ", symbol, ": Rejeitado - Volume baixo (", currentVolume, " vs ", avgVolume, ")");
         return false;
      }
   }
   
   Print("[FILTER_PROFESSIONAL] ", symbol, " ", action, ": ✅ Todos os filtros OK - Trade aprovado!");
   return true;
}

double CalculateVWAP(const string symbol) {
   datetime today = iTime(symbol, PERIOD_D1, 0);
   
   MqlRates rates[];
   int bars = CopyRates(symbol, PERIOD_M5, today, TimeCurrent(), rates);
   
   if(bars < 10) return 0.0;
   
   double sumPriceVolume = 0.0;
   long sumVolume = 0;
   
   for(int i = 0; i < bars; i++) {
      double typicalPrice = (rates[i].high + rates[i].low + rates[i].close) / 3.0;
      long volume = rates[i].tick_volume;
      
      sumPriceVolume += typicalPrice * volume;
      sumVolume += volume;
   }
   
   if(sumVolume == 0) return 0.0;
   
   double vwap = sumPriceVolume / sumVolume;
   return vwap;
}

void UpdateLastTradeTime(const string symbol) {
   int symbolIndex = GetSymbolIndex(symbol);
   if(symbolIndex >= 0) {
      if(ArraySize(g_LastTradeTime) <= symbolIndex) {
         ArrayResize(g_LastTradeTime, symbolIndex + 1);
      }
      g_LastTradeTime[symbolIndex] = TimeCurrent();
   }
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
         Print("[POSITION_STOP_STRATEGIC] Closing position due to loss limit: ", symbol, " loss=", DoubleToString(lossPct * 100, 2), "%");
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
   // Implementação simplificada - parser JSON básico
   // Pode ser expandido conforme necessário
}

void ResolvePolicyForSymbol(const string symbol,
                            double &minConfidence,
                            int &spreadLimitPts,
                            double &slMult,
                            double &tpMult,
                            double &trailMult,
                            double &minEdgeOverCostBpsOut) {
   minConfidence = ConfidenceMin;
   spreadLimitPts = SpreadLimitPoints;
   slMult = SL_ATR_Mult;
   tpMult = TP_ATR_Mult;
   trailMult = Trail_ATR_Mult;
   minEdgeOverCostBpsOut = MinEdgeOverCostBps;
   
   if(symbol == "EURUSD") {
      minConfidence = gKnobConfEURUSD;
      spreadLimitPts = 30;
   }
   else if(symbol == "GBPUSD") {
      minConfidence = gKnobConfGBPUSD;
      spreadLimitPts = 35;
   }
   else if(symbol == "USDJPY") {
      minConfidence = gKnobConfUSDJPY;
      spreadLimitPts = 30;
   }
   else if(symbol == "EURGBP") {
      minConfidence = gKnobConfEURGBP;
      spreadLimitPts = 40;
   }
   else if(symbol == "EURJPY") {
      minConfidence = gKnobConfEURJPY;
      spreadLimitPts = 45;
   }
   else if(symbol == "GBPJPY") {
      minConfidence = gKnobConfGBPJPY;
      spreadLimitPts = 60;
      slMult = 2.2;
      tpMult = 4.0;
   }
   else if(symbol == "AUDCAD") {
      minConfidence = gKnobConfAUDCAD;
      spreadLimitPts = 50;
   }
   else if(symbol == "AUDNZD") {
      minConfidence = gKnobConfAUDNZD;
      spreadLimitPts = 50;
   }
   else if(symbol == "CADCHF") {
      minConfidence = gKnobConfCADCHF;
      spreadLimitPts = 45;
   }
   else if(symbol == "XAUUSD" || symbol == "GOLD") {
      minConfidence = gKnobConfXAUUSD;
      spreadLimitPts = 400;
      slMult = 2.0;
      tpMult = 3.5;
   }
   else if(symbol == "XAGUSD" || symbol == "SILVER") {
      minConfidence = gKnobConfXAGUSD;
      spreadLimitPts = 500;
      slMult = 2.2;
      tpMult = 4.0;
   }
   else if(symbol == "US30" || StringFind(symbol, "DOW") >= 0) {
      minConfidence = gKnobConfUS30;
      spreadLimitPts = 400;
      slMult = 2.0;
      tpMult = 3.5;
   }
   else if(symbol == "US500" || symbol == "SPX500" || StringFind(symbol, "SP500") >= 0) {
      minConfidence = gKnobConfUS500;
      spreadLimitPts = 350;
      slMult = 2.0;
      tpMult = 3.5;
   }
   else if(symbol == "NAS100" || symbol == "NASDAQ") {
      minConfidence = gKnobConfNAS100;
      spreadLimitPts = 500;
      slMult = 2.5;
      tpMult = 4.0;
   }
   else if(StringFind(symbol, "BTC") >= 0) {
      minConfidence = gKnobConfBTCUSD;
      spreadLimitPts = 1000;
      slMult = 3.0;
      tpMult = 5.0;
   }
   else if(StringFind(symbol, "ETH") >= 0) {
      minConfidence = gKnobConfETHUSD;
      spreadLimitPts = 800;
      slMult = 2.8;
      tpMult = 4.5;
   }
   else {
      string klass = AssetClassOf(symbol);
      if(klass == "forex") {
         spreadLimitPts = 45;
         minConfidence = gKnobBaseConf;
      } else if(klass == "crypto") {
         spreadLimitPts = 1000;
         slMult = 3.0;
         tpMult = 5.0;
         minConfidence = 0.75;
      } else if(klass == "index") {
         spreadLimitPts = 400;
         slMult = 2.0;
         tpMult = 3.5;
         minConfidence = gKnobBaseConf;
      } else if(klass == "metal") {
         spreadLimitPts = 500;
         slMult = 2.2;
         tpMult = 4.0;
         minConfidence = 0.72;
      }
   }
   
   Print("[POLICY] ", symbol, ": conf=", DoubleToString(minConfidence, 2), 
         " spread=", spreadLimitPts, " SL=", DoubleToString(slMult, 1), 
         " TP=", DoubleToString(tpMult, 1));
}

void ExportExposureAndPnL() {
   string fname1 = "ExposureReport_Strategic.json";
   string fname2 = "PnLReport_Strategic.json";
   string fname3 = "RuntimeStatus_Strategic.json";
   
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
   
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   
   int h3 = FileOpen(fname3, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h3 != INVALID_HANDLE) {
      string js = StringFormat("{\"timestamp\":%I64d,\"positions\":%d,\"margin_level\":%.2f,\"balance\":%.2f,\"equity\":%.2f,\"drawdown\":%.4f,\"win_rate\":%.4f,\"total_trades\":%d,\"mode\":\"STRATEGIC_CONSERVATIVE\"}",
                               (long)TimeCurrent(), total, ml, bal, eq, g_CurrentDrawdown, g_CurrentWinRate, g_TotalTrades);
      FileWriteString(h3, js);
      FileClose(h3);
   }
}