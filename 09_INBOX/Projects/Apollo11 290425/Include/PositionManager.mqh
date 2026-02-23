#property copyright "Apollo11 Quantum Trading System"
#property version   "5.0"
#property strict

// Classe para gerenciar posições
class CPositionManager {
private:
    double trailingStop;
    double breakEvenLevel;
    double maxSpread;
    double minProfit;
    double maxLoss;
    int maxPositions;
    int currentPositions;
    
    int atrHandle;
    int maHandle;
    
public:
    CPositionManager(double trailStop = 0.5, double breakEven = 0.3, 
                    double maxSprd = 5.0, double minProf = 0.2, 
                    double maxLss = 2.0, int maxPos = 3) {
        trailingStop = trailStop;
        breakEvenLevel = breakEven;
        maxSpread = maxSprd;
        minProfit = minProf;
        maxLoss = maxLss;
        maxPositions = maxPos;
        currentPositions = 0;
        
        atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
    }
    
    ~CPositionManager() {
        if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
        if(maHandle != INVALID_HANDLE) IndicatorRelease(maHandle);
    }
    
    bool Initialize() {
        if(atrHandle == INVALID_HANDLE || maHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores em CPositionManager");
            return false;
        }
        return true;
    }
    
    void Process() {
        currentPositions = PositionsTotal();
        ManageOpenPositions();
    }
    
    void ManageOpenPositions() {
        for(int i = 0; i < currentPositions; i++) {
            ulong ticket = PositionGetTicket(i);
            if(ticket > 0) {
                if(PositionSelectByTicket(ticket)) {
                    double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
                    double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
                    double profit = PositionGetDouble(POSITION_PROFIT);
                    double volume = PositionGetDouble(POSITION_VOLUME);
                    ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
                    
                    double atr = iATR(_Symbol, PERIOD_CURRENT, 14);
                    double stopLoss = PositionGetDouble(POSITION_SL);
                    double takeProfit = PositionGetDouble(POSITION_TP);
                    
                    // Ajustar trailing stop
                    if(profit > 0) {
                        double newStopLoss = 0.0;
                        if(type == POSITION_TYPE_BUY) {
                            newStopLoss = currentPrice - (atr * trailingStop);
                            if(newStopLoss > stopLoss) {
                                ModifyPosition(ticket, newStopLoss, takeProfit);
                            }
                        }
                        else {
                            newStopLoss = currentPrice + (atr * trailingStop);
                            if(newStopLoss < stopLoss || stopLoss == 0) {
                                ModifyPosition(ticket, newStopLoss, takeProfit);
                            }
                        }
                    }
                    
                    // Ajustar break even
                    if(profit >= (openPrice * breakEvenLevel)) {
                        if(type == POSITION_TYPE_BUY) {
                            if(stopLoss < openPrice) {
                                ModifyPosition(ticket, openPrice, takeProfit);
                            }
                        }
                        else {
                            if(stopLoss > openPrice || stopLoss == 0) {
                                ModifyPosition(ticket, openPrice, takeProfit);
                            }
                        }
                    }
                    
                    // Verificar stop loss máximo
                    if(profit <= -(maxLoss * volume)) {
                        ClosePosition(ticket);
                    }
                }
            }
        }
    }
    
    bool OpenPosition(ENUM_POSITION_TYPE type, double volume, double stopLoss, double takeProfit) {
        if(currentPositions >= maxPositions) {
            Print("Número máximo de posições excedido");
            return false;
        }
        
        double spread = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - 
                       SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        
        if((spread / point) > maxSpread) {
            Print("Spread muito alto: ", spread / point);
            return false;
        }
        
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.symbol = _Symbol;
        request.volume = volume;
        request.type = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        request.price = (type == POSITION_TYPE_BUY) ? 
                       SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                       SymbolInfoDouble(_Symbol, SYMBOL_BID);
        request.sl = stopLoss;
        request.tp = takeProfit;
        request.deviation = 10;
        request.magic = 123456;
        request.comment = "Apollo11";
        request.type_filling = ORDER_FILLING_FOK;
        
        if(!OrderSend(request, result)) {
            Print("Erro ao abrir posição: ", GetLastError());
            return false;
        }
        
        return true;
    }
    
    bool ModifyPosition(ulong ticket, double stopLoss, double takeProfit) {
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_SLTP;
        request.position = ticket;
        request.symbol = _Symbol;
        request.sl = stopLoss;
        request.tp = takeProfit;
        
        if(!OrderSend(request, result)) {
            Print("Erro ao modificar posição: ", GetLastError());
            return false;
        }
        
        return true;
    }
    
    bool ClosePosition(ulong ticket) {
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.position = ticket;
        request.symbol = _Symbol;
        request.volume = PositionGetDouble(POSITION_VOLUME);
        request.type = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 
                      ORDER_TYPE_SELL : ORDER_TYPE_BUY;
        request.price = (request.type == ORDER_TYPE_SELL) ? 
                       SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                       SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        request.deviation = 10;
        request.magic = 123456;
        request.comment = "Apollo11";
        request.type_filling = ORDER_FILLING_FOK;
        
        if(!OrderSend(request, result)) {
            Print("Erro ao fechar posição: ", GetLastError());
            return false;
        }
        
        return true;
    }
    
    int GetCurrentPositions() { return currentPositions; }
    void SetMaxPositions(int maxPos) { maxPositions = maxPos; }
    void SetTrailingStop(double trailStop) { trailingStop = trailStop; }
    void SetBreakEven(double breakEven) { breakEvenLevel = breakEven; }
}; 