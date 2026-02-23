#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para configurações de ordem
struct OrderSettings {
    double lotSize;           // Tamanho do lote
    double stopLoss;          // Stop Loss
    double takeProfit;        // Take Profit
    int slippage;            // Slippage
    int magicNumber;         // Número mágico
    bool useTrailingStop;    // Usar trailing stop
    double trailingStart;    // Início do trailing stop
    double trailingStep;     // Passo do trailing stop
};

// Classe para gerenciamento de ordens
class COrderManager {
private:
    // Configurações
    OrderSettings m_settings;
    
    // Estado
    bool m_isInitialized;
    int m_totalOrders;
    int m_openOrders;
    double m_totalProfit;
    
    // Métodos privados
    bool ValidateOrder(const double& volume, const double& price, 
                      const double& sl, const double& tp) {
        // Validar volume
        if(volume <= 0) return false;
        
        // Validar preço
        if(price <= 0) return false;
        
        // Validar stop loss e take profit
        if(sl <= 0 || tp <= 0) return false;
        
        // Validar limites de posição
        double maxVolume = AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.1; // 10% da margem livre
        if(volume > maxVolume) return false;
        
        return true;
    }
    
    void UpdateTrailingStop() {
        if(!m_settings.useTrailingStop) return;
        
        for(int i = 0; i < PositionsTotal(); i++) {
            if(PositionSelectByTicket(PositionGetTicket(i))) {
                double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
                double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
                double currentSL = PositionGetDouble(POSITION_SL);
                
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                    if(currentPrice - openPrice > m_settings.trailingStart) {
                        double newSL = currentPrice - m_settings.trailingStep;
                        if(newSL > currentSL) {
                            ModifyPosition(newSL, PositionGetDouble(POSITION_TP));
                        }
                    }
                } else {
                    if(openPrice - currentPrice > m_settings.trailingStart) {
                        double newSL = currentPrice + m_settings.trailingStep;
                        if(newSL < currentSL || currentSL == 0) {
                            ModifyPosition(newSL, PositionGetDouble(POSITION_TP));
                        }
                    }
                }
            }
        }
    }
    
    bool ModifyPosition(const double& sl, const double& tp) {
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_SLTP;
        request.position = PositionGetTicket(0);
        request.symbol = _Symbol;
        request.sl = sl;
        request.tp = tp;
        
        return OrderSend(request, result);
    }
    
public:
    // Construtor
    COrderManager() {
        // Configurações padrão
        m_settings.lotSize = 0.1;
        m_settings.stopLoss = 50;
        m_settings.takeProfit = 100;
        m_settings.slippage = 3;
        m_settings.magicNumber = 123456;
        m_settings.useTrailingStop = false;
        m_settings.trailingStart = 20;
        m_settings.trailingStep = 10;
        
        m_isInitialized = false;
        m_totalOrders = 0;
        m_openOrders = 0;
        m_totalProfit = 0;
    }
    
    // Destrutor
    ~COrderManager() {
        // Limpar recursos
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Abrir posição
    bool OpenPosition(bool isBuy, const double& volume, const double& price,
                     const double& sl, const double& tp) {
        if(!m_isInitialized) return false;
        
        // Validar ordem
        if(!ValidateOrder(volume, price, sl, tp)) return false;
        
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.symbol = _Symbol;
        request.volume = volume;
        request.type = isBuy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        request.price = price;
        request.sl = sl;
        request.tp = tp;
        request.deviation = m_settings.slippage;
        request.magic = m_settings.magicNumber;
        request.comment = "Skyler EA";
        request.type_filling = ORDER_FILLING_FOK;
        
        if(OrderSend(request, result)) {
            m_totalOrders++;
            m_openOrders++;
            return true;
        }
        
        return false;
    }
    
    // Fechar posição
    bool ClosePosition(ulong ticket) {
        if(!m_isInitialized) return false;
        
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.position = ticket;
        request.symbol = _Symbol;
        request.volume = PositionGetDouble(POSITION_VOLUME);
        request.type = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 
                      ORDER_TYPE_SELL : ORDER_TYPE_BUY;
        request.price = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 
                       SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                       SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        request.deviation = m_settings.slippage;
        request.magic = m_settings.magicNumber;
        request.comment = "Skyler EA Close";
        request.type_filling = ORDER_FILLING_FOK;
        
        if(OrderSend(request, result)) {
            m_openOrders--;
            m_totalProfit += result.profit;
            return true;
        }
        
        return false;
    }
    
    // Fechar todas as posições
    void CloseAllPositions() {
        for(int i = PositionsTotal() - 1; i >= 0; i--) {
            if(PositionSelectByTicket(PositionGetTicket(i))) {
                ClosePosition(PositionGetTicket(i));
            }
        }
    }
    
    // Atualizar
    void Update() {
        if(!m_isInitialized) return;
        
        // Atualizar trailing stop
        UpdateTrailingStop();
        
        // Atualizar contagem de ordens abertas
        m_openOrders = PositionsTotal();
    }
    
    // Configurações
    void SetSettings(const OrderSettings& settings) {
        m_settings = settings;
    }
    
    // Acesso
    OrderSettings GetSettings() const {
        return m_settings;
    }
    
    int GetTotalOrders() const {
        return m_totalOrders;
    }
    
    int GetOpenOrders() const {
        return m_openOrders;
    }
    
    double GetTotalProfit() const {
        return m_totalProfit;
    }
    
    // Métricas
    void UpdateMetrics() {
        Print("Order Manager Metrics:");
        Print("Total Orders: ", m_totalOrders);
        Print("Open Orders: ", m_openOrders);
        Print("Total Profit: ", m_totalProfit);
    }
}; 