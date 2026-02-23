//+------------------------------------------------------------------+
//| MomentumAgent.mqh - Agente de momentum                           |
//+------------------------------------------------------------------+
#include "AgentBase.mqh"

class MomentumAgent : public AgentBase {
private:
   int m_period;
   
public:
   MomentumAgent() : AgentBase("MomentumAgent"), m_period(14) {}
   
   int Analyze(string symbol, ENUM_TIMEFRAMES timeframe=PERIOD_M1) override {
      double momentum = iMomentum(symbol, timeframe, m_period, 0);
      double threshold = 100 + iATR(symbol, timeframe, 14, 0)/_Point;
      
      if(momentum > threshold) {
         m_confidence = MathMin(1.0, (momentum - threshold)/threshold);
         return 1;
      }
      else if(momentum < 100 - threshold) {
         m_confidence = MathMin(1.0, (threshold - momentum)/threshold);
         return -1;
      }
      
      m_confidence = 0;
      return 0;
   }
};