
//+------------------------------------------------------------------+
//| HydraManager.mqh                                                 |
//| Módulo: ExecutionLogic                                           |
//| Sistema de execução adaptativa com múltiplas ordens             |
//+------------------------------------------------------------------+
#property strict

class HydraManager {
public:
    // Envia múltiplas ordens com trailing stops baseados no ATR
    static void ExecuteHydra(string symbol, double entry_price, int magic = 1001) {
        double atr = iATR(symbol, PERIOD_M5, 14);
        if (atr <= 0.0) {
            Print("ATR inválido para ", symbol);
            return;
        }

        for (int i = 0; i < 3; i++) {
            double lots = CalculateHydraLot(i);
            double sl = entry_price - (i == 0 ? 1.5 * atr : 0.8 * atr);
            double tp = entry_price + (i == 0 ? 2.5 * atr : 1.2 * atr);

            MqlTradeRequest request;
            MqlTradeResult result;
            ZeroMemory(request);
            ZeroMemory(result);

            request.action   = TRADE_ACTION_DEAL;
            request.symbol   = symbol;
            request.volume   = lots;
            request.price    = entry_price;
            request.sl       = sl;
            request.tp       = tp;
            request.magic    = magic + i;
            request.type     = ORDER_TYPE_BUY;
            request.type_filling = ORDER_FILLING_IOC;
            request.deviation = 10;

            if (!OrderSend(request, result) || result.retcode != TRADE_RETCODE_DONE) {
                Print("❌ HydraOrder[", i+1, "] erro: ", result.retcode);
            } else {
                Print("✅ HydraOrder[", i+1, "] enviada. Lote: ", lots, " SL: ", sl, " TP: ", tp);
            }
        }
    }

    static double CalculateHydraLot(int level) {
        switch(level) {
            case 0: return 0.10;
            case 1: return 0.20;
            case 2: return 0.30;
            default: return 0.10;
        }
    }
};
