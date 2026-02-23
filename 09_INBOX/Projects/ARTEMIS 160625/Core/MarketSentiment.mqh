//+------------------------------------------------------------------+
//| CMarketSentiment.mqh - Market Sentiment Analysis                 |
//| Inspirado em: Behavioral Finance, Market Psychology              |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>
#property copyright "Quantum Trading Labs - Confidential"
#property strict

class CMarketSentiment : public CObject
{
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_lookback;
   double m_sentiment;
   
public:
   CMarketSentiment()
   {
      m_symbol = Symbol();
      m_timeframe = PERIOD_CURRENT;
      m_lookback = 20;
      m_sentiment = 0.0;
   }
   
   // Atualizar sentimento
   void Update()
   {
      double volume[];
      ArraySetAsSeries(volume, true);
      ArrayResize(volume, m_lookback);
      
      if(CopyTickVolume(m_symbol, m_timeframe, 0, m_lookback, volume) > 0)
      {
         double sum_volume = 0.0;
         for(int i = 0; i < m_lookback; i++)
         {
            sum_volume += (double)volume[i];  // Conversão explícita
         }
         
         m_sentiment = sum_volume / m_lookback;
      }
   }
   
   // Obter sentimento
   double GetSentiment() const
   {
      return m_sentiment;
   }
   
   // Configurar parâmetros
   void SetParameters(const string symbol, const ENUM_TIMEFRAMES timeframe, const int lookback)
   {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_lookback = lookback;
   }
}; 