#property copyright "Position Management System"
#property strict

class CPositionManager {
private:
    // Configurações
    double stopLossPips;
    double takeProfitPips;
    double trailingStopPips;
    double breakEvenPips;
    
    // Métricas
    double entryPrice;
    double currentStopLoss;
    double currentTakeProfit;
    bool isTrailingStopActive;
    bool isBreakEvenActive;
    
public:
    CPositionManager(double slPips = 50.0, double tpPips = 100.0,
                    double trailPips = 30.0, double bePips = 20.0) {
        stopLossPips = slPips;
        takeProfitPips = tpPips;
        trailingStopPips = trailPips;
        breakEvenPips = bePips;
        
        Reset();
    }
    
    void Reset() {
        entryPrice = 0.0;
        currentStopLoss = 0.0;
        currentTakeProfit = 0.0;
        isTrailingStopActive = false;
        isBreakEvenActive = false;
    }
    
    bool OpenPosition(ENUM_POSITION_TYPE posType, double lotSize) {
        if(!IsTradeAllowed()) {
            Print("Trading não está permitido");
            return false;
        }
        
        double price = (posType == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) :
                                                       SymbolInfoDouble(_Symbol, SYMBOL_BID);
        
        double sl = CalculateStopLoss(posType, price);
        double tp = CalculateTakeProfit(posType, price);
        
        MqlTradeRequest request = {};
        request.action = TRADE_ACTION_DEAL;
        request.symbol = _Symbol;
        request.volume = lotSize;
        request.type = (posType == POSITION_TYPE_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        request.price = price;
        request.sl = sl;
        request.tp = tp;
        request.deviation = 10;
        request.magic = 123456;
        request.comment = "Position Manager";
        request.type_filling = ORDER_FILLING_FOK;
        
        MqlTradeResult result = {};
        if(!OrderSend(request, result)) {
            Print("Erro ao abrir posição: ", GetLastError());
            return false;
        }
        
        entryPrice = price;
        currentStopLoss = sl;
        currentTakeProfit = tp;
        
        Print("Posição aberta com sucesso:",
              "\nTipo: ", EnumToString(posType),
              "\nPreço: ", price,
              "\nStop Loss: ", sl,
              "\nTake Profit: ", tp);
        
        return true;
    }
    
    void ManagePosition() {
        if(!PositionSelect(_Symbol)) return;
        
        double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
        double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        double currentSL = PositionGetDouble(POSITION_SL);
        ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
        
        // Verifica break even
        if(!isBreakEvenActive) {
            double profitPips = (posType == POSITION_TYPE_BUY) ? 
                               (currentPrice - openPrice) / _Point :
                               (openPrice - currentPrice) / _Point;
            
            if(profitPips >= breakEvenPips) {
                MoveToBreakEven(posType);
                isBreakEvenActive = true;
            }
        }
        
        // Verifica trailing stop
        if(!isTrailingStopActive && isBreakEvenActive) {
            double profitPips = (posType == POSITION_TYPE_BUY) ? 
                               (currentPrice - openPrice) / _Point :
                               (openPrice - currentPrice) / _Point;
            
            if(profitPips >= trailingStopPips) {
                UpdateTrailingStop(posType, currentPrice);
                isTrailingStopActive = true;
            }
        }
        else if(isTrailingStopActive) {
            UpdateTrailingStop(posType, currentPrice);
        }
    }
    
    double CalculateStopLoss(ENUM_POSITION_TYPE posType, double price) {
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
        
        if(posType == POSITION_TYPE_BUY) {
            return price - (stopLossPips * point) - stopLevel;
        }
        else {
            return price + (stopLossPips * point) + stopLevel;
        }
    }
    
    double CalculateTakeProfit(ENUM_POSITION_TYPE posType, double price) {
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
        
        if(posType == POSITION_TYPE_BUY) {
            return price + (takeProfitPips * point) + stopLevel;
        }
        else {
            return price - (takeProfitPips * point) - stopLevel;
        }
    }
    
    void MoveToBreakEven(ENUM_POSITION_TYPE posType) {
        if(!PositionSelect(_Symbol)) return;
        
        double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
        
        double newSL = (posType == POSITION_TYPE_BUY) ? 
                      openPrice + stopLevel : 
                      openPrice - stopLevel;
        
        MqlTradeRequest request = {};
        request.action = TRADE_ACTION_SLTP;
        request.symbol = _Symbol;
        request.sl = newSL;
        request.tp = PositionGetDouble(POSITION_TP);
        request.position = PositionGetInteger(POSITION_TICKET);
        
        MqlTradeResult result = {};
        if(!OrderSend(request, result)) {
            Print("Erro ao mover para break even: ", GetLastError());
            return;
        }
        
        currentStopLoss = newSL;
        Print("Stop Loss movido para break even: ", newSL);
    }
    
    void UpdateTrailingStop(ENUM_POSITION_TYPE posType, double currentPrice) {
        if(!PositionSelect(_Symbol)) return;
        
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
        
        double newSL = (posType == POSITION_TYPE_BUY) ? 
                      currentPrice - (trailingStopPips * point) - stopLevel :
                      currentPrice + (trailingStopPips * point) + stopLevel;
        
        // Verifica se o novo stop loss é melhor que o atual
        if((posType == POSITION_TYPE_BUY && newSL > currentStopLoss) ||
           (posType == POSITION_TYPE_SELL && (currentStopLoss == 0 || newSL < currentStopLoss))) {
            
            MqlTradeRequest request = {};
            request.action = TRADE_ACTION_SLTP;
            request.symbol = _Symbol;
            request.sl = newSL;
            request.tp = PositionGetDouble(POSITION_TP);
            request.position = PositionGetInteger(POSITION_TICKET);
            
            MqlTradeResult result = {};
            if(!OrderSend(request, result)) {
                Print("Erro ao atualizar trailing stop: ", GetLastError());
                return;
            }
            
            currentStopLoss = newSL;
            Print("Trailing stop atualizado: ", newSL);
        }
    }
    
    bool IsTradeAllowed() {
        return TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) &&
               SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE) == SYMBOL_TRADE_MODE_FULL;
    }
}; 