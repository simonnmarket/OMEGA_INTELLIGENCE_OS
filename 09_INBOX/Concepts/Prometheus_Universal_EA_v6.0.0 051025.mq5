#property strict
#property copyright "PROMETHEUS_UNIVERSAL_SYSTEM"
#property version   "6.0.0"
#property description "Prometheus Universal EA v6.0.0 - Multi-Asset Generic Trading System"

#include <Trade/Trade.mqh>

input bool   UseMarketWatch        = false;  // processar apenas _Symbol para reduzir I/O
input int    MaxSymbolsPerCycle    = 5;      // reduzir varredura por ciclo
input int    CycleIntervalSec      = 15;     // intervalos mais longos para aliviar filesystem
input bool   UseOnTimer            = true;   // aciona ciclos a cada 1s, independente de ticks
input double ConfidenceMin         = 0.62;
input bool   EnableTrading         = true;
input int    MaxOpenPerSymbol      = 1;
input int    SpreadLimitPoints     = 200;
input bool   AutoTune              = false;  // auto inicialização e calibração (desativado por padrão para estabilidade)
input bool   MaxPotentialMode      = false;  // modo agressivo desativado por padrão
input int    MaxPositionsTotal     = 100;    // guarda‑chuva de risco por total de posições
input double MinMarginLevelPct     = 250.0;  // mínimo nível de margem para permitir novas entradas
// Gate adaptativo de margem (evita bloqueio total)
input bool   AdaptiveMarginGate    = true;   // se true, reduz risco ao invés de bloquear
input double OpMarginMinPct        = 110.0;  // margem mínima operacional para permitir qualquer entrada
input double MarginT1              = 150.0;  // abaixo deste nível aplica escala baixa
input double MarginT2              = 250.0;  // abaixo deste nível aplica escala média
input double MarginScaleLowPct     = 0.25;   // fração de risco quando ml < MarginT1
input double MarginScaleMidPct     = 0.50;   // fração de risco quando MarginT1<=ml<MarginT2
// Circuit breakers institucionais
input bool   UseCircuitBreakers    = true;
input double MaxDailyLossPct       = 3.0;    // stop diário (% de equity do início do dia)
input double MaxPositionLossPct    = 1.0;    // stop por posição (% do saldo)
// Session filter (terminal local time)
input bool   UseSessionFilter      = false;
input int    SessionStartHour      = 7;
input int    SessionEndHour        = 20;
// Trend gate (simple MA filter)
input bool   UseTrendGate          = true;
input int    FastMAPeriod          = 20;
input int    SlowMAPeriod          = 50;
// ATR-based SL/TP and trailing
input ENUM_TIMEFRAMES AtrTF        = PERIOD_M5;
input int    AtrPeriod             = 14;
input double SL_ATR_Mult           = 2.0;
input double TP_ATR_Mult           = 3.0;
input double Trail_ATR_Mult        = 1.5;
// Risk management (Kelly-based cap)
input double MaxRiskPct            = 0.5;   // % of balance per trade cap
input double KellyRR               = 1.5;   // reward:risk assumed
input double KellyMinFrac          = 0.05;  // 5% of Kelly
input double KellyMaxFrac          = 0.5;   // 50% of Kelly
// Edge vs Cost gate
input bool   UseEdgeCostGate       = false;
input double MinEdgeOverCostBps    = 8.0;   // edge must exceed cost by this bps
// Auditoria
input int    ExportIntervalSec     = 30;    // exportar Exposure/PnL a cada N segundos
// Mesa de som (controle dinâmico)
input int    ControlReloadSec      = 5;     // recarregar ControlPanel.json a cada N segundos

// Error codes used
#define ERR_INVALID_STOPS 130
#define ERR_MARKET_CLOSED 132

CTrade Trade;
datetime lastCycle = 0;
int      g_ScanIndex   = 0;
datetime g_LastExport   = 0;
double   g_EquityDayStart = 0.0;
bool     g_EmergencyStop  = false;
datetime g_LastKnobReload = 0;
// Overrides dinâmicos (mesa de som)
double   gKnobBaseConf = -1.0;
double   gKnobBaseEdge = -1.0;
double   gKnobConfForex = -1.0,  gKnobEdgeForex = -1.0;
double   gKnobConfCrypto = -1.0, gKnobEdgeCrypto = -1.0;
double   gKnobConfIndex = -1.0,  gKnobEdgeIndex = -1.0;
double   gKnobConfMetal = -1.0,  gKnobEdgeMetal = -1.0;
// Limites por classe por ciclo (mesa de som)
int      gMaxForexPerCycle  = 1000000;
int      gMaxCryptoPerCycle = 1000000;
int      gMaxIndexPerCycle  = 1000000;
int      gMaxMetalPerCycle  = 1000000;
int      gMaxEnergyPerCycle = 1000000;
int      gMaxEquityPerCycle = 1000000;
// Emergency remoto via ControlPanel
bool     g_RemoteEmergencyStop = false;
// Mixer de margem (globais)
double   gMixOpMin    = -1.0;  // op_margin_min
double   gMixT1       = -1.0;  // margin_t1
double   gMixT2       = -1.0;  // margin_t2
double   gMixScaleLow = -1.0;  // margin_scale_low_pct
double   gMixScaleMid = -1.0;  // margin_scale_mid_pct
// Mixer por classe (forex/crypto/index/metal/energy/equity)
double   gMixOpMinForex=-1.0, gMixT1Forex=-1.0, gMixT2Forex=-1.0, gMixLowForex=-1.0, gMixMidForex=-1.0;
double   gMixOpMinCrypto=-1.0, gMixT1Crypto=-1.0, gMixT2Crypto=-1.0, gMixLowCrypto=-1.0, gMixMidCrypto=-1.0;
double   gMixOpMinIndex=-1.0, gMixT1Index=-1.0, gMixT2Index=-1.0, gMixLowIndex=-1.0, gMixMidIndex=-1.0;
double   gMixOpMinMetal=-1.0, gMixT1Metal=-1.0, gMixT2Metal=-1.0, gMixLowMetal=-1.0, gMixMidMetal=-1.0;
double   gMixOpMinEnergy=-1.0, gMixT1Energy=-1.0, gMixT2Energy=-1.0, gMixLowEnergy=-1.0, gMixMidEnergy=-1.0;
double   gMixOpMinEquity=-1.0, gMixT1Equity=-1.0, gMixT2Equity=-1.0, gMixLowEquity=-1.0, gMixMidEquity=-1.0;
// Texto original do ControlPanel para overrides por símbolo
string   g_ControlPanelText = "";

