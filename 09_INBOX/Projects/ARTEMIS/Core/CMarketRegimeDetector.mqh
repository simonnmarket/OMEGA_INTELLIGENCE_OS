//+------------------------------------------------------------------+
//|                                     CMarketRegimeDetector.mqh     |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"
#include "..\\Core\\CStatistics.mqh"

//+------------------------------------------------------------------+
//| Enumeração de regimes de mercado                                  |
//+------------------------------------------------------------------+
enum MarketRegime
{
   REGIME_SIDEWAYS,    // Mercado lateral
   REGIME_TRENDING,    // Mercado em tendência
   REGIME_VOLATILE,    // Mercado volátil
   REGIME_UNKNOWN      // Regime desconhecido
};

//+------------------------------------------------------------------+
//| Estrutura para métricas de regime                                 |
//+------------------------------------------------------------------+
struct RegimeMetrics
{
   double trend_strength;      // Força da tendência
   double momentum;            // Momentum
   double volatility;          // Volatilidade
   double mean_reversion;      // Mean reversion
   double regime_probability;  // Probabilidade do regime
   double regime_entropy;      // Entropia do regime
   double regime_correlation;  // Correlação do regime
   double regime_transition;   // Transição do regime
   double regime_stability;    // Estabilidade do regime
   double regime_confidence;   // Confiança do regime
};

//+------------------------------------------------------------------+
//| Classe para detecção de regime de mercado                         |
//+------------------------------------------------------------------+
class CMarketRegimeDetector : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   CStatistics* m_statistics;            // Módulo de estatísticas
   RegimeMetrics m_metrics;              // Métricas de regime
   bool m_is_initialized;                // Se está inicializado
   string m_symbol;                      // Símbolo
   ENUM_TIMEFRAMES m_timeframe;          // Timeframe
   int m_lookback_period;                // Período de lookback
   double m_confidence_threshold;
   int m_min_duration;
   double m_feature_weights[];
   MarketRegime m_current_regime;
   datetime m_regime_start_time;
   
