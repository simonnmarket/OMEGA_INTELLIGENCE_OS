#property copyright "Sistema de Trading Quântico"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

//+------------------------------------------------------------------+
//| Enumeração para modos de cálculo de lote                         |
//+------------------------------------------------------------------+
enum MarginMode {
    FREEMARGIN = 0,     // MM baseado em margem livre
    BALANCE,            // MM baseado em saldo
    LOSSFREEMARGIN,     // MM baseado em perdas da margem livre
    LOSSBALANCE,        // MM baseado em perdas do saldo
    LOT                 // Lote fixo
};

//+------------------------------------------------------------------+
//| Classe para detecção de nova barra                                |
//+------------------------------------------------------------------+
class CIsNewBar {
private:
    datetime m_lastBarTime;
    
public:
    CIsNewBar() { m_lastBarTime = -1; }
    
    bool IsNewBar(string symbol, ENUM_TIMEFRAMES timeframe) {
        datetime currentBarTime = (datetime)SeriesInfoInteger(symbol, timeframe, SERIES_LASTBAR_DATE);
        
        if(currentBarTime != m_lastBarTime && currentBarTime) {
            m_lastBarTime = currentBarTime;
            return true;
        }
        return false;
    }
};

//+------------------------------------------------------------------+
//| Funções de gerenciamento de posições                             |
//+------------------------------------------------------------------+
bool BuyPositionOpen(bool &signal, string symbol, datetime timeLevel, 
                    double moneyManagement, int marginMode, uint deviation,
                    int stopLoss, int takeProfit) {
    if(!signal) return true;
    
    // Verifica tempo e posição existente
    if(!TradeTimeLevelCheck(symbol, POSITION_TYPE_BUY, timeLevel)) return true;
    if(PositionSelect(symbol)) return true;
    
    // Calcula volume
    double volume = BuyLotCount(symbol, moneyManagement, marginMode, stopLoss, deviation);
    if(volume <= 0) {
        Print(__FUNCTION__, "(): Volume inválido");
        return false;
    }
    
    // Prepara requisição
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    MqlTradeCheckResult check = {};
    
    // Obtém dados do símbolo
    long digit;
    double point, ask;
    if(!SymbolInfoInteger(symbol, SYMBOL_DIGITS, digit)) return true;
    if(!SymbolInfoDouble(symbol, SYMBOL_POINT, point)) return true;
    if(!SymbolInfoDouble(symbol, SYMBOL_ASK, ask)) return true;
    
    // Configura requisição
    request.type = ORDER_TYPE_BUY;
    request.price = ask;
    request.action = TRADE_ACTION_DEAL;
    request.symbol = symbol;
    request.volume = volume;
    
    // Define stop loss e take profit
    if(stopLoss) {
        if(!StopCorrect(symbol, stopLoss)) return false;
        double slDistance = stopLoss * point;
        request.sl = NormalizeDouble(request.price - slDistance, (int)digit);
    }
    
    if(takeProfit) {
        if(!StopCorrect(symbol, takeProfit)) return false;
        double tpDistance = takeProfit * point;
        request.tp = NormalizeDouble(request.price + tpDistance, (int)digit);
    }
    
    request.deviation = deviation;
    
    // Verifica requisição
    if(!OrderCheck(request, check)) {
        Print(__FUNCTION__, "(): Requisição inválida");
        Print(__FUNCTION__, "(): OrderCheck(): ", ResultRetcodeDescription(check.retcode));
        return false;
    }
    
    // Executa ordem
    if(!OrderSend(request, result) || result.retcode != TRADE_RETCODE_DONE) {
        Print(__FUNCTION__, "(): Falha ao executar ordem");
        Print(__FUNCTION__, "(): OrderSend(): ", ResultRetcodeDescription(result.retcode));
        return false;
    }
    
    // Atualiza estado
    TradeTimeLevelSet(symbol, POSITION_TYPE_BUY, timeLevel);
    signal = false;
    PlaySound("ok.wav");
    
    return true;
}

//+------------------------------------------------------------------+
//| Funções auxiliares                                                |
//+------------------------------------------------------------------+
bool StopCorrect(string symbol, int &stop) {
    long minStop;
    if(!SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL, minStop)) return false;
    if(stop < minStop) stop = (int)minStop;
    return true;
}

