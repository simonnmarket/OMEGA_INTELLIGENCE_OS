//+------------------------------------------------------------------+
//|                                            CAdaptiveMemory.mqh    |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Estrutura para armazenar parâmetros                               |
//+------------------------------------------------------------------+
struct MemoryParameters
{
   double values[];           // Valores dos parâmetros
   datetime timestamp;        // Timestamp da memória
   double performance;        // Performance associada
   int usage_count;          // Contador de uso
};

//+------------------------------------------------------------------+
//| Classe para memória adaptativa                                    |
//+------------------------------------------------------------------+
class CAdaptiveMemory : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   MemoryParameters m_parameters[];      // Array de parâmetros
   int m_max_memories;                   // Número máximo de memórias
   int m_current_index;                  // Índice atual
   bool m_is_initialized;                // Se está inicializado
   
public:
   // Construtor
   CAdaptiveMemory(int max_memories, CLogger* logger)
   {
      m_max_memories = max_memories;
      m_logger = logger;
      m_current_index = 0;
      m_is_initialized = false;
      
      // Inicializa array de parâmetros
      ArrayResize(m_parameters, m_max_memories);
      
      if(m_logger != NULL)
      {
         m_logger.Info("Memória adaptativa inicializada");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CAdaptiveMemory()
   {
      if(m_logger != NULL)
         m_logger.Info("Memória adaptativa finalizada");
   }
   
   // Adiciona nova memória
   bool AddMemory(const double& values[], double performance)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      // Copia valores
      ArrayResize(m_parameters[m_current_index].values, ArraySize(values));
      ArrayCopy(m_parameters[m_current_index].values, values);
      
      // Atualiza outros campos
      m_parameters[m_current_index].timestamp = TimeCurrent();
      m_parameters[m_current_index].performance = performance;
      m_parameters[m_current_index].usage_count = 0;
      
      // Atualiza índice
      m_current_index = (m_current_index + 1) % m_max_memories;
      
      return true;
   }
   
   // Obtém melhor memória
   bool GetBestMemory(double& values[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      int best_index = -1;
      double best_performance = -DBL_MAX;
      
      // Encontra melhor performance
      for(int i = 0; i < m_max_memories; i++)
      {
         if(m_parameters[i].performance > best_performance)
         {
            best_performance = m_parameters[i].performance;
            best_index = i;
         }
      }
      
      if(best_index >= 0)
      {
         // Copia valores
         ArrayResize(values, ArraySize(m_parameters[best_index].values));
         ArrayCopy(values, m_parameters[best_index].values);
         return true;
      }
      
      return false;
   }
   
   // Obtém memória mais recente
   bool GetLatestMemory(double& values[])
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      int latest_index = (m_current_index - 1 + m_max_memories) % m_max_memories;
      
      // Copia valores
      ArrayResize(values, ArraySize(m_parameters[latest_index].values));
      ArrayCopy(values, m_parameters[latest_index].values);
      
      return true;
   }
   
   // Atualiza performance
   bool UpdatePerformance(int index, double performance)
   {
      if(!m_is_initialized || m_logger == NULL || index < 0 || index >= m_max_memories)
         return false;
         
      m_parameters[index].performance = performance;
      m_parameters[index].usage_count++;
      
      return true;
   }
   
   // Obtém número de memórias
   int GetMemoryCount()
   {
      return m_max_memories;
   }
   
   // Obtém contador de uso
   int GetUsageCount(int index)
   {
      if(index < 0 || index >= m_max_memories)
         return 0;
         
      return m_parameters[index].usage_count;
   }
}; 