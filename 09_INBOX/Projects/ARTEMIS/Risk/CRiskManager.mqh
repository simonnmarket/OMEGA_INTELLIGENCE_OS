//+------------------------------------------------------------------+
//| CRiskManager.mqh - Institutional Risk Management System           |
//| Version 2.0 - Unified, Enhanced and Optimized (2025)             |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.quantumtrading.foundation" 
#property version   "1.0"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>
#include "..\Utils\CLogger.mqh"
#include "..\Math\CStatistics.mqh"
#include "..\Core\VolatilityAnalysis.mqh"
#include "..\Risk\PortfolioBalancer.mqh"
#include "DynamicLotManager.mqh"
#include "AdaptiveRiskSystem.mqh"
#include "..\Risk\TimeframeHierarchy.mqh"

// Estrutura para histórico de trades
struct TradeHistory {
   datetime time;
   string symbol;
   double profit;
   double risk;
   double reward;
};

// Estrutura para grupos de exposição
struct ExposureGroup {
   string name;
   double max_risk_percent;
   double current_exposure;
};

class CRiskManager : public CObject {
private:
   // Configurações gerais
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   double m_risk_per_trade;
   double m_max_daily_risk;
   double m_max_drawdown;
   int m_atr_period;
   int m_atr_handle;

   // Componentes especializados
   TimeframeHierarchy* m_timeframe_hierarchy;
   CStatistics* m_statistics;
   CVolatilityAnalysis* m_volatility;
   PortfolioBalancer* m_portfolio;
   CDynamicLotManager* m_lot_manager;
   CAdaptiveRiskSystem* m_risk_system;

   // Exposição por grupo
   ExposureGroup m_groups[];

   // Histórico de trades
   TradeHistory m_trades[];
   int m_monte_carlo_paths;

   // Estado do sistema
   bool m_is_initialized;

public:
   // Constructor
   CRiskManager(CLogger* logger = NULL) {
      m_symbol = "";
      m_timeframe = PERIOD_CURRENT;
      m_risk_per_trade = 0.02;
      m_max_daily_risk = 0.05;
      m_max_drawdown = 0.15;
      m_atr_period = 14;
      m_atr_handle = INVALID_HANDLE;

      m_timeframe_hierarchy = NULL;
      m_statistics = NULL;
      m_volatility = NULL;
      m_portfolio = NULL;
      m_lot_manager = NULL;
      m_risk_system = NULL;

      m_is_initialized = false;
      m_monte_carlo_paths = 1000;

      SetupExposureGroups();
   }

   // Destructor
   ~CRiskManager() {
      Release();
   }

