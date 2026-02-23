//+------------------------------------------------------------------+
//| DynamicRiskManager.mqh - Gerenciamento de risco                  |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>

class DynamicRiskManager {
private:
   double m_risk_percent;
   int m_max_orders;
   
public:
   DynamicRiskManager(double risk_percent=1.0, int max_orders=3) : 
      m_risk_percent(risk_percent), m_max_orders(max_orders) {}
   
   double CalcLot(string symbol, double sl_pips) {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double lot = (balance * m_risk_percent/100) / (sl_pips * _Point * tick_value);
      
      // Normaliza para limites do corretor
      double min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      lot = MathMax(min_lot, MathMin(max_lot, lot));
      
      return NormalizeDouble(lot, 2);
   }
   
   bool CanOpenNewPosition(string symbol, int magic) {
      int count = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         if(PositionGetSymbol(i) == symbol && PositionGetInteger(POSITION_MAGIC) == magic)
            count++;
      }
      return count < m_max_orders;
   }
};