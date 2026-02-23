//+------------------------------------------------------------------+
//|                                                Statistics.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Classe principal de estatísticas
class CStatistics : public IDataAnalyzer
{
private:
   double m_mean;
   double m_standard_deviation;
   double m_variance;
   double m_skewness;
   double m_kurtosis;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CStatistics()
   {
      m_mean = 0.0;
      m_standard_deviation = 0.0;
      m_variance = 0.0;
      m_skewness = 0.0;
      m_kurtosis = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_mean = 0.0;
      m_standard_deviation = 0.0;
      m_variance = 0.0;
      m_skewness = 0.0;
      m_kurtosis = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_standard_deviation >= 0.0 && m_variance >= 0.0;
   }
   
   void Cleanup() override
   {
      m_mean = 0.0;
      m_standard_deviation = 0.0;
      m_variance = 0.0;
      m_skewness = 0.0;
      m_kurtosis = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "Statistics"; }
   
   // Implementação de IDataAnalyzer
   bool AnalyzeData(const MqlRates &rates[], const double &volume[]) override
   {
      if(!m_is_initialized || ArraySize(rates) == 0 || ArraySize(volume) == 0) return false;
      
      // Calcular média
      CalculateMean(rates);
      
      // Calcular variância
      CalculateVariance(rates);
      
      // Calcular desvio padrão
      CalculateStandardDeviation();
      
      // Calcular assimetria
      CalculateSkewness(rates);
      
      // Calcular curtose
      CalculateKurtosis(rates);
      
      return true;
   }
   
   bool GetAnalysisResults(double &mean, double &standard_deviation, double &variance, double &skewness, double &kurtosis) override
   {
      if(!m_is_initialized) return false;
      
      mean = m_mean;
      standard_deviation = m_standard_deviation;
      variance = m_variance;
      skewness = m_skewness;
      kurtosis = m_kurtosis;
      
      return true;
   }
   
   // Métodos específicos do Statistics
   double CalculateMean(const double &data[])
   {
      if(ArraySize(data) == 0) return 0.0;
      
      double sum = 0.0;
      for(int i = 0; i < ArraySize(data); i++)
         sum += data[i];
      
      return sum / ArraySize(data);
   }
   
   double CalculateVariance(const double &data[])
   {
      if(ArraySize(data) == 0) return 0.0;
      
      double mean = CalculateMean(data);
      double sum_squared_diff = 0.0;
      
      for(int i = 0; i < ArraySize(data); i++)
         sum_squared_diff += MathPow(data[i] - mean, 2);
      
      return sum_squared_diff / ArraySize(data);
   }
   
   double CalculateStandardDeviation(const double &data[])
   {
      return MathSqrt(CalculateVariance(data));
   }
   
   double CalculateSkewness(const double &data[])
   {
      if(ArraySize(data) == 0) return 0.0;
      
      double mean = CalculateMean(data);
      double std_dev = CalculateStandardDeviation(data);
      
      if(std_dev == 0.0) return 0.0;
      
      double sum_cubed_diff = 0.0;
      for(int i = 0; i < ArraySize(data); i++)
         sum_cubed_diff += MathPow(data[i] - mean, 3);
      
      return (sum_cubed_diff / ArraySize(data)) / MathPow(std_dev, 3);
   }
   
   double CalculateKurtosis(const double &data[])
   {
      if(ArraySize(data) == 0) return 0.0;
      
      double mean = CalculateMean(data);
      double std_dev = CalculateStandardDeviation(data);
      
      if(std_dev == 0.0) return 0.0;
      
      double sum_quartic_diff = 0.0;
      for(int i = 0; i < ArraySize(data); i++)
         sum_quartic_diff += MathPow(data[i] - mean, 4);
      
      return (sum_quartic_diff / ArraySize(data)) / MathPow(std_dev, 4) - 3.0;
   }
   
   // Getters
   double GetMean() const { return m_mean; }
   double GetStandardDeviation() const { return m_standard_deviation; }
   double GetVariance() const { return m_variance; }
   double GetSkewness() const { return m_skewness; }
   double GetKurtosis() const { return m_kurtosis; }
   
private:
   void CalculateMean(const MqlRates &rates[])
   {
      double sum = 0.0;
      for(int i = 0; i < ArraySize(rates); i++)
         sum += rates[i].close;
      
      m_mean = sum / ArraySize(rates);
   }
   
   void CalculateVariance(const MqlRates &rates[])
   {
      double sum_squared_diff = 0.0;
      
      for(int i = 0; i < ArraySize(rates); i++)
         sum_squared_diff += MathPow(rates[i].close - m_mean, 2);
      
      m_variance = sum_squared_diff / ArraySize(rates);
   }
   
   void CalculateStandardDeviation()
   {
      m_standard_deviation = MathSqrt(m_variance);
   }
   
   void CalculateSkewness(const MqlRates &rates[])
   {
      double sum_cubed_diff = 0.0;
      
      for(int i = 0; i < ArraySize(rates); i++)
         sum_cubed_diff += MathPow(rates[i].close - m_mean, 3);
      
      m_skewness = (sum_cubed_diff / ArraySize(rates)) / MathPow(m_standard_deviation, 3);
   }
   
   void CalculateKurtosis(const MqlRates &rates[])
   {
      double sum_quartic_diff = 0.0;
      
      for(int i = 0; i < ArraySize(rates); i++)
         sum_quartic_diff += MathPow(rates[i].close - m_mean, 4);
      
      m_kurtosis = (sum_quartic_diff / ArraySize(rates)) / MathPow(m_standard_deviation, 4) - 3.0;
   }
}; 