// Auto-tuned runtime parameters
int    g_MaxSymbolsPerCycle = 30;
int    g_CycleIntervalSec   = 15;
int    g_SpreadLimitPoints  = 200;
double g_ConfidenceMin      = 0.60;
double g_MinEdgeOverCostBps = 5.0;
int    g_MaxPositionsGlobal = 100;
double g_MarginScale = 1.0;          // 0..1 escala de risco por margem
datetime g_LastMarginLog = 0;        // rate‑limit de log

string FilesDir() {
   // Common Files preferred
   string common = TerminalInfoString(TERMINAL_COMMONDATA_PATH)+"\\Files";
   return common;
}

bool MarginLevelOk() {
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   if(ml <= 0.0) return false;
   return (ml >= MinMarginLevelPct);
}

void ResolveMixerForSymbol(const string symbol,
                           double &opMin,
                           double &t1,
                           double &t2,
                           double &scaleLow,
                           double &scaleMid) {
   // defaults dos inputs
   opMin = OpMarginMinPct;
   t1 = MarginT1;
   t2 = MarginT2;
   scaleLow = MarginScaleLowPct;
   scaleMid = MarginScaleMidPct;
   // overrides globais
   if(gMixOpMin    > 0.0) opMin    = gMixOpMin;
   if(gMixT1       > 0.0) t1       = gMixT1;
   if(gMixT2       > 0.0) t2       = gMixT2;
   if(gMixScaleLow > 0.0) scaleLow = gMixScaleLow;
   if(gMixScaleMid > 0.0) scaleMid = gMixScaleMid;
   // overrides por classe
   string k = AssetClassOf(symbol);
   if(k == "forex") {
      if(gMixOpMinForex  > 0.0) opMin = gMixOpMinForex;
      if(gMixT1Forex     > 0.0) t1    = gMixT1Forex;
      if(gMixT2Forex     > 0.0) t2    = gMixT2Forex;
      if(gMixLowForex    > 0.0) scaleLow = gMixLowForex;
      if(gMixMidForex    > 0.0) scaleMid = gMixMidForex;
   } else if(k == "crypto") {
      if(gMixOpMinCrypto > 0.0) opMin = gMixOpMinCrypto;
      if(gMixT1Crypto    > 0.0) t1    = gMixT1Crypto;
      if(gMixT2Crypto    > 0.0) t2    = gMixT2Crypto;
      if(gMixLowCrypto   > 0.0) scaleLow = gMixLowCrypto;
      if(gMixMidCrypto   > 0.0) scaleMid = gMixMidCrypto;
   } else if(k == "index") {
      if(gMixOpMinIndex  > 0.0) opMin = gMixOpMinIndex;
      if(gMixT1Index     > 0.0) t1    = gMixT1Index;
      if(gMixT2Index     > 0.0) t2    = gMixT2Index;
      if(gMixLowIndex    > 0.0) scaleLow = gMixLowIndex;
      if(gMixMidIndex    > 0.0) scaleMid = gMixMidIndex;
   } else if(k == "metal") {
      if(gMixOpMinMetal  > 0.0) opMin = gMixOpMinMetal;
      if(gMixT1Metal     > 0.0) t1    = gMixT1Metal;
      if(gMixT2Metal     > 0.0) t2    = gMixT2Metal;
      if(gMixLowMetal    > 0.0) scaleLow = gMixLowMetal;
      if(gMixMidMetal    > 0.0) scaleMid = gMixMidMetal;
   } else if(k == "energy") {
      if(gMixOpMinEnergy > 0.0) opMin = gMixOpMinEnergy;
      if(gMixT1Energy    > 0.0) t1    = gMixT1Energy;
      if(gMixT2Energy    > 0.0) t2    = gMixT2Energy;
      if(gMixLowEnergy   > 0.0) scaleLow = gMixLowEnergy;
      if(gMixMidEnergy   > 0.0) scaleMid = gMixMidEnergy;
   } else if(k == "stock" || k == "etf" || k == "future") {
      if(gMixOpMinEquity > 0.0) opMin = gMixOpMinEquity;
      if(gMixT1Equity    > 0.0) t1    = gMixT1Equity;
      if(gMixT2Equity    > 0.0) t2    = gMixT2Equity;
      if(gMixLowEquity   > 0.0) scaleLow = gMixLowEquity;
      if(gMixMidEquity   > 0.0) scaleMid = gMixMidEquity;
   }
   // overrides por símbolo (do texto bruto)
   double v;
   string symKey = symbol + "_op_margin_min"; if(StringToValue(g_ControlPanelText, symKey, v)) opMin = v;
   symKey = symbol + "_margin_t1"; if(StringToValue(g_ControlPanelText, symKey, v)) t1 = v;
   symKey = symbol + "_margin_t2"; if(StringToValue(g_ControlPanelText, symKey, v)) t2 = v;
   symKey = symbol + "_margin_scale_low_pct"; if(StringToValue(g_ControlPanelText, symKey, v)) scaleLow = v;
   symKey = symbol + "_margin_scale_mid_pct"; if(StringToValue(g_ControlPanelText, symKey, v)) scaleMid = v;
}

