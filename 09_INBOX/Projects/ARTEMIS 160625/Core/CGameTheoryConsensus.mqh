//+------------------------------------------------------------------+
//|                                      CGameTheoryConsensus.mqh     |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.0"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Classe para gerenciar consenso baseado em teoria dos jogos        |
//+------------------------------------------------------------------+
class CGameTheoryConsensus
{
private:
   CLogger* m_logger;
   double m_agreement_threshold;
   double m_divergence_threshold;
   double m_nash_weight;
   double m_minimax_weight;
   double m_last_consensus;
   datetime m_last_update_time;
   
public:
   // Construtor
   CGameTheoryConsensus(CLogger* logger)
   {
      m_logger = logger;
      m_agreement_threshold = 0.7;  // 70% de acordo necessário
      m_divergence_threshold = 0.3;  // 30% de divergência máxima
      m_nash_weight = 0.6;  // 60% peso para equilíbrio de Nash
      m_minimax_weight = 0.4;  // 40% peso para estratégia minimax
      m_last_consensus = 0.0;
      m_last_update_time = TimeCurrent();
   }
   
   // Define thresholds
   void SetThresholds(double agreement_threshold, double divergence_threshold)
   {
      m_agreement_threshold = agreement_threshold;
      m_divergence_threshold = divergence_threshold;
      m_logger.Info("Thresholds de consenso atualizados");
   }
   
   // Define pesos
   void SetWeights(double nash_weight, double minimax_weight)
   {
      m_nash_weight = nash_weight;
      m_minimax_weight = minimax_weight;
      m_logger.Info("Pesos de estratégia atualizados");
   }
   
   // Obtém consenso
   double GetConsensus()
   {
      // Calcula equilíbrio de Nash
      double nash_equilibrium = CalculateNashEquilibrium();
      
      // Calcula estratégia minimax
      double minimax_strategy = CalculateMinimaxStrategy();
      
      // Combina estratégias
      m_last_consensus = nash_equilibrium * m_nash_weight + 
                        minimax_strategy * m_minimax_weight;
      
      m_last_update_time = TimeCurrent();
      
      return m_last_consensus;
   }
   
   // Valida sinal
   bool ValidateSignal(double signal)
   {
      // Verifica divergência
      double divergence = MathAbs(signal - m_last_consensus);
      if(divergence > m_divergence_threshold)
      {
         m_logger.Warn("Divergência alta detectada: " + DoubleToString(divergence, 2));
         return false;
      }
      
      // Verifica acordo
      double agreement = 1.0 - divergence;
      if(agreement < m_agreement_threshold)
      {
         m_logger.Warn("Acordo insuficiente: " + DoubleToString(agreement, 2));
         return false;
      }
      
      return true;
   }
   
   // Calcula equilíbrio de Nash
   double CalculateNashEquilibrium()
   {
      double equilibrium = 0.0;
      int count = 0;
      
      // Analisa últimos 20 candles
      for(int i = 0; i < 20; i++)
      {
         double close = iClose(_Symbol, PERIOD_CURRENT, i);
         double open = iOpen(_Symbol, PERIOD_CURRENT, i);
         
         if(close > 0 && open > 0)
         {
            double move = (close - open) / open;
            equilibrium += move;
            count++;
         }
      }
      
      return count > 0 ? equilibrium / count : 0.0;
   }
   
   // Calcula estratégia minimax
   double CalculateMinimaxStrategy()
   {
      double max_loss = 0.0;
      double max_gain = 0.0;
      
      // Analisa últimos 20 candles
      for(int i = 0; i < 20; i++)
      {
         double high = iHigh(_Symbol, PERIOD_CURRENT, i);
         double low = iLow(_Symbol, PERIOD_CURRENT, i);
         double open = iOpen(_Symbol, PERIOD_CURRENT, i);
         
         if(high > 0 && low > 0 && open > 0)
         {
            double gain = (high - open) / open;
            double loss = (low - open) / open;
            
            max_gain = MathMax(max_gain, gain);
            max_loss = MathMin(max_loss, loss);
         }
      }
      
      // Retorna estratégia que minimiza a máxima perda
      return -max_loss / (max_gain - max_loss);
   }
   
   // Obtém último consenso
   double GetLastConsensus()
   {
      return m_last_consensus;
   }
   
   // Obtém tempo da última atualização
   datetime GetLastUpdateTime()
   {
      return m_last_update_time;
   }
   
   // Obtém threshold de acordo
   double GetAgreementThreshold()
   {
      return m_agreement_threshold;
   }
   
   // Obtém threshold de divergência
   double GetDivergenceThreshold()
   {
      return m_divergence_threshold;
   }
}; 