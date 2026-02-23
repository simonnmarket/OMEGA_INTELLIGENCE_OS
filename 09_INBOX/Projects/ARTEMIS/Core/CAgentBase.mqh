//+------------------------------------------------------------------+
//| CAgentBase.mqh - Sistema Institucional Completo (v8.0)           |
//| Linhas originais: 375 | Novas linhas: 225 | Total: 600+         |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

//===========================================
// SEÇÃO 1: INCLUDES CENTRALIZADOS
//===========================================
#include "Include\\ProjectConfig.mqh"

//===========================================
// SEÇÃO 1: INCLUDES ORIGINAIS (MANTIDOS)
//===========================================
#include <Trade\\Trade.mqh>
#include "Utils\\CLogger.mqh"
#include "Risk\\CRiskManager.mqh"
#include "Quantum\\CQuantumMarketPhysics.mqh"
#include "Math\\CStatistics.mqh"
#include "Neural\\NeuralPredictor.mqh"
#include <Arrays\\ArrayObj.mqh>
#include "Include\\Crypt\\CHash.mqh"
#include "Quantum\\CVolatilityQuantum.mqh"
#include "Quantum\\VolatilityMetrics.mqh"
#include "Analysis\\CAnalysisModule.mqh"

//===========================================
// SEÇÃO 2: DECLARAÇÕES DE CLASSES
//===========================================
class CDarkPoolExecution;

//===========================================
// SEÇÃO 2: ESTRUTURAS ORIGINAIS (MANTIDAS)
//===========================================
enum TradeSignal {
   SIGNAL_NEUTRAL = 0,
   SIGNAL_BUY = 1,
   SIGNAL_SELL = -1
};

enum MarketRegime {
   REGIME_TRENDING = 0,
   REGIME_RANGING = 1,
   REGIME_VOLATILE = 2
};

struct AgentMetrics {
   int total_signals;
   int correct_signals;
   double win_rate;
   double avg_profit;
   double max_drawdown;
   datetime last_signal_time;
   double last_signal_value;
   double last_signal_confidence;
   double sharpe_ratio;
   double profit_factor;
   double max_consecutive_wins;
   double max_consecutive_losses;
};

struct Signal {
   datetime time;
   double value;
   double confidence;
   double profit;
   bool is_correct;
   string hash;
   MarketRegime regime;
   double ai_validation_score;
};

struct Venue {
   string name;
   double latency;
   double spread;
   double score;
};

//===========================================
// SEÇÃO 3: NOVAS ESTRUTURAS QUÂNTICAS
//===========================================
struct QuantumMetrics {
   double wave_collapse_probability;
   double entanglement_entropy;
   double superposition_score;
   int quantum_signals;
};

//===========================================
// SEÇÃO 4: ESTRUTURAS INSTITUCIONAIS
//===========================================
struct DarkPoolMetrics {
   double total_executed_volume;
   double avg_execution_price;
   double slippage;
   int total_fragments;
   double fill_ratio;
   datetime last_execution;
};

//===========================================
// CLASSE PRINCIPAL (COMPLETA)
//===========================================
class CAgentBase : public CObject {
private:
   //-----------------------------
   // VARIÁVEIS ORIGINAIS (MANTIDAS)
   //-----------------------------
   string m_name;
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   double m_confidence;
   AgentMetrics m_metrics;
   CLogger* m_logger;
   CRiskManager* m_risk_manager;
   CQuantumMarketPhysics* m_quantum_physics;
   double m_min_confidence;
   double m_max_position_size;
   int m_max_signals_per_day;
   int m_signals_today;
   datetime m_last_signal_date;
   double m_risk_percent;
   double m_stop_loss_pips;
   Signal m_signals[];

   //-----------------------------
   // NOVAS VARIÁVEIS QUÂNTICAS
   //-----------------------------
   QuantumMetrics m_qmetrics;
   double m_quantum_boost_factor;
   bool m_quantum_mode_enabled;

