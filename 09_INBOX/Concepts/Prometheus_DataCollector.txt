//+------------------------------------------------------------------+
//| Expert: Prometheus_DataCollector.mq5                              |
//| Purpose: Offline dataset generation for ML (Strategy Tester)     |
//| Notes:                                                            |
//|  - Runs standalone in Strategy Tester (no trading, no requests)   |
//|  - Multi-symbol scan (Market Watch or CSV list)                   |
//|  - Exports feature/label datasets to Common Files                 |
//|  - Safe for live: does nothing on live charts                     |
//+------------------------------------------------------------------+
#property copyright   "Prometheus Quantum Fund"
#property link        "https://prometheus.quantum"
#property version     "1.0"
#property strict

// MEMORY_ID: DATA_COLLECT_001
// TIMESTAMP: ISO 8601 will be printed at run time
// AUTHOR: Cursor_Omega

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input bool      UseMarketWatch              = true;         // Scan visible symbols from Market Watch
input string    SymbolsCSV                  = "";           // Optional explicit list (comma-separated)
input ENUM_TIMEFRAMES TimeframeBase         = PERIOD_M5;    // Base timeframe for dataset
input int       MaxBarsPerSymbol            = 200000;       // Cap to avoid excessive size
input int       ATR_Period1                 = 14;           // ATR fast
input int       ATR_Period2                 = 21;           // ATR slow
input int       ADX_Period                  = 14;           // ADX period
input int       EMA_Fast                    = 10;           // EMA fast
input int       EMA_Mid                     = 20;           // EMA mid
input int       EMA_Slow                    = 50;           // EMA slow
input int       EMA_Long                    = 200;          // EMA long
input int       Horizon1_Bars               = 5;            // Forward horizon 1
input int       Horizon2_Bars               = 20;           // Forward horizon 2
input int       Horizon3_Bars               = 60;           // Forward horizon 3
input double    BarrierUp_ATR               = 1.5;          // Triple-barrier up (in ATR multiple)
input double    BarrierDn_ATR               = 1.5;          // Triple-barrier down (in ATR multiple)
input int       TimeBarrier_Bars            = 30;           // Triple-barrier time limit
input double    CostModel_Bps               = 5.0;          // Approx trading cost in bps (spread+slippage)
input double    MinEdgeOverCost_Bps         = 2.0;          // Gate for meta-label
input bool      UseTesterDateRange          = true;         // Respect Strategy Tester date range
input string    OutputPrefix                = "Datasets/Prometheus"; // Common Files output root
input bool      ExportJSONMeta              = true;         // Write Meta.json and RunSummary.csv

//+------------------------------------------------------------------+
//| Utilities                                                        |
//+------------------------------------------------------------------+
string  g_RunIsoTs = "";

string TimeToISO8601(datetime t)
{
   return TimeToString(t, TIME_DATE|TIME_MINUTES|TIME_SECONDS);
}

void EnsureOutputFolders()
{
   // Create common folders: Datasets/Prometheus
   FolderCreate(OutputPrefix, FILE_COMMON);
}

bool SplitCSV(const string csv, string &out[])
{
   ArrayResize(out, 0);
   if(StringLen(csv) == 0)
      return false;
   int count = StringSplit(csv, ',', out);
   for(int i = 0; i < count; i++)
   {
      StringTrimLeft(out[i]);
      StringTrimRight(out[i]);
   }
   return count > 0;
}

int BuildSymbolList(string &symbols[])
{
   ArrayResize(symbols, 0);
   if(!UseMarketWatch && StringLen(SymbolsCSV) == 0)
   {
      // Fallback: current symbol only
      ArrayResize(symbols, 1);
      symbols[0] = Symbol();
      return 1;
   }
   if(UseMarketWatch)
   {
      int total = SymbolsTotal(true);
      for(int i = 0; i < total; i++)
      {
         string s = SymbolName(i, true);
         if(StringLen(s) == 0)
            continue;
         int n = ArraySize(symbols);
         ArrayResize(symbols, n + 1);
         symbols[n] = s;
      }
   }
   string extra[];
   if(SplitCSV(SymbolsCSV, extra))
   {
      for(int j = 0; j < ArraySize(extra); j++)
      {
         string s2 = extra[j];
         if(StringLen(s2) == 0)
            continue;
         int n2 = ArraySize(symbols);
         ArrayResize(symbols, n2 + 1);
         symbols[n2] = s2;
      }
   }
   return ArraySize(symbols);
}

