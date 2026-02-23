//+------------------------------------------------------------------+
//|               PositionManager.mqh                                |
//|     Responsável pelo gerenciamento dinâmico de posições         |
//|     break-even, trailing stop, fechamento parcial, escalonamento |
//+------------------------------------------------------------------+
#property strict

#include "..\\Config\\GlobalConfig.mqh"
#include "..\\Utils\\Log.mqh"
#include "TradeExecutor.mqh"

class CPositionManager {
private:
   double          trailingStart;
   double          trailingStep;
   double          breakEvenDistance;
   double          partialCloseRatio;
   double          maxExposure;
   
public:
   CPositionManager() {
      trailingStart     = GlobalConfig::TrailingStart;
      trailingStep      = GlobalConfig::TrailingStep;
      breakEvenDistance = GlobalConfig::BreakEvenDistance;
      partialCloseRatio = GlobalConfig::PartialCloseRatio;
      maxExposure       = GlobalConfig::MaxTotalLot;
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
            if (partialCloseRatio > 0.0 && profit > GlobalConfig::PartialCloseProfit) {
               ClosePartial(symbol, volume * partialCloseRatio);
            }
         }
      }
   }

   void ApplyBreakEven(string symbol, ulong ticket, int type, double openPrice) {
      double newSL = openPrice + ((type == POSITION_TYPE_BUY) ? GlobalConfig::BreakEvenBuffer : -GlobalConfig::BreakEvenBuffer);
      bool result = TradeExecutor::ModifyStopLoss(symbol, ticket, NormalizeDouble(newSL, _Digits));
      if (result) Log::Info("Break-even aplicado em " + symbol);
   }

   void ApplyTrailingStop(string symbol, ulong ticket, int type, double step) {
      double currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(symbol, SYMBOL_BID) : SymbolInfoDouble(symbol, SYMBOL_ASK);
      double newSL = currentPrice - ((type == POSITION_TYPE_BUY) ? step : -step);
      bool result = TradeExecutor::ModifyStopLoss(symbol, ticket, NormalizeDouble(newSL, _Digits));
      if (result) Log::Info("Trailing Stop ajustado em " + symbol);
   }

   void ClosePartial(string symbol, double volumeToClose) {
      bool result = TradeExecutor::ClosePartialPosition(symbol, volumeToClose);
      if (result) Log::Info("Fechamento parcial executado em " + symbol + " - volume: " + DoubleToString(volumeToClose));
   }
};
