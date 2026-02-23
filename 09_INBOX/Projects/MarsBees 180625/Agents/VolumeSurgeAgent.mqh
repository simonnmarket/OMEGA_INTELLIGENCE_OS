//+------------------------------------------------------------------+
//| VolumeSurgeAgent.mqh - Agente de Volume Anômalo                   |
//| Detecta volume inesperado e sinaliza mudança de tendência        |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"

class VolumeSurgeAgent : public AgentBase {
private:
   int m_period;

public:
   VolumeSurgeAgent() : AgentBase("VolumeSurgeBot"), m_period(20) {}

   // Analisa o ativo e retorna sinal: +1 (compra), -1 (venda), 0 (neutro)
   int Analyze(string symbol) override {
      double vol = iVolume(symbol, PERIOD_M1, 0);
      double avg_vol = iMA(symbol, PERIOD_M1, m_period, 0, MODE_SMA, PRICE_CLOSE, 0);

      if(vol > avg_vol * 1.5) {
         m_confidence = MathMin(1.0, vol / avg_vol / 2.0);
         return (iClose(symbol, PERIOD_M1, 0) > iClose(symbol, PERIOD_M1, 1)) ? 1 : -1;
      }

      m_confidence = 0.0;
      return 0;
   }
};