void UpdateMarginScaleForSymbol(const string symbol) {
   if(!AdaptiveMarginGate) { g_MarginScale = 1.0; return; }
   double opMin, t1, t2, sLow, sMid;
   ResolveMixerForSymbol(symbol, opMin, t1, t2, sLow, sMid);
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   // Se não há posições, margem pode ser 0 → liberar com escala 1.0
   if(ml <= 0.0) { g_MarginScale = 1.0; return; }
   if(ml < opMin) { g_MarginScale = 0.0; return; }
   if(ml < t1) { g_MarginScale = MathMax(0.0, MathMin(1.0, sLow)); return; }
   if(ml < t2) { g_MarginScale = MathMax(0.0, MathMin(1.0, sMid)); return; }
   g_MarginScale = 1.0;
}

bool IsSpreadOkBase(const string symbol, const int limitPoints) {
   int spread = (int)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
   return (spread >= 0 && spread <= limitPoints);
}

bool SymbolAllowed(const string symbol) {
   // basic gates: tradable and session
   bool selected = SymbolInfoInteger(symbol, SYMBOL_SELECT) != 0;
   bool tradeMode = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_DISABLED;
   if(!(selected && tradeMode)) return false;
   if(UseSessionFilter) {
      MqlDateTime dt; TimeCurrent(dt);
      int h = dt.hour;
      if(SessionStartHour <= SessionEndHour) {
         if(!(h >= SessionStartHour && h < SessionEndHour)) return false;
      } else {
         // overnight window
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

void ResolvePolicyForSymbol(const string symbol,
                            double &minConfidence,
                            int    &spreadLimitPts,
                            double &slMult,
                            double &tpMult,
                            double &trailMult,
                            double &minEdgeOverCostBpsOut) {
   string klass = AssetClassOf(symbol);
   minConfidence = g_ConfidenceMin;
   spreadLimitPts = g_SpreadLimitPoints;
   slMult = SL_ATR_Mult;
   tpMult = TP_ATR_Mult;
   trailMult = Trail_ATR_Mult;
   minEdgeOverCostBpsOut = MinEdgeOverCostBps;

   // Mesa de som: overrides dinâmicos por classe
   if(gKnobBaseConf > 0.0) { minConfidence = gKnobBaseConf; }
   if(gKnobBaseEdge > 0.0) { minEdgeOverCostBpsOut = gKnobBaseEdge; }

   if(klass == "forex") {
      // forex normalmente spread baixo
      spreadLimitPts = (int)MathMax(30, MathMin(spreadLimitPts, 180));
      double c = MathMax(0.62, minConfidence);
      double e = MathMax(MinEdgeOverCostBps, 8.0);
      if(gKnobConfForex > 0.0) c = MathMax(c, gKnobConfForex);
      if(gKnobEdgeForex > 0.0) e = MathMax(e, gKnobEdgeForex);
      minConfidence = c; minEdgeOverCostBpsOut = e;
   } else if(klass == "crypto") {
      // crypto: spreads maiores e volatilidade
      spreadLimitPts = (int)MathMax(spreadLimitPts, 800);
      slMult = MathMax(slMult, 2.5);
      tpMult = MathMax(tpMult, 4.0);
      double c = MathMax(0.68, minConfidence);
      double e = MathMax(MinEdgeOverCostBps, 12.0);
      if(gKnobConfCrypto > 0.0) c = MathMax(c, gKnobConfCrypto);
      if(gKnobEdgeCrypto > 0.0) e = MathMax(e, gKnobEdgeCrypto);
      minConfidence = c; minEdgeOverCostBpsOut = e;
   } else if(klass == "index") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 350);
      double c = MathMax(0.64, minConfidence);
      double e = MathMax(MinEdgeOverCostBps, 9.0);
      if(gKnobConfIndex > 0.0) c = MathMax(c, gKnobConfIndex);
      if(gKnobEdgeIndex > 0.0) e = MathMax(e, gKnobEdgeIndex);
      minConfidence = c; minEdgeOverCostBpsOut = e;
   } else if(klass == "metal") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 400);
      slMult = MathMax(slMult, 2.2);
      tpMult = MathMax(tpMult, 3.2);
      double c = MathMax(0.64, minConfidence);
      double e = MathMax(MinEdgeOverCostBps, 9.0);
      if(gKnobConfMetal > 0.0) c = MathMax(c, gKnobConfMetal);
      if(gKnobEdgeMetal > 0.0) e = MathMax(e, gKnobEdgeMetal);
      minConfidence = c; minEdgeOverCostBpsOut = e;
   } else if(klass == "energy") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 400);
      slMult = MathMax(slMult, 2.2);
      tpMult = MathMax(tpMult, 3.5);
      minConfidence = MathMax(0.64, minConfidence);
      minEdgeOverCostBpsOut = MathMax(MinEdgeOverCostBps, 9.0);
   } else if(klass == "stock" || klass == "etf" || klass == "future") {
      spreadLimitPts = (int)MathMax(spreadLimitPts, 500);
      minConfidence = MathMax(0.66, minConfidence);
      minEdgeOverCostBpsOut = MathMax(MinEdgeOverCostBps, 10.0);
   }
}