int OpenCommonCsv(const string relativePath)
{
   return FileOpen(relativePath, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON);
}

int OpenCommonAppendCsv(const string relativePath)
{
   return FileOpen(relativePath, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON);
}

double SafePoint(const string sym)
{
   double p = SymbolInfoDouble(sym, SYMBOL_POINT);
   if(p <= 0.0) p = 0.0001;
   return p;
}

// Note: helper for int64 not needed; use standard comparisons if required

//+------------------------------------------------------------------+
//| Feature helpers                                                  |
//+------------------------------------------------------------------+
bool LoadRates(const string sym, ENUM_TIMEFRAMES tf, MqlRates &rates[])
{
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(sym, tf, 0, MaxBarsPerSymbol, rates);
   return (copied > 0);
}

void ComputeReturns(const MqlRates &rates[], double &logret1[], double &logret5[], double &logret20[])
{
   int n = ArraySize(rates);
   ArrayResize(logret1, n);
   ArrayResize(logret5, n);
   ArrayResize(logret20, n);
   ArrayInitialize(logret1, 0.0);
   ArrayInitialize(logret5, 0.0);
   ArrayInitialize(logret20, 0.0);
   for(int i = 1; i < n; i++)
   {
      double c0 = rates[i].close;
      double c1 = rates[i-1].close;
      if(c0 > 0 && c1 > 0)
         logret1[i] = MathLog(c0 / c1);
      int k5 = i - 5;
      if(k5 >= 0)
      {
         double c5 = rates[k5].close;
         if(c5 > 0)
            logret5[i] = MathLog(c0 / c5);
      }
      int k20 = i - 20;
      if(k20 >= 0)
      {
         double c20 = rates[k20].close;
         if(c20 > 0)
            logret20[i] = MathLog(c0 / c20);
      }
   }
}

bool ComputeATR(const string sym, ENUM_TIMEFRAMES tf, int period, double &atr[])
{
   int handle = iATR(sym, tf, period);
   if(handle == INVALID_HANDLE) return false;
   ArraySetAsSeries(atr, true);
   int copied = CopyBuffer(handle, 0, 0, MaxBarsPerSymbol, atr);
   IndicatorRelease(handle);
   return (copied > 0);
}

bool ComputeEMA(const string sym, ENUM_TIMEFRAMES tf, int period, double &ema[])
{
   int handle = iMA(sym, tf, period, 0, MODE_EMA, PRICE_CLOSE);
   if(handle == INVALID_HANDLE) return false;
   ArraySetAsSeries(ema, true);
   int copied = CopyBuffer(handle, 0, 0, MaxBarsPerSymbol, ema);
   IndicatorRelease(handle);
   return (copied > 0);
}

bool ComputeADX(const string sym, ENUM_TIMEFRAMES tf, int period, double &adx[])
{
   int handle = iADX(sym, tf, period);
   if(handle == INVALID_HANDLE) return false;
   ArraySetAsSeries(adx, true);
   int copied = CopyBuffer(handle, 0, 0, MaxBarsPerSymbol, adx);
   IndicatorRelease(handle);
   return (copied > 0);
}

//+------------------------------------------------------------------+
//| Labeling helpers (Triple-Barrier)                                |
//+------------------------------------------------------------------+
void ComputeForwardReturns(const MqlRates &rates[], int h, double &fwdret[])
{
   int n = ArraySize(rates);
   ArrayResize(fwdret, n);
   ArrayInitialize(fwdret, 0.0);
   for(int i = 0; i < n; i++)
   {
      int j = i - h; // arrays are series (index 0 is latest bar)
      if(j >= 0)
      {
         double c_now = rates[i].close;
         double c_fut = rates[j].close;
         if(c_now > 0 && c_fut > 0)
            fwdret[i] = MathLog(c_now / c_fut);
      }
   }
}

