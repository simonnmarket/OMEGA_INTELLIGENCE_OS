//+------------------------------------------------------------------+
//| HistoryOrderInfo.mqh - Order History Management                   |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "..\\Utils\\CLogger.mqh"

class CHistoryOrderInfo {
private:
   CLogger* m_logger;
   double m_total_profit;
   int m_total_trades;
   int m_winning_trades;
   double m_max_drawdown;
   
public:
   CHistoryOrderInfo(CLogger* logger = NULL) :
      m_logger(logger),
      m_total_profit(0),
      m_total_trades(0),
      m_winning_trades(0),
      m_max_drawdown(0)
   {
   }
   
   ~CHistoryOrderInfo() {
   }
   
   bool Initialize() {
      UpdateMetrics();
      return true;
   }
   
   double GetTotalProfit() const {
      return m_total_profit;
   }
   
   double GetWinRate() const {
      return m_total_trades > 0 ? (double)m_winning_trades / m_total_trades : 0;
   }
   
   double GetAverageProfit() const {
      return m_total_trades > 0 ? m_total_profit / m_total_trades : 0;
   }
   
   double GetMaxDrawdown() const {
      return m_max_drawdown;
   }
   
   void UpdateMetrics() {
      m_total_profit = 0;
      m_total_trades = 0;
      m_winning_trades = 0;
      m_max_drawdown = 0;
      
      double current_drawdown = 0;
      double peak_balance = 0;
      
      for(int i = 0; i < OrdersHistoryTotal(); i++) {
         if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) {
            m_total_trades++;
            double profit = OrderProfit() + OrderSwap() + OrderCommission();
            m_total_profit += profit;
            
            if(profit > 0) {
               m_winning_trades++;
            }
            
            // Atualizar drawdown
            if(m_total_profit > peak_balance) {
               peak_balance = m_total_profit;
            }
            current_drawdown = peak_balance - m_total_profit;
            if(current_drawdown > m_max_drawdown) {
               m_max_drawdown = current_drawdown;
            }
         }
      }
      
      if(m_logger) {
         m_logger.Info(StringFormat("Métricas atualizadas - Lucro: %.2f, Trades: %d, Win Rate: %.2f%%, Drawdown: %.2f",
            m_total_profit, m_total_trades, GetWinRate() * 100, m_max_drawdown));
      }
   }
}; 