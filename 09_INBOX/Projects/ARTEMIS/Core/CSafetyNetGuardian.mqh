//+------------------------------------------------------------------+
//| CSafetyNetGuardian.mqh - Sistema de Proteção e Segurança (v1.0)  |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include <Object.mqh>
#include "..\Utils\CLogger.mqh"
#include "..\Core\CStatistics.mqh"
#include <Trade\Trade.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\DealInfo.mqh>

//===========================================
// ESTRUTURAS DE DADOS
//===========================================
enum SafetyStatus {
   SAFETY_NORMAL = 0,
   SAFETY_WARNING = 1,
   SAFETY_CRITICAL = 2,
   SAFETY_EMERGENCY = 3
};

struct MarketCondition {
   double volatility;
   double spread;
   double liquidity;
   double volume;
   bool is_circuit_breaker;
};

struct SafetyMetrics {
   double max_drawdown;
   double current_drawdown;
   double exposure_ratio;
   int consecutive_losses;
   datetime last_check;
   SafetyStatus status;
};

//===========================================
// CLASSE PRINCIPAL
//===========================================
class CSafetyNetGuardian : public CObject {
private:
   //-----------------------------
   // VARIÁVEIS DE SEGURANÇA
   //-----------------------------
   string m_symbol;
   CLogger* m_logger;
   CTrade* m_trade;
   SafetyMetrics m_metrics;
   MarketCondition m_market;
   
   //-----------------------------
   // PARÂMETROS DE CONFIGURAÇÃO
   //-----------------------------
   double m_max_drawdown_threshold;
   double m_max_exposure_ratio;
   double m_volatility_threshold;
   double m_spread_threshold;
   double m_liquidity_threshold;
   int m_max_consecutive_losses;
   
   //-----------------------------
   // MÉTODOS PRIVADOS
   //-----------------------------
   void UpdateMarketCondition() {
      // Atualiza condições de mercado
      m_market.volatility = iATR(m_symbol, PERIOD_H1, 14, 0);
      m_market.spread = SymbolInfoDouble(m_symbol, SYMBOL_ASK) - SymbolInfoDouble(m_symbol, SYMBOL_BID);
      m_market.volume = iVolume(m_symbol, PERIOD_H1, 0);
      m_market.liquidity = CalculateLiquidity();
      m_market.is_circuit_breaker = CheckCircuitBreaker();
   }
   
   double CalculateLiquidity() {
      double volume = 0;
      for(int i = 0; i < 24; i++) {
         volume += iVolume(m_symbol, PERIOD_H1, i);
      }
      return volume / 24.0;
   }
   
   bool CheckCircuitBreaker() {
      double price_change = MathAbs(
         (iClose(m_symbol, PERIOD_H1, 0) - iOpen(m_symbol, PERIOD_H1, 0)) / 
         iOpen(m_symbol, PERIOD_H1, 0)
      );
      return price_change > 0.05; // 5% de variação em 1 hora
   }
   
   void UpdateSafetyMetrics() {
      // Atualiza métricas de segurança
      m_metrics.current_drawdown = CalculateCurrentDrawdown();
      m_metrics.exposure_ratio = CalculateExposureRatio();
      m_metrics.consecutive_losses = CountConsecutiveLosses();
      m_metrics.last_check = TimeCurrent();
      
      // Atualiza status de segurança
      UpdateSafetyStatus();
   }
   
   double CalculateCurrentDrawdown() {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      return (balance - equity) / balance;
   }
   
   double CalculateExposureRatio() {
      double total_exposure = 0;
      for(int i = 0; i < PositionsTotal(); i++) {
         if(PositionSelectByTicket(PositionGetTicket(i))) {
            total_exposure += PositionGetDouble(POSITION_VOLUME);
         }
      }
      return total_exposure / AccountInfoDouble(ACCOUNT_BALANCE);
   }
   
   int CountConsecutiveLosses() {
      int count = 0;
      for(int i = 0; i < HistoryDealsTotal(); i++) {
         if(HistoryDealSelect(i)) {
            if(HistoryDealGetInteger(DEAL_ENTRY) == DEAL_ENTRY_OUT) {
               if(HistoryDealGetDouble(DEAL_PROFIT) < 0) {
                  count++;
               } else {
                  break;
               }
            }
         }
      }
      return count;
   }
   
   void UpdateSafetyStatus() {
      if(m_metrics.current_drawdown > m_max_drawdown_threshold ||
         m_metrics.exposure_ratio > m_max_exposure_ratio ||
         m_metrics.consecutive_losses >= m_max_consecutive_losses ||
         m_market.is_circuit_breaker) {
         m_metrics.status = SAFETY_EMERGENCY;
      }
      else if(m_market.volatility > m_volatility_threshold ||
              m_market.spread > m_spread_threshold ||
              m_market.liquidity < m_liquidity_threshold) {
         m_metrics.status = SAFETY_CRITICAL;
      }
      else if(m_metrics.current_drawdown > m_max_drawdown_threshold * 0.7 ||
              m_metrics.exposure_ratio > m_max_exposure_ratio * 0.7) {
         m_metrics.status = SAFETY_WARNING;
      }
      else {
         m_metrics.status = SAFETY_NORMAL;
      }
   }
   
