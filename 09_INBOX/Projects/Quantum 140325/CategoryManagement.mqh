#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Tipos de mercado
enum MarketType {
    MARKET_FOREX,     // Forex
    MARKET_STOCKS,    // Ações
    MARKET_CRYPTO     // Criptomoedas
};

// Estrutura para configuração de mercado
struct MarketConfig {
    MarketType type;           // Tipo de mercado
    string name;              // Nome do mercado
    string manager;           // Gestor
    string[] symbols;         // Símbolos
    string[] strategies;      // Estratégias
    double riskPerTrade;      // Risco por trade
    double maxDrawdown;       // Máximo drawdown
    bool enabled;             // Habilitado
};

// Classe para gerenciamento de categorias
class CCategoryManagement {
private:
    // Estado
    bool m_isInitialized;
    MarketConfig m_markets[];
    int m_marketCount;
    
    // Métodos privados
    void InitializeForexMarket() {
        MarketConfig market;
        market.type = MARKET_FOREX;
        market.name = "Forex";
        market.manager = "Trading Specialist 1";
        market.riskPerTrade = 0.02;  // 2%
        market.maxDrawdown = 0.15;    // 15%
        market.enabled = true;
        
        // Configurar símbolos
        ArrayResize(market.symbols, 3);
        market.symbols[0] = "EURUSD";
        market.symbols[1] = "USDJPY";
        market.symbols[2] = "GBPUSD";
        
        // Configurar estratégias
        ArrayResize(market.strategies, 2);
        market.strategies[0] = "Trend Following";
        market.strategies[1] = "Mean Reversion";
        
        AddMarket(market);
    }
    
    void InitializeStocksMarket() {
        MarketConfig market;
        market.type = MARKET_STOCKS;
        market.name = "Stocks";
        market.manager = "Trading Specialist 2";
        market.riskPerTrade = 0.02;  // 2%
        market.maxDrawdown = 0.15;    // 15%
        market.enabled = true;
        
        // Configurar símbolos
        ArrayResize(market.symbols, 3);
        market.symbols[0] = "AAPL";  // Tech
        market.symbols[1] = "XOM";   // Energy
        market.symbols[2] = "JNJ";   // Healthcare
        
        // Configurar estratégias
        ArrayResize(market.strategies, 2);
        market.strategies[0] = "Sector Rotation";
        market.strategies[1] = "Value Investing";
        
        AddMarket(market);
    }
    
    void InitializeCryptoMarket() {
        MarketConfig market;
        market.type = MARKET_CRYPTO;
        market.name = "Crypto";
        market.manager = "Trading Specialist 3";
        market.riskPerTrade = 0.01;  // 1% (menor devido à volatilidade)
        market.maxDrawdown = 0.10;    // 10%
        market.enabled = true;
        
        // Configurar símbolos
        ArrayResize(market.symbols, 3);
        market.symbols[0] = "BTCUSD";
        market.symbols[1] = "ETHUSD";
        market.symbols[2] = "SOLUSD";
        
        // Configurar estratégias
        ArrayResize(market.strategies, 2);
        market.strategies[0] = "Volatility Breakout";
        market.strategies[1] = "Momentum Trading";
        
        AddMarket(market);
    }
    
public:
    // Construtor
    CCategoryManagement() {
        m_isInitialized = false;
        m_marketCount = 0;
    }
    
    // Destrutor
    ~CCategoryManagement() {
        ArrayFree(m_markets);
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return false;
        
        // Inicializar mercados
        InitializeForexMarket();
        InitializeStocksMarket();
        InitializeCryptoMarket();
        
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar mercado
    bool AddMarket(const MarketConfig& market) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_markets);
        ArrayResize(m_markets, size + 1);
        m_markets[size] = market;
        m_marketCount++;
        
        return true;
    }
    
    // Remover mercado
    bool RemoveMarket(int index) {
        if(!m_isInitialized || index < 0 || index >= m_marketCount) return false;
        
        // Remover mercado
        for(int i = index; i < m_marketCount - 1; i++) {
            m_markets[i] = m_markets[i + 1];
        }
        
        // Redimensionar array
        ArrayResize(m_markets, m_marketCount - 1);
        m_marketCount--;
        
        return true;
    }
    
    // Obter mercado por tipo
    MarketConfig GetMarketByType(MarketType type) {
        if(!m_isInitialized) {
            MarketConfig empty;
            return empty;
        }
        
        for(int i = 0; i < m_marketCount; i++) {
            if(m_markets[i].type == type) {
                return m_markets[i];
            }
        }
        
        MarketConfig empty;
        return empty;
    }
    
    // Obter mercado por nome
    MarketConfig GetMarketByName(const string& name) {
        if(!m_isInitialized) {
            MarketConfig empty;
            return empty;
        }
        
        for(int i = 0; i < m_marketCount; i++) {
            if(m_markets[i].name == name) {
                return m_markets[i];
            }
        }
        
        MarketConfig empty;
        return empty;
    }
    
    // Habilitar/desabilitar mercado
    bool SetMarketEnabled(int index, bool enabled) {
        if(!m_isInitialized || index < 0 || index >= m_marketCount) return false;
        
        m_markets[index].enabled = enabled;
        return true;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetMarketCount() const {
        return m_marketCount;
    }
    
    MarketConfig* GetMarkets() {
        return m_markets;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Category Management Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Market Count: ", m_marketCount);
        
        // Imprimir detalhes de cada mercado
        for(int i = 0; i < m_marketCount; i++) {
            Print("Market ", i + 1, ":");
            Print("Name: ", m_markets[i].name);
            Print("Manager: ", m_markets[i].manager);
            Print("Type: ", m_markets[i].type);
            Print("Risk per Trade: ", m_markets[i].riskPerTrade);
            Print("Max Drawdown: ", m_markets[i].maxDrawdown);
            Print("Enabled: ", m_markets[i].enabled);
            
            Print("Symbols:");
            for(int j = 0; j < ArraySize(m_markets[i].symbols); j++) {
                Print("  ", m_markets[i].symbols[j]);
            }
            
            Print("Strategies:");
            for(int j = 0; j < ArraySize(m_markets[i].strategies); j++) {
                Print("  ", m_markets[i].strategies[j]);
            }
        }
    }
}; 