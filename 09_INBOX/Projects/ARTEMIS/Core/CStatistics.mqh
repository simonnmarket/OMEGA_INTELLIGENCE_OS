#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Classe para cálculos estatísticos                                 |
//+------------------------------------------------------------------+
class CStatistics : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   bool m_is_initialized;                // Se está inicializado
   
public:
   // Construtor
   CStatistics(CLogger* logger)
   {
      m_logger = logger;
      m_is_initialized = false;
      
      if(m_logger != NULL)
      {
         m_logger.Info("Módulo de estatísticas inicializado");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CStatistics()
   {
      if(m_logger != NULL)
         m_logger.Info("Módulo de estatísticas finalizado");
   }
   
   // Calcula média
   double CalculateMean(const double& data[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double sum = 0.0;
      int count = ArraySize(data);
      
      for(int i = 0; i < count; i++)
         sum += data[i];
         
      return count > 0 ? sum / count : 0.0;
   }
   
   // Calcula desvio padrão
   double CalculateStdDev(const double& data[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double mean = CalculateMean(data);
      double sum = 0.0;
      int count = ArraySize(data);
      
      for(int i = 0; i < count; i++)
         sum += MathPow(data[i] - mean, 2);
         
      return count > 1 ? MathSqrt(sum / (count - 1)) : 0.0;
   }
   
   // Calcula skewness
   double CalculateSkewness(const double& data[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double mean = CalculateMean(data);
      double std = CalculateStdDev(data);
      double sum = 0.0;
      int count = ArraySize(data);
      
      if(std == 0.0 || count < 3)
         return 0.0;
         
      for(int i = 0; i < count; i++)
         sum += MathPow((data[i] - mean) / std, 3);
         
      return sum * count / ((count - 1) * (count - 2));
   }
   
   // Calcula kurtosis
   double CalculateKurtosis(const double& data[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double mean = CalculateMean(data);
      double std = CalculateStdDev(data);
      double sum = 0.0;
      int count = ArraySize(data);
      
      if(std == 0.0 || count < 4)
         return 0.0;
         
      for(int i = 0; i < count; i++)
         sum += MathPow((data[i] - mean) / std, 4);
         
      return sum * count * (count + 1) / ((count - 1) * (count - 2) * (count - 3)) - 3 * (count - 1) * (count - 1) / ((count - 2) * (count - 3));
   }
   
   // Calcula correlação
   double CalculateCorrelation(const double& data1[], const double& data2[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      int count = ArraySize(data1);
      if(count != ArraySize(data2) || count < 2)
         return 0.0;
         
      double mean1 = CalculateMean(data1);
      double mean2 = CalculateMean(data2);
      double sum = 0.0;
      double sum1 = 0.0;
      double sum2 = 0.0;
      
      for(int i = 0; i < count; i++)
      {
         double diff1 = data1[i] - mean1;
         double diff2 = data2[i] - mean2;
         sum += diff1 * diff2;
         sum1 += diff1 * diff1;
         sum2 += diff2 * diff2;
      }
      
      if(sum1 == 0.0 || sum2 == 0.0)
         return 0.0;
         
      return sum / MathSqrt(sum1 * sum2);
   }
   
   // Calcula retornos
   bool CalculateReturns(const double& prices[], double& returns[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      int count = ArraySize(prices);
      if(count < 2)
         return false;
         
      ArrayResize(returns, count - 1);
      
      for(int i = 1; i < count; i++)
         returns[i - 1] = (prices[i] - prices[i - 1]) / prices[i - 1];
         
      return true;
   }
   
   // Calcula drawdown
   double CalculateDrawdown(const double& equity[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      int count = ArraySize(equity);
      if(count < 2)
         return 0.0;
         
      double max_equity = equity[0];
      double max_drawdown = 0.0;
      
      for(int i = 1; i < count; i++)
      {
         if(equity[i] > max_equity)
            max_equity = equity[i];
         else
         {
            double drawdown = (max_equity - equity[i]) / max_equity;
            if(drawdown > max_drawdown)
               max_drawdown = drawdown;
         }
      }
      
      return max_drawdown;
   }
   
   // Calcula Sharpe Ratio
   double CalculateSharpeRatio(const double& returns[], double risk_free_rate = 0.0)
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double mean = CalculateMean(returns);
      double std = CalculateStdDev(returns);
      
      if(std == 0.0)
         return 0.0;
         
      return (mean - risk_free_rate) / std;
   }
   
   // Calcula Sortino Ratio
   double CalculateSortinoRatio(const double& returns[], double risk_free_rate = 0.0)
   {
      if(!m_is_initialized || m_logger == NULL)
         return 0.0;
         
      double mean = CalculateMean(returns);
      double sum = 0.0;
      int count = ArraySize(returns);
      int negative_count = 0;
      
      for(int i = 0; i < count; i++)
      {
         if(returns[i] < 0)
         {
            sum += returns[i] * returns[i];
            negative_count++;
         }
      }
      
      if(negative_count == 0)
         return 0.0;
         
      double downside_deviation = MathSqrt(sum / negative_count);
      
      if(downside_deviation == 0.0)
         return 0.0;
         
      return (mean - risk_free_rate) / downside_deviation;
   }
}; 