void ComputeTripleBarrierLabels(const MqlRates &rates[], const double &atr[], const int timeBarrierBars, const double upATR, const double dnATR, int &label[])
{
   int n = ArraySize(rates);
   ArrayResize(label, n);
   ArrayInitialize(label, 0);
   // Note: arrays are series, so forward in time is decreasing index
   for(int i = n - 1; i >= 0; i--)
   {
      double entry = rates[i].close;
      double a = (i < ArraySize(atr) ? atr[i] : 0.0);
      if(entry <= 0.0 || a <= 0.0) { label[i] = 0; continue; }
      double up = entry + upATR * a;
      double dn = entry - dnATR * a;
      int hit = 0; // 1 up, -1 down, 0 time
      int look = timeBarrierBars;
      int k = i - 1;
      while(k >= 0 && look > 0)
      {
         if(rates[k].high >= up) { hit = 1; break; }
         if(rates[k].low  <= dn) { hit = -1; break; }
         k--;
         look--;
      }
      label[i] = hit;
   }
}

//+------------------------------------------------------------------+
//| Core processing                                                  |
//+------------------------------------------------------------------+
void WriteCsvHeader(const int fh)
{
   FileWrite(fh,
      "time,open,high,low,close,volume,logret_1,logret_5,logret_20,"
      "tr,atr14,atr21,ema10,ema20,ema50,ema200,adx14,"
      "wick_top_ratio,wick_bot_ratio,body_to_tr,spread_points,spread_bps,"
      "fwdret_"+IntegerToString(Horizon1_Bars)+","+
      "fwdret_"+IntegerToString(Horizon2_Bars)+","+
      "fwdret_"+IntegerToString(Horizon3_Bars)+","+
      "tb_label");
}

