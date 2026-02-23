// Include/IAgents/IAgent_XAGUSD.mqh
// Agente IA autônomo dedicado ao ativo XAGUSD
// Projeto: Lenovo Apollo11 Quantum EA Hybrid

#ifndef __IAGENT_XAGUSD_MQH__
#define __IAGENT_XAGUSD_MQH__
#include "IAgent_TEMPLATE.mqh"

class IAgent_XAGUSD : public IAgent_TEMPLATE
  {
public:
   IAgent_XAGUSD() : IAgent_TEMPLATE("XAGUSD", PERIOD_M5, 1.5) {}

   // Estratégia adaptativa com trailing por entropia
   bool CheckSignal(string &direction) override
     {
      double maFast = iMA(m_symbol, m_timeframe, 5, 0, MODE_EMA, PRICE_CLOSE, 0);
      double maSlow = iMA(m_symbol, m_timeframe, 21, 0, MODE_EMA, PRICE_CLOSE, 0);
      double rsi     = iRSI(m_symbol, m_timeframe, 14, PRICE_CLOSE, 0);

      if(maFast > maSlow && rsi < 70)
        {
         direction = "BUY";
         return true;
        }
      else if(maFast < maSlow && rsi > 30)
        {
         direction = "SELL";
         return true;
        }

      return false;
     }

   double CalculateLot() override
     {
      double atr = iATR(m_symbol, m_timeframe, 14, 0);
      return NormalizeDouble(0.02 / atr, 2) * m_lotMultiplier;
     }

   void UpdateState() override
     {
      Print("[IAgent_XAGUSD] Estado atualizado para ", m_symbol);
     }
  };

#endif
