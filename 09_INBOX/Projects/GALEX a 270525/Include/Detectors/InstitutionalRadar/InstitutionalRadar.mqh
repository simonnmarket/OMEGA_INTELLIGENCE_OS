//+------------------------------------------------------------------+
//|                                            InstitutionalRadar.mqh |
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
#include "..\..\Utils\Statistics\Statistics.mqh"

// Classe principal de detecção institucional
class CInstitutionalRadar
{
private:
   double m_volume_pulse;
   double m_energy_flow;
   double m_cosmic_frequency;
   double m_neural_confidence;
   double m_volume_threshold;
   double m_price_threshold;
   int m_lookback_period;
   
public:
   // Construtor
   CInstitutionalRadar()
   {
      m_volume_pulse = 0.0;
      m_energy_flow = 0.0;
      m_cosmic_frequency = 0.0;
      m_neural_confidence = 0.0;
      m_volume_threshold = 2.0;
      m_price_threshold = 0.001;
      m_lookback_period = 20;
   }
   
   // Inicialização
   bool Init(double volume_threshold = 2.0, double price_threshold = 0.001, int lookback_period = 20)
   {
      m_volume_threshold = volume_threshold;
      m_price_threshold = price_threshold;
      m_lookback_period = lookback_period;
      
      return true;
   }
   
   // Atualizar detecção
   void Update(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      // Calcular pulso de volume
      ScanInstitutionalPulse(volume, period);
      
      // Mapear fluxo de energia
      MapEnergyFlow(price, volume, period);
      
      // Sintonizar frequência cósmica
      TuneCosmicFrequency(price, volume, period);
   }
   
   // Detectar atividade institucional
   bool DetectInstitutionalActivity()
   {
      return m_volume_pulse > m_volume_threshold &&
             MathAbs(m_energy_flow) > m_price_threshold &&
             m_neural_confidence > 70.0;
   }
   
   // Getters
   double GetVolumePulse() const { return m_volume_pulse; }
   double GetEnergyFlow() const { return m_energy_flow; }
   double GetCosmicFrequency() const { return m_cosmic_frequency; }
   double GetNeuralConfidence() const { return m_neural_confidence; }
   
private:
   // Escanear pulso institucional
   void ScanInstitutionalPulse(const double &volume[], int period)
   {
      if(ArraySize(volume) < period) return;
      
      double avg_volume = CStatistics::Mean(volume, period);
      double std_volume = CStatistics::StdDev(volume, period);
      
      if(std_volume > 0.0)
      {
         m_volume_pulse = (volume[0] - avg_volume) / std_volume;
      }
      else
      {
         m_volume_pulse = 0.0;
      }
   }
   
   // Mapear fluxo de energia
   void MapEnergyFlow(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      double price_correlation = CStatistics::Correlation(price, volume, period);
      double volume_trend = (volume[0] - volume[period-1]) / volume[period-1];
      
      m_energy_flow = price_correlation * volume_trend;
   }
   
   // Sintonizar frequência cósmica
   void TuneCosmicFrequency(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      int peak_count = 0;
      double volume_sum = 0.0;
      
      for(int i = 1; i < period-1; i++)
      {
         if(volume[i] > volume[i-1] && volume[i] > volume[i+1])
         {
            peak_count++;
            volume_sum += volume[i];
         }
      }
      
      m_cosmic_frequency = (double)peak_count / (double)period;
      
      // Calcular confiança neural
      double volume_ratio = volume_sum / ArraySum(volume, period);
      double price_volatility = CStatistics::StdDev(price, period) / CStatistics::Mean(price, period);
      
      m_neural_confidence = (m_cosmic_frequency * 0.4 + volume_ratio * 0.4 + (1.0 - price_volatility) * 0.2) * 100.0;
   }
   
   // Função auxiliar para somar array
   double ArraySum(const double &array[], int count)
   {
      double sum = 0.0;
      
      for(int i = 0; i < count && i < ArraySize(array); i++)
      {
         sum += array[i];
      }
      
      return sum;
   }
}; 