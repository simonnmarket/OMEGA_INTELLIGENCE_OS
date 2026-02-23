//+------------------------------------------------------------------+
//|                   MarketAnalysisAgent.mqh                        |
//|     Responsável pela análise técnica e institucional do mercado |
//+------------------------------------------------------------------+
#pragma once
#include "..\Utils\IndicatorUtils.mqh"
#include "..\Utils\Log.mqh"
#include "..\Core\types.mqh"

class MarketAnalysisAgent {
private:
   string symbol;
   ENUM_TIMEFRAMES timeframe;

public:
   MarketAnalysisAgent(string _symbol, ENUM_TIMEFRAMES _timeframe) {
      symbol = _symbol;
      timeframe = _timeframe;
   }

   //--- Detecta aumento de volatilidade com base no ATR
   double GetVolatilityLevel(int period = 14) {
      return iATR(symbol, timeframe, period, 0);
   }

   //--- Detecta pressão de compra/venda com base no RSI
   double GetMomentum(int period = 14) {
      return iRSI(symbol, timeframe, period, PRICE_CLOSE, 0);
   }

   //--- Verifica volume institucional (placeholder para futura lógica de dark pool)
   double GetInstitutionalVolume() {
      return iVolume(symbol, timeframe, 0);
   }

   //--- Detecta candle de força direcional (exemplo básico)
   bool IsStrongDirectionalCandle(double threshold = 1.5) {
      double body = MathAbs(iClose(symbol, timeframe, 0) - iOpen(symbol, timeframe, 0));
      double range = iHigh(symbol, timeframe, 0) - iLow(symbol, timeframe, 0);
      if (range == 0) return false;

      double body_ratio = body / range;
      return body_ratio >= threshold;
   }

   //--- Verifica se há confluência entre ATR e RSI para movimentação relevante
   bool DetectDirectionalBias() {
      double rsi = GetMomentum();
      double atr = GetVolatilityLevel();

      if (atr > 0.0005 && (rsi > 60 || rsi < 40)) {
         PrintLog("Bias identificado: ATR=", atr, " RSI=", rsi);
         return true;
      }
      return false;
   }
};
