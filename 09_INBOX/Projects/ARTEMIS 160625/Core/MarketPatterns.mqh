//+------------------------------------------------------------------+
//| CMarketPatterns.mqh - Advanced Market Pattern Recognition        |
//| Inspirado em: Technical Analysis, Chart Patterns                  |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include <Object.mqh>
#include "..\\Utils\\CLogger.mqh"
#include "..\\Core\\CStatistics.mqh"
#include "..\\Core\\CQuantumMarketPhysics.mqh"

//+------------------------------------------------------------------+
//| Classe para padrões de mercado                                    |
//+------------------------------------------------------------------+
class CMarketPatterns : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   CStatistics* m_statistics;            // Módulo de estatísticas
   CQuantumMarketPhysics* m_physics;     // Física quântica do mercado
   
   string m_symbol;                      // Símbolo
   double m_pattern_strength;            // Força do padrão
   double m_pattern_direction;           // Direção do padrão
   double m_pattern_probability;         // Probabilidade do padrão
   bool m_is_initialized;                // Se está inicializado
   
   // Arrays para armazenar padrões
   double m_patterns[];                  // Array de padrões
   double m_pattern_weights[];           // Pesos dos padrões
   int m_pattern_count;                  // Contador de padrões
   
public:
   // Construtor
   CMarketPatterns(string symbol, CLogger* logger)
   {
      m_symbol = symbol;
      m_logger = logger;
      m_is_initialized = false;
      m_pattern_count = 0;
      
      // Inicializa módulos
      m_statistics = new CStatistics(m_logger);
      m_physics = new CQuantumMarketPhysics(m_logger);
      
      if(m_logger != NULL && m_statistics != NULL && m_physics != NULL)
      {
         m_logger.Info("Padrões de mercado inicializados");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CMarketPatterns()
   {
      if(m_statistics != NULL)
         delete m_statistics;
         
      if(m_physics != NULL)
         delete m_physics;
         
      if(m_logger != NULL)
         m_logger.Info("Padrões de mercado finalizados");
   }
   
   // Atualiza padrões
   void Update()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Atualiza física quântica
      if(m_physics != NULL)
      {
         m_pattern_strength = m_physics.GetWaveAmplitude(m_symbol);
         m_pattern_direction = m_physics.GetWavePhase(m_symbol);
         m_pattern_probability = m_physics.GetMarketEnergy(m_symbol);
      }
   }
   
   // Adiciona padrão
   bool AddPattern(double pattern, double weight)
   {
      if(!m_is_initialized)
         return false;
         
      int new_size = m_pattern_count + 1;
      
      if(!ArrayResize(m_patterns, new_size) || !ArrayResize(m_pattern_weights, new_size))
         return false;
         
      m_patterns[m_pattern_count] = pattern;
      m_pattern_weights[m_pattern_count] = weight;
      m_pattern_count++;
      
      return true;
   }
   
   // Obtém força do padrão
   double GetPatternStrength()
   {
      return m_pattern_strength;
   }
   
   // Obtém direção do padrão
   double GetPatternDirection()
   {
      return m_pattern_direction;
   }
   
   // Obtém probabilidade do padrão
   double GetPatternProbability()
   {
      return m_pattern_probability;
   }
   
   // Obtém padrão por índice
   bool GetPattern(int index, double &pattern, double &weight)
   {
      if(index < 0 || index >= m_pattern_count)
         return false;
         
      pattern = m_patterns[index];
      weight = m_pattern_weights[index];
      
      return true;
   }
   
   // Obtém contagem de padrões
   int GetPatternCount()
   {
      return m_pattern_count;
   }
   
   // Limpa padrões
   void ClearPatterns()
   {
      ArrayResize(m_patterns, 0);
      ArrayResize(m_pattern_weights, 0);
      m_pattern_count = 0;
   }
   
   // Obtém padrão mais forte
   bool GetStrongestPattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      int strongest_index = 0;
      double strongest_weight = m_pattern_weights[0];
      
      for(int i = 1; i < m_pattern_count; i++)
      {
         if(m_pattern_weights[i] > strongest_weight)
         {
            strongest_index = i;
            strongest_weight = m_pattern_weights[i];
         }
      }
      
      pattern = m_patterns[strongest_index];
      weight = strongest_weight;
      
      return true;
   }
   
   // Obtém padrão mais provável
   bool GetMostProbablePattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      int most_probable_index = 0;
      double highest_probability = m_pattern_probability * m_pattern_weights[0];
      
      for(int i = 1; i < m_pattern_count; i++)
      {
         double probability = m_pattern_probability * m_pattern_weights[i];
         if(probability > highest_probability)
         {
            most_probable_index = i;
            highest_probability = probability;
         }
      }
      
      pattern = m_patterns[most_probable_index];
      weight = m_pattern_weights[most_probable_index];
      
      return true;
   }
   
   // Obtém padrão mais recente
   bool GetLatestPattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      pattern = m_patterns[m_pattern_count - 1];
      weight = m_pattern_weights[m_pattern_count - 1];
      
      return true;
   }
   
   // Obtém padrão mais antigo
   bool GetOldestPattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      pattern = m_patterns[0];
      weight = m_pattern_weights[0];
      
      return true;
   }
   
   // Obtém média dos padrões
   bool GetAveragePattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      double sum_pattern = 0.0;
      double sum_weight = 0.0;
      
      for(int i = 0; i < m_pattern_count; i++)
      {
         sum_pattern += m_patterns[i] * m_pattern_weights[i];
         sum_weight += m_pattern_weights[i];
      }
      
      if(sum_weight == 0.0)
         return false;
         
      pattern = sum_pattern / sum_weight;
      weight = sum_weight / m_pattern_count;
      
      return true;
   }
   
   // Obtém mediana dos padrões
   bool GetMedianPattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      // Cria arrays temporários para ordenação
      double temp_patterns[];
      double temp_weights[];
      
      if(!ArrayResize(temp_patterns, m_pattern_count) || !ArrayResize(temp_weights, m_pattern_count))
         return false;
         
      // Copia arrays
      ArrayCopy(temp_patterns, m_patterns);
      ArrayCopy(temp_weights, m_pattern_weights);
      
      // Ordena arrays
      ArraySort(temp_patterns, temp_weights);
      
      // Obtém mediana
      int median_index = m_pattern_count / 2;
      
      if(m_pattern_count % 2 == 0)
      {
         pattern = (temp_patterns[median_index - 1] + temp_patterns[median_index]) / 2.0;
         weight = (temp_weights[median_index - 1] + temp_weights[median_index]) / 2.0;
      }
      else
      {
         pattern = temp_patterns[median_index];
         weight = temp_weights[median_index];
      }
      
      return true;
   }
   
   // Obtém moda dos padrões
   bool GetModePattern(double &pattern, double &weight)
   {
      if(m_pattern_count == 0)
         return false;
         
      // Cria arrays temporários para contagem
      double temp_patterns[];
      double temp_weights[];
      
      if(!ArrayResize(temp_patterns, m_pattern_count) || !ArrayResize(temp_weights, m_pattern_count))
         return false;
         
      // Copia arrays
      ArrayCopy(temp_patterns, m_patterns);
      ArrayCopy(temp_weights, m_pattern_weights);
      
      // Ordena arrays
      ArraySort(temp_patterns, temp_weights);
      
      // Encontra moda
      double current_pattern = temp_patterns[0];
      double current_weight = temp_weights[0];
      int current_count = 1;
      
      double mode_pattern = current_pattern;
      double mode_weight = current_weight;
      int mode_count = current_count;
      
      for(int i = 1; i < m_pattern_count; i++)
      {
         if(temp_patterns[i] == current_pattern)
         {
            current_count++;
            current_weight += temp_weights[i];
         }
         else
         {
            if(current_count > mode_count)
            {
               mode_pattern = current_pattern;
               mode_weight = current_weight / current_count;
               mode_count = current_count;
            }
            
            current_pattern = temp_patterns[i];
            current_weight = temp_weights[i];
            current_count = 1;
         }
      }
      
      // Verifica último grupo
      if(current_count > mode_count)
      {
         mode_pattern = current_pattern;
         mode_weight = current_weight / current_count;
      }
      
      pattern = mode_pattern;
      weight = mode_weight;
      
      return true;
   }
}; 