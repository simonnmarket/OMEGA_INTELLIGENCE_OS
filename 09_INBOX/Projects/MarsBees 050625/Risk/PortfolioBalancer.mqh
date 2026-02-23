//+------------------------------------------------------------------+
//| PortfolioBalancer.mqh - Controle de Exposição Vetorial            |
//| Usa análise quântica para balancear risco entre múltiplos ativos   |
//+------------------------------------------------------------------+

#include "..\Core\MarketField.mqh"

class PortfolioBalancer {
private:
   MarketField* m_market_field;
   double m_max_total_risk;

public:
   PortfolioBalancer(MarketField* field, double max_total_risk = 30.0) {
      m_market_field = field;
      m_max_total_risk = max_total_risk;
   }

   // Verifica se pode abrir nova posição com base na exposição total
   bool CanOpenNewPosition(string symbol, double risk_per_position) {
      double total = TotalPortfolioRisk();

      Print("Exposição Atual: ", DoubleToString(total, 2), "% | Risco por Posição: ", DoubleToString(risk_per_position, 2), "%");

      return (total + risk_per_position) <= m_max_total_risk;
   }

   // Calcula risco total atual no mercado
   double TotalPortfolioRisk() {
      double total = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         string sym = PositionGetString(POSITION_SYMBOL);
         double lot = PositionGetDouble(POSITION_VOLUME_REAL);
         double sl = PositionGetDouble(POSITION_SL);
         double price = PositionGetDouble(POSITION_PRICE_OPEN);
         double tick_value = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);

         double position_risk = (price - sl) * tick_value * lot;
         total += position_risk;
      }

      double acc_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      return (total / acc_balance) * 100; // Em percentual
   }
};