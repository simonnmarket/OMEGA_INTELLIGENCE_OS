//+------------------------------------------------------------------+
//| HistoryOrderInfo.mqh - Order History Management                   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include <Object.mqh>
#include "Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Classe para informações de ordens históricas                      |
//+------------------------------------------------------------------+
class CHistoryOrderInfo : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   double m_total_profit;                // Lucro total
   int m_total_trades;                   // Total de trades
   int m_winning_trades;                 // Trades vencedores
   double m_max_drawdown;                // Máximo drawdown
   bool m_is_initialized;                // Se está inicializado
   
public:
   // Construtor
   CHistoryOrderInfo(CLogger* logger)
   {
      m_logger = logger;
      m_total_profit = 0.0;
      m_total_trades = 0;
      m_winning_trades = 0;
      m_max_drawdown = 0.0;
      m_is_initialized = false;
      
      if(m_logger != NULL)
      {
         m_logger.Info("Módulo de ordens históricas inicializado");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CHistoryOrderInfo()
   {
      if(m_logger != NULL)
         m_logger.Info("Módulo de ordens históricas finalizado");
   }
   
   // Atualiza métricas
   void UpdateMetrics()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Implementar lógica de atualização
   }
   
   // Obtém lucro total
   double GetTotalProfit() const
   {
      return m_total_profit;
   }
   
   // Obtém total de trades
   int GetTotalTrades() const
   {
      return m_total_trades;
   }
   
   // Obtém trades vencedores
   int GetWinningTrades() const
   {
      return m_winning_trades;
   }
   
   // Obtém máximo drawdown
   double GetMaxDrawdown() const
   {
      return m_max_drawdown;
   }
}; 