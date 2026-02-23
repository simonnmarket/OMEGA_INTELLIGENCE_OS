//+------------------------------------------------------------------+
//| CVolatilityManager.mqh - Advanced Volatility Management System    |
//| Version 3.0 - Unified and Enhanced (2025)                        |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property link      "https://www.quantumtrading.foundation"
#property version   "3.0"
#property strict

#include "..\Utils\CLogger.mqh"
#include "VolatilityMetrics.mqh"
#include <Trade\Trade.mqh>
#include <Object.mqh>
#include <StdLibErr.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>

//===========================================
// ENUMS
//===========================================
enum VolatilityRegime {
   REGIME_LOW = 0,
   REGIME_NORMAL = 1,
   REGIME_HIGH = 2,
   REGIME_EXTREME = 3
};

enum VolatilityMethod {
   METHOD_ATR = 0,
   METHOD_GARCH = 1,
   METHOD_HYBRID = 2,
   METHOD_QUANTUM = 3
};

//===========================================
// STRUCTURES
//===========================================
struct VolatilityConfig {
   string symbol;
   ENUM_TIMEFRAMES timeframe;
   int lookback_period;
   int atr_period;
   double volatility_threshold;
   VolatilityMethod method;
   bool use_quantum;
   int monte_carlo_paths;
   int min_data_points;
};

//===========================================
// CLASS: VOLATILITY MANAGER
//===========================================
class CVolatilityManager : public CObject {
private:
   // Configuração
   VolatilityConfig m_config;
   bool m_is_initialized;
   CLogger* m_logger;
   
   // Handles e Buffers
   int m_atr_handle;
   double m_volatility_buffer[];
   double m_returns_buffer[];
   
   // Métricas
   VolatilityMetrics m_metrics;
   VolatilityRegime m_current_regime;
   
   // Validações
   bool ValidateConfig(const VolatilityConfig &config) {
      if(config.symbol == NULL || config.symbol == "") {
         if(m_logger) m_logger.LogError("Símbolo inválido");
         return false;
      }
      
      if(config.timeframe <= 0) {
         if(m_logger) m_logger.LogError("Timeframe inválido");
         return false;
      }
      
      if(config.lookback_period < m_config.min_data_points) {
         if(m_logger) m_logger.LogError("Período de lookback insuficiente");
         return false;
      }
      
      if(config.atr_period <= 0) {
         if(m_logger) m_logger.LogError("Período ATR inválido");
         return false;
      }
      
      if(config.volatility_threshold <= 0) {
         if(m_logger) m_logger.LogError("Limite de volatilidade inválido");
         return false;
      }
      
      return true;
   }
   
   // Cálculos
   double CalculateATRVolatility() {
      if(m_atr_handle == INVALID_HANDLE) return 0;
      
      double buffer[];
      if(CopyBuffer(m_atr_handle, 0, 0, 1, buffer) <= 0) return 0;
      
      double close = iClose(m_config.symbol, m_config.timeframe, 0);
      if(close == 0) return 0;
      
      return buffer[0] / close;
   }
   
   double CalculateGARCHVolatility() {
      if(!m_is_initialized) return 0;
      
      datetime end_time = TimeCurrent();
      datetime start_time = end_time - m_config.lookback_period * PeriodSeconds(m_config.timeframe);
      
      if(!HistorySelect(start_time, end_time)) {
         if(m_logger) m_logger.LogError("Falha ao selecionar histórico");
         return 0;
      }
      
      int total = HistoryDealsTotal();
      if(total < m_config.min_data_points) {
         if(m_logger) m_logger.LogWarn("Dados insuficientes para GARCH");
         return 0;
      }
      
      ArrayResize(m_returns_buffer, total);
      for(int i = 0; i < total; i++) {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0) {
            m_returns_buffer[i] = HistoryDealGetDouble(ticket, DEAL_PROFIT);
         }
      }
      
