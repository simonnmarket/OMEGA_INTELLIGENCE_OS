//+------------------------------------------------------------------+
//| RiskManager.mqh - Gerenciador de Risco                           |
//+------------------------------------------------------------------+
class RiskManager
{
private:
   double risk_percent;
   int max_orders;
   double take_profit;
   double stop_loss;
   bool use_trailing;
   double trailing_start;
   double trailing_step;
   bool use_breakeven;
   double breakeven_trigger;
   
public:
   RiskManager(double risk = 2.0, int max_ord = 3, double tp = 100, double sl = 100,
               bool use_trail = true, double trail_start = 50, double trail_step = 20,
               bool use_break = true, double break_trigger = 60)
   {
      risk_percent = risk;
      max_orders = max_ord;
      take_profit = tp;
      stop_loss = sl;
      use_trailing = use_trail;
      trailing_start = trail_start;
      trailing_step = trail_step;
      use_breakeven = use_break;
      breakeven_trigger = break_trigger;
   }
   
   double CalcLot(string symbol, double stoploss)
   {
      double acc_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double lot = (acc_balance * risk_percent / 100.0) / (stoploss * tick_value);

      double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      double stepLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);

      lot = MathMax(minLot, MathMin(maxLot, lot));
      lot = MathFloor(lot / stepLot) * stepLot;

      return NormalizeDouble(lot, 2);
   }
   
   void ManageTrailingStop(string symbol, int magic_number)
   {
      if(!use_trailing) return;
      
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(PositionGetSymbol(i) != symbol || PositionGetInteger(POSITION_MAGIC) != magic_number) continue;
         
         double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
         double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
         double current_sl = PositionGetDouble(POSITION_SL);
         double points_profit = MathAbs(current_price - open_price) / _Point;
         
         if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
         {
            if(points_profit > trailing_start)
            {
               double new_sl = current_price - trailing_step * _Point;
               if(new_sl > current_sl)
                  ModifyPosition(PositionGetInteger(POSITION_TICKET), new_sl);
            }
            
            if(use_breakeven && points_profit > breakeven_trigger && current_sl < open_price)
               ModifyPosition(PositionGetInteger(POSITION_TICKET), open_price);
         }
         else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
         {
            if(points_profit > trailing_start)
            {
               double new_sl = current_price + trailing_step * _Point;
               if(new_sl < current_sl || current_sl == 0)
                  ModifyPosition(PositionGetInteger(POSITION_TICKET), new_sl);
            }
            
            if(use_breakeven && points_profit > breakeven_trigger && (current_sl > open_price || current_sl == 0))
               ModifyPosition(PositionGetInteger(POSITION_TICKET), open_price);
         }
      }
   }
   
   bool CanOpenNewPosition(string symbol, int magic_number)
   {
      int count = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(PositionGetSymbol(i) == symbol && PositionGetInteger(POSITION_MAGIC) == magic_number)
            count++;
      }
      
      return count < max_orders;
   }
   
private:
   void ModifyPosition(ulong ticket, double new_sl)
   {
      CTrade trade;
      trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
   }
}; 