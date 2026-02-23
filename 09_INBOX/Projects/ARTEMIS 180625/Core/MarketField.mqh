//+------------------------------------------------------------------+
//| MarketField.mqh - Market Field Analysis                          |
//+------------------------------------------------------------------+

class MarketField
{
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_rsi_period;
   int m_macd_fast;
   int m_macd_slow;
   int m_macd_signal;
   int m_ma_period;
   
public:
   MarketField()
   {
      m_symbol = Symbol();
      m_timeframe = PERIOD_CURRENT;
      m_rsi_period = 14;
      m_macd_fast = 12;
      m_macd_slow = 26;
      m_macd_signal = 9;
      m_ma_period = 20;
   }
   
   // Obter RSI
   double GetRSI()
   {
      double rsi[];
      ArraySetAsSeries(rsi, true);
      ArrayResize(rsi, 1);
      
      int handle = iRSI(m_symbol, m_timeframe, m_rsi_period, PRICE_CLOSE);
      if(handle == INVALID_HANDLE) return 0.0;
      
      if(CopyBuffer(handle, 0, 0, 1, rsi) > 0)
      {
         IndicatorRelease(handle);
         return rsi[0];
      }
      
      IndicatorRelease(handle);
      return 0.0;
   }
   
   // Obter MACD
   bool GetMACD(double &macd_main, double &macd_signal)
   {
      double macd[];
      double signal[];
      ArraySetAsSeries(macd, true);
      ArraySetAsSeries(signal, true);
      ArrayResize(macd, 1);
      ArrayResize(signal, 1);
      
      int handle = iMACD(m_symbol, m_timeframe, m_macd_fast, m_macd_slow, m_macd_signal, PRICE_CLOSE);
      if(handle == INVALID_HANDLE) return false;
      
      bool result = CopyBuffer(handle, 0, 0, 1, macd) > 0 && 
                   CopyBuffer(handle, 1, 0, 1, signal) > 0;
                   
      IndicatorRelease(handle);
      
      if(result)
      {
         macd_main = macd[0];
         macd_signal = signal[0];
      }
      
      return result;
   }
   
   // Obter Média Móvel
   double GetMA()
   {
      double ma[];
      ArraySetAsSeries(ma, true);
      ArrayResize(ma, 1);
      
      int handle = iMA(m_symbol, m_timeframe, m_ma_period, 0, MODE_SMA, PRICE_CLOSE);
      if(handle == INVALID_HANDLE) return 0.0;
      
      if(CopyBuffer(handle, 0, 0, 1, ma) > 0)
      {
         IndicatorRelease(handle);
         return ma[0];
      }
      
      IndicatorRelease(handle);
      return 0.0;
   }
   
   // Configurar parâmetros
   void SetParameters(const string symbol, const ENUM_TIMEFRAMES timeframe,
                     const int rsi_period, const int macd_fast, const int macd_slow,
                     const int macd_signal, const int ma_period)
   {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_rsi_period = rsi_period;
      m_macd_fast = macd_fast;
      m_macd_slow = macd_slow;
      m_macd_signal = macd_signal;
      m_ma_period = ma_period;
   }
}; 