   // Inicialização do sistema
   bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe,
                  double risk_per_trade = 0.02, double max_daily_risk = 0.05,
                  double max_drawdown = 0.15, int atr_period = 14) {

      if(m_is_initialized) return true;

      if(StringLen(symbol) == 0 || timeframe <= 0) {
         Log("Invalid parameters", "ERROR");
         return false;
      }

      m_symbol = symbol;
      m_timeframe = timeframe;
      m_risk_per_trade = risk_per_trade;
      m_max_daily_risk = max_daily_risk;
      m_max_drawdown = max_drawdown;
      m_atr_period = atr_period;

      // Inicializar ATR
      m_atr_handle = iATR(m_symbol, m_timeframe, m_atr_period);
      if(m_atr_handle == INVALID_HANDLE) {
         Log("Failed to create ATR handle", "ERROR");
         return false;
      }

      // Inicializar componentes
      m_timeframe_hierarchy = new TimeframeHierarchy();
      if(!m_timeframe_hierarchy.Initialize(m_symbol, m_timeframe)) {
         Log("Failed to initialize TimeframeHierarchy", "ERROR");
         return false;
      }

      m_statistics = new CStatistics();
      if(!m_statistics.Initialize(m_symbol, m_timeframe)) {
         Log("Failed to initialize Statistics", "ERROR");
         return false;
      }

      m_volatility = new CVolatilityAnalysis();
      if(!m_volatility.Initialize(m_symbol, m_timeframe)) {
         Log("Failed to initialize VolatilityAnalysis", "ERROR");
         return false;
      }

      m_portfolio = new PortfolioBalancer();
      if(!m_portfolio.Initialize(m_symbol, m_timeframe)) {
         Log("Failed to initialize PortfolioBalancer", "ERROR");
         return false;
      }

      m_lot_manager = new CDynamicLotManager();
      if(!m_lot_manager.Initialize(m_symbol, m_timeframe, m_risk_per_trade)) {
         Log("Failed to initialize DynamicLotManager", "ERROR");
         return false;
      }

      m_risk_system = new CAdaptiveRiskSystem();
      if(!m_risk_system.Initialize(m_symbol, m_timeframe, m_risk_per_trade, m_max_daily_risk, m_max_drawdown)) {
         Log("Failed to initialize AdaptiveRiskSystem", "ERROR");
         return false;
      }

      m_is_initialized = true;
      return true;
   }

   // Libera recursos
   void Release() {
      if(!m_is_initialized) return;

      IndicatorRelease(m_atr_handle);
      delete m_timeframe_hierarchy;
      delete m_statistics;
      delete m_volatility;
      delete m_portfolio;
      if(m_lot_manager != NULL) {
         delete m_lot_manager;
         m_lot_manager = NULL;
      }
      if(m_risk_system != NULL) {
         delete m_risk_system;
         m_risk_system = NULL;
      }
      m_is_initialized = false;
   }

   // Verificar se está inicializado
   bool IsInitialized() const {
      return m_is_initialized;
   }

   // Obter valor ATR
   double GetATR(int shift) {
      if(!m_is_initialized || m_risk_system == NULL) return 0;
      return m_risk_system.GetATR(shift);
   }

   // Verificar risco diário
   bool CheckDailyRisk() {
      if(!m_is_initialized) return false;
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double daily_profit = equity - balance;
      double max_loss = balance * m_max_daily_risk;
      return daily_profit >= -max_loss;
   }

   // Verificar drawdown
   bool CheckDrawdown() {
      if(!m_is_initialized) return false;
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double drawdown = (balance - equity) / balance;
      return drawdown <= m_max_drawdown;
   }

   // Calcular tamanho da posição com base no risco
   double CalculatePositionSize(double stop_loss_points) {
      if(!m_is_initialized || m_lot_manager == NULL) return 0;
      return m_lot_manager.CalculateLotSize(stop_loss_points);
   }

   // Calcular Sharpe Ratio
   double CalculateSharpeRatio(double risk_free_rate = 0.02) {
      double returns[];
      ArrayResize(returns, m_monte_carlo_paths);
      MathSrand((int)(TimeCurrent() * TimeGMT()));
      for(int i = 0; i < m_monte_carlo_paths; i++) {
         double z = MathRand() / 32767.0;
         z = MathSqrt(-2.0 * MathLog(z)) * MathCos(2.0 * M_PI * MathRand() / 32767.0);
         returns[i] = CalculateGARCHVolatility() * z;
      }
      double mean = ArrayMean(returns);
      double std_dev = ArrayStdDev(returns);
      if(std_dev == 0) return 0.0;
      return (mean - risk_free_rate / 252) / std_dev * MathSqrt(252);
   }

   // Simular cenário de estresse
   double SimulateStressScenario(double stress_factor = 3.0) {
      double volatility = CalculateGARCHVolatility();
      double stressed_volatility = volatility * stress_factor;
      Log(StringFormat("Stressed Volatility (%.1fx): %.4f%%", stress_factor, stressed_volatility * 100), "INFO");
      return stressed_volatility;
   }

   // Calcular VaR com volatilidade customizada
   double CalculateVaRWithVolatility(double custom_volatility, double confidence_level = 0.95) {
      double returns[];
      ArrayResize(returns, m_monte_carlo_paths);
      for(int i = 0; i < m_monte_carlo_paths; i++) {
         double z = MathRand() / 32767.0;
         z = MathSqrt(-2.0 * MathLog(z)) * MathCos(2.0 * M_PI * MathRand() / 32767.0);
         returns[i] = custom_volatility * z;
      }
      ArraySort(returns);
      int index = (int)MathFloor(m_monte_carlo_paths * (1 - confidence_level));
      return -returns[index];
   }

   // Verificar resiliência do portfólio
   bool IsPortfolioResilient(double max_allowed_var = 0.05) {
      double stressed_var = CalculateVaRWithVolatility(SimulateStressScenario());
      return stressed_var <= max_allowed_var;
   }

   // Salvar histórico de trades
   bool SaveTradeHistory(string filename = "trade_history.csv") {
      int handle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_COMMON);
      if(handle == INVALID_HANDLE) {
         Log("Failed to open file for saving history: " + filename, "ERROR");
         return false;
      }
      FileWrite(handle, "Time,Symbol,Profit,Risk,Reward");

      for(int i = 0; i < ArraySize(m_trades); i++) {
         string line = TimeToString(m_trades[i].time, TIME_DATE|TIME_MINUTES) + "," +
                       m_trades[i].symbol + "," +
                       DoubleToString(m_trades[i].profit, 2) + "," +
                       DoubleToString(m_trades[i].risk, 2) + "," +
                       DoubleToString(m_trades[i].reward, 2);
         FileWrite(handle, line);
      }

      FileClose(handle);
      Log("Trade history saved successfully: " + filename, "INFO");
      return true;
   }

   // Carregar histórico de trades
   bool LoadTradeHistory(string filename = "trade_history.csv") {
      int handle = FileOpen(filename, FILE_READ | FILE_CSV | FILE_COMMON);
      if(handle == INVALID_HANDLE) {
         Log("Trade history file not found: " + filename, "WARN");
         return false;
      }

      int count = 0;
      while(!FileIsEnding(handle)) {
         string row = FileReadString(handle);
         if(row == "" || StringFind(row, "Time,Symbol") != -1) continue;

         string values[];
         StringSplit(row, ',', values);
         if(ArraySize(values) >= 5) {
            TradeHistory trade;
            trade.time = StringToTime(values[0]);
            trade.symbol = values[1];
            trade.profit = StringToDouble(values[2]);
            trade.risk = StringToDouble(values[3]);
            trade.reward = StringToDouble(values[4]);
            ArrayPush(m_trades, trade);
            count++;
         }
      }

      FileClose(handle);
      Log(StringFormat("Loaded %d trades from history", count), "INFO");
      return count > 0;
   }

   // Calcular volatilidade GARCH
   double CalculateGARCHVolatility() {
      double prices[];
      if(!LoadDailyReturns(prices)) {
         Log("Failed to load returns for GARCH", "ERROR");
         return 0.0;
      }

      alglib::real_1d_array r;
      r.setcontent(ArraySize(prices), prices);

      double mu, alpha0, alpha1, beta1;
      alglib::garchreport report;
      alglib::garchfit(r, r.length(), 1, 1, mu, alpha0, alpha1, beta1, report);
      double h = alpha0 + alpha1 * r[r.length()-1]*r[r.length()-1] + beta1 * 0.01;
      double volatility = MathSqrt(h);

      Log(StringFormat("GARCH Volatility Calculated: %.4f%%", volatility * 100), "INFO");
      return volatility;
   }

   // Validar estado quântico
   bool ValidateQuantumState() {
      double coherence = 0.0;
      if(m_statistics != NULL)
         coherence = m_statistics.GetQuantumCoherence();

      if(coherence < 0.0 || coherence > 1.0) {
         Log("Quantum coherence validation failed", "ERROR");
         return false;
      }

      double volatility = 0.0;
      if(m_volatility != NULL)
         volatility = m_volatility.GetVolatility();

      if(volatility <= 0) {
         Log("Quantum state validation failed: Zero volatility", "ERROR");
         return false;
      }

      return true;
   }

   // Setup dos grupos de exposição
   void SetupExposureGroups() {
      ArrayResize(m_groups, 3);
      m_groups[0].name = "Forex";
      m_groups[0].max_risk_percent = 40.0;
      m_groups[0].current_exposure = 0.0;

      m_groups[1].name = "Commodities";
      m_groups[1].max_risk_percent = 30.0;
      m_groups[1].current_exposure = 0.0;

      m_groups[2].name = "Crypto";
      m_groups[2].max_risk_percent = 20.0;
      m_groups[2].current_exposure = 0.0;
   }

   // Identificar grupo do símbolo
   string GetSymbolGroup(string symbol) {
      if(StringFind(symbol, "XAUUSD") != -1 || StringFind(symbol, "XAGUSD") != -1)
         return "Commodities";
      if(StringFind(symbol, "BTCUSD") != -1 || StringFind(symbol, "ETHUSD") != -1)
         return "Crypto";
      return "Forex";
   }

   // Verificar limite de exposição
   bool CheckExposureLimit(string symbol, double risk_amount) {
      string group_name = GetSymbolGroup(symbol);
      for(int i = 0; i < ArraySize(m_groups); i++) {
         if(m_groups[i].name == group_name) {
            if(m_groups[i].current_exposure + risk_amount > m_groups[i].max_risk_percent) {
               Log("Exposure limit exceeded for group: " + group_name, "WARN");
               return false;
            }
            m_groups[i].current_exposure += risk_amount;
            return true;
         }
      }
      return false;
   }

   // Calcular volatilidade usando GARCH
   double CalculateVolatility(int period = 20) {
      double prices[];
      int copied = CopyClose(m_symbol, m_timeframe, 0, period, prices);
      if(copied < 2) return 0.0;

      double returns[];
      ArrayResize(returns, period - 1);
      for(int i = 0; i < period - 1; i++) {
         returns[i] = (prices[i] - prices[i + 1]) / prices[i + 1];
      }

      double std_dev;
      MathSd(returns, std_dev);
      return std_dev * MathSqrt(252);
   }

   // Calcular entropia do mercado
   double CalculateEntropy(int period = 50) {
      double prices[];
      int copied = CopyClose(m_symbol, m_timeframe, 0, period, prices);
      if(copied < 2) return 0.0;

      double min_price = prices[0], max_price = prices[0];
      for(int i = 1; i < copied; i++) {
         min_price = MathMin(min_price, prices[i]);
         max_price = MathMax(max_price, prices[i]);
      }

      double entropy = 0.0;
      int bins = 10;
      int counts[];
      ArrayResize(counts, bins);
      ArrayInitialize(counts, 0);
      double bin_size = (max_price - min_price) / bins;

      for(int i = 0; i < copied; i++) {
         int bin = (int)((prices[i] - min_price) / bin_size);
         if(bin >= bins) bin = bins - 1;
         counts[bin]++;
      }

      for(int i = 0; i < bins; i++) {
         if(counts[i] > 0) {
            double p = (double)counts[i] / copied;
            entropy -= p * MathLog(p);
         }
      }

      return entropy;
   }

   // Registrar evento de trade
   void RegisterTrade(double profit, double risk, double reward) {
      TradeHistory trade;
      trade.time = TimeCurrent();
      trade.profit = profit;
      trade.risk = risk;
      trade.reward = reward;
      ArrayPush(m_trades, trade);
   }

