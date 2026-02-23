//+------------------------------------------------------------------+
//|                    IndicatorUtils.mqh                            |
//|  Funções auxiliares para trabalhar com indicadores integrados    |
//+------------------------------------------------------------------+
#ifndef __INDICATOR_UTILS_MQH__
#define __INDICATOR_UTILS_MQH__

// Média Móvel Simples (SMA)
double iSMAValue(string symbol, ENUM_TIMEFRAMES tf, int period, int shift = 0, int applied_price = PRICE_CLOSE) {
   return iMA(symbol, tf, period, 0, MODE_SMA, applied_price, shift);
}

// Média Móvel Exponencial (EMA)
double iEMAValue(string symbol, ENUM_TIMEFRAMES tf, int period, int shift = 0, int applied_price = PRICE_CLOSE) {
   return iMA(symbol, tf, period, 0, MODE_EMA, applied_price, shift);
}

// RSI
double iRSIValue(string symbol, ENUM_TIMEFRAMES tf, int period, int shift = 0, int applied_price = PRICE_CLOSE) {
   return iRSI(symbol, tf, period, applied_price, shift);
}

// MACD Main Line
double iMACDMain(string symbol, ENUM_TIMEFRAMES tf, int fast_ema = 12, int slow_ema = 26, int signal = 9, int shift = 0, int applied_price = PRICE_CLOSE) {
   double macd_main[], macd_signal[];
   if (CopyBuffer(iMACD(symbol, tf, fast_ema, slow_ema, signal, applied_price), 0, shift, 1, macd_main) > 0)
      return macd_main[0];
   return 0.0;
}

// MACD Signal Line
double iMACDSignal(string symbol, ENUM_TIMEFRAMES tf, int fast_ema = 12, int slow_ema = 26, int signal = 9, int shift = 0, int applied_price = PRICE_CLOSE) {
   double macd_main[], macd_signal[];
   if (CopyBuffer(iMACD(symbol, tf, fast_ema, slow_ema, signal, applied_price), 1, shift, 1, macd_signal) > 0)
      return macd_signal[0];
   return 0.0;
}

// Indicador genérico de candles de reversão: retorna TRUE se candle atual for um martelo
bool IsHammer(double open, double close, double high, double low) {
   double body = MathAbs(close - open);
   double upperWick = high - MathMax(open, close);
   double lowerWick = MathMin(open, close) - low;

   return (body <= (high - low) * 0.3 && lowerWick > 2 * body && upperWick <= body);
}

#endif // __INDICATOR_UTILS_MQH__ 