void ProcessSymbol(const string sym, const datetime fromDate, const datetime toDate)
{
   MqlRates rates[];
   if(!LoadRates(sym, TimeframeBase, rates))
   {
      Print("[DC] No rates for ", sym);
      return;
   }
   int n = ArraySize(rates);
   if(n <= 300)
   {
      Print("[DC] Too few bars for ", sym, " (", n, ")");
      return;
   }

   // Bound by tester dates if requested
   int startIdx = n - 1;
   int endIdx = 0;
   if(UseTesterDateRange)
   {
      // Find indices where time within [fromDate, toDate]
      for(int i = n - 1; i >= 0; i--)
      {
         datetime t = rates[i].time;
         if(t >= fromDate && t <= toDate)
         {
            startIdx = i; // oldest inside window
            break;
         }
      }
      for(int j = 0; j < n; j++)
      {
         datetime t2 = rates[j].time;
         if(t2 <= toDate)
         {
            endIdx = j; // newest inside window
            break;
         }
      }
   }

   double atr14[];   ComputeATR(sym, TimeframeBase, ATR_Period1, atr14);
   double atr21[];   ComputeATR(sym, TimeframeBase, ATR_Period2, atr21);
   double ema10[];   ComputeEMA(sym, TimeframeBase, EMA_Fast,  ema10);
   double ema20[];   ComputeEMA(sym, TimeframeBase, EMA_Mid,   ema20);
   double ema50[];   ComputeEMA(sym, TimeframeBase, EMA_Slow,  ema50);
   double ema200[];  ComputeEMA(sym, TimeframeBase, EMA_Long,  ema200);
   double adx14[];   ComputeADX(sym, TimeframeBase, ADX_Period, adx14);

   double logret1[]; double logret5[]; double logret20[];
   ComputeReturns(rates, logret1, logret5, logret20);

   double fwd1[]; ComputeForwardReturns(rates, Horizon1_Bars, fwd1);
   double fwd2[]; ComputeForwardReturns(rates, Horizon2_Bars, fwd2);
   double fwd3[]; ComputeForwardReturns(rates, Horizon3_Bars, fwd3);

   int tb_label[]; ComputeTripleBarrierLabels(rates, atr14, TimeBarrier_Bars, BarrierUp_ATR, BarrierDn_ATR, tb_label);

   // Spread approximation (current property); used as cost proxy
   long spread_points_long = SymbolInfoInteger(sym, SYMBOL_SPREAD);
   double point = SafePoint(sym);
   double spread_pts_default = (double)spread_points_long;

   // Prepare file
   string tfStr = EnumToString(TimeframeBase);
   string outRel = OutputPrefix + "/" + sym + "_" + tfStr + ".csv";
   int fh = OpenCommonCsv(outRel);
   if(fh == INVALID_HANDLE)
   {
      Print("[DC] Cannot open file: ", outRel);
      return;
   }
   WriteCsvHeader(fh);

   // Iterate and write rows
   for(int i = startIdx; i >= endIdx; i--)
   {
      datetime t = rates[i].time;
      double open = rates[i].open;
      double high = rates[i].high;
      double low  = rates[i].low;
      double close= rates[i].close;
      long   vol  = rates[i].tick_volume;
      double tr   = (high - low);
      if(tr <= 0.0) tr = 0.0;
      double wickTop = 0.0;
      double wickBot = 0.0;
      double bodyToTr = 0.0;
      double body = MathAbs(close - open);
      if(tr > 0.0)
      {
         double upperBody = MathMax(open, close);
         double lowerBody = MathMin(open, close);
         wickTop = (high - upperBody) / tr;
         wickBot = (lowerBody - low) / tr;
         bodyToTr = body / tr;
      }
      double atr14v  = (i < ArraySize(atr14)  ? atr14[i]  : 0.0);
      double atr21v  = (i < ArraySize(atr21)  ? atr21[i]  : 0.0);
      double ema10v  = (i < ArraySize(ema10)  ? ema10[i]  : 0.0);
      double ema20v  = (i < ArraySize(ema20)  ? ema20[i]  : 0.0);
      double ema50v  = (i < ArraySize(ema50)  ? ema50[i]  : 0.0);
      double ema200v = (i < ArraySize(ema200) ? ema200[i] : 0.0);
      double adxv    = (i < ArraySize(adx14)  ? adx14[i]  : 0.0);
      double lr1     = (i < ArraySize(logret1)? logret1[i]: 0.0);
      double lr5     = (i < ArraySize(logret5)? logret5[i]: 0.0);
      double lr20    = (i < ArraySize(logret20)? logret20[i]: 0.0);
      double fr1     = (i < ArraySize(fwd1)   ? fwd1[i]   : 0.0);
      double fr2     = (i < ArraySize(fwd2)   ? fwd2[i]   : 0.0);
      double fr3     = (i < ArraySize(fwd3)   ? fwd3[i]   : 0.0);
      int    lbl     = (i < ArraySize(tb_label)? tb_label[i] : 0);
      double spread_pts = spread_pts_default; // proxy
      double spread_bps = 0.0;
      if(close > 0.0)
         spread_bps = (spread_pts * point / close) * 10000.0;

      string line = TimeToISO8601(t) + "," +
         DoubleToString(open, 8) + "," +
         DoubleToString(high, 8) + "," +
         DoubleToString(low, 8) + "," +
         DoubleToString(close, 8) + "," +
         IntegerToString(vol) + "," +
         DoubleToString(lr1, 10) + "," +
         DoubleToString(lr5, 10) + "," +
         DoubleToString(lr20, 10) + "," +
         DoubleToString(tr, 8) + "," +
         DoubleToString(atr14v, 8) + "," +
         DoubleToString(atr21v, 8) + "," +
         DoubleToString(ema10v, 8) + "," +
         DoubleToString(ema20v, 8) + "," +
         DoubleToString(ema50v, 8) + "," +
         DoubleToString(ema200v, 8) + "," +
         DoubleToString(adxv, 6) + "," +
         DoubleToString(wickTop, 6) + "," +
         DoubleToString(wickBot, 6) + "," +
         DoubleToString(bodyToTr, 6) + "," +
         DoubleToString(spread_pts, 2) + "," +
         DoubleToString(spread_bps, 4) + "," +
         DoubleToString(fr1, 10) + "," +
         DoubleToString(fr2, 10) + "," +
         DoubleToString(fr3, 10) + "," +
         IntegerToString(lbl);
      FileWrite(fh, line);
   }
   FileClose(fh);
   Print("[DC] Wrote ", sym, " → ", outRel);
}

