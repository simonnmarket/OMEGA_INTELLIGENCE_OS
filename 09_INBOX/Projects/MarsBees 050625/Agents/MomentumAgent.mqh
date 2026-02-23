//+------------------------------------------------------------------+
//| MomentumAgent.mqh - Agente de Impulso                             |
//| Detecta momentos de forte momentum e sinaliza entrada            |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"

class MomentumAgent : public AgentBase {
private:
   int m_period;
   double m_volatilityFactor;

public:
   // Construtor com parâmetros para período e fator de volatilidade
   MomentumAgent(int period = 14, double volatilityFactor = 1.5)
      : AgentBase("MomentumHunter"), m_period(period), m_volatilityFactor(volatilityFactor) {}

   // Sobrescreve o método Analyze da base
   int Analyze(string symbol, ENUM_TIMEFRAMES timeframe = PERIOD_M1) override {
      double price = iClose(symbol, timeframe, 0);
      double prev_price = iClose(symbol, timeframe, 1);
      double delta = price - prev_price;

      // Usa o método Volatility da classe base para obter ATR na barra 0
      double volatility = Volatility(symbol, timeframe, m_period, 0);

      if(delta > 0 && delta > volatility * m_volatilityFactor) {
         m_confidence = MathMin(1.0, delta / (volatility + 1e-8));
         return 1;
      }
      else if(delta < 0 && delta < -volatility * m_volatilityFactor) {
         m_confidence = MathMin(1.0, -delta / (volatility + 1e-8));
         return -1;
      }

      m_confidence = 0.0;
      return 0;
   }
};