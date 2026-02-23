// Include/IAgents/IAgent_TEMPLATE.mqh
// Template base para criação de agentes IA autônomos por ativo
// Projeto: Lenovo Apollo11 Quantum EA Hybrid
// Autor: ChatGPT CIO System

#ifndef __IAGENT_TEMPLATE_MQH__
#define __IAGENT_TEMPLATE_MQH__

class IAgent_TEMPLATE
  {
protected:
   string   m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   double   m_lotMultiplier;

public:
   IAgent_TEMPLATE(const string symbol, ENUM_TIMEFRAMES tf, double lotMultiplier=1.0)
     {
      m_symbol        = symbol;
      m_timeframe     = tf;
      m_lotMultiplier = lotMultiplier;
     }

   // Função principal para checar sinal
   virtual bool CheckSignal(string &direction) { return false; }

   // Cálculo de lote com base em risco e características do ativo
   virtual double CalculateLot()
     {
      return 0.01 * m_lotMultiplier; // Padrão, pode ser sobrescrito
     }

   // Execução da ordem com base na lógica
   virtual bool ExecuteTrade()
     {
      string direction;
      if(!CheckSignal(direction)) return false;

      double lot = CalculateLot();
      if(direction == "BUY")
         return OrderSend(m_symbol, OP_BUY, lot, Ask, 10, 0, 0);
      else if(direction == "SELL")
         return OrderSend(m_symbol, OP_SELL, lot, Bid, 10, 0, 0);

      return false;
     }

   // Atualiza estados internos do agente
   virtual void UpdateState() {}

   string Symbol() const { return m_symbol; }
  };

#endif // __IAGENT_TEMPLATE_MQH__
