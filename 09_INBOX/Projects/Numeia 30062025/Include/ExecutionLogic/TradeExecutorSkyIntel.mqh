//+------------------------------------------------------------------+
//| TradeExecutorSkyIntel.mqh - Executor de Sinais SkyIntel          |
//| Projeto: EA Numeia - ExecutionLogic                              |
//| Função: Executa ordens baseadas em sinais estratégicos do        |
//| SkyIntel com validação de risco e compliance                     |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>
#include "../../Utils/Log.mqh"
#include "../../Core/types.mqh"

// Parâmetros de execução
input double RiskPerTrade = 0.01;
input double SL_Pips      = 20;
input double TP_Pips      = 40;
input int    MaxOpenSkyIntelTrades = 1;

class TradeExecutorSkyIntel
{
private:
    CTrade trade;
    bool initialized;

public:
    void Initialize()
    {
        initialized = true;
        AuditLog("TradeExecutorSkyIntel", "SYSTEM", "✅ Executor SkyIntel inicializado.");
    }

    // Executa ordem baseada em sinal SkyIntel
    bool ExecuteSkyIntelSignal(string symbol, ENUM_SIGNAL_TYPE signal)
    {
        if (!initialized)
            Initialize();

        if (PositionsTotal() >= 5) // Limite de posições
        {
            AuditLog("TradeExecutorSkyIntel", symbol, "⚠️ Ordem não executada - limite de posições já atingido.");
            return false;
        }

        double volume = 0.1; // Volume padrão
        double price = 0.0;

        if (signal == SIGNAL_SPIKE_LONG)
        {
            price = SymbolInfoDouble(symbol, SYMBOL_ASK);
            if (trade.Buy(volume, symbol, price, 0, 0, "SKYINTEL_LONG"))
            {
                AuditLog("TradeExecutorSkyIntel", symbol, "✅ Ordem BUY executada com sucesso.");
                return true;
            }
        }
        else if (signal == SIGNAL_SPIKE_SHORT)
        {
            price = SymbolInfoDouble(symbol, SYMBOL_BID);
            if (trade.Sell(volume, symbol, price, 0, 0, "SKYINTEL_SHORT"))
            {
                AuditLog("TradeExecutorSkyIntel", symbol, "✅ Ordem SELL executada com sucesso.");
                return true;
            }
        }
        else
        {
            AuditLog("TradeExecutorSkyIntel", symbol, "🔍 Nenhuma ordem executada - sinal não executável.");
        }

        return false;
    }

    // Cálculo de tamanho de lote baseado em risco
    double CalculateLotSize(string symbol, double riskPercent)
    {
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        double stopDistance = SL_Pips * point;

        if (stopDistance == 0.0 || tickValue == 0.0)
            return 0.01;

        double valuePerPoint = tickValue / point;
        double riskAmount = balance * riskPercent;
        double lot = NormalizeDouble(riskAmount / (stopDistance * valuePerPoint), 2);
        return MathMax(lot, 0.01);
    }

    // Contador de posições abertas no símbolo
    int PositionsTotalBySymbol(string symbol)
    {
        int count = 0;
        for (int i = 0; i < PositionsTotal(); i++)
        {
            if (PositionGetSymbol(i) == symbol)
                count++;
        }
        return count;
    }
}; 