   void TakeEmergencyAction() {
      if(m_metrics.status == SAFETY_EMERGENCY) {
         // Fecha todas as posições
         for(int i = PositionsTotal() - 1; i >= 0; i--) {
            if(PositionSelectByTicket(PositionGetTicket(i))) {
               m_trade.PositionClose(PositionGetTicket(i));
            }
         }
         
         // Cancela todas as ordens pendentes
         for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(OrderSelect(OrderGetTicket(i))) {
               m_trade.OrderDelete(OrderGetTicket(i));
            }
         }
         
         Log("EMERGENCY: All positions closed and orders cancelled", "ERROR");
      }
   }
   
   void Log(string message, string severity = "INFO") {
      if(m_logger) {
         string full_message = StringFormat("[SafetyNet] %s", message);
         if(severity == "ERROR") m_logger.Error(full_message);
         else if(severity == "WARN") m_logger.Warn(full_message);
         else m_logger.Info(full_message);
      }
   }

public:
   //===========================================
   // CONSTRUTOR
   //===========================================
   CSafetyNetGuardian(const string &symbol, CLogger* logger = NULL) : 
      m_symbol(symbol),
      m_logger(logger)
   {
      m_trade = new CTrade();
      
      // Inicializa thresholds
      m_max_drawdown_threshold = 0.15;  // 15%
      m_max_exposure_ratio = 0.5;       // 50%
      m_volatility_threshold = 0.002;   // 0.2%
      m_spread_threshold = 0.0005;      // 5 pips
      m_liquidity_threshold = 1000;     // Volume mínimo
      m_max_consecutive_losses = 5;
      
      // Inicializa métricas
      m_metrics.max_drawdown = 0;
      m_metrics.current_drawdown = 0;
      m_metrics.exposure_ratio = 0;
      m_metrics.consecutive_losses = 0;
      m_metrics.last_check = 0;
      m_metrics.status = SAFETY_NORMAL;
      
      Log("Safety Net Guardian initialized", "DEBUG");
   }
   
   //===========================================
   // DESTRUTOR
   //===========================================
   ~CSafetyNetGuardian() {
      if(m_trade) delete m_trade;
   }
   
   //===========================================
   // MÉTODOS PÚBLICOS
   //===========================================
   void Update() {
      UpdateMarketCondition();
      UpdateSafetyMetrics();
      
      if(m_metrics.status >= SAFETY_CRITICAL) {
         TakeEmergencyAction();
      }
      
      Log(StringFormat("Safety status: %d, Drawdown: %.2f%%, Exposure: %.2f%%", 
         m_metrics.status,
         m_metrics.current_drawdown * 100,
         m_metrics.exposure_ratio * 100), "DEBUG");
   }
   
   bool IsSafeToTrade() const {
      return m_metrics.status == SAFETY_NORMAL;
   }
   
   SafetyStatus GetSafetyStatus() const {
      return m_metrics.status;
   }
   
   void SetMaxDrawdown(double threshold) {
      m_max_drawdown_threshold = MathMax(0.0, MathMin(1.0, threshold));
      Log(StringFormat("Max drawdown threshold set to %.1f%%", 
         m_max_drawdown_threshold * 100), "INFO");
   }
   
   void SetMaxExposure(double ratio) {
      m_max_exposure_ratio = MathMax(0.0, MathMin(1.0, ratio));
      Log(StringFormat("Max exposure ratio set to %.1f%%", 
         m_max_exposure_ratio * 100), "INFO");
   }
   
   string GetSafetyReport() const {
      return StringFormat(
         "=== Safety Net Report ===\n" +
         "Status: %d\n" +
         "Current Drawdown: %.2f%%\n" +
         "Max Drawdown: %.2f%%\n" +
         "Exposure Ratio: %.2f%%\n" +
         "Consecutive Losses: %d\n" +
         "Market Conditions:\n" +
         "  Volatility: %.5f\n" +
         "  Spread: %.5f\n" +
         "  Liquidity: %.2f\n" +
         "  Circuit Breaker: %s\n",
         m_metrics.status,
         m_metrics.current_drawdown * 100,
         m_metrics.max_drawdown * 100,
         m_metrics.exposure_ratio * 100,
         m_metrics.consecutive_losses,
         m_market.volatility,
         m_market.spread,
         m_market.liquidity,
         m_market.is_circuit_breaker ? "YES" : "NO"
      );
   }
}; 