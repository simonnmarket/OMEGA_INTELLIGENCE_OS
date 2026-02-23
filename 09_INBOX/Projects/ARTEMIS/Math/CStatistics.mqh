//+------------------------------------------------------------------+
//| CStatistics.mqh - Institutional Statistical Analysis             |
//| Version 2.0 - Unified and Enhanced (2025)                       |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.quantumtrading.foundation" 
#property version   "2.0"
#property strict

#include "..\\Utils\\CLogger.mqh"
#include "..\\Math\\Stat\\Math.mqh"
#include "..\Trade\HistoryOrderInfo.mqh"
#include "..\\Math\\Alglib\\alglib.mqh"

// Estrutura para métricas estatísticas
struct StatMetrics {
   double mean;
   double std_dev;
   double variance;
   double skewness;
   double kurtosis;
   datetime last_update;
};

class CStatistics : public CObject {
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_lookback_period;
   double m_volatility;
   double m_drawdown;
   bool m_is_initialized;
   CLogger* m_logger;
   int m_min_data_points;
   int m_monte_carlo_paths;
   StatMetrics m_metrics;

public:
   CStatistics(CLogger* logger = NULL) {
      m_symbol = "";
      m_timeframe = PERIOD_CURRENT;
      m_lookback_period = 100;
      m_volatility = 0;
      m_drawdown = 0;
      m_is_initialized = false;
      m_logger = logger;
      m_min_data_points = 30;
      m_monte_carlo_paths = 1000;
      m_metrics.mean = 0;
      m_metrics.std_dev = 0;
      m_metrics.variance = 0;
      m_metrics.skewness = 0;
      m_metrics.kurtosis = 0;
      m_metrics.last_update = 0;
   }

   ~CStatistics() {
      m_logger = NULL;
   }

   bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int lookback_period = 100) {
      if(m_is_initialized) {
         if(m_logger != NULL) m_logger.Log(LOG_LEVEL_INFO, "CStatistics já inicializado");
         return false;
      }
      
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_lookback_period = lookback_period;
      m_is_initialized = true;
      
      if(m_logger != NULL) m_logger.Log(LOG_LEVEL_INFO, "CStatistics inicializado");
      return true;
   }

   bool IsInitialized() const {
      return m_is_initialized;
   }

   double CalculateGARCHVolatility() {
      if(!m_is_initialized) return 0;
      
      double returns[];
      datetime end_time = TimeCurrent();
      datetime start_time = end_time - m_lookback_period * PeriodSeconds(m_timeframe);
      
      if(!HistorySelect(start_time, end_time)) {
         if(m_logger != NULL) m_logger.Log(LOG_LEVEL_ERROR, "Falha ao selecionar histórico");
         return 0;
      }
      
      int total = HistoryDealsTotal();
      if(total < m_min_data_points) {
         if(m_logger != NULL) m_logger.Log(LOG_LEVEL_WARNING, "Dados insuficientes para GARCH");
         return 0;
      }
      
      ArrayResize(returns, total);
      for(int i = 0; i < total; i++) {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0) {
            returns[i] = HistoryDealGetDouble(ticket, DEAL_PROFIT);
         }
      }
      
      double variance = 0;
      CAlglib::GARCHFit(returns, variance);
      return MathSqrt(variance);
   }

   double CalculateSortinoRatio(const double &returns[]) {
      if(!m_is_initialized || ArraySize(returns) < 2) return 0;
      
      double mean_return = 0;
      double downside_deviation = 0;
      int downside_count = 0;
      
      for(int i = 0; i < ArraySize(returns); i++) {
         mean_return += returns[i];
         if(returns[i] < 0) {
            downside_deviation += returns[i] * returns[i];
            downside_count++;
         }
      }
      
      mean_return /= ArraySize(returns);
      if(downside_count > 0) {
         downside_deviation = MathSqrt(downside_deviation / downside_count);
      }
      
      if(downside_deviation == 0) return 0;
      return mean_return / downside_deviation;
   }

   double CalculateCalmarRatio(const double &returns[], const double &drawdown) {
      if(!m_is_initialized || ArraySize(returns) < 2 || drawdown == 0) return 0;
      
      double mean_return = 0;
      for(int i = 0; i < ArraySize(returns); i++) {
         mean_return += returns[i];
      }
      mean_return /= ArraySize(returns);
      
      return mean_return / drawdown;
   }

   // --- Métodos estatísticos básicos ---
   static double Mean(const double &data[]) {
      if(ArraySize(data) < 2) return 0.0;
      double sum = 0.0;
      for(int i = 0; i < ArraySize(data); i++) {
         sum += data[i];
      }
      return sum / ArraySize(data);
   }

   static double StandardDeviation(const double &data[]) {
      if(ArraySize(data) < 2) return 0.0;
      double mean = Mean(data);
      double sum = 0.0;

      for(int i = 0; i < ArraySize(data); i++) {
         sum += MathPow(data[i] - mean, 2);
      }

      return MathSqrt(sum / (ArraySize(data) - 1));
   }

   static double Variance(const double &data[]) {
      if(ArraySize(data) < 2) return 0.0;
      double mean = Mean(data);
      double sum = 0.0;

      for(int i = 0; i < ArraySize(data); i++) {
         sum += MathPow(data[i] - mean, 2);
      }

      return sum / (ArraySize(data) - 1);
   }

   static double Covariance(const double &data1[], const double &data2[]) {
      if(ArraySize(data1) != ArraySize(data2)) {
         Print("Erro: Tamanhos incompatíveis em covariância");
         return 0.0;
      }

      if(ArraySize(data1) < 2) return 0.0;

      double mean1 = Mean(data1);
      double mean2 = Mean(data2);
      double sum = 0.0;

      for(int i = 0; i < ArraySize(data1); i++) {
         sum += (data1[i] - mean1) * (data2[i] - mean2);
      }

      return sum / (ArraySize(data1) - 1);
   }

   static double Correlation(const double &data1[], const double &data2[]) {
      double cov = Covariance(data1, data2);
      double std1 = StandardDeviation(data1);
      double std2 = StandardDeviation(data2);

      if(std1 == 0 || std2 == 0) return 0.0;
      return cov / (std1 * std2);
   }

   static double Skewness(const double &data[]) {
      if(ArraySize(data) < 2) return 0.0;
      double mean = Mean(data);
      double std = StandardDeviation(data);
      double sum = 0.0;

      for(int i = 0; i < ArraySize(data); i++) {
         sum += MathPow((data[i] - mean) / std, 3);
      }

      return sum / ArraySize(data);
   }

   static double Kurtosis(const double &data[]) {
      if(ArraySize(data) < 2) return 0.0;
      double mean = Mean(data);
      double std = StandardDeviation(data);
      double sum = 0.0;

      for(int i = 0; i < ArraySize(data); i++) {
         sum += MathPow((data[i] - mean) / std, 4);
      }

      return sum / ArraySize(data) - 3;
   }

   static double Percentile(const double &data[], double percentile) {
      if(percentile < 0 || percentile > 1) return 0.0;
      if(ArraySize(data) == 0) return 0.0;

      double sorted[];
      ArrayCopy(sorted, data);
      ArraySort(sorted);

      int index = (int)MathRound(ArraySize(sorted) * percentile);
      return sorted[index];
   }

   static double Median(const double &data[]) {
      return Percentile(data, 0.5);
   }

   static double Quartile(const double &data[], int quartile) {
      if(quartile < 1 || quartile > 3) return 0.0;
      return Percentile(data, quartile * 0.25);
   }

   // --- Métricas de risco e performance ---
   double MaxDrawdown(const double &equity[]) {
      if(ArraySize(equity) < 2) return 0.0;

      double max_equity = equity[0];
      double max_drawdown = 0.0;

      for(int i = 1; i < ArraySize(equity); i++) {
         max_equity = MathMax(max_equity, equity[i]);
         double drawdown = (max_equity - equity[i]) / max_equity;
         max_drawdown = MathMax(max_drawdown, drawdown);
      }

      return max_drawdown;
   }

   double SharpeRatio(const double &returns[], double risk_free_rate = 0.02) {
      if(ArraySize(returns) < 2) return 0.0;

      double mean_return = Mean(returns);
      double std_dev = StandardDeviation(returns);
      if(std_dev == 0) return 0.0;

      return (mean_return - risk_free_rate / 252) / std_dev * MathSqrt(252);
   }

   double InformationRatio(const double &returns[], const double &benchmark[]) {
      if(ArraySize(returns) != ArraySize(benchmark) || ArraySize(returns) < 2) return 0.0;
      double excess_returns[];
      ArrayResize(excess_returns, ArraySize(returns));
      for(int i = 0; i < ArraySize(returns); i++) {
         excess_returns[i] = returns[i] - benchmark[i];
      }
      double mean = Mean(excess_returns);
      double std_dev = StandardDeviation(excess_returns);
      return std_dev > 0 ? mean / std_dev * MathSqrt(252) : 0.0;
   }

   double ValueAtRisk(const double &returns[], double confidence_level = 0.95, double horizon = 1) {
      double sorted[];
      ArrayCopy(sorted, returns);
      ArraySort(sorted);
      int index = (int)MathFloor(ArraySize(sorted) * (1 - confidence_level));
      return -sorted[index] * horizon;
   }

   double ConditionalValueAtRisk(const double &returns[], double confidence_level = 0.95, double horizon = 1) {
      double sorted[];
      ArrayCopy(sorted, returns);
      ArraySort(sorted);
      int index = (int)MathFloor(ArraySize(sorted) * (1 - confidence_level));
      double cvar_sum = 0.0;
      for(int i = 0; i < index; i++) {
         cvar_sum += sorted[i];
      }
      return -cvar_sum / index * horizon;
   }

   // --- Outros métodos úteis ---
   double CoefficientOfVariation(const double &data[]) {
      double mean = Mean(data);
      double std_dev = StandardDeviation(data);
      if(mean == 0) return 0.0;
      return std_dev / mean;
   }

   bool LinearRegression(const double &x[], const double &y[], double &slope, double &intercept) {
      if(ArraySize(x) != ArraySize(y) || ArraySize(x) < 2) return false;

      double x_mean = Mean(x);
      double y_mean = Mean(y);
      double numerator = 0.0, denominator = 0.0;

      for(int i = 0; i < ArraySize(x); i++) {
         numerator += (x[i] - x_mean) * (y[i] - y_mean);
         denominator += MathPow(x[i] - x_mean, 2);
      }

      if(denominator == 0) return false;

      slope = numerator / denominator;
      intercept = y_mean - slope * x_mean;
      return true;
   }

   double RSquared(const double &x[], const double &y[]) {
      double y_mean = Mean(y);
      double total_variance = 0.0, explained_variance = 0.0;
      double predicted[];
      ArrayResize(predicted, ArraySize(x));

      double slope, intercept;
      if(!LinearRegression(x, y, slope, intercept)) return 0.0;

      for(int i = 0; i < ArraySize(x); i++) {
         predicted[i] = slope * x[i] + intercept;
         total_variance += MathPow(y[i] - y_mean, 2);
         explained_variance += MathAbs(predicted[i] - y[i]);
      }

      return 1 - (explained_variance / total_variance);
   }

   double CalculateDailyReturn() {
      double equity[];
      HistorySelect(TimeCurrent() - 86400, TimeCurrent(), equity);
      if(ArraySize(equity) < 2) return 0.0;

      return (equity[0] - equity[1]) / equity[1];
   }

   double CalculateHistoricalVolatility(int period = 20) {
      double prices[];
      int copied = CopyClose(Symbol(), PERIOD_M1, 0, period, prices);
      if(copied < 2) return 0.0;

      double returns[];
      ArrayResize(returns, period - 1);
      for(int i = 0; i < period - 1; i++) {
         returns[i] = (prices[i] - prices[i + 1]) / prices[i + 1];
      }

      return StandardDeviation(returns);
   }

   double MarketBeta(const double &asset_returns[], const double &market_returns[]) {
      if(ArraySize(asset_returns) != ArraySize(market_returns) || ArraySize(asset_returns) < 2) return 0.0;

      double covariance = Covariance(asset_returns, market_returns);
      double market_variance = Variance(market_returns);
      if(market_variance == 0) return 0.0;

      return covariance / market_variance;
   }

   double AdjustedMarketBeta(const double &asset_returns[], const double &market_returns[]) {
      if(ArraySize(asset_returns) != ArraySize(market_returns) || ArraySize(asset_returns) < 2) return 0.0;
      double asset_vol = StandardDeviation(asset_returns);
      double market_vol = StandardDeviation(market_returns);
      double beta = MarketBeta(asset_returns, market_returns);
      return market_vol > 0 ? (beta * asset_vol) / market_vol : 0.0;
   }

protected:
   // Logging centralizado
   void Log(string message, string severity = "INFO") {
      if(m_logger != NULL) {
         string full_message = StringFormat("[%s] %s", "Statistics", message);
         if(severity == "ERROR")
            m_logger.Error(full_message);
         else if(severity == "WARN")
            m_logger.Warn(full_message);
         else
            m_logger.Info(full_message);
      } else {
         Print(message);
      }
   }

private:
   // Validar dados
   bool ValidateData(const double &data[], int min_size = 2) {
      if(ArraySize(data) < min_size) {
         Log("Dados insuficientes para análise estatística", "ERROR");
         return false;
      }
      return true;
   }
};