   //-----------------------------
   // NOVAS VARIÁVEIS DE MERCADO
   //-----------------------------
   MarketRegime m_current_regime;
   double m_atr_threshold;
   double m_roc_threshold;
   int m_regime_detection_period;
   double m_profits[];
   Venue m_venues[];

   //-----------------------------
   // NOVAS VARIÁVEIS INSTITUCIONAIS
   //-----------------------------
   CDarkPoolExecution* m_dark_pool;
   CVolatilityQuantum* m_volatility;
   bool m_use_dark_pool;
   bool m_use_volatility_filter;
   double m_min_volatility_threshold;
   double m_max_volatility_threshold;

   //-----------------------------
   // MÉTODOS PRIVADOS NOVOS
   //-----------------------------
   MarketRegime DetectMarketRegime() {
      double atr = iATR(m_symbol, m_timeframe, 14, 0);
      double roc = iROC(m_symbol, m_timeframe, 20, PRICE_CLOSE, 0);
      
      if(atr > m_atr_threshold && MathAbs(roc) > m_roc_threshold)
         return REGIME_VOLATILE;
      else if(MathAbs(roc) > 0.1)
         return REGIME_TRENDING;
      else
         return REGIME_RANGING;
   }

   double ValidateSignalWithAI(const Signal &signal) {
      double score = 0.2 * signal.value + 
                    0.4 * signal.confidence + 
                    0.4 * m_qmetrics.superposition_score;
      return 1.0 / (1.0 + MathExp(-score));
   }

   void UpdatePerformanceMetrics() {
      if(ArraySize(m_profits) == 0) return;
      
      m_metrics.sharpe_ratio = CalculateSharpeRatio();
      m_metrics.profit_factor = CalculateProfitFactor();
      CalculateConsecutiveStats();
      
      // Log de métricas de performance
      m_logger.Audit(StringFormat("Performance Update - Sharpe: %.2f, Profit Factor: %.2f", 
         m_metrics.sharpe_ratio, m_metrics.profit_factor));
   }

   double CalculateSharpeRatio() {
      double avg = CStatistics::Mean(m_profits);
      double std = CStatistics::StdDev(m_profits);
      return std > 0 ? (avg / std) * MathSqrt(252) : 0;
   }

   double CalculateProfitFactor() {
      double gross_profit = 0, gross_loss = 0;
      for(int i = 0; i < ArraySize(m_profits); i++) {
         if(m_profits[i] > 0)
            gross_profit += m_profits[i];
         else
            gross_loss += MathAbs(m_profits[i]);
      }
      return gross_loss > 0 ? gross_profit / gross_loss : 0;
   }

   void CalculateConsecutiveStats() {
      int current_wins = 0, current_losses = 0;
      m_metrics.max_consecutive_wins = 0;
      m_metrics.max_consecutive_losses = 0;
      
      for(int i = 0; i < ArraySize(m_profits); i++) {
         if(m_profits[i] > 0) {
            current_wins++;
            current_losses = 0;
            m_metrics.max_consecutive_wins = MathMax(m_metrics.max_consecutive_wins, current_wins);
         } else {
            current_losses++;
            current_wins = 0;
            m_metrics.max_consecutive_losses = MathMax(m_metrics.max_consecutive_losses, current_losses);
         }
      }
   }

   string HashSignal(const Signal &signal) {
      string payload = StringFormat("%.2f|%.2f|%d|%d", 
         signal.value, signal.confidence, signal.time, signal.regime);
      uchar hash[];
      InstitutionalCrypto::HashData(CRYPT_HASH_SHA256, payload, hash);
      return CharArrayToString(hash);
   }

   void PlotSignal(const Signal &signal) {
      string label = "Signal_" + IntegerToString((int)signal.time);
      ObjectCreate(0, label, OBJ_ARROW, 0, signal.time, signal.value);
      ObjectSetInteger(0, label, OBJPROP_COLOR, signal.is_correct ? clrLime : clrRed);
      ObjectSetInteger(0, label, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, label, OBJPROP_ARROWCODE, signal.value > 0 ? 241 : 242);
   }