void WriteMetaAndSummary(string &symbols[], const datetime fromDate, const datetime toDate)
{
   if(!ExportJSONMeta) return;
   string metaRel = OutputPrefix + "/Meta.json";
   int fh = FileOpen(metaRel, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON);
   if(fh != INVALID_HANDLE)
   {
      FileWrite(fh, "{\"run_ts\":\"" + g_RunIsoTs + "\",\"timeframe\":\"" + EnumToString(TimeframeBase) + "\",");
      FileWrite(fh, " \"from\":\"" + TimeToISO8601(fromDate) + "\",\"to\":\"" + TimeToISO8601(toDate) + "\",");
      FileWrite(fh, " \"symbols\":[");
      for(int i = 0; i < ArraySize(symbols); i++)
      {
         string s = symbols[i];
         FileWrite(fh, (i==0?"  \"":"  ,\"") + s + "\"");
      }
      FileWrite(fh, " ]}");
      FileClose(fh);
   }
   string sumRel = OutputPrefix + "/RunSummary.csv";
   int sh = FileOpen(sumRel, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON);
   if(sh != INVALID_HANDLE)
   {
      FileWrite(sh, "run_ts,timeframe,from,to,num_symbols");
      FileWrite(sh, g_RunIsoTs + "," + EnumToString(TimeframeBase) + "," + TimeToISO8601(fromDate) + "," + TimeToISO8601(toDate) + "," + IntegerToString(ArraySize(symbols)) );
      FileClose(sh);
   }
}

//+------------------------------------------------------------------+
//| Expert lifecycle                                                 |
//+------------------------------------------------------------------+
int OnInit()
{
   g_RunIsoTs = TimeToISO8601(TimeCurrent());
   if(MQLInfoInteger(MQL_TESTER) == 0)
   {
      Print("[DC] This EA is intended for Strategy Tester only. Doing nothing.");
      return(INIT_SUCCEEDED);
   }

   EnsureOutputFolders();

   string symbols[];
   int cnt = BuildSymbolList(symbols);
   if(cnt <= 0)
   {
      Print("[DC] No symbols to process.");
      return(INIT_FAILED);
   }

   // Determine tester date range
   datetime fromDate = 0;
   datetime toDate   = TimeCurrent();
   if(UseTesterDateRange)
   {
      // Try to infer from the current symbol series info
      string baseSym = (cnt > 0 ? symbols[0] : Symbol());
      long firstDate = (long)SeriesInfoInteger(baseSym, TimeframeBase, SERIES_FIRSTDATE);
      long lastDate  = (long)SeriesInfoInteger(baseSym, TimeframeBase, SERIES_LASTBAR_DATE);
      if(firstDate > 0) fromDate = (datetime)firstDate;
      if(lastDate  > 0) toDate   = (datetime)lastDate;
   }

   Print("[DC] Run=", g_RunIsoTs, " TF=", EnumToString(TimeframeBase), " Symbols=", cnt, " Range=", TimeToISO8601(fromDate), " → ", TimeToISO8601(toDate));

   // Process all symbols
   for(int i = 0; i < cnt; i++)
   {
      string s = symbols[i];
      SymbolSelect(s, true);
      ProcessSymbol(s, fromDate, toDate);
   }

   WriteMetaAndSummary(symbols, fromDate, toDate);
   Print("[DC] Completed dataset generation.");

   // Optional: end early in tester
   ExpertRemove();
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
}

void OnTick()
{
}

//+------------------------------------------------------------------+

