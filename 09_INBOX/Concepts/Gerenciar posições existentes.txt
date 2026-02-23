//+------------------------------------------------------------------+
//| Gerenciar posições existentes                                    |
//+------------------------------------------------------------------+
void ManagePositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
      
      double position_profit = PositionGetDouble(POSITION_PROFIT);
      double position_volume = PositionGetDouble(POSITION_VOLUME);
      ENUM_POSITION_TYPE position_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      
      // Break Even
      if(UseBreakEven && position_profit > 0)
      {
         double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
         double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
         
         if(position_type == POSITION_TYPE_BUY && 
            current_price - open_price >= BreakEvenPoints * _Point)
         {
            g_trade.PositionModify(ticket, 
                                 open_price + BreakEvenProfit * _Point,
                                 PositionGetDouble(POSITION_TP));
         }
         else if(position_type == POSITION_TYPE_SELL && 
                 open_price - current_price >= BreakEvenPoints * _Point)
         {
            g_trade.PositionModify(ticket, 
                                 open_price - BreakEvenProfit * _Point,
                                 PositionGetDouble(POSITION_TP));
         }
      }
      
      // Trailing Stop
      if(UseTrailingStop && position_profit > 0)
      {
         double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
         double current_sl = PositionGetDouble(POSITION_SL);
         
         if(position_type == POSITION_TYPE_BUY)
         {
            double new_sl = current_price - TrailingStop * _Point;
            if(new_sl > current_sl + TrailingStep * _Point)
            {
               g_trade.PositionModify(ticket, new_sl,
                                    PositionGetDouble(POSITION_TP));
            }
         }
         else if(position_type == POSITION_TYPE_SELL)
         {
            double new_sl = current_price + TrailingStop * _Point;
            if(new_sl < current_sl - TrailingStep * _Point)
            {
               g_trade.PositionModify(ticket, new_sl,
                                    PositionGetDouble(POSITION_TP));
            }
         }
      }
   }
}