   Venue SelectBestVenue() {
      double best_score = DBL_MAX;
      Venue best;
      
      for(int i = 0; i < ArraySize(m_venues); i++) {
         m_venues[i].score = m_venues[i].latency * m_venues[i].spread;
         if(m_venues[i].score < best_score) {
            best_score = m_venues[i].score;
            best = m_venues[i];
         }
      }
      
      // Log da seleção de venue
      m_logger.Log(LOG_LEVEL_INFO, StringFormat("Venue selecionada: %s (Score: %.2f)", 
         best.name, best.score));
      
      return best;
   }

   bool ValidateExecutionConditions() {
      if(m_use_volatility_filter && m_volatility) {
         double volatility = m_volatility->AdvancedFilter(m_symbol);
         if(volatility < m_min_volatility_threshold || volatility > m_max_volatility_threshold) {
            m_logger.Warn(StringFormat("Volatilidade fora dos limites: %.4f", volatility));
            return false;
         }
      }
      return true;
   }

   bool ExecuteOrder(double volume, double price) {
      if(m_use_dark_pool && m_dark_pool) {
         return m_dark_pool->ExecuteTWAP(m_symbol, volume, 30); // 30 minutos TWAP
      } else {
         CTrade trade;
         trade.SetDeviationInPoints(10);
         return trade.SellLimit(volume, price, m_symbol, 0, 0, ORDER_TIME_GTC);
      }
   }

   CAnalysisModule* m_analysis_module;

public:
   //===========================================
   // CONSTRUTOR ORIGINAL (EXPANDIDO)
   //===========================================
   CAgentBase(const string &name, const string &symbol, ENUM_TIMEFRAMES timeframe,
              CLogger* logger = NULL, CRiskManager* risk_manager = NULL,
              CQuantumMarketPhysics* quantum_physics = NULL) :
      m_name(name),
      m_symbol(symbol),
      m_timeframe(timeframe),
      m_confidence(0.5),
      m_logger(logger),
      m_risk_manager(risk_manager),
      m_quantum_physics(quantum_physics)
   {
      // Inicialização original mantida
      m_metrics.total_signals = 0;
      m_metrics.correct_signals = 0;
      m_metrics.win_rate = 0.0;
      m_metrics.avg_profit = 0.0;
      m_metrics.max_drawdown = 0.0;
      m_metrics.last_signal_time = 0;
      m_metrics.last_signal_value = 0.0;
      m_metrics.last_signal_confidence = 0.0;
      m_metrics.sharpe_ratio = 0.0;
      m_metrics.profit_factor = 0.0;
      m_metrics.max_consecutive_wins = 0;
      m_metrics.max_consecutive_losses = 0;

      m_min_confidence = 0.6;
      m_max_position_size = 1.0;
      m_max_signals_per_day = 5;
      m_signals_today = 0;
      m_last_signal_date = TimeCurrent();
      m_risk_percent = 1.0;
      m_stop_loss_pips = 50.0;

      // Inicialização quântica
      m_qmetrics.wave_collapse_probability = 1.0;
      m_qmetrics.entanglement_entropy = 0.0;
      m_qmetrics.superposition_score = 0.0;
      m_qmetrics.quantum_signals = 0;
      m_quantum_boost_factor = 1.0;
      m_quantum_mode_enabled = true;

      // Inicialização de mercado
      m_current_regime = REGIME_RANGING;
      m_atr_threshold = 0.002;
      m_roc_threshold = 0.001;
      m_regime_detection_period = 20;

      // Inicialização de venues
      InitializeVenues();

      // Inicialização institucional
      m_dark_pool = new CDarkPoolExecution(symbol, logger);
      m_volatility = new CVolatilityQuantum(symbol, logger);
      m_use_dark_pool = true;
      m_use_volatility_filter = true;
      m_min_volatility_threshold = 0.001;
      m_max_volatility_threshold = 0.05;

      // Inicialização do módulo de análise
      m_analysis_module = new CAnalysisModule(logger);
      
      // Configurar dependências
      ModuleDependency dp_dep;
      dp_dep.module_name = "Dark Pool";
      dp_dep.required_version = "1.0";
      dp_dep.is_optional = false;
      m_analysis_module.AddDependency(dp_dep);
      
      ModuleDependency vol_dep;
      vol_dep.module_name = "Volatility";
      vol_dep.required_version = "1.0";
      vol_dep.is_optional = false;
      m_analysis_module.AddDependency(vol_dep);
      
      Log("Agent fully initialized with institutional features", "DEBUG");
   }

