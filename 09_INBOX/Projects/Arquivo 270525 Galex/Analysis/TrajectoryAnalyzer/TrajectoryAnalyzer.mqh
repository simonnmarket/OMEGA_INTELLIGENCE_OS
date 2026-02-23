//+------------------------------------------------------------------+
//|                                            TrajectoryAnalyzer.mqh |
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

// Classe principal de análise de trajetória
class CTrajectoryAnalyzer
{
private:
   double m_gravitational_force;
   double m_poc_levels[];
   double m_support_levels[];
   double m_resistance_levels[];
   int m_poc_count;
   
public:
   // Construtor
   CTrajectoryAnalyzer()
   {
      m_gravitational_force = 0.0;
      m_poc_count = 0;
      ArrayResize(m_poc_levels, 10);
      ArrayResize(m_support_levels, 10);
      ArrayResize(m_resistance_levels, 10);
   }
   
   // Inicialização
   bool Init()
   {
      m_gravitational_force = 0.0;
      m_poc_count = 0;
      ArrayInitialize(m_poc_levels, 0.0);
      ArrayInitialize(m_support_levels, 0.0);
      ArrayInitialize(m_resistance_levels, 0.0);
      
      return true;
   }
   
   // Atualizar análise
   void Update(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      // Calcular forças gravitacionais
      CalculateGravitationalForce(price, volume, period);
      
      // Calcular POCs
      CalculatePOCs(price, volume, period);
      
      // Calcular níveis de suporte e resistência
      CalculateSupportResistance(price, period);
   }
   
   // Obter força gravitacional
   double GetGravitationalForce() const { return m_gravitational_force; }
   
   // Obter POCs
   bool GetPOCs(double &pocs[], int &count)
   {
      count = m_poc_count;
      ArrayResize(pocs, count);
      ArrayCopy(pocs, m_poc_levels, 0, 0, count);
      return count > 0;
   }
   
   // Obter níveis de suporte
   bool GetSupportLevels(double &levels[], int &count)
   {
      count = 0;
      for(int i = 0; i < ArraySize(m_support_levels); i++)
      {
         if(m_support_levels[i] > 0.0)
            count++;
      }
      
      ArrayResize(levels, count);
      int index = 0;
      for(int i = 0; i < ArraySize(m_support_levels); i++)
      {
         if(m_support_levels[i] > 0.0)
         {
            levels[index] = m_support_levels[i];
            index++;
         }
      }
      
      return count > 0;
   }
   
   // Obter níveis de resistência
   bool GetResistanceLevels(double &levels[], int &count)
   {
      count = 0;
      for(int i = 0; i < ArraySize(m_resistance_levels); i++)
      {
         if(m_resistance_levels[i] > 0.0)
            count++;
      }
      
      ArrayResize(levels, count);
      int index = 0;
      for(int i = 0; i < ArraySize(m_resistance_levels); i++)
      {
         if(m_resistance_levels[i] > 0.0)
         {
            levels[index] = m_resistance_levels[i];
            index++;
         }
      }
      
      return count > 0;
   }
   
private:
   // Calcular força gravitacional
   void CalculateGravitationalForce(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      double price_sum = 0.0;
      double volume_sum = 0.0;
      
      for(int i = 0; i < period; i++)
      {
         price_sum += price[i] * volume[i];
         volume_sum += volume[i];
      }
      
      if(volume_sum > 0.0)
      {
         double vwap = price_sum / volume_sum;
         m_gravitational_force = (price[0] - vwap) / vwap;
      }
   }
   
   // Calcular POCs (Points of Control)
   void CalculatePOCs(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      m_poc_count = 0;
      double max_volume = 0.0;
      
      // Encontrar o volume máximo
      for(int i = 0; i < period; i++)
      {
         if(volume[i] > max_volume)
            max_volume = volume[i];
      }
      
      // Encontrar POCs (níveis com volume significativo)
      for(int i = 0; i < period && m_poc_count < ArraySize(m_poc_levels); i++)
      {
         if(volume[i] >= max_volume * 0.8) // 80% do volume máximo
         {
            m_poc_levels[m_poc_count] = price[i];
            m_poc_count++;
         }
      }
   }
   
   // Calcular níveis de suporte e resistência
   void CalculateSupportResistance(const double &price[], int period)
   {
      if(ArraySize(price) < period) return;
      
      // Encontrar máximos e mínimos locais
      for(int i = 2; i < period-2; i++)
      {
         // Resistência
         if(price[i] > price[i-1] && price[i] > price[i-2] &&
            price[i] > price[i+1] && price[i] > price[i+2])
         {
            AddResistanceLevel(price[i]);
         }
         
         // Suporte
         if(price[i] < price[i-1] && price[i] < price[i-2] &&
            price[i] < price[i+1] && price[i] < price[i+2])
         {
            AddSupportLevel(price[i]);
         }
      }
   }
   
   // Adicionar nível de suporte
   void AddSupportLevel(double level)
   {
      for(int i = 0; i < ArraySize(m_support_levels); i++)
      {
         if(m_support_levels[i] == 0.0)
         {
            m_support_levels[i] = level;
            break;
         }
      }
   }
   
   // Adicionar nível de resistência
   void AddResistanceLevel(double level)
   {
      for(int i = 0; i < ArraySize(m_resistance_levels); i++)
      {
         if(m_resistance_levels[i] == 0.0)
         {
            m_resistance_levels[i] = level;
            break;
         }
      }
   }
}; 