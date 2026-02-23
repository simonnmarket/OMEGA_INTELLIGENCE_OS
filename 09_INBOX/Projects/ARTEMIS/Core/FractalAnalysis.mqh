//+------------------------------------------------------------------+
//| CFractalAnalysis.mqh - Advanced Fractal Market Analysis          |
//| Version 4.0 - Corrected and Complete                             |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Math\Alglib\alglib.mqh>

class CFractalAnalysis : public CObject
{
private:
   string            m_symbol;
   ENUM_TIMEFRAMES   m_timeframes[6]; // Fixed list of timeframes
   int               m_period;        // Period for indicators

   // Optimized data structure
   struct TimeframeData {
      double prices[];
      long   volumes[];   // Long type, compatible with CopyTickVolume
      double indicators[];
      int    rsi_handle;
      int    ma1_handle;
      int    ma2_handle;
   };

   TimeframeData     m_data[6];
   double            m_hurst_exponent;
   double            m_fractal_dimension;
   double            m_correlation_dimension;

   // Helper function for safe timeframe search
   int FindTimeframeIndex(ENUM_TIMEFRAMES tf)
   {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
         if(m_timeframes[i] == tf) return i;
      return -1;
   }

public:
   // Constructor with safe initialization
   CFractalAnalysis(string symbol, int period = 14) :
      m_symbol(symbol), m_period(period)
   {
      // Timeframe configuration
      m_timeframes[0] = PERIOD_D1;
      m_timeframes[1] = PERIOD_H4;
      m_timeframes[2] = PERIOD_H1;
      m_timeframes[3] = PERIOD_M15;
      m_timeframes[4] = PERIOD_M5;
      m_timeframes[5] = PERIOD_M1;

      // Data initialization
      for(int i = 0; i < ArraySize(m_timeframes); i++)
      {
         ArrayResize(m_data[i].prices, 1000);
         ArrayResize(m_data[i].volumes, 1000);
         ArrayResize(m_data[i].indicators, 1000);

         // Creation of indicator handles
         m_data[i].rsi_handle = iRSI(m_symbol, m_timeframes[i], m_period, PRICE_CLOSE);
         m_data[i].ma1_handle = iMA(m_symbol, m_timeframes[i], 20, 0, MODE_SMA, PRICE_CLOSE);
         m_data[i].ma2_handle = iMA(m_symbol, m_timeframes[i], 50, 0, MODE_SMA, PRICE_CLOSE);
      }

      // Initialization of metrics
      m_hurst_exponent = 0.5;
      m_fractal_dimension = 1.0;
      m_correlation_dimension = 1.0;
   }

   // Destructor for safe cleanup
   ~CFractalAnalysis()
   {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
      {
         IndicatorRelease(m_data[i].rsi_handle);
         IndicatorRelease(m_data[i].ma1_handle);
         IndicatorRelease(m_data[i].ma2_handle);
      }
   }

   // Main data update method
   void UpdateData()
   {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
      {
         // Update price data
         CopyClose(m_symbol, m_timeframes[i], 0, 1000, m_data[i].prices);

         // Update volume
         CopyTickVolume(m_symbol, m_timeframes[i], 0, 1000, m_data[i].volumes);

         // Update indicators
         CopyBuffer(m_data[i].rsi_handle, 0, 0, 1000, m_data[i].indicators);

         // Calculate fractal metrics
         if(ArraySize(m_data[i].prices) > 100)
         {
            m_hurst_exponent = CalculateHurstExponent(m_data[i].prices);
            m_fractal_dimension = CalculateFractalDimension(m_data[i].prices);
            m_correlation_dimension = CalculateCorrelationDimension(m_data[i].prices);
         }
      }
   }

   // Robust Hurst exponent calculation
   double CalculateHurstExponent(const double &price_series[])
   {
      int n = ArraySize(price_series);
      if(n < 50) return 0.5;

      double sum = 0.0;
      double mean = 0.0;
      double max_dev = 0.0;
      double min_dev = 0.0;
      double cumulative_dev = 0.0;
      double std_dev = 0.0;

      // Mean calculation
      for(int i = 0; i < n; i++)
         mean += price_series[i];
      mean /= n;

      // Standard deviation and range calculation
      for(int i = 0; i < n; i++)
      {
         double dev = price_series[i] - mean;
         cumulative_dev += dev;
         std_dev += dev * dev;

         if(cumulative_dev > max_dev) max_dev = cumulative_dev;
         if(cumulative_dev < min_dev) min_dev = cumulative_dev;
      }

      std_dev = MathSqrt(std_dev / n);
      double range = max_dev - min_dev;

      return (std_dev != 0) ? MathLog(range / std_dev) / MathLog(n) : 0.5;
   }

