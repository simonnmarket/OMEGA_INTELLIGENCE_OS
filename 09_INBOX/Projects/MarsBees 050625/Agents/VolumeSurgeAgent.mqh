//+------------------------------------------------------------------+
//| VolumeSurgeAgent.mqh - Agente de Volume Anômalo                   |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"

class VolumeSurgeAgent : public AgentBase {
private:
   int m_period;

public:
   VolumeSurgeAgent() : AgentBase("VolumeSurgeBot"), m_period(20) {}

   int Analyze(string symbol) override {
      double volume = iVolume(symbol, PERIOD_M1, 0);
      double avg_volume = SimpleMovingAverage(symbol, PERIOD_M1, m_period, 0);

      if(volume > avg_volume * 1.5) {
         m_confidence = MathMin(1.0, volume / avg_volume / 2.0);
         return (iClose(symbol, PERIOD_M1, 0) > iClose(symbol, PERIOD_M1, 1)) ? 1 : -1;
      }

      m_confidence = 0.0;
      return 0;
   }
};