//+------------------------------------------------------------------+
//| DynamicRiskManager.mqh - Sistema de Risco Institucional          |
//| v12.0 - Gerenciamento de Risco Quântico e Alocação Adaptativa    |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>
#include <Math\Alglib\alglib.mqh>

class DynamicRiskManager {
private:
   double m_risk_percent;            // Risco base por operação
   double m_portfolio_risk;          // Risco máximo da carteira
   int m_max_orders;                 // Máximo de ordens por ativo
   double m_volatility_adjustment;   // Fator de ajuste por volatilidade
   double m_correlation_factor;      // Fator de correlação entre ativos
   
   // Proteção contra drawdown
   double m_drawdown_limit;          // Limite máximo de drawdown
   double m_equity_protection;       // Nível de proteção de equity
   
   // Sistema de trailing avançado
   struct TrailingProfile {
      double start;
      double step;
      double breakeven;
      bool dynamic;
   } m_trailing;
   
   // Memória de desempenho
   double m_performance[3];          // Desempenho [curto, médio, longo prazo]
   
   // Calcula exposição atual da carteira
   double CurrentPortfolioExposure() {
      double exposure = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         ulong ticket = PositionGetTicket(i);
         exposure += PositionGetDouble(POSITION_VOLUME) * 
                    PositionGetDouble(POSITION_PRICE_OPEN);
      }
      return exposure;
   }
   
   // Calcula volatilidade normalizada
   double NormalizedVolatility(string symbol) {
      double atr = iATR(symbol, PERIOD_D1, 14, 0);
      double avg_atr = iMA(symbol, PERIOD_D1, 30, 0, MODE_SMA, PRICE_CLOSE, 0);
      return atr / (avg_atr + 1e-8);
   }

public:
   DynamicRiskManager(double base_risk = 1.0, 
                     double portfolio_risk = 5.0,
                     int max_orders = 3) {
      m_risk_percent = base_risk;
      m_portfolio_risk = portfolio_risk;
      m_max_orders = max_orders;
      m_volatility_adjustment = 1.0;
      m_correlation_factor = 0.5;
      m_drawdown_limit = 20.0;
      m_equity_protection = 5.0;
      
      // Configuração padrão do trailing
      m_trailing.start = 50;
      m_trailing.step = 20;
      m_trailing.breakeven = 60;
      m_trailing.dynamic = true;
      
      ArrayInitialize(m_performance, 0);
   }

   // Verificação de risco hierárquico
   bool CanOpenNewPosition(string symbol, int magic, double potential_loss) {
      // 1. Verifica limite por ativo
      int count = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         if(PositionGetString(POSITION_SYMBOL) == symbol &&
            PositionGetInteger(POSITION_MAGIC) == magic)
            count++;
      }
      if(count >= m_max_orders) return false;
      
      // 2. Verifica risco da carteira
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double drawdown = (balance - equity) / balance * 100;
      
      if(drawdown >= m_drawdown_limit) return false;
      
      // 3. Verifica exposição total
      double exposure = CurrentPortfolioExposure();
      double max_exposure = equity * m_portfolio_risk / 100.0;
      if(exposure + potential_loss > max_exposure) return false;
      
      return true;
   }

   // Cálculo de lote com gestão adaptativa
   double CalcLot(string symbol, double sl_pips, double confidence = 1.0) {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      
      // Ajuste por volatilidade
      double vol_factor = MathPow(NormalizedVolatility(symbol), 0.5);
      
      // Ajuste por desempenho
      double performance_factor = 1.0 + (m_performance[0] + m_performance[1])/2;
      
      // Cálculo do lote base
      double risk_amount = balance * (m_risk_percent/100.0) * confidence * 
                          vol_factor * performance_factor;
      double lot = risk_amount / (sl_pips * _Point * tick_value);
      
      // Ajuste para limites do corretor
      double min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      double step_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
      
      lot = MathMax(min_lot, MathMin(max_lot, lot));
      lot = MathFloor(lot / step_lot) * step_lot;
      
      return NormalizeDouble(lot, 2);
   }

   // Gerenciamento de posições avançado
   void ManagePositions(string symbol, CTrade& trade, int magic) {
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      
      // Proteção de equity
      if((balance - equity) >= m_equity_protection/100.0 * balance) {
         CloseAllPositions(trade, magic);
         return;
      }
      
      // Trailing stop dinâmico
      for(int i=0; i<PositionsTotal(); i++) {
         ulong ticket = PositionGetTicket(i);
         if(PositionGetString(POSITION_SYMBOL) != symbol ||
            PositionGetInteger(POSITION_MAGIC) != magic)
            continue;
            
         ManageTrailingStop(ticket, trade);
         ManageBreakeven(ticket, trade);
      }
   }

