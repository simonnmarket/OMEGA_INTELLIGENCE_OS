//+------------------------------------------------------------------+
//| VolatilityMetrics.mqh - Volatility Analysis Metrics              |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

struct VolatilityMetrics {
   double garch_volatility;      // Volatilidade GARCH
   double markov_state;          // Estado do modelo de Markov
   double regime_probability;    // Probabilidade do regime atual
   double entropy;               // Entropia do mercado
   double transfer_entropy;      // Entropia de transferência
   double information_flow;      // Fluxo de informação
   double quantum_state;         // Estado quântico
   double wave_collapse;         // Probabilidade de colapso da onda
   double uncertainty;           // Incerteza quântica
   double correlation;           // Correlação quântica
}; 