//+------------------------------------------------------------------+
//|                                           CTimeframeHierarchy.mqh |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.0"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Classe para gerenciar hierarquia de timeframes                    |
//+------------------------------------------------------------------+
class CTimeframeHierarchy
{
private:
   CLogger* m_logger;
   ENUM_TIMEFRAMES m_timeframes[];
   int m_total_timeframes;
   double m_weights[];
   
public:
   // Construtor
   CTimeframeHierarchy(CLogger* logger)
   {
      m_logger = logger;
      InitializeTimeframes();
   }
   
   // Destrutor
   ~CTimeframeHierarchy()
   {
      ArrayFree(m_timeframes);
      ArrayFree(m_weights);
   }
   
   // Inicializa timeframes
   void InitializeTimeframes()
   {
      // Timeframes padrão
      m_total_timeframes = 5;
      ArrayResize(m_timeframes, m_total_timeframes);
      ArrayResize(m_weights, m_total_timeframes);
      
      m_timeframes[0] = PERIOD_M1;
      m_timeframes[1] = PERIOD_M5;
      m_timeframes[2] = PERIOD_M15;
      m_timeframes[3] = PERIOD_H1;
      m_timeframes[4] = PERIOD_H4;
      
      // Pesos padrão
      m_weights[0] = 0.1;  // M1
      m_weights[1] = 0.2;  // M5
      m_weights[2] = 0.3;  // M15
      m_weights[3] = 0.3;  // H1
      m_weights[4] = 0.1;  // H4
      
      m_logger.Info("Hierarquia de timeframes inicializada");
   }
   
   // Obtém timeframe superior
   ENUM_TIMEFRAMES GetHigherTimeframe(ENUM_TIMEFRAMES timeframe)
   {
      for(int i = 0; i < m_total_timeframes - 1; i++)
      {
         if(m_timeframes[i] == timeframe)
            return m_timeframes[i + 1];
      }
      return timeframe;
   }
   
   // Obtém timeframe inferior
   ENUM_TIMEFRAMES GetLowerTimeframe(ENUM_TIMEFRAMES timeframe)
   {
      for(int i = 1; i < m_total_timeframes; i++)
      {
         if(m_timeframes[i] == timeframe)
            return m_timeframes[i - 1];
      }
      return timeframe;
   }
   
   // Obtém peso do timeframe
   double GetTimeframeWeight(ENUM_TIMEFRAMES timeframe)
   {
      for(int i = 0; i < m_total_timeframes; i++)
      {
         if(m_timeframes[i] == timeframe)
            return m_weights[i];
      }
      return 0.0;
   }
   
   // Define peso do timeframe
   void SetTimeframeWeight(ENUM_TIMEFRAMES timeframe, double weight)
   {
      for(int i = 0; i < m_total_timeframes; i++)
      {
         if(m_timeframes[i] == timeframe)
         {
            m_weights[i] = weight;
            m_logger.Info("Peso do timeframe " + EnumToString(timeframe) + " atualizado para " + DoubleToString(weight, 2));
            return;
         }
      }
   }
   
   // Obtém total de timeframes
   int GetTotalTimeframes()
   {
      return m_total_timeframes;
   }
   
   // Obtém timeframe pelo índice
   ENUM_TIMEFRAMES GetTimeframeByIndex(int index)
   {
      if(index >= 0 && index < m_total_timeframes)
         return m_timeframes[index];
      return PERIOD_CURRENT;
   }
}; 