protected:
   // Carregar retornos diários
   bool LoadDailyReturns(double &returns[]) {
      double equity[];
      if(!HistorySelect(TimeCurrent() - 365 * 86400, TimeCurrent(), equity)) return false;
      ArraySetAsSeries(equity, true);
      int size = ArraySize(equity);
      if(size < 2) return false;

      ArrayResize(returns, size - 1);
      for(int i = 0; i < size - 1; i++)
         returns[i] = (equity[i] - equity[i + 1]) / MathMax(equity[i + 1], 1e-7);

      return true;
   }

   // Logging centralizado
   void Log(string message, string severity = "INFO") {
      if(m_logger != NULL) {
         string full_message = StringFormat("[%s] %s", "RiskManager", message);
         if(severity == "ERROR") m_logger.Error(full_message);
         else if(severity == "WARN") m_logger.Warn(full_message);
         else m_logger.Info(full_message);
      } else {
         Print(message);
      }
   }

private:
   // Função auxiliar para média
   double ArrayMean(const double& arr[]) {
      int n = ArraySize(arr);
      if(n == 0) return 0.0;
      double sum = 0.0;
      for(int i = 0; i < n; i++) sum += arr[i];
      return sum / n;
   }

   // Função auxiliar para desvio padrão
   void MathSd(const double& arr[], double& result) {
      int n = ArraySize(arr);
      if(n == 0) return;
      double mean = ArrayMean(arr);
      double variance = 0.0;
      for(int i = 0; i < n; i++) {
         variance += (arr[i] - mean) * (arr[i] - mean);
      }
      result = MathSqrt(variance / n);
   }
};