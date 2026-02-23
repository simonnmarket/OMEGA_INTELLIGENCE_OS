
//+------------------------------------------------------------------+
//| BiasToAlphaConverter.mqh                                         |
//| Converte padrões irracionais em edge financeiro (alpha)         |
//+------------------------------------------------------------------+
#pragma once

class BiasToAlphaConverter {
public:
    double ConvertAnchoringToAlpha(double anchor, double price);
    double ConvertOverconfidenceToReversal(double volatilitySpike);
    double GetAlphaFromCognitivePattern(string pattern);
};
