#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados de ordem
struct OrderData {
    datetime time;           // Tempo da ordem
    double price;           // Preço
    double volume;          // Volume
    double stopLoss;        // Stop Loss
    double takeProfit;      // Take Profit
    string comment;         // Comentário
};

// Estrutura para dados de trade
struct TradeData {
    datetime time;           // Tempo do trade
    double openPrice;        // Preço de abertura
    double closePrice;       // Preço de fechamento
    double volume;          // Volume
    double profit;          // Lucro/Prejuízo
    string comment;         // Comentário
};

// Classe para gerenciamento de dados
class CDataManager {
private:
    // Estado
    bool m_isInitialized;
    
    // Arrays de dados
    OrderData m_orders[];
    TradeData m_trades[];
    
    // Métricas
    int m_totalOrders;
    int m_totalTrades;
    double m_totalProfit;
    double m_maxDrawdown;
    double m_winRate;
    
    // Métodos privados
    void UpdateMetrics() {
        // Atualizar métricas de trades
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        
        m_maxDrawdown = MathMax(m_maxDrawdown, (balance - equity) / balance * 100);
        
        // Calcular win rate
        int winningTrades = 0;
        for(int i = 0; i < ArraySize(m_trades); i++) {
            if(m_trades[i].profit > 0) winningTrades++;
        }
        m_winRate = ArraySize(m_trades) > 0 ? 
                   (double)winningTrades / ArraySize(m_trades) * 100 : 0;
    }
    
    string FormatOrderData(const OrderData& order) {
        return StringFormat("%s,%f,%f,%f,%f,%s",
                          TimeToString(order.time),
                          order.price,
                          order.volume,
                          order.stopLoss,
                          order.takeProfit,
                          order.comment);
    }
    
    string FormatTradeData(const TradeData& trade) {
        return StringFormat("%s,%f,%f,%f,%f,%s",
                          TimeToString(trade.time),
                          trade.openPrice,
                          trade.closePrice,
                          trade.volume,
                          trade.profit,
                          trade.comment);
    }
    
    void ParseOrderData(const string& data, OrderData& order) {
        string parts[];
        StringSplit(data, ',', parts);
        
        if(ArraySize(parts) >= 6) {
            order.time = StringToTime(parts[0]);
            order.price = StringToDouble(parts[1]);
            order.volume = StringToDouble(parts[2]);
            order.stopLoss = StringToDouble(parts[3]);
            order.takeProfit = StringToDouble(parts[4]);
            order.comment = parts[5];
        }
    }
    
    void ParseTradeData(const string& data, TradeData& trade) {
        string parts[];
        StringSplit(data, ',', parts);
        
        if(ArraySize(parts) >= 6) {
            trade.time = StringToTime(parts[0]);
            trade.openPrice = StringToDouble(parts[1]);
            trade.closePrice = StringToDouble(parts[2]);
            trade.volume = StringToDouble(parts[3]);
            trade.profit = StringToDouble(parts[4]);
            trade.comment = parts[5];
        }
    }
    
public:
    // Construtor
    CDataManager() {
        m_isInitialized = false;
        m_totalOrders = 0;
        m_totalTrades = 0;
        m_totalProfit = 0;
        m_maxDrawdown = 0;
        m_winRate = 0;
    }
    
    // Destrutor
    ~CDataManager() {
        // Limpar arrays
        ArrayFree(m_orders);
        ArrayFree(m_trades);
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Log de ordem
    void LogOrder(const OrderData& order) {
        if(!m_isInitialized) return;
        
        int size = ArraySize(m_orders);
        ArrayResize(m_orders, size + 1);
        m_orders[size] = order;
        m_totalOrders++;
    }
    
    // Log de trade
    void LogTrade(const TradeData& trade) {
        if(!m_isInitialized) return;
        
        int size = ArraySize(m_trades);
        ArrayResize(m_trades, size + 1);
        m_trades[size] = trade;
        m_totalTrades++;
        m_totalProfit += trade.profit;
        
        UpdateMetrics();
    }
    
    // Salvar dados
    bool SaveData(const string& filename) {
        if(!m_isInitialized) return false;
        
        int handle = FileOpen(filename, FILE_WRITE|FILE_CSV);
        if(handle == INVALID_HANDLE) return false;
        
        // Salvar ordens
        FileWriteString(handle, "Orders\n");
        for(int i = 0; i < ArraySize(m_orders); i++) {
            FileWriteString(handle, FormatOrderData(m_orders[i]) + "\n");
        }
        
        // Salvar trades
        FileWriteString(handle, "\nTrades\n");
        for(int i = 0; i < ArraySize(m_trades); i++) {
            FileWriteString(handle, FormatTradeData(m_trades[i]) + "\n");
        }
        
        FileClose(handle);
        return true;
    }
    
    // Carregar dados
    bool LoadData(const string& filename) {
        if(!m_isInitialized) return false;
        
        int handle = FileOpen(filename, FILE_READ|FILE_CSV);
        if(handle == INVALID_HANDLE) return false;
        
        // Limpar arrays
        ArrayFree(m_orders);
        ArrayFree(m_trades);
        
        string line;
        bool readingOrders = true;
        
        while(!FileIsEnding(handle)) {
            line = FileReadString(handle);
            
            if(line == "Trades") {
                readingOrders = false;
                continue;
            }
            
            if(readingOrders) {
                OrderData order;
                ParseOrderData(line, order);
                LogOrder(order);
            } else {
                TradeData trade;
                ParseTradeData(line, trade);
                LogTrade(trade);
            }
        }
        
        FileClose(handle);
        return true;
    }
    
    // Acesso
    int GetTotalOrders() const {
        return m_totalOrders;
    }
    
    int GetTotalTrades() const {
        return m_totalTrades;
    }
    
    double GetTotalProfit() const {
        return m_totalProfit;
    }
    
    double GetMaxDrawdown() const {
        return m_maxDrawdown;
    }
    
    double GetWinRate() const {
        return m_winRate;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Data Manager Metrics:");
        Print("Total Orders: ", m_totalOrders);
        Print("Total Trades: ", m_totalTrades);
        Print("Total Profit: ", m_totalProfit);
        Print("Max Drawdown: ", m_maxDrawdown, "%");
        Print("Win Rate: ", m_winRate, "%");
    }
}; 