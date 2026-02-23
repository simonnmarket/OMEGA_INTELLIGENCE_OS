//+------------------------------------------------------------------+
//|                                                RiskManager.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CRiskManager {
private:
    double maxRiskPercent;
    double maxDrawdown;
    int maxPositions;
    double accountBalance;
    double currentDrawdown;
    
public:
    CRiskManager() {
        maxRiskPercent = 1.0;
        maxDrawdown = 10.0;
        maxPositions = 5;
        accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        currentDrawdown = 0.0;
    }
    
    bool CanOpenPosition() {
        if(PositionsTotal() >= maxPositions) {
            Print("Limite de posições atingido: ", PositionsTotal());
            return false;
        }
            
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        currentDrawdown = (accountBalance - equity) / accountBalance * 100.0;
        
        if(currentDrawdown > maxDrawdown) {
            Print("Drawdown máximo excedido: ", currentDrawdown, "%");
            return false;
        }
            
        return true;
    }
    
    double GetPositionSize(double stopLoss, double initialLot, bool useAutoLotSize) {
        if(!useAutoLotSize) return initialLot;
            
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double riskAmount = equity * maxRiskPercent / 100.0;
        
        double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
        
        if(tickSize == 0 || tickValue == 0 || lotStep == 0) {
            Print("Erro nos parâmetros de símbolo para cálculo de lote: ", GetLastError());
            return initialLot;
        }
            
        double lotSize = riskAmount / (stopLoss * tickValue / tickSize);
        lotSize = MathFloor(lotSize / lotStep) * lotStep;
        
        double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
        
        return MathMax(MathMin(lotSize, maxLot), minLot);
    }
    
    void UpdateAccountBalance() {
        accountBalance = MathMax(accountBalance, AccountInfoDouble(ACCOUNT_BALANCE));
    }
    
    double GetCurrentDrawdown() {
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        currentDrawdown = (accountBalance - equity) / accountBalance * 100.0;
        return currentDrawdown;
    }
    
    void SetMaxRiskPercent(double risk) { maxRiskPercent = risk; }
    void SetMaxDrawdown(double drawdown) { maxDrawdown = drawdown; }
    void SetMaxPositions(int positions) { maxPositions = positions; }
}; 