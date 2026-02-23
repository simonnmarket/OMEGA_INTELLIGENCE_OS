//+------------------------------------------------------------------+
//| InstitutionalIntegration.mq5 - Exemplo de Integração Institucional|
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

#include "..\Core\CAgentBase_Institutional.mqh"

// Variáveis globais
CAgentBase_Institutional* g_agent;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   // Inicializa o agente institucional
   g_agent = new CAgentBase_Institutional(
      "InstitutionalAgent",
      Symbol(),
      PERIOD_M1
   );
   
   // Configura parâmetros institucionais
   g_agent.EnableDarkPool(true);
   g_agent.EnableVolatilityFilter(true);
   g_agent.SetVolatilityThresholds(0.001, 0.05);
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   if(g_agent) {
      delete g_agent;
      g_agent = NULL;
   }
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
   if(!g_agent) return;
   
   // Obtém sinal do agente
   double signal = g_agent.GetSignal();
   
   // Obtém métricas
   DarkPoolMetrics dp_metrics = g_agent.GetDarkPoolMetrics();
   VolatilityMetrics vol_metrics = g_agent.GetVolatilityMetrics();
   
   // Exibe métricas
   Comment(
      "Dark Pool Metrics:\n",
      "Total Volume: ", dp_metrics.total_executed_volume, "\n",
      "Avg Price: ", dp_metrics.avg_execution_price, "\n",
      "Fill Ratio: ", dp_metrics.fill_ratio, "\n\n",
      "Volatility Metrics:\n",
      "GARCH Vol: ", vol_metrics.garch_volatility, "\n",
      "Markov State: ", vol_metrics.markov_state, "\n",
      "Combined Filter: ", vol_metrics.combined_filter
   );
} 