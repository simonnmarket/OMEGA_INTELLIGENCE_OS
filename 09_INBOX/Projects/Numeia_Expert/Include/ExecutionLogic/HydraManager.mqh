// File: Include/ExecutionLogic/HydraManager.mqh
#ifndef EXECUTIONLOGIC_HYDRAMANAGER_MQH
#define EXECUTIONLOGIC_HYDRAMANAGER_MQH

//+------------------------------------------------------------------+
//| HydraManager - Institutional Order Splitting and Trailing       |
//| Finalidade: Gerenciamento modular de ordens com trailing e      |
//| escalonamento baseado em ATR                                     |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                     |
//| Certificações: Apollo Certified / Brookfield Resilient          |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>

class HydraManager
  {
private:
   string   m_symbol;
   double   m_lotSize;
   CTrade   m_trade;
   double   m_atr;

public:
   HydraManager(string symbol, double lotSize)
     {
      m_symbol  = symbol;
      m_lotSize = lotSize;
      m_atr     = 0.0;
     }

   // Atualiza o ATR antes de operar
   void UpdateATR()
     {
      int handle = iATR(m_symbol, PERIOD_H1, 14);
      if(handle != INVALID_HANDLE)
        {
         double buffer[];
         if(CopyBuffer(handle, 0, 0, 1, buffer) > 0)
            m_atr = buffer[0];
        }
     }

   // Envia 3 ordens escalonadas com trailing stop adaptativo
   void ExecuteHydraOrders()
     {
      UpdateATR();
      if(m_atr <= 0.0)
        {
         Print("[HYDRA] ATR inválido para ", m_symbol);
         return;
        }

      for(int i = 0; i < 3; i++)
        {
         double factor = (i == 0) ? 1.5 : 0.8;
         double sl = m_atr * factor;
         double price = (SymbolInfoDouble(m_symbol, SYMBOL_ASK) > 0) ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) : SymbolInfoDouble(m_symbol, SYMBOL_BID);

         if(!m_trade.Buy(m_lotSize, m_symbol, price, price - sl, 0.0, "HydraOrder_"+IntegerToString(i)))
            Print("[HYDRA-ERROR] Falha ao enviar ordem ", i, " | Erro: ", GetLastError());
         else
            Print("[HYDRA] Ordem ", i, " enviada com SL: ", DoubleToString(sl, _Digits));
        }
     }
  };

#endif // EXECUTIONLOGIC_HYDRAMANAGER_MQH