   // Fractal dimension calculation
   double CalculateFractalDimension(const double &price_series[])
   {
      int n = ArraySize(price_series);
      if(n < 2) return 1.0;

      double sum = 0.0;
      for(int i = 1; i < n; i++)
         sum += MathLog(MathAbs(price_series[i] - price_series[i-1]));

      return 1.0 + (sum / (n * MathLog(1.0 / n)));
   }

   // Correlation dimension calculation
   double CalculateCorrelationDimension(const double &price_series[])
   {
      int n = ArraySize(price_series);
      if(n < 10) return 1.0;

      double sum = 0.0;
      for(int i = 0; i < n; i++)
         for(int j = i+1; j < n; j++)
            sum += MathAbs(price_series[i] - price_series[j]);

      return sum > 0 ? MathLog(n * (n - 1) / (2 * sum)) : 1.0;
   }

   // Timeframe correlation analysis
   double CalculateTimeframeCorrelation(ENUM_TIMEFRAMES tf1, ENUM_TIMEFRAMES tf2)
   {
      int idx1 = FindTimeframeIndex(tf1);
      int idx2 = FindTimeframeIndex(tf2);

      if(idx1 == -1 || idx2 == -1) return 0.0;

      double corr = 0.0;
      double sum1 = 0.0, sum2 = 0.0;
      double sum1Sq = 0.0, sum2Sq = 0.0, sumProd = 0.0;
      int count = MathMin(ArraySize(m_data[idx1].prices), ArraySize(m_data[idx2].prices));

      for(int i = 0; i < count; i++)
      {
         sum1 += m_data[idx1].prices[i];
         sum2 += m_data[idx2].prices[i];
         sum1Sq += m_data[idx1].prices[i] * m_data[idx1].prices[i];
         sum2Sq += m_data[idx2].prices[i] * m_data[idx2].prices[i];
         sumProd += m_data[idx1].prices[i] * m_data[idx2].prices[i];
      }

      double numerator = sumProd - (sum1 * sum2 / count);
      double denominator = MathSqrt((sum1Sq - sum1 * sum1 / count) * (sum2Sq - sum2 * sum2 / count));

      return denominator != 0 ? numerator / denominator : 0.0;
   }

   // Accessor methods
   double GetHurstExponent() const { return m_hurst_exponent; }
   double GetFractalDimension() const { return m_fractal_dimension; }
   double GetCorrelationDimension() const { return m_correlation_dimension; }

   // Additional analysis methods from Math version
   bool IsTrending() const { return m_hurst_exponent > 0.6; }
   bool IsMeanReverting() const { return m_hurst_exponent < 0.4; }
   bool IsRandomWalk() const { return m_hurst_exponent >= 0.4 && m_hurst_exponent <= 0.6; }

   bool IsFractalForming(int timeframe_index)
   {
      if(timeframe_index < 0 || timeframe_index >= ArraySize(m_timeframes))
         return false;
         
      double rsi_values[];
      double ma1_values[];
      double ma2_values[];
      
      ArraySetAsSeries(rsi_values, true);
      ArraySetAsSeries(ma1_values, true);
      ArraySetAsSeries(ma2_values, true);
      
      if(CopyBuffer(m_data[timeframe_index].rsi_handle, 0, 0, 1, rsi_values) <= 0 ||
         CopyBuffer(m_data[timeframe_index].ma1_handle, 0, 0, 1, ma1_values) <= 0 ||
         CopyBuffer(m_data[timeframe_index].ma2_handle, 0, 0, 1, ma2_values) <= 0)
      {
         Print("Error copying indicator buffers: ", GetLastError());
         return false;
      }
      
      return (rsi_values[0] > 70 && ma1_values[0] > ma2_values[0]) || 
             (rsi_values[0] < 30 && ma1_values[0] < ma2_values[0]);
   }
};