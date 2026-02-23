
//+------------------------------------------------------------------+
//| EntropyTrailingStop.mqh - Trailing Stop por Entropia            |
//| Adapta trailing à estrutura de dispersão do mercado              |
//+------------------------------------------------------------------+
#property strict

class EntropyTrailingStop {
private:
    int windowSize;
    double entropyThreshold;  // quanto menor, mais tendência

public:
    EntropyTrailingStop(int window = 20, double threshold = 0.5) {
        windowSize = window;
        entropyThreshold = threshold;
    }

    // Calcula a entropia do retorno normalizado
    double CalculateEntropy(const double &returns[]) {
        int n = ArraySize(returns);
        if (n <= 1) return 1.0;

        double bins[10] = {0};
        int binCount = 10;

        double minVal = ArrayMinimum(returns, 0, n);
        double maxVal = ArrayMaximum(returns, 0, n);
        if (maxVal - minVal == 0) return 0;

        double binWidth = (maxVal - minVal) / binCount;

        for (int i = 0; i < n; i++) {
            int binIndex = int((returns[i] - minVal) / binWidth);
            if (binIndex >= binCount) binIndex = binCount - 1;
            bins[binIndex]++;
        }

        double entropy = 0.0;
        for (int i = 0; i < binCount; i++) {
            if (bins[i] > 0) {
                double p = bins[i] / n;
                entropy -= p * MathLog(p) / MathLog(2);
            }
        }

        return entropy;
    }

    // Decide se trailing deve ser ativado
    bool ShouldApplyTrailing(const string symbol, const ENUM_TIMEFRAMES tf = PERIOD_M5) {
        double close[];
        if (CopyClose(symbol, tf, 0, windowSize, close) <= 0) return false;

        double returns[];
        ArrayResize(returns, windowSize - 1);

        for (int i = 1; i < windowSize; i++)
            returns[i - 1] = close[i] - close[i - 1];

        double entropy = CalculateEntropy(returns);
        Print("📉 Entropia calculada: ", entropy);

        return (entropy < entropyThreshold);
    }
};
