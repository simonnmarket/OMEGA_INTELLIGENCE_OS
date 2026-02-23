//+---------------------------------------------------------+
//| EngulfingPattern.mqh - Detecção de Engulfing            |
//+---------------------------------------------------------+
#pragma once
#include "PatternBase.mqh"

class EngulfingPattern : public IPatternModel {
public:
    string GetName() {
        return "Engulfing";
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
