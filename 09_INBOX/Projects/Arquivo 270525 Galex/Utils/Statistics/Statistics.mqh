//+------------------------------------------------------------------+
//|                                                  Statistics.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Arrays\ArrayDouble.mqh>
#include <Math\Stat\Math.mqh>

// Classe principal de estatísticas
class CStatistics
{
public:
   // Calcular média
   static double Mean(const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double sum = 0.0;
      for(int i = 0; i < count; i++)
      {
         sum += data[i];
      }
      
      return sum / count;
   }
   
   // Calcular desvio padrão
   static double StdDev(const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double mean = Mean(data, count);
      double sum_squares = 0.0;
      
      for(int i = 0; i < count; i++)
      {
         double deviation = data[i] - mean;
         sum_squares += deviation * deviation;
      }
      
      return MathSqrt(sum_squares / count);
   }
   
   // Calcular correlação
   static double Correlation(const double &data1[], const double &data2[], int count = 0)
   {
      if(ArraySize(data1) == 0 || ArraySize(data2) == 0) return 0.0;
      
      if(count <= 0 || count > MathMin(ArraySize(data1), ArraySize(data2)))
         count = MathMin(ArraySize(data1), ArraySize(data2));
         
      double mean1 = Mean(data1, count);
      double mean2 = Mean(data2, count);
      double sum_products = 0.0;
      double sum_squares1 = 0.0;
      double sum_squares2 = 0.0;
      
      for(int i = 0; i < count; i++)
      {
         double deviation1 = data1[i] - mean1;
         double deviation2 = data2[i] - mean2;
         sum_products += deviation1 * deviation2;
         sum_squares1 += deviation1 * deviation1;
         sum_squares2 += deviation2 * deviation2;
      }
      
      if(sum_squares1 == 0.0 || sum_squares2 == 0.0)
         return 0.0;
         
      return sum_products / MathSqrt(sum_squares1 * sum_squares2);
   }
   
   // Calcular Z-Score
   static double ZScore(double value, const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double mean = Mean(data, count);
      double std_dev = StdDev(data, count);
      
      if(std_dev == 0.0)
         return 0.0;
         
      return (value - mean) / std_dev;
   }
   
   // Calcular percentil
   static double Percentile(const double &data[], double percentile, int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double sorted[];
      ArrayResize(sorted, count);
      ArrayCopy(sorted, data, 0, 0, count);
      ArraySort(sorted);
      
      int index = (int)MathRound(percentile * count / 100.0);
      if(index >= count)
         index = count - 1;
         
      return sorted[index];
   }
   
   // Calcular mediana
   static double Median(const double &data[], int count = 0)
   {
      return Percentile(data, 50.0, count);
   }
   
   // Calcular moda
   static double Mode(const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double sorted[];
      ArrayResize(sorted, count);
      ArrayCopy(sorted, data, 0, 0, count);
      ArraySort(sorted);
      
      double mode = sorted[0];
      int max_count = 1;
      int current_count = 1;
      
      for(int i = 1; i < count; i++)
      {
         if(sorted[i] == sorted[i-1])
         {
            current_count++;
            if(current_count > max_count)
            {
               max_count = current_count;
               mode = sorted[i];
            }
         }
         else
         {
            current_count = 1;
         }
      }
      
      return mode;
   }
   
   // Calcular skewness
   static double Skewness(const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double mean = Mean(data, count);
      double std_dev = StdDev(data, count);
      
      if(std_dev == 0.0)
         return 0.0;
         
      double sum_cubes = 0.0;
      for(int i = 0; i < count; i++)
      {
         double deviation = (data[i] - mean) / std_dev;
         sum_cubes += deviation * deviation * deviation;
      }
      
      return sum_cubes / count;
   }
   
   // Calcular kurtosis
   static double Kurtosis(const double &data[], int count = 0)
   {
      if(ArraySize(data) == 0) return 0.0;
      
      if(count <= 0 || count > ArraySize(data))
         count = ArraySize(data);
         
      double mean = Mean(data, count);
      double std_dev = StdDev(data, count);
      
      if(std_dev == 0.0)
         return 0.0;
         
      double sum_quads = 0.0;
      for(int i = 0; i < count; i++)
      {
         double deviation = (data[i] - mean) / std_dev;
         sum_quads += deviation * deviation * deviation * deviation;
      }
      
      return sum_quads / count - 3.0;
   }
}; 