int OnInit() {
   Print("[PROMETHEUS_UNIVERSAL_V6] Online. FilesDir=", FilesDir());
   if(UseOnTimer) {
      EventSetTimer(1);
   }
   // registrar equity inicial do dia
   g_EquityDayStart = AccountInfoDouble(ACCOUNT_EQUITY);
   g_EmergencyStop = false;

   if(AutoTune) {
      int symCount = SymbolsTotal(true);
      if(symCount <= 0) symCount = 50;

      // MaxSymbolsPerCycle: metade dos símbolos visíveis, limitado
      g_MaxSymbolsPerCycle = MathMax(10, MathMin(100, symCount/2));
      // CycleIntervalSec: mais símbolos => intervalo maior
      g_CycleIntervalSec = (symCount > 100 ? 30 : 15);
      // Confidence mínima padrão
      g_ConfidenceMin = 0.60;

      // Calibração de spread: 75º percentil * 1.5
      int n = MathMin(symCount, 512);
      int count = 0;
      int spreads[512];
      for(int i=0; i<symCount && count<n; i++) {
         string s = SymbolName(i, true);
         if(s == NULL || s == "") continue;
         int sp = (int)SymbolInfoInteger(s, SYMBOL_SPREAD);
         if(sp > 0) { spreads[count++] = sp; }
      }
      if(count > 0) {
         // simple selection of 75th percentile
         // insertion sort (small n)
         for(int a=1; a<count; a++) {
            int key = spreads[a];
            int b = a-1;
            while(b>=0 && spreads[b] > key) { spreads[b+1] = spreads[b]; b--; }
            spreads[b+1] = key;
         }
         int idx75 = (int)MathFloor(0.75 * (count-1));
         if(idx75 < 0) idx75 = 0; if(idx75 >= count) idx75 = count-1;
         int p75 = spreads[idx75];
         g_SpreadLimitPoints = (int)MathCeil(p75 * 1.5);
         if(g_SpreadLimitPoints < 50) g_SpreadLimitPoints = 50;
         if(g_SpreadLimitPoints > 2000) g_SpreadLimitPoints = 2000;
      } else {
         g_SpreadLimitPoints = 200;
      }

      // base edge
      g_MinEdgeOverCostBps = MinEdgeOverCostBps;

      // Modo agressivo (potencial máximo)
      if(MaxPotentialMode) {
         g_MaxSymbolsPerCycle = MathMin(150, MathMax(g_MaxSymbolsPerCycle, (int)MathFloor(symCount*0.4)));
         g_CycleIntervalSec   = MathMax(5, g_CycleIntervalSec - 5);
         g_ConfidenceMin      = MathMax(0.50, g_ConfidenceMin - 0.07);
         g_SpreadLimitPoints  = (int)MathMin(4000, MathCeil(g_SpreadLimitPoints * 1.5));
         g_MinEdgeOverCostBps = MathMax(1.0, g_MinEdgeOverCostBps - 3.0);
      }

      Print("[AUTOTUNE] sym=", symCount,
            " maxPerCycle=", g_MaxSymbolsPerCycle,
            " cycleSec=", g_CycleIntervalSec,
            " confMin=", DoubleToString(g_ConfidenceMin,2),
            " spreadPts=", g_SpreadLimitPoints,
            " edgeBps=", DoubleToString(g_MinEdgeOverCostBps,1));
   } else {
      g_MaxSymbolsPerCycle = MaxSymbolsPerCycle;
      g_CycleIntervalSec   = CycleIntervalSec;
      g_ConfidenceMin      = ConfidenceMin;
      g_SpreadLimitPoints  = SpreadLimitPoints;
      g_MinEdgeOverCostBps = MinEdgeOverCostBps;
   }

   g_MaxPositionsGlobal = MaxPositionsTotal;

   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {
   Print("[PROMETHEUS_UNIVERSAL_V6] Stopped. Reason=", reason);
   if(UseOnTimer) {
      EventKillTimer();
   }
}

void SendRequestForSymbol(const string symbol) {
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick)) return;
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   // Use FILE_COMMON e nome relativo para garantir gravação em Common/Files
   string fname = "AIRequest."+symbol+".json";
   string payload = StringFormat(
      "{\"symbol\":\"%s\",\"bid\":%.10f,\"ask\":%.10f,\"time\":%I64d,\"point\":%.10f}",
      symbol, tick.bid, tick.ask, (long)tick.time, point);
   int handle = FileOpen(fname, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle != INVALID_HANDLE) {
      FileWriteString(handle, payload);
      FileClose(handle);
      //Print("[REQ] ", path);
   }
}

bool TryReadResponse(const string symbol, string &action, double &confidence) {
   string tmpConfidence = "";
   double parsedConfidence = confidence;
   // Ler da Common/Files usando FILE_COMMON
   string fname = "AIResponse."+symbol+".json";
   int h = FileOpen(fname, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h == INVALID_HANDLE) return false;
   string text = FileReadString(h);
   FileClose(h);
   int posAct = StringFind(text, "\"action\":");
   int posConf = StringFind(text, "\"confidence\":");
   if(posAct < 0 || posConf < 0) return false;
   // crude extraction
   int q1 = StringFind(text, "\"", posAct+9);
   int q2 = StringFind(text, "\"", q1+1);
   if(q1 < 0 || q2 < 0) return false;
   action = StringSubstr(text, q1+1, q2-q1-1);
   // parse numeric value after "confidence":
   string key = "\"confidence\":";
   int keyLen = StringLen(key);
   int i = posConf + keyLen;
   int n = StringLen(text);
   // skip whitespace and colon (ASCII: space=32, tab=9, ':'=58)
   while(i < n)
   {
      int ch = StringGetCharacter(text, i);
      if(ch == 32 || ch == 9 || ch == 58) { i++; continue; }
      break;
   }
   int startNum = i;
   while(i < n)
   {
      int ch = StringGetCharacter(text, i);
      bool isDigit = (ch >= 48 && ch <= 57); // '0'..'9'
      if(!(isDigit || ch==46 || ch==45 || ch==43 || ch==101 || ch==69)) break; // . - + e E
      i++;
   }
   int endNum = i;
   if(endNum > startNum)
   {
      tmpConfidence = StringSubstr(text, startNum, endNum-startNum);
      parsedConfidence = StringToDouble(tmpConfidence);
   }
   confidence = parsedConfidence;
   // Remover após leitura (se possível, pode falhar silenciosamente)
   FileDelete(fname);
   return true;
}

