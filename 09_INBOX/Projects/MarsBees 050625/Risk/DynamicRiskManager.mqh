//+------------------------------------------------------------------+
//| DynamicRiskManager.mqh - Gerenciamento de Risco Dinâmico         |
//+------------------------------------------------------------------+
#ifndef DYNAMIC_RISK_MANAGER_MQH
#define DYNAMIC_RISK_MANAGER_MQH

#include <Trade\Trade.mqh>

class DynamicRiskManager {
private:
   double m_risk_percent;
   int m_max_orders;
   double m_max_drawdown;
   
public:
   DynamicRiskManager(double risk_pct=1.0, int max_orders=3, double max_dd=20.0) :
      m_risk_percent(risk_pct), m_max_orders(max_orders), m_max_drawdown(max_dd) {}
   
   double CalculateLotSize(string symbol, double stop_loss_pips) const {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double risk_amount = balance * m_risk_percent / 100.0;
      double lot_size = risk_amount / (stop_loss_pips * _Point * tick_value);
      
      // Normalização para limites do corretor
      double min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      double lot_step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
      
      lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
      lot_size = MathRound(lot_size / lot_step) * lot_step;
      
      return NormalizeDouble(lot_size, 2);
   }
   
   bool CanOpenNewPosition(string symbol, int magic_number) const {
      if(IsOverMaxDrawdown()) return false;
      
      int count = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         if(PositionGetSymbol(i) == symbol && PositionGetInteger(POSITION_MAGIC) == magic_number) {
            count++;
            if(count >= m_max_orders) return false;
         }
      }
      return true;
   }
   
   bool IsOverMaxDrawdown() const {
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double drawdown = (balance - equity) / balance * 100.0;
      return drawdown >= m_max_drawdown;
   }
};
#endif