//+------------------------------------------------------------------+
//| DecisionMatrix.mqh - Sistema de decisão coletiva                  |
//| Com base nos sinais dos agentes                                 |
//+------------------------------------------------------------------+

#include "..\Agents/AgentBase.mqh"

class DecisionMatrix {
private:
   double m_buy_weight;
   double m_sell_weight;
   int    m_total_agents;

public:
   DecisionMatrix() : m_buy_weight(0.0), m_sell_weight(0.0), m_total_agents(0) {}

   // Calcula decisão coletiva com base nos agentes
   int CollectiveDecision(AgentBase* &agents[], string symbol) {
      m_buy_weight = 0.0;
      m_sell_weight = 0.0;
      m_total_agents = ArraySize(agents);

      for(int j=0; j<ArraySize(agents); j++) {
         if(agents[j] == NULL) continue;

         int signal = agents[j]->Analyze(symbol);
         if(signal == 1)
            m_buy_weight += agents[j]->Confidence();
         else if(signal == -1)
            m_sell_weight += agents[j]->Confidence();
      }

      double threshold = 0.4 + 0.2 * NormalizeDouble(MathRand() / 32767.0, 2);

      return (m_buy_weight > threshold) ? 1 :
             (m_sell_weight > threshold) ? -1 : 0;
   }
};