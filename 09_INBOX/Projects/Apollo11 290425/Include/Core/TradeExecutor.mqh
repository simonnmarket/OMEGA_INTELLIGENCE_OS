//+------------------------------------------------------------------+
//|                                                TradeExecutor.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>

class CTradeExecutor {
private:
    CTrade trade;
    double maxRiskPercent;
    double maxDrawdown;
    int maxPositions;
    
public:
    CTradeExecutor() {
        maxRiskPercent = 1.0;
        maxDrawdown = 10.0;
        maxPositions = 5;
        trade.SetExpertMagicNumber(123456);
    }
    
    bool OpenLongPosition(double lotSize, double sl, double tp) {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double riskAmount = equity * maxRiskPercent / 100.0;
        double potentialLoss = lotSize * sl * SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE) / SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        
        if(potentialLoss > riskAmount * 2) {
            Print("Risco por trade excedido: PotentialLoss=", potentialLoss, ", MaxRisk=", riskAmount * 2);
            return false;
        }
        
        if(trade.Buy(lotSize, _Symbol, ask, ask - sl, ask + tp)) {
            Print("Posição comprada aberta - Volume: ", lotSize, " SL: ", DoubleToString(ask - sl, _Digits), " TP: ", DoubleToString(ask + tp, _Digits));
            return true;
        }
        Print("Erro ao abrir posição comprada: ", GetLastError());
        return false;
    }
    
    bool OpenShortPosition(double lotSize, double sl, double tp) {
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double riskAmount = equity * maxRiskPercent / 100.0;
        double potentialLoss = lotSize * sl * SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE) / SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        
        if(potentialLoss > riskAmount * 2) {
            Print("Risco por trade excedido: PotentialLoss=", potentialLoss, ", MaxRisk=", riskAmount * 2);
            return false;
        }
        
        if(trade.Sell(lotSize, _Symbol, bid, bid + sl, bid - tp)) {
            Print("Posição vendida aberta - Volume: ", lotSize, " SL: ", DoubleToString(bid + sl, _Digits), " TP: ", DoubleToString(bid - tp, _Digits));
            return true;
        }
        Print("Erro ao abrir posição vendida: ", GetLastError());
        return false;
    }
    
    void ClosePosition(ulong ticket) {
        if(ticket > 0) {
            trade.PositionClose(ticket);
            Print("Posição fechada: Ticket=", ticket);
        }
    }
    
    void SetMaxRiskPercent(double risk) { maxRiskPercent = risk; }
    void SetMaxDrawdown(double drawdown) { maxDrawdown = drawdown; }
    void SetMaxPositions(int positions) { maxPositions = positions; }
}; 