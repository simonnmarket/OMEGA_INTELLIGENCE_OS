//+------------------------------------------------------------------+
//|                                             MarketAnalyzer.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Constantes de análise de mercado
#define MIN_TREND_POINTS 20
#define MAX_VOLATILITY 0.02
#define MIN_VOLUME_THRESHOLD 1000

// Classe principal de análise de mercado
class CMarketAnalyzer : public IDataAnalyzer
{
private:
   double m_trend_strength;
   double m_volatility;
   double m_volume_ratio;
   double m_market_sentiment;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CMarketAnalyzer()
   {
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_volume_ratio = 0.0;
      m_market_sentiment = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_volume_ratio = 0.0;
      m_market_sentiment = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_volatility >= 0.0 && m_volume_ratio >= 0.0;
   }
   
   void Cleanup() override
   {
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_volume_ratio = 0.0;
      m_market_sentiment = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "MarketAnalyzer"; }
   
   // Implementação de IDataAnalyzer
   bool AnalyzeData(const MqlRates &rates[], const double &volume[]) override
   {
      if(!m_is_initialized || ArraySize(rates) < MIN_TREND_POINTS || ArraySize(volume) < MIN_TREND_POINTS) return false;
      
      // Analisar força da tendência
      AnalyzeTrendStrength(rates);
      
      // Analisar volatilidade
      AnalyzeVolatility(rates);
      
      // Analisar volume
      AnalyzeVolume(volume);
      
      // Analisar sentimento do mercado
      AnalyzeMarketSentiment(rates, volume);
      
      return true;
   }
   
   bool GetAnalysisResults(double &trend_strength, double &volatility, double &volume_ratio, double &market_sentiment) override
   {
      if(!m_is_initialized) return false;
      
      trend_strength = m_trend_strength;
      volatility = m_volatility;
      volume_ratio = m_volume_ratio;
      market_sentiment = m_market_sentiment;
      
      return true;
   }
   
   // Métodos específicos do MarketAnalyzer
   bool IsMarketStable(const MqlRates &rates[], const double &volume[])
   {
      if(!m_is_initialized || ArraySize(rates) < MIN_TREND_POINTS || ArraySize(volume) < MIN_TREND_POINTS) return false;
      
      // Verificar volatilidade
      if(m_volatility > MAX_VOLATILITY)
         return false;
      
      // Verificar volume
      if(m_volume_ratio < MIN_VOLUME_THRESHOLD)
         return false;
      
      return true;
   }
   
   // Getters
   double GetTrendStrength() const { return m_trend_strength; }
   double GetVolatility() const { return m_volatility; }
   double GetVolumeRatio() const { return m_volume_ratio; }
   double GetMarketSentiment() const { return m_market_sentiment; }
   
private:
   void AnalyzeTrendStrength(const MqlRates &rates[])
   {
      double total_price_change = 0.0;
      double total_abs_price_change = 0.0;
      
      for(int i = 1; i < ArraySize(rates); i++)
      {
         double price_change = rates[i].close - rates[i-1].close;
         total_price_change += price_change;
         total_abs_price_change += MathAbs(price_change);
      }
      
      if(total_abs_price_change > 0.0)
         m_trend_strength = total_price_change / total_abs_price_change;
      else
         m_trend_strength = 0.0;
   }
   
   void AnalyzeVolatility(const MqlRates &rates[])
   {
      double sum_squared_diff = 0.0;
      double mean = 0.0;
      
      // Calcular média
      for(int i = 0; i < ArraySize(rates); i++)
         mean += rates[i].close;
      
      mean /= ArraySize(rates);
      
      // Calcular variância
      for(int i = 0; i < ArraySize(rates); i++)
         sum_squared_diff += MathPow(rates[i].close - mean, 2);
      
      m_volatility = MathSqrt(sum_squared_diff / ArraySize(rates)) / mean;
   }
   
   void AnalyzeVolume(const double &volume[])
   {
      double total_volume = 0.0;
      double max_volume = 0.0;
      
      for(int i = 0; i < ArraySize(volume); i++)
      {
         total_volume += volume[i];
         if(volume[i] > max_volume)
            max_volume = volume[i];
      }
      
      if(max_volume > 0.0)
         m_volume_ratio = total_volume / (max_volume * ArraySize(volume));
      else
         m_volume_ratio = 0.0;
   }
   
   void AnalyzeMarketSentiment(const MqlRates &rates[], const double &volume[])
   {
      double bullish_volume = 0.0;
      double bearish_volume = 0.0;
      
      for(int i = 1; i < ArraySize(rates); i++)
      {
         if(rates[i].close > rates[i-1].close)
            bullish_volume += volume[i];
         else if(rates[i].close < rates[i-1].close)
            bearish_volume += volume[i];
      }
      
      double total_volume = bullish_volume + bearish_volume;
      
      if(total_volume > 0.0)
         m_market_sentiment = (bullish_volume - bearish_volume) / total_volume;
      else
         m_market_sentiment = 0.0;
   }
}; 