int CountOpenPositions(const string symbol) {
   int total = PositionsTotal();
   int count = 0;
   for(int idx=0; idx<total; idx++) {
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
   if(bars < AtrPeriod+2) return 0.0;
   int h = iATR(symbol, AtrTF, AtrPeriod);
   if(h == INVALID_HANDLE) return 0.0;
   double buf[];
   int copied = CopyBuffer(h, 0, 0, 2, buf);
   IndicatorRelease(h);
   if(copied <= 0) return 0.0;
   return buf[0];
}

int GetMinStopDistancePoints(const string symbol) {
   // Minimal stop distance in points (broker requirement)
   int stopsPts = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(stopsPts < 0) stopsPts = 0;
   return stopsPts;
}

void EnsureMinStopDistance(const string symbol, const ENUM_ORDER_TYPE type, const double price,
                           double &sl, double &tp) {
   int minPts = GetMinStopDistancePoints(symbol);
   int freezePts = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   if(freezePts < 0) freezePts = 0;
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double tick  = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   if(point <= 0.0) return;
   if(tick <= 0.0) tick = point;
   double minDist = (minPts + freezePts + 2) * point; // inclui freeze + margem
   if(type == ORDER_TYPE_BUY) {
      if(sl > 0.0 && (price - sl) < minDist) sl = price - minDist;
      if(tp > 0.0 && (tp - price) < minDist) tp = price + minDist;
   } else {
      if(sl > 0.0 && (sl - price) < minDist) sl = price + minDist;
      if(tp > 0.0 && (price - tp) < minDist) tp = price - minDist;
   }
   // Normalizar para a grade de ticks do símbolo
   if(sl > 0.0) {
      sl = MathRound(sl / tick) * tick;
      sl = NormalizeDouble(sl, (int)MathMax(0.0, -MathLog10(tick)));
   }
   if(tp > 0.0) {
      tp = MathRound(tp / tick) * tick;
      tp = NormalizeDouble(tp, (int)MathMax(0.0, -MathLog10(tick)));
   }
}

bool TrySetStopsWithRetries(const string symbol,
                            const ENUM_ORDER_TYPE type,
                            double slIn,
                            double tpIn,
                            const int maxRetries = 3) {
   double sl = slIn, tp = tpIn;
   double factor = 1.0;
   for(int a=0; a<maxRetries; a++) {
      MqlTick t; if(!SymbolInfoTick(symbol, t)) return false;
      double price = (type == ORDER_TYPE_BUY ? t.ask : t.bid);
      int minPts = GetMinStopDistancePoints(symbol);
      int freezePts = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL);
      if(freezePts < 0) freezePts = 0;
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double tick  = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      if(tick <= 0.0) tick = point;
      double minDist = MathMax(0.0, (minPts + freezePts + 2) * point * factor);
      // recalcula respeitando preço atual
      if(type == ORDER_TYPE_BUY) {
         if(sl > 0.0 && (price - sl) < minDist) sl = price - minDist;
         if(tp > 0.0 && (tp - price) < minDist) tp = price + minDist;
      } else {
         if(sl > 0.0 && (sl - price) < minDist) sl = price + minDist;
         if(tp > 0.0 && (price - tp) < minDist) tp = price - minDist;
      }
      // Normalizar para grid de ticks
      if(sl > 0.0) { sl = MathRound(sl / tick) * tick; sl = NormalizeDouble(sl, (int)MathMax(0.0, -MathLog10(tick))); }
      if(tp > 0.0) { tp = MathRound(tp / tick) * tick; tp = NormalizeDouble(tp, (int)MathMax(0.0, -MathLog10(tick))); }
      ResetLastError();
      if(Trade.PositionModify(symbol, sl, tp)) {
         Print("[EXEC][STOPS] Applied SL/TP after retry ", a+1, " for ", symbol);
         return true;
      }
      factor *= 1.5; // ampliar afastamento
   }
   return false;
}

bool TrendAllows(const string symbol) {
   if(!UseTrendGate) return true;
   int bars = (int)Bars(symbol, PERIOD_M5);
   if(bars < MathMax(FastMAPeriod, SlowMAPeriod)+2) return true;
   int f = iMA(symbol, PERIOD_M5, FastMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   int s = iMA(symbol, PERIOD_M5, SlowMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   if(f == INVALID_HANDLE || s == INVALID_HANDLE) return true;
   double bf[2], bs[2];
   int c1 = CopyBuffer(f, 0, 0, 2, bf);
   int c2 = CopyBuffer(s, 0, 0, 2, bs);
   IndicatorRelease(f);
   IndicatorRelease(s);
   if(c1 < 2 || c2 < 2) return true;
   // simple trend: fast above slow -> uptrend
   return (bf[0] >= bs[0]);
}

double CalculateKellyRiskFraction(const double confidence) {
   double p = MathMin(MathMax(confidence, 0.0), 1.0);
   double r = MathMax(KellyRR, 0.1);
   double k = p - (1.0 - p) / r; // Kelly fraction of equity
   // clamp and scale
   double kScaled = MathMin(MathMax(k, 0.0), 1.0);
   double frac = MathMin(MathMax(kScaled, KellyMinFrac), KellyMaxFrac);
   return frac;
}

double CalculateLotsByRisk(const string symbol, const double stopDistancePrice, const double riskPct) {
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskMoney = balance * (riskPct/100.0);
   double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0.0 || tickValue <= 0.0 || stopDistancePrice <= 0.0) return 0.01;
   double ticks = stopDistancePrice / tickSize;
   if(ticks <= 0.0) return 0.01;
   double lots = riskMoney / (ticks * tickValue);
   double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double step  = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   if(step <= 0.0) step = 0.01;
   // round down to step
   double steps = MathFloor(lots/step);
   double lotsRounded = steps * step;
   lotsRounded = MathMax(minLot, MathMin(lotsRounded, maxLot));
   return lotsRounded;
}

void ComputeSLTP(const string symbol, const ENUM_ORDER_TYPE type, const double atr, double &sl, double &tp, const double slMultLocal, const double tpMultLocal) {
   sl = 0.0; tp = 0.0;
   MqlTick tick; if(!SymbolInfoTick(symbol, tick)) return;
   if(atr <= 0.0) return;
   if(type == ORDER_TYPE_BUY) {
      sl = tick.bid - slMultLocal * atr;
      tp = tick.ask + tpMultLocal * atr;
   } else {
      sl = tick.ask + slMultLocal * atr;
      tp = tick.bid - tpMultLocal * atr;
   }
}

bool EdgeBeatsCost(const string symbol, const double confidence, const double minEdgeBps) {
   if(!UseEdgeCostGate) return true;
   MqlTick t; if(!SymbolInfoTick(symbol, t)) return false;
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   int spreadPts = (int)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
   double spread = spreadPts * point;
   double mid = (t.ask + t.bid) * 0.5;
   if(mid <= 0.0) return false;
   double costBps = (spread / mid) * 10000.0; // approx bps
   double edgeBps = MathMax((confidence - 0.5) * 200.0, 0.0); // heuristic
   return (edgeBps - costBps) >= MathMin(minEdgeBps, g_MinEdgeOverCostBps);
}

bool CircuitBreakersAllowEntry() {
   if(!UseCircuitBreakers) return true;
   if(g_EmergencyStop || g_RemoteEmergencyStop) return false;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_EquityDayStart <= 0.0) g_EquityDayStart = eq;
   double dd = (g_EquityDayStart - eq) / g_EquityDayStart * 100.0;
   if(dd >= MaxDailyLossPct) {
      g_EmergencyStop = true;
      Print("[CB][DAILY] Emergency stop activated. dd=", DoubleToString(dd,2), "%");
      return false;
   }
   return true;
}

