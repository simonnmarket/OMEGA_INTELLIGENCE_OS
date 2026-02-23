//+------------------------------------------------------------------+
//|                                                MarketAnalyzer.mqh |
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
#include "..\..\Core\MarketSignal\MarketSignal.mqh"

// Classe principal de análise de mercado
class CMarketAnalyzer
{
private:
   double m_market_trend;
   double m_volume_trend;
   double m_volatility_trend;
   double m_momentum;
   double m_rsi;
   double m_macd;
   double m_signal;
   
public:
   // Construtor
   CMarketAnalyzer()
   {
      m_market_trend = 0.0;
      m_volume_trend = 0.0;
      m_volatility_trend = 0.0;
      m_momentum = 0.0;
      m_rsi = 50.0;
      m_macd = 0.0;
      m_signal = 0.0;
   }
   
   // Inicialização
   bool Init()
   {
      m_market_trend = 0.0;
      m_volume_trend = 0.0;
      m_volatility_trend = 0.0;
      m_momentum = 0.0;
      m_rsi = 50.0;
      m_macd = 0.0;
      m_signal = 0.0;
      
      return true;
   }
   
   // Atualizar análise
   void Update(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      // Calcular tendências
      CalculateMarketTrend(price, period);
      CalculateVolumeTrend(volume, period);
      CalculateVolatilityTrend(price, period);
      
      // Calcular indicadores
      CalculateMomentum(price, period);
      CalculateRSI(price, period);
      CalculateMACD(price);
      
      // Gerar sinal
      GenerateSignal();
   }
   
   // Analisar mercado
   ENUM_MARKET_SIGNAL AnalyzeMarket()
   {
      if(m_market_trend > 0.0 && m_volume_trend > 0.0 && m_momentum > 0.0)
         return SIGNAL_BUY;
      else if(m_market_trend < 0.0 && m_volume_trend < 0.0 && m_momentum < 0.0)
         return SIGNAL_SELL;
         
      return SIGNAL_NONE;
   }
   
   // Getters
   double GetMarketTrend() const { return m_market_trend; }
   double GetVolumeTrend() const { return m_volume_trend; }
   double GetVolatilityTrend() const { return m_volatility_trend; }
   double GetMomentum() const { return m_momentum; }
   double GetRSI() const { return m_rsi; }
   double GetMACD() const { return m_macd; }
   double GetSignal() const { return m_signal; }
   
private:
   // Calcular tendência de mercado
   void CalculateMarketTrend(const double &price[], int period)
   {
      if(ArraySize(price) < period) return;
      
      double sum = 0.0;
      for(int i = 0; i < period; i++)
      {
         sum += price[i];
      }
      
      double avg = sum / period;
      m_market_trend = (price[0] - avg) / avg;
   }
   
   // Calcular tendência de volume
   void CalculateVolumeTrend(const double &volume[], int period)
   {
      if(ArraySize(volume) < period) return;
      
      double sum = 0.0;
      for(int i = 0; i < period; i++)
      {
         sum += volume[i];
      }
      
      double avg = sum / period;
      m_volume_trend = (volume[0] - avg) / avg;
   }
   
   // Calcular tendência de volatilidade
   void CalculateVolatilityTrend(const double &price[], int period)
   {
      if(ArraySize(price) < period) return;
      
      double high[], low[];
      ArrayResize(high, period);
      ArrayResize(low, period);
      
      for(int i = 0; i < period; i++)
      {
         high[i] = price[i];
         low[i] = price[i];
      }
      
      double sum_volatility = 0.0;
      for(int i = 0; i < period; i++)
      {
         sum_volatility += (high[i] - low[i]) / _Point;
      }
      
      double avg_volatility = sum_volatility / period;
      m_volatility_trend = ((high[0] - low[0]) / _Point - avg_volatility) / avg_volatility;
   }
   
   // Calcular momentum
   void CalculateMomentum(const double &price[], int period)
   {
      if(ArraySize(price) < period) return;
      
      m_momentum = (price[0] - price[period-1]) / price[period-1];
   }
   
   // Calcular RSI
   void CalculateRSI(const double &price[], int period)
   {
      if(ArraySize(price) < period) return;
      
      double gains = 0.0;
      double losses = 0.0;
      
      for(int i = 1; i < period; i++)
      {
         double change = price[i-1] - price[i];
         if(change >= 0)
            gains += change;
         else
            losses -= change;
      }
      
      double avg_gain = gains / (period - 1);
      double avg_loss = losses / (period - 1);
      
      if(avg_loss == 0.0)
         m_rsi = 100.0;
      else
         m_rsi = 100.0 - (100.0 / (1.0 + avg_gain / avg_loss));
   }
   
   // Calcular MACD
   void CalculateMACD(const double &price[])
   {
      if(ArraySize(price) < 26) return;
      
      double ema12 = CalculateEMA(price, 12);
      double ema26 = CalculateEMA(price, 26);
      
      m_macd = ema12 - ema26;
      m_signal = CalculateEMA(&m_macd, 9);
   }
   
   // Calcular EMA
   double CalculateEMA(const double &price[], int period)
   {
      if(ArraySize(price) < period) return 0.0;
      
      double multiplier = 2.0 / (period + 1);
      double ema = price[0];
      
      for(int i = 1; i < period; i++)
      {
         ema = (price[i] - ema) * multiplier + ema;
      }
      
      return ema;
   }
   
   // Gerar sinal
   void GenerateSignal()
   {
      if(m_macd > m_signal && m_rsi > 50.0)
         m_signal = 1.0;
      else if(m_macd < m_signal && m_rsi < 50.0)
         m_signal = -1.0;
      else
         m_signal = 0.0;
   }
}; 