//+------------------------------------------------------------------+
//|                                        MomentumAgent.mqh          |
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
//| Classe para agente de momentum                                    |
//+------------------------------------------------------------------+
class CMomentumAgent : public CAgentBase
{
private:
   int m_period;
   double m_threshold;
   double m_momentum;
   double m_previous_momentum;
   datetime m_last_update_time;
   double m_confidence;
   CQuantumMarketPhysics* m_quantum_state;
   double m_previous_state;
   double m_quantum_coherence;
   
public:
   // Construtor
   CMomentumAgent(string symbol, ENUM_TIMEFRAMES timeframe, CLogger* logger)
      : CAgentBase(symbol, timeframe, logger)
   {
      m_period = 14;
      m_threshold = 100.0;
      m_momentum = 0.0;
      m_previous_momentum = 0.0;
      m_last_update_time = 0;
      m_confidence = 0.0;
      m_quantum_state = NULL;
      m_previous_state = 0.0;
      m_quantum_coherence = 0.0;
   }
   
   // Define parâmetros
   void SetParameters(int period, double threshold)
   {
      m_period = period;
      m_threshold = threshold;
      m_logger.Info("Parâmetros do agente de momentum atualizados");
   }
   
   // Atualiza métricas
   void Update() override
   {
      // Calcula momentum
      double momentum = iMomentum(m_symbol, m_timeframe, m_period, PRICE_CLOSE);
      
      if(momentum > 0)
      {
         m_previous_momentum = m_momentum;
         m_momentum = momentum;
         
         // Atualiza estados quânticos
         if(m_quantum_state != NULL)
         {
            m_previous_state = m_quantum_state.GetQuantumState();
            m_quantum_coherence = m_quantum_state.GetCoherence();
         }
      }
      
      m_last_update_time = TimeCurrent();
   }
   
   // Obtém sinal
   double GetSignal() override
   {
      if(m_momentum > m_threshold && m_previous_momentum <= m_threshold)
         return 1.0;   // Sinal de compra
      else if(m_momentum < -m_threshold && m_previous_momentum >= -m_threshold)
         return -1.0;  // Sinal de venda
      
      return 0.0;  // Sem sinal
   }
   
   // Obtém confiança
   double GetConfidence() override
   {
      double momentum_strength = MathAbs(m_momentum) / m_threshold;
      m_confidence = MathMin(momentum_strength, 1.0);
      
      // Ajusta confiança baseado no estado quântico
      if(m_quantum_state != NULL)
      {
         m_confidence *= m_quantum_coherence;
      }
      
      return m_confidence;
   }
   
   // Atualiza performance
   void UpdatePerformance() override
   {
      // Atualiza métricas de performance
      if(m_logger != NULL)
      {
         m_logger.Info(StringFormat("Momentum Agent Performance - Signal: %.2f, Confidence: %.2f",
            GetSignal(), GetConfidence()));
      }
   }
   
   // Obtém momentum atual
   double GetCurrentMomentum()
   {
      return m_momentum;
   }
   
   // Obtém momentum anterior
   double GetPreviousMomentum()
   {
      return m_previous_momentum;
   }
   
   // Obtém tempo da última atualização
   datetime GetLastUpdateTime()
   {
      return m_last_update_time;
   }
}; 