
//+------------------------------------------------------------------+
//| AsymmetricCorrelationDetector.mqh                                |
//| Módulo: Analysis                                                  |
//| Detecta defasagem entre pares correlacionados                    |
//+------------------------------------------------------------------+
#property strict

class AsymmetricCorrelationDetector {
public:
    // Retorna o lag normalizado entre dois pares com base na diferença de fechamento
    // e o ATR para dimensionamento
    static double DetectLag(string pair1, string pair2, int bars=50) {
        double price1 = iClose(pair1, PERIOD_CURRENT, 0);
        double price2 = iClose(pair2, PERIOD_CURRENT, 0);
        double atr = iATR(pair1, PERIOD_CURRENT, 14);

        if (atr == 0.0)
            return 0.0;

        double lag = (price1 - price2) / atr;
        Print("[LagDetect] ", pair1, " vs ", pair2, " → Lag: ", DoubleToString(lag, 3));
        return lag;
    }
};