string ResultRetcodeDescription(int retcode) {
    switch(retcode) {
        case TRADE_RETCODE_REQUOTE: return "Requote";
        case TRADE_RETCODE_REJECT: return "Rejeitado";
        case TRADE_RETCODE_CANCEL: return "Cancelado";
        case TRADE_RETCODE_PLACED: return "Colocado";
        case TRADE_RETCODE_DONE: return "Executado";
        case TRADE_RETCODE_DONE_PARTIAL: return "Executado parcialmente";
        case TRADE_RETCODE_ERROR: return "Erro";
        case TRADE_RETCODE_TIMEOUT: return "Timeout";
        case TRADE_RETCODE_INVALID: return "Inválido";
        case TRADE_RETCODE_INVALID_VOLUME: return "Volume inválido";
        case TRADE_RETCODE_INVALID_PRICE: return "Preço inválido";
        case TRADE_RETCODE_INVALID_STOPS: return "Stops inválidos";
        case TRADE_RETCODE_TRADE_DISABLED: return "Trading desabilitado";
        case TRADE_RETCODE_MARKET_CLOSED: return "Mercado fechado";
        case TRADE_RETCODE_NO_MONEY: return "Sem dinheiro suficiente";
        case TRADE_RETCODE_PRICE_CHANGED: return "Preço alterado";
        case TRADE_RETCODE_PRICE_OFF: return "Sem cotações";
        case TRADE_RETCODE_INVALID_EXPIRATION: return "Expiração inválida";
        case TRADE_RETCODE_ORDER_CHANGED: return "Ordem alterada";
        case TRADE_RETCODE_TOO_MANY_REQUESTS: return "Muitas requisições";
        case TRADE_RETCODE_NO_CHANGES: return "Sem alterações";
        case TRADE_RETCODE_SERVER_DISABLES_AT: return "Trading desabilitado pelo servidor";
        case TRADE_RETCODE_CLIENT_DISABLES_AT: return "Trading desabilitado pelo cliente";
        case TRADE_RETCODE_LOCKED: return "Bloqueado";
        case TRADE_RETCODE_FROZEN: return "Congelado";
        case TRADE_RETCODE_INVALID_FILL: return "Preenchimento inválido";
        case TRADE_RETCODE_CONNECTION: return "Sem conexão";
        case TRADE_RETCODE_ONLY_REAL: return "Apenas contas reais";
        case TRADE_RETCODE_LIMIT_ORDERS: return "Limite de ordens atingido";
        case TRADE_RETCODE_LIMIT_VOLUME: return "Limite de volume atingido";
        case TRADE_RETCODE_INVALID_ORDER: return "Ordem inválida";
        case TRADE_RETCODE_POSITION_CLOSED: return "Posição fechada";
        case TRADE_RETCODE_INVALID_CLOSE_VOLUME: return "Volume de fechamento inválido";
        case TRADE_RETCODE_CLOSE_ORDER_EXIST: return "Ordem de fechamento existente";
        case TRADE_RETCODE_LIMIT_POSITIONS: return "Limite de posições atingido";
        default: return "Resultado desconhecido";
    }
}

//+------------------------------------------------------------------+
//| Funções de gerenciamento de tempo                                |
//+------------------------------------------------------------------+
string GetTimeLevelName(string symbol, ENUM_POSITION_TYPE type) {
    string name;
    if(MQL5InfoInteger(MQL5_TESTING) || MQL5InfoInteger(MQL5_OPTIMIZATION) || MQL5InfoInteger(MQL5_DEBUGGING))
        StringConcatenate(name, "TimeLevel_", AccountInfoInteger(ACCOUNT_LOGIN), "_", symbol, "_", type, "_Test_");
    else
        StringConcatenate(name, "TimeLevel_", AccountInfoInteger(ACCOUNT_LOGIN), "_", symbol, "_", type);
    return name;
}

bool TradeTimeLevelCheck(string symbol, ENUM_POSITION_TYPE type, datetime timeLevel) {
    if(timeLevel > 0) {
        if(TimeCurrent() < GlobalVariableGet(GetTimeLevelName(symbol, type))) return false;
    }
    return true;
}

void TradeTimeLevelSet(string symbol, ENUM_POSITION_TYPE type, datetime timeLevel) {
    GlobalVariableSet(GetTimeLevelName(symbol, type), timeLevel);
}

datetime TradeTimeLevelGet(string symbol, ENUM_POSITION_TYPE type) {
    return (datetime)GlobalVariableGet(GetTimeLevelName(symbol, type));
}

void TimeLevelGlobalVariableDel(string symbol, ENUM_POSITION_TYPE type) {
    if(MQL5InfoInteger(MQL5_TESTING) || MQL5InfoInteger(MQL5_OPTIMIZATION) || MQL5InfoInteger(MQL5_DEBUGGING))
        GlobalVariableDel(GetTimeLevelName(symbol, type));
}

void GlobalVariableDel_(string symbol) {
    TimeLevelGlobalVariableDel(symbol, POSITION_TYPE_BUY);
    TimeLevelGlobalVariableDel(symbol, POSITION_TYPE_SELL);
} 