      double variance = 0;
      CAlglib::GARCHFit(m_returns_buffer, variance);
      return MathSqrt(variance);
   }
   
   double CalculateQuantumVolatility() {
      if(!m_config.use_quantum) return 0;
      
      double atr = CalculateATRVolatility();
      double garch = CalculateGARCHVolatility();
      double roc = iROC(m_config.symbol, m_config.timeframe, 20, PRICE_CLOSE, 0);
      
      // Quantum superposition of volatility measures
      double quantum_factor = MathSin(TimeCurrent() * 0.0001); // Quantum oscillation
      return (atr * 0.4 + garch * 0.4 + MathAbs(roc) * 0.2) * (1 + quantum_factor * 0.1);
   }
   
   VolatilityRegime DetermineRegime(double volatility) {
      if(volatility < m_config.volatility_threshold * 0.5)
         return REGIME_LOW;
      else if(volatility < m_config.volatility_threshold)
         return REGIME_NORMAL;
      else if(volatility < m_config.volatility_threshold * 2)
         return REGIME_HIGH;
      else
         return REGIME_EXTREME;
   }
   
   void UpdateMetrics(double volatility) {
      m_metrics.garch_volatility = CalculateGARCHVolatility();
      m_metrics.markov_state = (int)m_current_regime;
      m_metrics.combined_filter = volatility;
      m_metrics.regime_probability = volatility / m_config.volatility_threshold;
      m_metrics.last_update = TimeCurrent();
   }

public:
   CVolatilityManager(CLogger* logger = NULL) : m_logger(logger) {
      m_is_initialized = false;
      m_atr_handle = INVALID_HANDLE;
      m_current_regime = REGIME_NORMAL;
      
      // Configuração padrão
      m_config.symbol = "";
      m_config.timeframe = PERIOD_CURRENT;
      m_config.lookback_period = 100;
      m_config.atr_period = 14;
      m_config.volatility_threshold = 0.002;
      m_config.method = METHOD_HYBRID;
      m_config.use_quantum = true;
      m_config.monte_carlo_paths = 1000;
      m_config.min_data_points = 30;
   }
   
   ~CVolatilityManager() {
      Release();
   }
   
   bool Initialize(const VolatilityConfig &config) {
      if(m_is_initialized) {
         if(m_logger) m_logger.LogError("CVolatilityManager já inicializado");
         return false;
      }
      
      if(!ValidateConfig(config)) return false;
      
      m_config = config;
      
      // Inicializar ATR
      m_atr_handle = iATR(m_config.symbol, m_config.timeframe, m_config.atr_period);
      if(m_atr_handle == INVALID_HANDLE) {
         if(m_logger) m_logger.LogError("Erro ao criar ATR");
         return false;
      }
      
      m_is_initialized = true;
      if(m_logger) m_logger.LogInfo("CVolatilityManager inicializado");
      return true;
   }
   
   void Release() {
      if(!m_is_initialized) return;
      
      if(m_atr_handle != INVALID_HANDLE) {
         IndicatorRelease(m_atr_handle);
         m_atr_handle = INVALID_HANDLE;
      }
      
      m_is_initialized = false;
   }
   
   double GetVolatility() {
      if(!m_is_initialized) return 0;
      
      double volatility = 0;
      
      switch(m_config.method) {
         case METHOD_ATR:
            volatility = CalculateATRVolatility();
            break;
         case METHOD_GARCH:
            volatility = CalculateGARCHVolatility();
            break;
         case METHOD_QUANTUM:
            volatility = CalculateQuantumVolatility();
            break;
         case METHOD_HYBRID:
         default:
            volatility = (CalculateATRVolatility() * 0.4 + 
                         CalculateGARCHVolatility() * 0.4 + 
                         CalculateQuantumVolatility() * 0.2);
            break;
      }
      
      m_current_regime = DetermineRegime(volatility);
      UpdateMetrics(volatility);
      
      return volatility;
   }
   
   double AdjustSignal(double signal) {
      if(!m_is_initialized) return signal;
      
      double volatility = GetVolatility();
      double adjustment = 1.0 - (volatility / m_config.volatility_threshold);
      
      // Limitar ajuste entre 0.1 e 1.0
      adjustment = MathMax(0.1, MathMin(1.0, adjustment));
      
      return signal * adjustment;
   }
   
   bool IsVolatile() {
      if(!m_is_initialized) return false;
      return GetVolatility() > m_config.volatility_threshold;
   }
   
   VolatilityRegime GetCurrentRegime() const {
      return m_current_regime;
   }
   
   VolatilityMetrics GetMetrics() const {
      return m_metrics;
   }
   
   bool IsInitialized() const {
      return m_is_initialized;
   }
}; 