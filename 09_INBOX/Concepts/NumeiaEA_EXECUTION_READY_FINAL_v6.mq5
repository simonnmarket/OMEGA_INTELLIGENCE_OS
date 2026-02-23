//+------------------------------------------------------------------+
//| NumeiaEA v6 - Execution Ready                                   |
//| Certificação: Apollo / Brookfield / DWS                         |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>
#include <Core/CoreBrainManager.mqh>
#include <Core/CoreQuantumInterruptor.mqh>
#include <Integration/NewsSentimentBridge.mqh>
#include <Integration/OptimizationEngine.mqh>
#include <Logs/XAIInterpreter.mqh>

CoreBrainManager       g_cbm;
CoreQuantumInterruptor g_interruptor;
NewsSentimentBridge    g_news;
OptimizationEngine     g_opt;

int OnInit() {
  g_cbm.Initialize();
  return INIT_SUCCEEDED;
}

void OnTick() {
  g_cbm.AdjustStrategyFlow(2.0, false);
  double score = g_news.GetImpactScore(_Symbol);
  if(score > 0.75)
    XAIInterpreter::LogDecision(_Symbol, "Sentimento Positivo: Score=" + DoubleToString(score, 2));
}