//+------------------------------------------------------------------+
//| VolatilityAnalysis.mqh - Advanced Volatility Analysis            |
//| Version 2.0 - Enhanced with multiple volatility estimators       |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict

#include <Math\Alglib\alglib.mqh>

class VolatilityAnalysis
{
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   bool m_use_ewma;
   double m_ewma_lambda;
   double m_garch_alpha;
   double m_garch_beta;
   double m_garch_omega;
   int m_lookback_period;
   
   // Validações
   bool ValidateSymbol(string symbol) {
      return (symbol != NULL && symbol != "");
   }
   
   bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe) {
      return (timeframe > 0);
   }
   
   bool ValidateParameters() {
      if(!ValidateSymbol(m_symbol)) {
         Print("Símbolo inválido: ", m_symbol);
         return false;
      }
      
      if(!ValidateTimeframe(m_timeframe)) {
         Print("Timeframe inválido: ", m_timeframe);
         return false;
      }
      
      if(m_lookback_period <= 0) {
         Print("Período de lookback inválido: ", m_lookback_period);
         return false;
      }
      
      return true;
   }
   
public:
   VolatilityAnalysis(string symbol, ENUM_TIMEFRAMES timeframe, bool use_ewma = false, 
                     double ewma_lambda = 0.94, int lookback_period = 100) {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_use_ewma = use_ewma;
      m_ewma_lambda = ewma_lambda;
      m_lookback_period = lookback_period;
      
      // Parâmetros GARCH padrão
      m_garch_alpha = 0.1;
      m_garch_beta = 0.8;
      m_garch_omega = 0.0001;
   }
   
   // Calcula retornos logarítmicos
   bool CalculateReturns(double &returns[]) {
      if(!ValidateParameters()) return false;
      
      ArraySetAsSeries(returns, true);
      ArrayResize(returns, m_lookback_period);
      
      double prices[];
      ArraySetAsSeries(prices, true);
      ArrayResize(prices, m_lookback_period + 1);
      
      // Obtém preços de fechamento
      for(int i = 0; i < m_lookback_period + 1; i++) {
         prices[i] = iClose(m_symbol, m_timeframe, i);
      }
      
      // Calcula retornos logarítmicos
      for(int i = 0; i < m_lookback_period; i++) {
         if(prices[i+1] > 0) {
            returns[i] = MathLog(prices[i] / prices[i+1]);
         } else {
            returns[i] = 0;
         }
      }
      
      return true;
   }
   
   // Calcula volatilidade usando EWMA
   double CalculateEWMAVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      double variance = returns[0] * returns[0];
      for(int i = 1; i < m_lookback_period; i++) {
         variance = m_ewma_lambda * variance + (1 - m_ewma_lambda) * returns[i] * returns[i];
      }
      
      return MathSqrt(variance * 252); // Anualizado
   }
   
   // Calcula volatilidade usando GARCH(1,1)
   double CalculateGARCHVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      // Inicializa variância
      double variance = returns[0] * returns[0];
      double long_run_variance = 0;
      
      // Calcula variância de longo prazo
      for(int i = 0; i < m_lookback_period; i++) {
         long_run_variance += returns[i] * returns[i];
      }
      long_run_variance /= m_lookback_period;
      
      // Aplica GARCH(1,1)
      for(int i = 1; i < m_lookback_period; i++) {
         variance = m_garch_omega + 
                   m_garch_alpha * returns[i-1] * returns[i-1] + 
                   m_garch_beta * variance;
      }
      
      return MathSqrt(variance * 252); // Anualizado
   }
   
   // Obtém a volatilidade atual usando o método configurado
   double GetCurrentVolatility() {
      return m_use_ewma ? CalculateEWMAVolatility() : CalculateGARCHVolatility();
   }
   
   // Configura parâmetros GARCH
   void SetGARCHParameters(double alpha, double beta, double omega) {
      m_garch_alpha = alpha;
      m_garch_beta = beta;
      m_garch_omega = omega;
   }
   
   // Configura parâmetros EWMA
   void SetEWMAParameters(double lambda) {
      m_ewma_lambda = lambda;
   }
   
   // Obtém a volatilidade histórica (desvio padrão simples)
   double GetHistoricalVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      double sum = 0;
      double sum_squared = 0;
      
      for(int i = 0; i < m_lookback_period; i++) {
         sum += returns[i];
         sum_squared += returns[i] * returns[i];
      }
      
      double mean = sum / m_lookback_period;
      double variance = (sum_squared / m_lookback_period) - (mean * mean);
      
      return MathSqrt(variance * 252); // Anualizado
   }
};