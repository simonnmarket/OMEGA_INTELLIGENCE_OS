
//+------------------------------------------------------------------+
//| CognitiveBiasAnalyzer.mqh                                        |
//| Detecta e classifica vieses cognitivos no comportamento do mercado |
//+------------------------------------------------------------------+
#pragma once

class CognitiveBiasAnalyzer {
public:
    bool DetectAnchoringBias(double recentHigh, double recentLow, double currentPrice);
    bool DetectOverconfidence(double volume, double avgVolume);
    bool DetectHerdBehavior(double sentimentScore, double volatility);

    void LogBiasDetection(string biasName);
};
