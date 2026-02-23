#property copyright "Apollo11 Quantum Trading System"
#property version   "5.0"
#property strict

#include "BigPlayerTracker.mqh"
#include "GalacticOptimizer.mqh"

// Classe para gerenciamento de execução em massa
class CMassExecutionManager {
private:
    string symbols[];
    int symbolCount;
    int executionInterval;
    double minVolume;
    double maxSpread;
    
    CBigPlayerTracker* trackers[];
    CGalacticOptimizer* optimizer;
    
public:
    CMassExecutionManager(int interval = 100, double minVol = 0.5, double maxSprd = 5.0) {
        executionInterval = interval;
        minVolume = minVol;
        maxSpread = maxSprd;
        
        InitializeSymbols();
    }
    
    ~CMassExecutionManager() {
        for(int i = 0; i < symbolCount; i++) {
            if(trackers[i] != NULL) delete trackers[i];
        }
        if(optimizer != NULL) delete optimizer;
    }
    
    bool Initialize() {
        if(!InitializeTrackers()) return false;
        optimizer = new CGalacticOptimizer();
        
        if(!optimizer->Initialize()) return false;
        
        return true;
    }
    
    void Process() {
        if(TimeCurrent() % executionInterval != 0) return;
        
        for(int i = 0; i < symbolCount; i++) {
            ProcessSymbol(symbols[i], trackers[i]);
        }
    }
    
private:
    void InitializeSymbols() {
        int total = SymbolsTotal(true);
        symbolCount = 0;
        
        for(int i = 0; i < total; i++) {
            string symbol = SymbolName(i, true);
            if(StringFind(symbol, "USD") != -1 || 
               StringFind(symbol, "EUR") != -1 || 
               StringFind(symbol, "GBP") != -1 || 
               StringFind(symbol, "JPY") != -1) {
                ArrayResize(symbols, symbolCount + 1);
                symbols[symbolCount++] = symbol;
            }
        }
    }
    
    bool InitializeTrackers() {
        ArrayResize(trackers, symbolCount);
        
        for(int i = 0; i < symbolCount; i++) {
            trackers[i] = new CBigPlayerTracker();
            if(!trackers[i]->Initialize()) return false;
        }
        
        return true;
    }
    
    void ProcessSymbol(string symbol, CBigPlayerTracker* tracker) {
        if(!CheckSymbolConditions(symbol)) return;
        
        tracker->Process();
        
        if(tracker->IsBigPlayerDetected()) {
            MarketDNA dna = optimizer->GetBestDNA();
            ExecuteTrade(symbol, dna);
        }
    }
    
    bool CheckSymbolConditions(string symbol) {
        double volume = iVolume(symbol, PERIOD_CURRENT, 0);
        double avgVolume = iMA(symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
        
        if(volume / avgVolume < minVolume) return false;
        
        double spread = SymbolInfoDouble(symbol, SYMBOL_ASK) - 
                       SymbolInfoDouble(symbol, SYMBOL_BID);
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        
        if((spread / point) > maxSpread) return false;
        
        return true;
    }
    
    void ExecuteTrade(string symbol, MarketDNA &dna) {
        double atr = iATR(symbol, PERIOD_CURRENT, 14);
        double stopLoss = atr * dna.atrMultiplier;
        double takeProfit = stopLoss * 2.0;
        
        double volume = CalculatePositionSize(symbol, stopLoss, dna.riskPercent);
        
        if(volume > 0) {
            MqlTradeRequest request = {};
            MqlTradeResult result = {};
            
            request.action = TRADE_ACTION_DEAL;
            request.symbol = symbol;
            request.volume = volume;
            request.type = ORDER_TYPE_BUY;
            request.price = SymbolInfoDouble(symbol, SYMBOL_ASK);
            request.sl = request.price - stopLoss;
            request.tp = request.price + takeProfit;
            request.deviation = 10;
            request.magic = 123456;
            request.comment = "Apollo11";
            request.type_filling = ORDER_FILLING_FOK;
            
            if(!OrderSend(request, result)) {
                Print("Erro ao executar trade em ", symbol, ": ", GetLastError());
            }
        }
    }
    
    double CalculatePositionSize(string symbol, double stopLoss, double riskPercent) {
        double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        double riskAmount = accountBalance * (riskPercent / 100.0);
        double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        
        if(tickSize == 0 || tickValue == 0) return 0.0;
        
        double positionSize = riskAmount / (stopLoss * tickValue / tickSize);
        
        double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        
        return MathMax(minLot, MathMin(maxLot, positionSize));
    }
}; 