private:
   // Gerenciamento de trailing stop adaptativo
   void ManageTrailingStop(ulong ticket, CTrade& trade) {
      string symbol = PositionGetString(POSITION_SYMBOL);
      double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
      double current_sl = PositionGetDouble(POSITION_SL);
      double current_tp = PositionGetDouble(POSITION_TP);
      
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
         double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
         double profit_pips = (bid - open_price) / _Point;
         
         if(profit_pips > m_trailing.start) {
            double new_sl = bid - m_trailing.step * _Point;
            if(new_sl > current_sl || current_sl == 0) {
               trade.PositionModify(ticket, new_sl, current_tp);
            }
         }
      }
      else {
         double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
         double profit_pips = (open_price - ask) / _Point;
         
         if(profit_pips > m_trailing.start) {
            double new_sl = ask + m_trailing.step * _Point;
            if(new_sl < current_sl || current_sl == 0) {
               trade.PositionModify(ticket, new_sl, current_tp);
            }
         }
      }
   }
   
   // Gerenciamento de breakeven adaptativo
   void ManageBreakeven(ulong ticket, CTrade& trade) {
      string symbol = PositionGetString(POSITION_SYMBOL);
      double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
      double current_sl = PositionGetDouble(POSITION_SL);
      double current_tp = PositionGetDouble(POSITION_TP);
      
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
         double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
         double profit_pips = (bid - open_price) / _Point;
         
         if(profit_pips > m_trailing.breakeven && 
            (current_sl < open_price || current_sl == 0)) {
            trade.PositionModify(ticket, open_price, current_tp);
         }
      }
      else {
         double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
         double profit_pips = (open_price - ask) / _Point;
         
         if(profit_pips > m_trailing.breakeven && 
            (current_sl > open_price || current_sl == 0)) {
            trade.PositionModify(ticket, open_price, current_tp);
         }
      }
   }
   
   // Fechamento emergencial de posições
   void CloseAllPositions(CTrade& trade, int magic) {
      for(int i=PositionsTotal()-1; i>=0; i--) {
         ulong ticket = PositionGetTicket(i);
         if(PositionGetInteger(POSITION_MAGIC) == magic) {
            trade.PositionClose(ticket);
         }
      }
   }

public:
   // Cálculo de SL com base na volatilidade
   double CalculateSL(string symbol, double entry, int direction) {
      double atr = iATR(symbol, PERIOD_H1, 14, 0);
      double volatility_sl = atr * 2.0; // 2x ATR
      
      return (direction == ORDER_TYPE_BUY)
             ? entry - volatility_sl
             : entry + volatility_sl;
   }

   // Cálculo de TP com base no risco
   double CalculateTP(string symbol, double entry, int direction, double sl_pips) {
      double risk_reward = 1.5; // Ratio padrão
      return (direction == ORDER_TYPE_BUY)
             ? entry + sl_pips * risk_reward * _Point
             : entry - sl_pips * risk_reward * _Point;
   }
   
   // Atualiza desempenho do sistema
   void UpdatePerformance(double trade_result) {
      // Desloca o array de desempenho
      m_performance[2] = m_performance[1];
      m_performance[1] = m_performance[0];
      m_performance[0] = trade_result > 0 ? 0.1 : -0.1;
   }
   
   // Configuração dinâmica de parâmetros
   void SetTrailingParameters(double start, double step, double breakeven, bool dynamic=true) {
      m_trailing.start = start;
      m_trailing.step = step;
      m_trailing.breakeven = breakeven;
      m_trailing.dynamic = dynamic;
   }
};