//+------------------------------------------------------------------+
//| MeanReversionAgent.mqh - Agente de Reversão à Média                |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"

class MeanReversionAgent : public AgentBase {
private:
   int m_period;

public:
   MeanReversionAgent() : AgentBase("MeanReversionBot"), m_period(20) {}

   int Analyze(string symbol) override {
      double price = iClose(symbol, PERIOD_M1, 0);
      double ma = SimpleMovingAverage(symbol, PERIOD_M1, m_period, 0);
      double dev = (price - ma) / Volatility(symbol, PERIOD_M1, 14, 0);

      if(dev < -1.5) {
         m_confidence = MathMin(1.0, -dev / 2.0);
         return 1;
      } else if(dev > 1.5) {
         m_confidence = MathMin(1.0, dev / 2.0);
         return -1;
      }

      m_confidence = 0.0;
      return 0;
   }
};