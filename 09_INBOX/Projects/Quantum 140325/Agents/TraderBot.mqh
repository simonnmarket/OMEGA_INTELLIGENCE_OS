#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Trading/AdvancedTradingSystem.mqh"

// Estrutura para parâmetros de risco
struct RiskParameters {
    double maxDrawdown;      // Máximo drawdown permitido (2%)
    double profitTarget;     // Alvo de lucro (3%)
    double correlationLimit; // Limite de correlação (0.7)
    double marginBuffer;     // Buffer de margem (20%)
    int    maxPositions;     // Máximo de posições simultâneas
};

// Estrutura para ordem dinâmica
struct DynamicOrder {
    string          symbol;
    ENUM_ORDER_TYPE type;
    double          volume;
    double          price;
    double          stopLoss;
    double          takeProfit;
    double          trailingStop;
    datetime        expiration;
    string          comment;
};

//+------------------------------------------------------------------+
//| Classe TraderBot                                                   |
//+------------------------------------------------------------------+
class CTraderBot {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    RiskParameters  m_risk;
    
    // Estado do bot
    bool            m_isActive;
    double          m_dailyPnL;
    int             m_totalTrades;
    
    // Cache de ordens
    DynamicOrder    m_pendingOrders[];
    
    // Métodos privados
    bool            ValidateOrder(const DynamicOrder &order);
    bool            CheckMargin(const DynamicOrder &order);
    bool            UpdateStops(const DynamicOrder &order);
    double          CalculatePositionSize(string symbol, double riskAmount);
    
public:
                    CTraderBot();
                   ~CTraderBot();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            Start();
    void            Stop();
    
    // Métodos de execução
    bool            ExecuteMarketOrder(string symbol, ENUM_ORDER_TYPE type, double volume);
    bool            ExecuteLimitOrder(const DynamicOrder &order);
    bool            ExecuteStopOrder(const DynamicOrder &order);
    bool            ModifyOrder(ulong ticket, double price, double sl, double tp);
    bool            CancelOrder(ulong ticket);
    