   ~CAgentBase() {
      if(m_dark_pool) delete m_dark_pool;
      if(m_volatility) delete m_volatility;
      if(m_analysis_module) delete m_analysis_module;
   }

   //===========================================
   // MÉTODOS ORIGINAIS (COMPLETOS)
   //===========================================
   virtual void Update() {
      ResetDailyCounters();
      if(m_quantum_mode_enabled) {
         UpdateQuantumState();
      }
      m_current_regime = DetectMarketRegime();
      UpdatePerformanceMetrics();
   }

   virtual double GetSignal() {
      double classic_signal = CalculateSignal();
      
      if(m_quantum_mode_enabled && m_quantum_physics) {
         double quantum_signal = m_quantum_physics->CalculateSignal(m_symbol);
         classic_signal = (classic_signal * 0.6) + (quantum_signal * 0.4);
         m_qmetrics.quantum_signals++;
      }

      if(classic_signal != 0.0 && m_confidence >= m_min_confidence && 
         m_signals_today < m_max_signals_per_day) {
         
         // Validação institucional
         if(!ValidateExecutionConditions()) {
            Log("Signal rejected: execution conditions not met", "WARN");
            return 0.0;
         }

         if(m_risk_manager && !m_risk_manager.CheckExposureLimit(m_symbol, MathAbs(classic_signal))) {
            Log("Signal rejected: exposure limit exceeded", "WARN");
            return 0.0;
         }

         Signal new_signal;
         new_signal.time = TimeCurrent();
         new_signal.value = classic_signal;
         new_signal.confidence = m_confidence;
         new_signal.regime = m_current_regime;
         new_signal.ai_validation_score = ValidateSignalWithAI(new_signal);
         new_signal.hash = HashSignal(new_signal);

         RegisterSignal(new_signal);
         PlotSignal(new_signal);
         
         m_signals_today++;
         Log(StringFormat("New hybrid signal: %.2f (confidence: %.2f, quantum boost: %.2f, regime: %d, AI score: %.2f)", 
            classic_signal, m_confidence, m_quantum_boost_factor, m_current_regime, new_signal.ai_validation_score));
         
         return classic_signal;
      }
      return 0.0;
   }

   //===========================================
   // MÉTODOS QUÂNTICOS NOVOS
   //===========================================
   void EnableQuantumMode(bool enable) {
      m_quantum_mode_enabled = enable;
      Log(StringFormat("Quantum mode %s", enable ? "ACTIVATED" : "DEACTIVATED"), "INFO");
   }

   void UpdateQuantumState() {
      if(!m_quantum_physics) return;
      
      m_qmetrics.wave_collapse_probability = m_quantum_physics->GetCollapseProbability(m_symbol);
      m_qmetrics.entanglement_entropy = m_quantum_physics->CalculateEntanglement(m_symbol, "EURUSD,GBPUSD,XAUUSD");
      m_quantum_boost_factor = 1.0 + (m_qmetrics.wave_collapse_probability * 0.5);
   }

   QuantumMetrics GetQuantumMetrics() const {
      return m_qmetrics;
   }

   //===========================================
   // NOVOS MÉTODOS INSTITUCIONAIS
   //===========================================
   void EnableDarkPool(bool enable) {
      m_use_dark_pool = enable;
      Log(StringFormat("Dark Pool Execution %s", enable ? "ACTIVATED" : "DEACTIVATED"), "INFO");
   }

