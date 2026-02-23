#pragma once
//+------------------------------------------------------------------+
//| TradeExecutorSkyIntel.mqh - Executor de Ordens via SKYINTEL     |
//| Projeto: Numeia EA - Integração Estratégica Inteligente          |
//| Função: Executar BUY/SELL com base em sinais estratégicos        |
//| gerados pelo CoreBrainManager (SKYINTEL)                         |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>
#include <Core/CoreBrainManager.mqh>
#include <Logs/AuditManager.mqh>

CTrade trade;

// Parâmetros de execução
input double RiskPerTrade = 0.01;
input double SL_Pips      = 20;
input double TP_Pips      = 40;
input int    MaxOpenSkyIntelTrades = 1;

namespace TradeExecutorSkyIntel
{
    // Executa a decisão estratégica recebida
    void ExecuteSkyIntelDecision(string symbol)
    {
        DECISION_ACTION action = CoreBrainManager::MakeStrategicDecision(symbol);

        // Verifica se já existe ordem aberta para evitar duplicação
        if (PositionsTotalBySymbol(symbol) >= MaxOpenSkyIntelTrades)
        {
            AuditLog("TradeExecutorSkyIntel", symbol, "⚠️ Ordem não executada - limite de posições já atingido.");
            return;
        }

        double lot = CalculateLotSize(symbol, RiskPerTrade);
        double price = SymbolInfoDouble(symbol, SYMBOL_ASK);
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        double sl = 0, tp = 0;

        if (action == ACTION_BUY)
        {
            sl = price - SL_Pips * point;
            tp = price + TP_Pips * point;
            if (trade.Buy(lot, symbol, price, sl, tp))
                AuditLog("TradeExecutorSkyIntel", symbol, "✅ Ordem BUY executada com sucesso.");
        }
        else if (action == ACTION_SELL)
        {
            price = SymbolInfoDouble(symbol, SYMBOL_BID);
            sl = price + SL_Pips * point;
            tp = price - TP_Pips * point;
            if (trade.Sell(lot, symbol, price, sl, tp))
                AuditLog("TradeExecutorSkyIntel", symbol, "✅ Ordem SELL executada com sucesso.");
        }
        else
        {
            AuditLog("TradeExecutorSkyIntel", symbol, "🔍 Nenhuma ordem executada - decisão foi AVOID ou NONE.");
        }
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
}