void EnforcePositionLossStops() {
   if(!UseCircuitBreakers || MaxPositionLossPct <= 0.0) return;
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double maxLossMoney = balance * (MaxPositionLossPct/100.0);
   int total = PositionsTotal();
   for(int i=0; i<total; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      double profit = PositionGetDouble(POSITION_PROFIT);
      if(profit < 0.0 && MathAbs(profit) >= maxLossMoney) {
         string sym = PositionGetString(POSITION_SYMBOL);
         Print("[CB][POS] Closing due to loss limit: ", sym, " loss=", DoubleToString(profit,2));
         Trade.PositionClose(sym);
      }
   }
}

void ExecuteSignal(const string symbol, const string action, const double confidence,
                   const double slMultLocal, const double tpMultLocal, const double trailMultLocal,
                   const double minEdgeBpsLocal) {
   if(!EnableTrading) return;
   if(!CircuitBreakersAllowEntry()) return;
   if(CountOpenPositions(symbol) >= MaxOpenPerSymbol) return;
   if(PositionsTotal() >= g_MaxPositionsGlobal) return;
   // Gate de margem adaptativo
   UpdateMarginScaleForSymbol(symbol);
   if(g_MarginScale <= 0.0) {
      if(TimeCurrent() - g_LastMarginLog >= 5) { Print("[RISK][BLOCK] Margin level too low. symbol=", symbol); g_LastMarginLog = TimeCurrent(); }
      return;
   }
   if(!TrendAllows(symbol)) return;
   if(!EdgeBeatsCost(symbol, confidence, minEdgeBpsLocal)) return;
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick)) return;

   ENUM_ORDER_TYPE type = ORDER_TYPE_BUY;
   double price = tick.ask;
   if(action == "SELL") { type = ORDER_TYPE_SELL; price = tick.bid; }

   Trade.SetExpertMagicNumber(777000);
   Trade.SetDeviationInPoints(10);
   double atr = GetAtr(symbol);
   double sl=0.0, tp=0.0;
   ComputeSLTP(symbol, type, atr, sl, tp, slMultLocal, tpMultLocal);
   EnsureMinStopDistance(symbol, type, price, sl, tp);

   double stopDistance = 0.0;
   if(type == ORDER_TYPE_BUY) stopDistance = (sl>0.0? (price - sl): 0.0); else stopDistance = (sl>0.0? (sl - price): 0.0);
   double kellyFrac = CalculateKellyRiskFraction(confidence);
   double riskPct = MathMin(MaxRiskPct, kellyFrac * MaxRiskPct);
   // aplica escala de margem
   riskPct *= g_MarginScale;
   double lots = CalculateLotsByRisk(symbol, stopDistance, riskPct);
   if(lots <= 0.0) lots = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);

   bool ok = Trade.PositionOpen(symbol, type, lots, price, sl, tp, "PROMETHEUS");
   if(!ok) {
      int err = _LastError;
      Print("[EXEC][FAIL] ", symbol, " action=", action, " err=", err);
      // Fallback geral: abrir sem SL/TP e modificar depois (cobre diferentes retcodes de invalid stops)
      ResetLastError();
      if(Trade.PositionOpen(symbol, type, lots, price, 0.0, 0.0, "PROMETHEUS")) {
         Sleep(120);
         if(!TrySetStopsWithRetries(symbol, type, sl, tp, 3)) {
            Print("[EXEC][RECOVER][WARN] Could not set SL/TP due to broker constraints: ", symbol);
         }
      }
      ResetLastError();
   } else {
      Print("[EXEC][OK] ", symbol, " action=", action);
   }
}

void UpdateTrailingStops() {
   if(Trail_ATR_Mult <= 0.0) return;
   int total = PositionsTotal();
   for(int i=0; i<total; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      string sym = PositionGetString(POSITION_SYMBOL);
      long type = PositionGetInteger(POSITION_TYPE);
      double priceOpen = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double tp = PositionGetDouble(POSITION_TP);
      MqlTick t; if(!SymbolInfoTick(sym, t)) continue;
      double atr = GetAtr(sym);
      if(atr <= 0.0) continue;
      double newSL = sl;
      if(type == POSITION_TYPE_BUY) {
         double trail = t.bid - Trail_ATR_Mult * atr;
         if(sl <= 0.0 || trail > sl) newSL = trail;
      } else if(type == POSITION_TYPE_SELL) {
         double trail = t.ask + Trail_ATR_Mult * atr;
         if(sl <= 0.0 || trail < sl) newSL = trail;
      }
   if(newSL != sl) {
         Trade.PositionModify(sym, newSL, tp);
      }
   }
}

