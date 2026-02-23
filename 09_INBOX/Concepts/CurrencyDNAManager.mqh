
//+------------------------------------------------------------------+
//| CurrencyDNAManager.mqh                                           |
//| Módulo: Analysis                                                 |
//| Clusterização institucional com função externa                   |
//+------------------------------------------------------------------+
#property strict

class CurrencyDNAManager {
private:
    string clusters[10];
    string labels[10];

public:
    void StoreLabel(int index, string symbol, string label) {
        if (index < 10) {
            clusters[index] = symbol;
            labels[index] = label;
        }
    }

    string GetLabel(string symbol) {
        for (int i = 0; i < ArraySize(clusters); i++) {
            if (clusters[i] == symbol)
                return labels[i];
        }
        return "UNKNOWN";
    }
};

// Função externa para processar a matriz
bool ClassifyCurrencyData(string &symbols[], double &volMatrix[][3], double &macroMatrix[][3], int rows, CurrencyDNAManager &manager) {
    for (int i = 0; i < rows; i++) {
        string label;
        double vol_sum = 0, macro_sum = 0;
        for (int j = 0; j < 3; j++) {
            vol_sum += volMatrix[i][j];
            macro_sum += macroMatrix[i][j];
        }

        if (vol_sum > 1.5 && macro_sum < 0.5)
            label = "CommodityFX";
        else if (macro_sum > 2.0)
            label = "DollarSensitive";
        else
            label = "SafeHaven";

        manager.StoreLabel(i, symbols[i], label);
        Print("[DNA] ", symbols[i], " → ", label, " | Vol=", DoubleToString(vol_sum, 2), ", Macro=", DoubleToString(macro_sum, 2));
    }

    return true;
}