    // Métodos de gestão de risco
    bool            ValidateRisk(string symbol, double volume);
    void            UpdateTrailingStops();
    void            CheckDrawdown();
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    double          GetDailyPnL() const { return m_dailyPnL; }
    int             GetTotalTrades() const { return m_totalTrades; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CTraderBot::CTraderBot() {
    m_core = NULL;
    m_isActive = false;
    m_dailyPnL = 0;
    m_totalTrades = 0;
    
    // Configura parâmetros de risco padrão
    m_risk.maxDrawdown = 2.0;      // 2%
    m_risk.profitTarget = 3.0;     // 3%
    m_risk.correlationLimit = 0.7;  // 70%
    m_risk.marginBuffer = 20.0;     // 20%
    m_risk.maxPositions = 5;        // 5 posições simultâneas
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CTraderBot::~CTraderBot() {
    Stop();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CTraderBot::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicia o bot                                                       |
//+------------------------------------------------------------------+
bool CTraderBot::Start() {
    if(m_isActive) return true;
    
    if(!m_core || !m_core.GetTradingSystem().IsConnected()) {
        Print("Trading system not connected");
        return false;
    }
    
    m_isActive = true;
    return true;
}

//+------------------------------------------------------------------+
//| Para o bot                                                         |
//+------------------------------------------------------------------+
void CTraderBot::Stop() {
    if(!m_isActive) return;
    
    // Cancela ordens pendentes
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS)) {
            CancelOrder(OrderTicket());
        }
    }
    
    m_isActive = false;
}

//+------------------------------------------------------------------+
//| Executa ordem a mercado                                           |
//+------------------------------------------------------------------+
bool CTraderBot::ExecuteMarketOrder(string symbol, ENUM_ORDER_TYPE type, double volume) {
    if(!m_isActive || !m_core) return false;
    
    // Valida risco
    if(!ValidateRisk(symbol, volume)) {
        Print("Risk validation failed for ", symbol);
        return false;
    }
    
    // Executa ordem
    if(!m_core.GetTradingSystem().ExecuteOrder(type, volume)) {
        Print("Failed to execute market order for ", symbol);
        return false;
    }
    
    m_totalTrades++;
    return true;
}

//+------------------------------------------------------------------+
//| Executa ordem limite                                              |
//+------------------------------------------------------------------+
bool CTraderBot::ExecuteLimitOrder(const DynamicOrder &order) {
    if(!m_isActive || !ValidateOrder(order)) return false;
    
    // Adiciona ordem ao cache
    int size = ArraySize(m_pendingOrders);
    ArrayResize(m_pendingOrders, size + 1);
    m_pendingOrders[size] = order;
    
    // Executa ordem limite
    MqlTradeRequest request = {};
    request.action = TRADE_ACTION_PENDING;
    request.symbol = order.symbol;
    request.volume = order.volume;
    request.type = order.type;
    request.price = order.price;
    request.sl = order.stopLoss;
    request.tp = order.takeProfit;
    request.expiration = order.expiration;
    request.comment = order.comment;
    
    MqlTradeResult result = {};
    return OrderSend(request, result);
}

//+------------------------------------------------------------------+
//| Executa ordem stop                                                |
//+------------------------------------------------------------------+
bool CTraderBot::ExecuteStopOrder(const DynamicOrder &order) {
    if(!m_isActive || !ValidateOrder(order)) return false;
    
    // Adiciona ordem ao cache
    int size = ArraySize(m_pendingOrders);
    ArrayResize(m_pendingOrders, size + 1);
    m_pendingOrders[size] = order;
    
    // Executa ordem stop
    MqlTradeRequest request = {};
    request.action = TRADE_ACTION_PENDING;
    request.symbol = order.symbol;
    request.volume = order.volume;
    request.type = order.type;
    request.price = order.price;
    request.sl = order.stopLoss;
    request.tp = order.takeProfit;
    request.expiration = order.expiration;
    request.comment = order.comment;
    
    MqlTradeResult result = {};
    return OrderSend(request, result);
}

//+------------------------------------------------------------------+
//| Modifica ordem                                                     |
//+------------------------------------------------------------------+
bool CTraderBot::ModifyOrder(ulong ticket, double price, double sl, double tp) {
    if(!m_isActive) return false;
    
    MqlTradeRequest request = {};
    request.action = TRADE_ACTION_MODIFY;
    request.order = ticket;
    request.price = price;
    request.sl = sl;
    request.tp = tp;
    
    MqlTradeResult result = {};
    return OrderSend(request, result);
}

//+------------------------------------------------------------------+
//| Cancela ordem                                                      |
//+------------------------------------------------------------------+
bool CTraderBot::CancelOrder(ulong ticket) {
    if(!m_isActive) return false;
    
    MqlTradeRequest request = {};
    request.action = TRADE_ACTION_REMOVE;
    request.order = ticket;
    
    MqlTradeResult result = {};
    return OrderSend(request, result);
}

//+------------------------------------------------------------------+
//| Valida risco                                                       |
//+------------------------------------------------------------------+
bool CTraderBot::ValidateRisk(string symbol, double volume) {
    if(!m_core) return false;
    
    // Verifica número máximo de posições
    if(PositionsTotal() >= m_risk.maxPositions) {
        Print("Maximum positions reached");
        return false;
    }
    
    // Verifica drawdown
    if(m_dailyPnL <= -m_risk.maxDrawdown) {
        Print("Maximum daily drawdown reached");
        return false;
    }
    
    // Verifica margem
    if(!CheckMargin(DynamicOrder{symbol, ORDER_TYPE_BUY, volume})) {
        Print("Insufficient margin");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica margem                                                    |
//+------------------------------------------------------------------+
bool CTraderBot::CheckMargin(const DynamicOrder &order) {
    double margin = AccountInfoDouble(ACCOUNT_MARGIN);
    double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
    double marginRequired = SymbolInfoDouble(order.symbol, SYMBOL_MARGIN_INITIAL) * order.volume;
    
    return (freeMargin - marginRequired) >= (margin * m_risk.marginBuffer / 100.0);
}

//+------------------------------------------------------------------+
//| Valida ordem                                                       |
//+------------------------------------------------------------------+
bool CTraderBot::ValidateOrder(const DynamicOrder &order) {
    if(order.symbol == "" || order.volume <= 0) return false;
    
    // Valida preços
    if(order.price <= 0) return false;
    if(order.stopLoss < 0) return false;
    if(order.takeProfit < 0) return false;
    
    // Valida risco
    return ValidateRisk(order.symbol, order.volume);
}

//+------------------------------------------------------------------+
//| Atualiza stops dinâmicos                                          |
//+------------------------------------------------------------------+
void CTraderBot::UpdateTrailingStops() {
    if(!m_isActive) return;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionSelectByTicket(PositionGetTicket(i))) {
            double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
            double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            double stopLoss = PositionGetDouble(POSITION_SL);
            
            // Atualiza trailing stop
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                if(currentPrice > openPrice && (stopLoss == 0 || currentPrice - stopLoss > 0)) {
                    double newStopLoss = currentPrice - (currentPrice - openPrice) * 0.5;
                    ModifyOrder(PositionGetInteger(POSITION_TICKET), 0, newStopLoss, 0);
                }
            }
            else {
                if(currentPrice < openPrice && (stopLoss == 0 || stopLoss - currentPrice > 0)) {
                    double newStopLoss = currentPrice + (openPrice - currentPrice) * 0.5;
                    ModifyOrder(PositionGetInteger(POSITION_TICKET), 0, newStopLoss, 0);
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Verifica drawdown                                                  |
//+------------------------------------------------------------------+
void CTraderBot::CheckDrawdown() {
    if(!m_isActive) return;
    
    // Calcula PnL diário
    m_dailyPnL = 0;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionSelectByTicket(PositionGetTicket(i))) {
            m_dailyPnL += PositionGetDouble(POSITION_PROFIT);
        }
    }
    
    // Verifica se atingiu limite de drawdown
    if(m_dailyPnL <= -m_risk.maxDrawdown) {
        Print("Maximum daily drawdown reached. Stopping bot...");
        Stop();
    }
} 