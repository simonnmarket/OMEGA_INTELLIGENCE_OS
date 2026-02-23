#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Tipos de mercado
enum EquityMarket {
    MARKET_TECH,      // Tech Stocks
    MARKET_ENERGY,    // Energy Stocks
    MARKET_HEALTH,    // Healthcare Stocks
    MARKET_INDEX      // Market Indices
};

// Estrutura para configuração de ativo
struct EquityConfig {
    string symbol;              // Símbolo
    EquityMarket market;        // Mercado
    string[] triggers;          // Gatilhos
    string[] correlations;      // Correlações
    string[] riskFactors;       // Fatores de risco
    double minVolume;           // Volume mínimo
    double maxSpread;           // Spread máximo
    bool enabled;               // Habilitado
};

// Classe para sistema de trading de ações
class CEquityTradingSystem {
private:
    // Estado
    bool m_isInitialized;
    EquityConfig m_equities[];
    int m_equityCount;
    
    // Métodos privados
    void InitializeTechStocks() {
        EquityConfig equity;
        equity.symbol = "AAPL";
        equity.market = MARKET_TECH;
        equity.minVolume = 1000000;  // 1M ações
        equity.maxSpread = 0.5;      // 0.5%
        equity.enabled = true;
        
        // Configurar gatilhos
        ArrayResize(equity.triggers, 2);
        equity.triggers[0] = "Earnings Release";
        equity.triggers[1] = "Product Launch";
        
        // Configurar correlações
        ArrayResize(equity.correlations, 2);
        equity.correlations[0] = "NASDAQ";
        equity.correlations[1] = "SOXX";  // Semiconductor Index
        
        // Configurar fatores de risco
        ArrayResize(equity.riskFactors, 2);
        equity.riskFactors[0] = "Interest Rates";
        equity.riskFactors[1] = "Tech Regulations";
        
        AddEquity(equity);
    }
    
    void InitializeIndices() {
        EquityConfig equity;
        equity.symbol = "SP500";
        equity.market = MARKET_INDEX;
        equity.minVolume = 100000000;  // 100M
        equity.maxSpread = 0.1;        // 0.1%
        equity.enabled = true;
        
        // Configurar gatilhos
        ArrayResize(equity.triggers, 2);
        equity.triggers[0] = "Fed Decision";
        equity.triggers[1] = "Economic Data";
        
        // Configurar correlações
        ArrayResize(equity.correlations, 2);
        equity.correlations[0] = "VIX";    // Volatility Index
        equity.correlations[1] = "US10Y";  // 10-Year Treasury
        
        // Configurar fatores de risco
        ArrayResize(equity.riskFactors, 2);
        equity.riskFactors[0] = "Market Sentiment";
        equity.riskFactors[1] = "Global Events";
        
        AddEquity(equity);
    }
    
    bool ValidateVolume(const string& symbol) {
        EquityConfig equity = GetEquityBySymbol(symbol);
        if(!equity.enabled) return false;
        
        double volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME);
        return (volume >= equity.minVolume);
    }
    
    bool ValidateSpread(const string& symbol) {
        EquityConfig equity = GetEquityBySymbol(symbol);
        if(!equity.enabled) return false;
        
        double spread = SymbolInfoInteger(symbol, SYMBOL_SPREAD) * SymbolInfoDouble(symbol, SYMBOL_POINT);
        return (spread <= equity.maxSpread);
    }
    
public:
    // Construtor
    CEquityTradingSystem() {
        m_isInitialized = false;
        m_equityCount = 0;
    }
    
    // Destrutor
    ~CEquityTradingSystem() {
        ArrayFree(m_equities);
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return false;
        
        // Inicializar mercados
        InitializeTechStocks();
        InitializeIndices();
        
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar ativo
    bool AddEquity(const EquityConfig& equity) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_equities);
        ArrayResize(m_equities, size + 1);
        m_equities[size] = equity;
        m_equityCount++;
        
        return true;
    }
    
    // Remover ativo
    bool RemoveEquity(int index) {
        if(!m_isInitialized || index < 0 || index >= m_equityCount) return false;
        
        // Remover ativo
        for(int i = index; i < m_equityCount - 1; i++) {
            m_equities[i] = m_equities[i + 1];
        }
        
        // Redimensionar array
        ArrayResize(m_equities, m_equityCount - 1);
        m_equityCount--;
        
        return true;
    }
    
    // Obter ativo por símbolo
    EquityConfig GetEquityBySymbol(const string& symbol) {
        if(!m_isInitialized) {
            EquityConfig empty;
            return empty;
        }
        
        for(int i = 0; i < m_equityCount; i++) {
            if(m_equities[i].symbol == symbol) {
                return m_equities[i];
            }
        }
        
        EquityConfig empty;
        return empty;
    }
    
    // Verificar se ativo está ativo
    bool IsEquityActive(const string& symbol) {
        if(!m_isInitialized) return false;
        
        EquityConfig equity = GetEquityBySymbol(symbol);
        if(!equity.enabled) return false;
        
        // Verificar volume
        if(!ValidateVolume(symbol)) return false;
        
        // Verificar spread
        if(!ValidateSpread(symbol)) return false;
        
        return true;
    }
    
    // Habilitar/desabilitar ativo
    bool SetEquityEnabled(const string& symbol, bool enabled) {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < m_equityCount; i++) {
            if(m_equities[i].symbol == symbol) {
                m_equities[i].enabled = enabled;
                return true;
            }
        }
        
        return false;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetEquityCount() const {
        return m_equityCount;
    }
    
    EquityConfig* GetEquities() {
        return m_equities;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Equity Trading System Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Equity Count: ", m_equityCount);
        
        // Imprimir detalhes de cada ativo
        for(int i = 0; i < m_equityCount; i++) {
            Print("Equity ", i + 1, ":");
            Print("Symbol: ", m_equities[i].symbol);
            Print("Market: ", m_equities[i].market);
            Print("Min Volume: ", m_equities[i].minVolume);
            Print("Max Spread: ", m_equities[i].maxSpread);
            Print("Enabled: ", m_equities[i].enabled);
            
            Print("Triggers:");
            for(int j = 0; j < ArraySize(m_equities[i].triggers); j++) {
                Print("  ", m_equities[i].triggers[j]);
            }
            
            Print("Correlations:");
            for(int j = 0; j < ArraySize(m_equities[i].correlations); j++) {
                Print("  ", m_equities[i].correlations[j]);
            }
            
            Print("Risk Factors:");
            for(int j = 0; j < ArraySize(m_equities[i].riskFactors); j++) {
                Print("  ", m_equities[i].riskFactors[j]);
            }
        }
    }
}; 