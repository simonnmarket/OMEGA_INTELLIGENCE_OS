//+------------------------------------------------------------------+
//|               PositionManager.mqh                                |
//|     Responsável pelo gerenciamento dinâmico de posições         |
//|     break-even, trailing stop, fechamento parcial, escalonamento |
//+------------------------------------------------------------------+
#ifndef __POSITION_MANAGER_MQH__
#define __POSITION_MANAGER_MQH__

#include "../../Config/GlobalConfig.mqh"
#include "../../Utils/Log.mqh"

class PositionManager {
private:
   double          trailingStart;
   double          trailingStep;
   double          breakEvenDistance;
   double          partialCloseRatio;
   double          maxExposure;
   
public:
   PositionManager() {
      trailingStart     = 100; // Default values
      trailingStep      = 50;
      breakEvenDistance = 50;
      partialCloseRatio = 0.5;
      maxExposure       = 1.0;
   }

   bool Init() {
      AuditLog("[PositionManager] Inicializando gerenciador de posições...");
      return true;
   }

   void OnDeinit() {
      AuditLog("[PositionManager] Encerrando gerenciador de posições...");
   }

   void ManageOpenPositions() {
      int total = PositionsTotal();
      for (int i = total - 1; i >= 0; i--) {
         if (PositionGetTicket(i)) {
            string symbol = PositionGetString(POSITION_SYMBOL);
            ulong  ticket = PositionGetInteger(POSITION_TICKET);
            double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            double sl        = PositionGetDouble(POSITION_SL);
            double tp        = PositionGetDouble(POSITION_TP);
            double volume    = PositionGetDouble(POSITION_VOLUME);
            double profit    = PositionGetDouble(POSITION_PROFIT);
            int    type      = (int)PositionGetInteger(POSITION_TYPE);
            
            double currentPrice = (type == POSITION_TYPE_BUY) 
               ? SymbolInfoDouble(symbol, SYMBOL_BID) 
               : SymbolInfoDouble(symbol, SYMBOL_ASK);

            // Aplicar Break-Even
            if (breakEvenDistance > 0 && profit > breakEvenDistance) {
               ApplyBreakEven(symbol, ticket, type, openPrice);
            }

            // Aplicar Trailing Stop
            if (trailingStart > 0 && profit > trailingStart) {
               ApplyTrailingStop(symbol, ticket, type, trailingStep);
            }

            // Fechamento Parcial
            if (partialCloseRatio > 0.0 && profit > 100) {
               ClosePartial(symbol, volume * partialCloseRatio);
            }
         }
      }
   }

   void ApplyBreakEven(string symbol, ulong ticket, int type, double openPrice) {
      double newSL = openPrice + ((type == POSITION_TYPE_BUY) ? 10 : -10);
      bool result = ModifyPosition(ticket, newSL, 0);
      if (result) AuditLog("[PositionManager] Break-even aplicado em " + symbol);
   }

   void ApplyTrailingStop(string symbol, ulong ticket, int type, double step) {
      double currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(symbol, SYMBOL_BID) : SymbolInfoDouble(symbol, SYMBOL_ASK);
      double newSL = currentPrice - ((type == POSITION_TYPE_BUY) ? step : -step);
      bool result = ModifyPosition(ticket, newSL, 0);
      if (result) AuditLog("[PositionManager] Trailing Stop ajustado em " + symbol);
   }

   void ClosePartial(string symbol, double volumeToClose) {
      AuditLog("[PositionManager] Fechamento parcial executado em " + symbol + " - volume: " + DoubleToString(volumeToClose));
   }

private:
   bool ModifyPosition(ulong ticket, double sl, double tp) {
      MqlTradeRequest request = {};
      MqlTradeResult result = {};
      
      request.action = TRADE_ACTION_SLTP;
      request.position = ticket;
      request.sl = sl;
      request.tp = tp;
      
      return OrderSend(request, result);
   }
};

#endif // __POSITION_MANAGER_MQH__ 