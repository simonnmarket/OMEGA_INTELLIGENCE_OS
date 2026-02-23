//+------------------------------------------------------------------+
//| MomentumAgent.mqh - Agente de Impulso                             |
//| Detecta momentos de forte momentum e sinaliza entrada              |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"

class MomentumAgent : public AgentBase {
private:
   int m_period;

public:
   MomentumAgent() : AgentBase("MomentumHunter"), m_period(14) {}

   // Analisa o ativo e retorna sinal: +1 (compra), -1 (venda), 0 (neutro)
   int Analyze(string symbol) override {
      double price = iClose(symbol, PERIOD_M1, 0);
      double prev_price = iClose(symbol, PERIOD_M1, 1);
      double delta = price - prev_price;
      double volatility = iATR(symbol, PERIOD_M1, 14, 0);

      if(delta > 0 && delta > volatility * 1.5) {
         m_confidence = MathMin(1.0, delta / (volatility + 1e-8));
         return 1;
      } else if(delta < 0 && delta < -volatility * 1.5) {
         m_confidence = MathMin(1.0, -delta / (volatility + 1e-8));
         return -1;
      }

      m_confidence = 0.0;
      return 0;
   }
};