void ProcessCycle() {
   int processed = 0;
   int forexCount=0, cryptoCount=0, indexCount=0, metalCount=0, energyCount=0, equityCount=0;
   if(UseMarketWatch) {
      int total = SymbolsTotal(true);
      if(g_ScanIndex >= total) g_ScanIndex = 0;
      int i = g_ScanIndex;
      while(processed < g_MaxSymbolsPerCycle && total > 0) {
         if(i >= total) i = 0;
         string sym = SymbolName(i, true);
         if(!SymbolAllowed(sym)) { i++; continue; }
         double minConf; int spreadPts; double slm, tpm, trm; double minEdgeBps;
         ResolvePolicyForSymbol(sym, minConf, spreadPts, slm, tpm, trm, minEdgeBps);
         string klass = AssetClassOf(sym);
         // Throttles por classe por ciclo
         if(klass == "forex"  && forexCount  >= gMaxForexPerCycle)  { i++; continue; }
         if(klass == "crypto" && cryptoCount >= gMaxCryptoPerCycle) { i++; continue; }
         if(klass == "index"  && indexCount  >= gMaxIndexPerCycle)  { i++; continue; }
         if(klass == "metal"  && metalCount  >= gMaxMetalPerCycle)  { i++; continue; }
         // Sempre enviar request para telemetria/resposta, mesmo se depois gates bloquearem execução
         SendRequestForSymbol(sym);
         string action; double conf=0.0;
         if(TryReadResponse(sym, action, conf)) {
            if(IsSpreadOkBase(sym, spreadPts) && conf >= minConf && (action == "BUY" || action == "SELL")) {
               ExecuteSignal(sym, action, conf, slm, tpm, trm, minEdgeBps);
            } else {
               // resposta recebida, mas filtros bloquearam execução
            }
         }
         // Contagem por classe
         if(klass == "forex") forexCount++;
         else if(klass == "crypto") cryptoCount++;
         else if(klass == "index") indexCount++;
         else if(klass == "metal") metalCount++;
         processed++;
         i++;
      }
      g_ScanIndex = i % (total==0?1:total);
   } else {
      string sym = _Symbol;
      if(SymbolAllowed(sym)) {
         double minConf; int spreadPts; double slm, tpm, trm; double minEdgeBps;
         ResolvePolicyForSymbol(sym, minConf, spreadPts, slm, tpm, trm, minEdgeBps);
         SendRequestForSymbol(sym);
         string action; double conf=0.0;
         if(TryReadResponse(sym, action, conf)) {
            if(IsSpreadOkBase(sym, spreadPts) && conf >= minConf && (action == "BUY" || action == "SELL")) {
               ExecuteSignal(sym, action, conf, slm, tpm, trm, minEdgeBps);
            }
         }
      }
   }
}

void OnTick() {
   if(TimeCurrent() - lastCycle < g_CycleIntervalSec) return;
   lastCycle = TimeCurrent();
   MaybeReloadControlPanel();
   ProcessCycle();
   UpdateTrailingStops();
   EnforcePositionLossStops();
   // Exportar relatórios periódicos
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
   if(TimeCurrent() - g_LastExport >= ExportIntervalSec) {
      g_LastExport = TimeCurrent();
      ExportExposureAndPnL();
   }
}

void MaybeReloadControlPanel() {
   if(TimeCurrent() - g_LastKnobReload < ControlReloadSec) return;
   g_LastKnobReload = TimeCurrent();
   string fname = "ControlPanel.json";
   int h = FileOpen(fname, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h == INVALID_HANDLE) return;
   string txt = FileReadString(h);
   FileClose(h);
   g_ControlPanelText = txt; // manter cópia para overrides por símbolo
   // parser simples por chaves específicas (evita dependência JSON externa)
   double v;
   if(StringToValue(txt, "base_conf", v)) gKnobBaseConf = v;
   if(StringToValue(txt, "base_edge_bps", v)) gKnobBaseEdge = v;
   if(StringToValue(txt, "forex_conf", v)) gKnobConfForex = v;
   if(StringToValue(txt, "forex_edge_bps", v)) gKnobEdgeForex = v;
   if(StringToValue(txt, "crypto_conf", v)) gKnobConfCrypto = v;
   if(StringToValue(txt, "crypto_edge_bps", v)) gKnobEdgeCrypto = v;
   if(StringToValue(txt, "index_conf", v)) gKnobConfIndex = v;
   if(StringToValue(txt, "index_edge_bps", v)) gKnobEdgeIndex = v;
   if(StringToValue(txt, "metal_conf", v)) gKnobConfMetal = v;
   if(StringToValue(txt, "metal_edge_bps", v)) gKnobEdgeMetal = v;
   // Throttles por classe e emergência remota
   double iv;
   if(StringToValue(txt, "max_forex_per_cycle", iv)) gMaxForexPerCycle = (int)iv;
   if(StringToValue(txt, "max_crypto_per_cycle", iv)) gMaxCryptoPerCycle = (int)iv;
   if(StringToValue(txt, "max_index_per_cycle", iv)) gMaxIndexPerCycle = (int)iv;
   if(StringToValue(txt, "max_metal_per_cycle", iv)) gMaxMetalPerCycle = (int)iv;
   if(StringToValue(txt, "max_energy_per_cycle", iv)) gMaxEnergyPerCycle = (int)iv;
   if(StringToValue(txt, "max_equity_per_cycle", iv)) gMaxEquityPerCycle = (int)iv;
   double em;
   if(StringToValue(txt, "emergency_stop", em)) g_RemoteEmergencyStop = (em > 0.5);
   // Mixer global e por classe
   if(StringToValue(txt, "op_margin_min", v)) gMixOpMin = v;
   if(StringToValue(txt, "margin_t1", v)) gMixT1 = v;
   if(StringToValue(txt, "margin_t2", v)) gMixT2 = v;
   if(StringToValue(txt, "margin_scale_low_pct", v)) gMixScaleLow = v;
   if(StringToValue(txt, "margin_scale_mid_pct", v)) gMixScaleMid = v;
   if(StringToValue(txt, "forex_op_margin_min", v)) gMixOpMinForex = v;
   if(StringToValue(txt, "forex_margin_t1", v)) gMixT1Forex = v;
   if(StringToValue(txt, "forex_margin_t2", v)) gMixT2Forex = v;
   if(StringToValue(txt, "forex_margin_scale_low_pct", v)) gMixLowForex = v;
   if(StringToValue(txt, "forex_margin_scale_mid_pct", v)) gMixMidForex = v;
   if(StringToValue(txt, "crypto_op_margin_min", v)) gMixOpMinCrypto = v;
   if(StringToValue(txt, "crypto_margin_t1", v)) gMixT1Crypto = v;
   if(StringToValue(txt, "crypto_margin_t2", v)) gMixT2Crypto = v;
   if(StringToValue(txt, "crypto_margin_scale_low_pct", v)) gMixLowCrypto = v;
   if(StringToValue(txt, "crypto_margin_scale_mid_pct", v)) gMixMidCrypto = v;
   if(StringToValue(txt, "index_op_margin_min", v)) gMixOpMinIndex = v;
   if(StringToValue(txt, "index_margin_t1", v)) gMixT1Index = v;
   if(StringToValue(txt, "index_margin_t2", v)) gMixT2Index = v;
   if(StringToValue(txt, "index_margin_scale_low_pct", v)) gMixLowIndex = v;
   if(StringToValue(txt, "index_margin_scale_mid_pct", v)) gMixMidIndex = v;
   if(StringToValue(txt, "metal_op_margin_min", v)) gMixOpMinMetal = v;
   if(StringToValue(txt, "metal_margin_t1", v)) gMixT1Metal = v;
   if(StringToValue(txt, "metal_margin_t2", v)) gMixT2Metal = v;
   if(StringToValue(txt, "metal_margin_scale_low_pct", v)) gMixLowMetal = v;
   if(StringToValue(txt, "metal_margin_scale_mid_pct", v)) gMixMidMetal = v;
}

