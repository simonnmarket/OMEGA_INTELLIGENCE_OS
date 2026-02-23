//+------------------------------------------------------------------+
//| EngulfingPattern.mqh - Padrão Engolfo                           |
//| Projeto: EA Numeia - PatternModels                              |
//| Função: Detecta padrões de engolfo (bullish/bearish engulfing)  |
//+------------------------------------------------------------------+
#ifndef __ENGULFING_PATTERN_MQH__
#define __ENGULFING_PATTERN_MQH__

#include "PatternBase.mqh"

class EngulfingPattern : public IPatternModel {
private:
   string patternName;
   double confidence;

public:
   EngulfingPattern() {
      patternName = "Engulfing";
      confidence = 0.0;
   }

   bool Detect(string symbol, ENUM_TIMEFRAMES tf) override {
      // Implementação da detecção de engolfo
      confidence = 0.75;
      return true;
   }

   string GetName() override {
      return patternName;
   }

   double GetConfidence() override {
      return confidence;
   }

    bool CheckPattern() {
        int shift = 1;

        double open1 = iOpen(_Symbol, PERIOD_M15, shift + 1);
        double close1 = iClose(_Symbol, PERIOD_M15, shift + 1);
        double open2 = iOpen(_Symbol, PERIOD_M15, shift);
        double close2 = iClose(_Symbol, PERIOD_M15, shift);

        // Engulfing de alta
        if (close1 < open1 && close2 > open2 && close2 > open1 && open2 < close1)
            return true;

        // Engulfing de baixa
        if (close1 > open1 && close2 < open2 && close2 < open1 && open2 > close1)
            return true;

        return false;
    }
};

#endif // __ENGULFING_PATTERN_MQH__ 