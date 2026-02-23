//+------------------------------------------------------------------+
//|                                        MeanReversionAgent.mqh     |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Core\\CAgentBase.mqh"
#include "..\\Quantum\\CQuantumMarketPhysics.mqh"

//+------------------------------------------------------------------+
//| Classe para agente de reversão à média                            |
//+------------------------------------------------------------------+
class CMeanReversionAgent : public CAgentBase
{
private:
   int m_period;
   double m_deviation_threshold;
   double m_mean;
   double m_std_dev;
   datetime m_last_update_time;
   double m_oversold;
   double m_overbought;
   double m_confidence;
   CQuantumMarketPhysics* m_quantum_state;
   double m_mean_state;
   double m_quantum_coherence;
   
public:
   // Construtor
   CMeanReversionAgent(string symbol, ENUM_TIMEFRAMES timeframe, CLogger* logger)
      : CAgentBase(symbol, timeframe, logger)
   {
      m_period = 20;
      m_deviation_threshold = 2.0;
      m_mean = 0.0;
      m_std_dev = 0.0;
      m_last_update_time = 0;
      m_oversold = -2.0;
      m_overbought = 2.0;
      m_confidence = 0.0;
      m_quantum_state = NULL;
      m_mean_state = 0.0;
      m_quantum_coherence = 0.0;
   }
   
   // Define parâmetros
   void SetParameters(int period, double deviation_threshold)
   {
      m_period = period;
      m_deviation_threshold = deviation_threshold;
      m_logger.Info("Parâmetros do agente de reversão atualizados");
   }
   
   // Atualiza métricas
   void Update() override
   {
      // Calcula média móvel e desvio padrão
      double ma = iMA(m_symbol, m_timeframe, m_period, 0, MODE_SMA, PRICE_CLOSE);
      double std = iStdDev(m_symbol, m_timeframe, m_period, 0, MODE_SMA, PRICE_CLOSE);
      
      if(std > 0)
      {
         m_mean = ma;
         m_std_dev = std;
         
         // Atualiza estados quânticos
         if(m_quantum_state != NULL)
         {
            m_mean_state = m_quantum_state.GetMeanState();
            m_quantum_coherence = m_quantum_state.GetCoherence();
         }
      }
      
      m_last_update_time = TimeCurrent();
   }
   
   // Obtém sinal
   double GetSignal() override
   {
      double closes[];
      ArraySetAsSeries(closes, true);
      
      if(CopyClose(m_symbol, m_timeframe, 0, 1, closes) > 0)
      {
         double current_price = closes[0];
         
         if(m_std_dev > 0)
         {
            double z_score = (current_price - m_mean) / m_std_dev;
            
            if(z_score > m_overbought)
               return -1.0;  // Sinal de venda
            else if(z_score < m_oversold)
               return 1.0;   // Sinal de compra
         }
      }
      
      return 0.0;  // Sem sinal
   }
   
   // Obtém confiança
   double GetConfidence() override
   {
      double current_price = SymbolInfoDouble(m_symbol, SYMBOL_BID);
      
      if(m_std_dev > 0)
      {
         double z_score = MathAbs((current_price - m_mean) / m_std_dev);
         m_confidence = MathMin(z_score / m_deviation_threshold, 1.0);
         
         // Ajusta confiança baseado no estado quântico
         if(m_quantum_state != NULL)
         {
            m_confidence *= m_quantum_coherence;
         }
         
         return m_confidence;
      }
      
      return 0.0;
   }
   
   // Obtém média atual
   double GetCurrentMean()
   {
      return m_mean;
   }
   
   // Obtém desvio padrão atual
   double GetCurrentStdDev()
   {
      return m_std_dev;
   }
   
   // Obtém Z-score atual
   double GetCurrentZScore()
   {
      double current_price = SymbolInfoDouble(m_symbol, SYMBOL_BID);
      
      if(m_std_dev > 0)
         return (current_price - m_mean) / m_std_dev;
      
      return 0.0;
   }
   
   // Obtém tempo da última atualização
   datetime GetLastUpdateTime()
   {
      return m_last_update_time;
   }
};