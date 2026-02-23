// File: Include/AI_AGENTS/TradeExecutionAgent.mqh
// Project: Quantum Omega God Mode
// Role: Agente IA responsável por executar ordens reais e estratégicas

#ifndef __TRADE_EXECUTION_AGENT_MQH__
#define __TRADE_EXECUTION_AGENT_MQH__

#include <Trade\Trade.mqh>
CTrade trade;

class TradeExecutionAgent {
public:
   bool ExecuteBuy(string symbol, double lot) {
      return trade.Buy(lot, symbol);
   }

   bool ExecuteSell(string symbol, double lot) {
      return trade.Sell(lot, symbol);
   }

   void CloseAll(string symbol) {
      for(int i=PositionsTotal()-1; i>=0; i--) {
         if(PositionGetSymbol(i)==symbol) trade.PositionClose(symbol);
      }
   }
};

#endif