public:
   // Construtor
   CMarketRegimeDetector(string symbol, ENUM_TIMEFRAMES timeframe, int lookback_period, CLogger* logger)
   {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_lookback_period = lookback_period;
      m_logger = logger;
      m_is_initialized = false;
      
      // Inicializa módulos
      m_statistics = new CStatistics(m_logger);
      
      // Inicializa métricas
      ZeroMemory(m_metrics);
      
      if(m_logger != NULL && m_statistics != NULL)
      {
         m_logger.Info("Detector de regime de mercado inicializado");
         m_is_initialized = true;
      }
      
      m_confidence_threshold = 0.7;
      m_min_duration = 20;
      m_current_regime = REGIME_UNKNOWN;
      m_regime_start_time = 0;
      
      // Pesos para características
      ArrayResize(m_feature_weights, 4);
      m_feature_weights[0] = 0.3;  // Tendência
      m_feature_weights[1] = 0.3;  // Volatilidade
      m_feature_weights[2] = 0.2;  // Volume
      m_feature_weights[3] = 0.2;  // Momentum
   }
   
   // Destrutor
   ~CMarketRegimeDetector()
   {
      if(m_statistics != NULL)
         delete m_statistics;
         
      if(m_logger != NULL)
         m_logger.Info("Detector de regime de mercado finalizado");
   }
   
   // Atualiza métricas
   void Update()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Atualiza métricas
      m_metrics.trend_strength = CalculateTrendStrength();
      m_metrics.momentum = CalculateMomentum();
      m_metrics.volatility = CalculateVolatility();
      m_metrics.mean_reversion = CalculateMeanReversion();
      m_metrics.regime_probability = CalculateRegimeProbability();
      m_metrics.regime_entropy = CalculateRegimeEntropy();
      m_metrics.regime_correlation = CalculateRegimeCorrelation();
      m_metrics.regime_transition = CalculateRegimeTransition();
      m_metrics.regime_stability = CalculateRegimeStability();
      m_metrics.regime_confidence = CalculateRegimeConfidence();
   }
   
   // Obtém métricas
   bool GetMetrics(RegimeMetrics& metrics)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      metrics = m_metrics;
      return true;
   }
   
   // Detecta regime atual
   MarketRegime DetectRegime()
   {
      // Calcula características
      double trend = CalculateTrend();
      double volatility = CalculateVolatility();
      double volume = CalculateVolume();
      double momentum = CalculateMomentum();
      
      // Calcula scores para cada regime
      double sideways_score = CalculateSidewaysScore(trend, volatility, volume, momentum);
      double trending_score = CalculateTrendingScore(trend, volatility, volume, momentum);
      double volatile_score = CalculateVolatileScore(trend, volatility, volume, momentum);
      
      // Determina regime com maior score
      MarketRegime new_regime = REGIME_UNKNOWN;
      double max_score = 0.0;
      
      if(sideways_score > max_score)
      {
         max_score = sideways_score;
         new_regime = REGIME_SIDEWAYS;
      }
      
      if(trending_score > max_score)
      {
         max_score = trending_score;
         new_regime = REGIME_TRENDING;
      }
      
      if(volatile_score > max_score)
      {
         max_score = volatile_score;
         new_regime = REGIME_VOLATILE;
      }
      
      // Verifica confiança e duração mínima
      if(max_score >= m_confidence_threshold)
      {
         if(new_regime != m_current_regime)
         {
            if(TimeCurrent() - m_regime_start_time >= m_min_duration * PeriodSeconds(PERIOD_CURRENT))
            {
               m_current_regime = new_regime;
               m_regime_start_time = TimeCurrent();
               m_logger.Info("Novo regime detectado: " + EnumToString(new_regime));
            }
         }
      }
      
      return m_current_regime;
   }
   
   // Calcula força da tendência
   double CalculateTrendStrength()
   {
      double strength = 0.0;
      // Implementar cálculo
      return strength;
   }
   
   // Calcula volatilidade
   double CalculateVolatility()
   {
      double volatility = 0.0;
      // Implementar cálculo
      return volatility;
   }
   
   // Calcula momentum
   double CalculateMomentum()
   {
      double momentum = 0.0;
      // Implementar cálculo
      return momentum;
   }
   
   // Calcula mean reversion
   double CalculateMeanReversion()
   {
      double reversion = 0.0;
      // Implementar cálculo
      return reversion;
   }
   
   // Calcula probabilidade do regime
   double CalculateRegimeProbability()
   {
      double probability = 0.0;
      // Implementar cálculo
      return probability;
   }
   
   // Calcula entropia do regime
   double CalculateRegimeEntropy()
   {
      double entropy = 0.0;
      // Implementar cálculo
      return entropy;
   }
   
   // Calcula correlação do regime
   double CalculateRegimeCorrelation()
   {
      double correlation = 0.0;
      // Implementar cálculo
      return correlation;
   }
   
   // Calcula transição do regime
   double CalculateRegimeTransition()
   {
      double transition = 0.0;
      // Implementar cálculo
      return transition;
   }
   
   // Calcula estabilidade do regime
   double CalculateRegimeStability()
   {
      double stability = 0.0;
      // Implementar cálculo
      return stability;
   }
   
   // Calcula confiança do regime
   double CalculateRegimeConfidence()
   {
      double confidence = 0.0;
      // Implementar cálculo
      return confidence;
   }
   
   // Calcula tendência
   double CalculateTrend()
   {
      double sum = 0.0;
      int count = 0;
      
      for(int i = 0; i < m_lookback_period; i++)
      {
         double close = iClose(_Symbol, PERIOD_CURRENT, i);
         double open = iOpen(_Symbol, PERIOD_CURRENT, i);
         
         if(close > 0 && open > 0)
         {
            sum += (close - open) / open;
            count++;
         }
      }
      
      return count > 0 ? sum / count : 0.0;
   }
   
   // Calcula volume
   double CalculateVolume()
   {
      double sum = 0.0;
      double sum2 = 0.0;
      int count = 0;
      
      for(int i = 0; i < m_lookback_period; i++)
      {
         double volume = iVolume(_Symbol, PERIOD_CURRENT, i);
         
         if(volume > 0)
         {
            sum += volume;
            sum2 += volume * volume;
            count++;
         }
      }
      
      if(count > 1)
      {
         double mean = sum / count;
         double variance = (sum2 - sum * sum / count) / (count - 1);
         return MathSqrt(variance) / mean;
      }
      
      return 0.0;
   }
   
   // Calcula score para regime lateral
   double CalculateSidewaysScore(double trend, double volatility, double volume, double momentum)
   {
      return (1.0 - MathAbs(trend)) * m_feature_weights[0] +
             (1.0 - volatility) * m_feature_weights[1] +
             (1.0 - volume) * m_feature_weights[2] +
             (1.0 - MathAbs(momentum)) * m_feature_weights[3];
   }
   
   // Calcula score para regime de tendência
   double CalculateTrendingScore(double trend, double volatility, double volume, double momentum)
   {
      return MathAbs(trend) * m_feature_weights[0] +
             volatility * m_feature_weights[1] +
             volume * m_feature_weights[2] +
             MathAbs(momentum) * m_feature_weights[3];
   }
   
   // Calcula score para regime volátil
   double CalculateVolatileScore(double trend, double volatility, double volume, double momentum)
   {
      return (1.0 - MathAbs(trend)) * m_feature_weights[0] +
             volatility * m_feature_weights[1] +
             volume * m_feature_weights[2] +
             MathAbs(momentum) * m_feature_weights[3];
   }
   
   // Obtém regime atual
   MarketRegime GetCurrentRegime()
   {
      return m_current_regime;
   }
   
   // Obtém duração do regime atual
   int GetCurrentRegimeDuration()
   {
      if(m_regime_start_time > 0)
         return (int)((TimeCurrent() - m_regime_start_time) / PeriodSeconds(PERIOD_CURRENT));
      return 0;
   }
   
   // Obtém confiança do regime atual
   double GetCurrentRegimeConfidence()
   {
      double trend = CalculateTrend();
      double volatility = CalculateVolatility();
      double volume = CalculateVolume();
      double momentum = CalculateMomentum();
      
      switch(m_current_regime)
      {
         case REGIME_SIDEWAYS:
            return CalculateSidewaysScore(trend, volatility, volume, momentum);
         case REGIME_TRENDING:
            return CalculateTrendingScore(trend, volatility, volume, momentum);
         case REGIME_VOLATILE:
            return CalculateVolatileScore(trend, volatility, volume, momentum);
         default:
            return 0.0;
      }
   }
}; 