bool StringToValue(const string text, const string key, double &out) {
   string k = StringFormat("\"%s\"", key);
   int p = StringFind(text, k);
   if(p < 0) return false;
   int colon = StringFind(text, ":", p + StringLen(k));
   if(colon < 0) return false;
   int i = colon + 1;
   int n = StringLen(text);
   while(i < n) { int ch = StringGetCharacter(text, i); if(ch==' '||ch=='\t') { i++; } else break; }
   int start = i;
   while(i < n) {
      int ch = StringGetCharacter(text, i);
      bool isDigit = (ch >= 48 && ch <= 57);
      if(!(isDigit || ch==46 || ch==45 || ch==43 || ch==101 || ch==69)) break;
      i++;
   }
   if(i <= start) return false;
   string num = StringSubstr(text, start, i-start);
   out = StringToDouble(num);
   return true;
}

void ExportExposureAndPnL() {
   // Exporta posições atuais em JSON simples: por símbolo
   string fname1 = "ExposureReport.json";
   string fname2 = "PnLReport.json";
   string fname3 = "RuntimeStatus.json";
   int total = PositionsTotal();
   // Exposure por símbolo: soma volumes (buy positivo, sell negativo)
   // PnL por símbolo: soma lucro flutuante
   string symbols[1024];
   double expo[1024];
   double pnl[1024];
   int count = 0;
   for(int i=0; i<total && i<1024; i++) {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      string sym = PositionGetString(POSITION_SYMBOL);
      long type = PositionGetInteger(POSITION_TYPE);
      double vol = PositionGetDouble(POSITION_VOLUME);
      double profit = PositionGetDouble(POSITION_PROFIT);
      int idx = -1;
      for(int k=0; k<count; k++) { if(symbols[k] == sym) { idx = k; break; } }
      if(idx < 0) { idx = count; symbols[count] = sym; expo[count] = 0.0; pnl[count] = 0.0; count++; }
      double signedVol = (type == POSITION_TYPE_BUY ? vol : -vol);
      expo[idx] += signedVol;
      pnl[idx] += profit;
   }
   // escrever Exposure
   int h1 = FileOpen(fname1, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h1 != INVALID_HANDLE) {
      FileWriteString(h1, "{\"timestamp\":"+IntegerToString((long)TimeCurrent())+",\"exposure\":[");
      for(int a=0; a<count; a++) {
         if(a>0) FileWriteString(h1, ",");
         string row = StringFormat("{\"symbol\":\"%s\",\"volume\":%.4f}", symbols[a], expo[a]);
         FileWriteString(h1, row);
      }
      FileWriteString(h1, "]}");
      FileClose(h1);
   }
   // escrever PnL
   int h2 = FileOpen(fname2, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h2 != INVALID_HANDLE) {
      FileWriteString(h2, "{\"timestamp\":"+IntegerToString((long)TimeCurrent())+",\"pnl\":[");
      for(int b=0; b<count; b++) {
         if(b>0) FileWriteString(h2, ",");
         string row2 = StringFormat("{\"symbol\":\"%s\",\"profit\":%.2f}", symbols[b], pnl[b]);
         FileWriteString(h2, row2);
      }
      FileWriteString(h2, "]}");
      FileClose(h2);
   }
   // escrever RuntimeStatus
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   double eq  = AccountInfoDouble(ACCOUNT_EQUITY);
   int h3 = FileOpen(fname3, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h3 != INVALID_HANDLE) {
      string js = StringFormat("{\"timestamp\":%I64d,\"positions\":%d,\"margin_level\":%.2f,\"balance\":%.2f,\"equity\":%.2f}",
                               (long)TimeCurrent(), total, ml, bal, eq);
      FileWriteString(h3, js);
      FileClose(h3);
   }
}