   void EnableVolatilityFilter(bool enable) {
      m_use_volatility_filter = enable;
      Log(StringFormat("Volatility Filter %s", enable ? "ACTIVATED" : "DEACTIVATED"), "INFO");
   }

   void SetVolatilityThresholds(double min_threshold, double max_threshold) {
      m_min_volatility_threshold = min_threshold;
      m_max_volatility_threshold = max_threshold;
      Log(StringFormat("Volatility thresholds updated: %.4f - %.4f", 
         min_threshold, max_threshold), "INFO");
   }

   DarkPoolMetrics GetDarkPoolMetrics() const {
      return m_dark_pool ? m_dark_pool->GetMetrics() : DarkPoolMetrics();
   }

   VolatilityMetrics GetVolatilityMetrics() const {
      return m_volatility ? m_volatility->GetMetrics() : VolatilityMetrics();
   }

   //===========================================
   // MÉTODOS ORIGINAIS (MANTIDOS)
   //===========================================
   virtual double CalculateSignal() = 0;

   void RegisterSignal(const Signal &signal) {
      ArrayResize(m_signals, ArraySize(m_signals) + 1);
      m_signals[ArraySize(m_signals) - 1] = signal;

      m_metrics.total_signals++;
      m_metrics.last_signal_time = signal.time;
      m_metrics.last_signal_value = signal.value;
      m_metrics.last_signal_confidence = signal.confidence;
   }

   void ResetDailyCounters() {
      datetime now = TimeCurrent();
      if(TimeDay(now) != TimeDay(m_last_signal_date)) {
         m_signals_today = 0;
         m_last_signal_date = now;
      }
   }

   void Log(string message, string severity = "INFO") {
      if(m_logger) {
         string full_message = StringFormat("[%s] %s", m_name, message);
         if(severity == "ERROR") m_logger.Error(full_message);
         else if(severity == "WARN") m_logger.Warn(full_message);
         else m_logger.Info(full_message);
      }
   }

   //===========================================
   // NOVOS MÉTODOS PÚBLICOS
   //===========================================
   void SetRegimeThresholds(double atr_threshold, double roc_threshold) {
      m_atr_threshold = atr_threshold;
      m_roc_threshold = roc_threshold;
   }

   MarketRegime GetCurrentRegime() const {
      return m_current_regime;
   }

   AgentMetrics GetMetrics() const {
      return m_metrics;
   }

   string GetMetricsReport() const {
      return StringFormat(
         "=== Agent Performance Report ===\n" +
         "Total Signals: %d\n" +
         "Win Rate: %.2f%%\n" +
         "Avg Profit: %.2f\n" +
         "Max Drawdown: %.2f%%\n" +
         "Sharpe Ratio: %.2f\n" +
         "Profit Factor: %.2f\n" +
         "Max Consecutive Wins: %.0f\n" +
         "Max Consecutive Losses: %.0f\n" +
         "Current Regime: %d\n" +
         "Quantum Signals: %d\n" +
         "Quantum Coherence: %.2f\n",
         m_metrics.total_signals,
         m_metrics.win_rate * 100,
         m_metrics.avg_profit,
         m_metrics.max_drawdown * 100,
         m_metrics.sharpe_ratio,
         m_metrics.profit_factor,
         m_metrics.max_consecutive_wins,
         m_metrics.max_consecutive_losses,
         m_current_regime,
         m_qmetrics.quantum_signals,
         m_qmetrics.wave_collapse_probability
      );
   }

   bool ValidateSystem() {
      if(!m_analysis_module) return false;
      return m_analysis_module->ValidateAll();
   }

   string GetValidationReport() const {
      return m_analysis_module ? m_analysis_module->GetValidationReport() : "Módulo de análise não inicializado";
   }

   ValidationMetrics GetValidationMetrics() const {
      return m_analysis_module ? m_analysis_module->GetMetrics() : ValidationMetrics();
   }

private:
   void InitializeVenues() {
      ArrayResize(m_venues, 3);
      
      // Venue 1
      m_venues[0].name = "Primary";
      m_venues[0].latency = 0.001;
      m_venues[0].spread = 0.0002;
      
      // Venue 2
      m_venues[1].name = "Secondary";
      m_venues[1].latency = 0.002;
      m_venues[1].spread = 0.00015;
      
      // Venue 3
      m_venues[2].name = "Tertiary";
      m_venues[2].latency = 0.003;
      m_venues[2].spread = 0.0001;
   }
};

//===========================================
// CLASSE: DARK POOL EXECUTION (CITADEL)
//===========================================
class CDarkPoolExecution {
private:
   string m_symbol;
   CLogger* m_logger;
   DarkPoolMetrics m_metrics;
   double m_min_fragment_size;
   double m_max_fragment_size;
   int m_max_retries;
   
   void FragmentOrder(double volume, double &fragments[]) {
      int fragmentsCount = (int)MathCeil(volume / m_max_fragment_size);
      ArrayResize(fragments, fragmentsCount);
      double remaining = volume;
      
      for(int i = 0; i < fragmentsCount; i++) {
         fragments[i] = MathMin(m_max_fragment_size, remaining);
         remaining -= fragments[i];
      }
   }
   
   bool ExecuteHiddenOrder(string symbol, double volume, double price) {
      // Implementação do Iceberg Order
      double fragments[];
      FragmentOrder(volume, fragments);
      
      for(int i = 0; i < ArraySize(fragments); i++) {
         if(!ExecuteFragment(symbol, fragments[i], price)) {
            m_logger.Error(StringFormat("Falha na execução do fragmento %d", i));
            return false;
         }
         Sleep(100); // Delay entre fragmentos
      }
      
      return true;
   }
   
   bool ExecuteFragment(string symbol, double volume, double price) {
      // Implementação da execução de fragmento
      CTrade trade;
      trade.SetDeviationInPoints(10);
      trade.SetTypeFilling(ORDER_FILLING_FOK);
      
      return trade.SellLimit(volume, price, symbol, 0, 0, ORDER_TIME_GTC);
   }
   
public:
   CDarkPoolExecution(string symbol, CLogger* logger = NULL) :
      m_symbol(symbol),
      m_logger(logger),
      m_min_fragment_size(1000),
      m_max_fragment_size(5000),
      m_max_retries(3)
   {
      m_metrics.total_executed_volume = 0;
      m_metrics.avg_execution_price = 0;
      m_metrics.slippage = 0;
      m_metrics.total_fragments = 0;
      m_metrics.fill_ratio = 0;
      m_metrics.last_execution = 0;
   }
   
   bool ExecuteTWAP(string symbol, double volume, int durationMinutes) {
      datetime endTime = TimeCurrent() + durationMinutes * 60;
      double executedVolume = 0;
      double totalPrice = 0;
      
      while(TimeCurrent() < endTime && executedVolume < volume) {
         double remaining = volume - executedVolume;
         double slice = MathMin(remaining, volume * 0.05); // 5% por execução
         double currentPrice = SymbolInfoDouble(symbol, SYMBOL_BID);
         
         if(ExecuteHiddenOrder(symbol, slice, currentPrice)) {
            executedVolume += slice;
            totalPrice += currentPrice * slice;
         }
         
         Sleep(60000); // Executa a cada 1 minuto
      }
      
      // Atualiza métricas
      m_metrics.total_executed_volume += executedVolume;
      m_metrics.avg_execution_price = totalPrice / executedVolume;
      m_metrics.fill_ratio = executedVolume / volume;
      m_metrics.last_execution = TimeCurrent();
      
      return (executedVolume >= volume * 0.95); // 95% de preenchimento mínimo
   }
   
   DarkPoolMetrics GetMetrics() const {
      return m_metrics;
   }
};