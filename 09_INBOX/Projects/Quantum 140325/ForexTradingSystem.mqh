#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Tipos de sessão
enum TradingSession {
    SESSION_ASIAN,      // Sessão Asiática
    SESSION_LONDON,     // Sessão de Londres
    SESSION_NEWYORK,    // Sessão de Nova York
    SESSION_OVERLAP     // Sessão de sobreposição
};

// Estrutura para configuração de par
struct PairConfig {
    string symbol;              // Símbolo
    TradingSession session;     // Sessão de trading
    string strategy;            // Estratégia
    bool volatilityFilter;      // Filtro de volatilidade
    string[] newsSources;       // Fontes de notícias
    double minVolatility;       // Volatilidade mínima
    double maxVolatility;       // Volatilidade máxima
    double minSpread;           // Spread mínimo
    double maxSpread;           // Spread máximo
    bool enabled;               // Habilitado
};

// Classe para sistema de trading Forex
class CForexTradingSystem {
private:
    // Estado
    bool m_isInitialized;
    PairConfig m_pairs[];
    int m_pairCount;
    
    // Métodos privados
    void InitializeUSDJPY() {
        PairConfig pair;
        pair.symbol = "USDJPY";
        pair.session = SESSION_ASIAN;
        pair.strategy = "Trend Following";
        pair.volatilityFilter = true;
        pair.minVolatility = 0.5;  // 50 pips
        pair.maxVolatility = 2.0;  // 200 pips
        pair.minSpread = 0.1;      // 0.1 pips
        pair.maxSpread = 0.5;      // 0.5 pips
        pair.enabled = true;
        
        // Configurar fontes de notícias
        ArrayResize(pair.newsSources, 2);
        pair.newsSources[0] = "BOJ";  // Banco do Japão
        pair.newsSources[1] = "FED";  // Reserva Federal dos EUA
        
        AddPair(pair);
    }
    
    void InitializeEURUSD() {
        PairConfig pair;
        pair.symbol = "EURUSD";
        pair.session = SESSION_NEWYORK;
        pair.strategy = "News Reaction";
        pair.volatilityFilter = true;
        pair.minVolatility = 0.5;  // 50 pips
        pair.maxVolatility = 2.0;  // 200 pips
        pair.minSpread = 0.1;      // 0.1 pips
        pair.maxSpread = 0.5;      // 0.5 pips
        pair.enabled = true;
        
        // Configurar fontes de notícias
        ArrayResize(pair.newsSources, 3);
        pair.newsSources[0] = "ECB";  // Banco Central Europeu
        pair.newsSources[1] = "FED";  // Reserva Federal dos EUA
        pair.newsSources[2] = "NFP";  // Non-Farm Payrolls
        
        AddPair(pair);
    }
    
    bool IsSessionActive(TradingSession session) {
        datetime now = TimeCurrent();
        int hour = TimeHour(now);
        
        switch(session) {
            case SESSION_ASIAN:
                return (hour >= 0 && hour < 8);  // 00:00-08:00 GMT
            case SESSION_LONDON:
                return (hour >= 8 && hour < 16); // 08:00-16:00 GMT
            case SESSION_NEWYORK:
                return (hour >= 13 && hour < 21); // 13:00-21:00 GMT
            case SESSION_OVERLAP:
                return ((hour >= 8 && hour < 16) || (hour >= 13 && hour < 21)); // Londres/NY
            default:
                return false;
        }
    }
    
    bool ValidateVolatility(const string& symbol) {
        PairConfig pair = GetPairBySymbol(symbol);
        if(!pair.enabled) return false;
        
        double volatility = SymbolInfoDouble(symbol, SYMBOL_VOLATILITY);
        return (volatility >= pair.minVolatility && volatility <= pair.maxVolatility);
    }
    
    bool ValidateSpread(const string& symbol) {
        PairConfig pair = GetPairBySymbol(symbol);
        if(!pair.enabled) return false;
        
        double spread = SymbolInfoInteger(symbol, SYMBOL_SPREAD) * SymbolInfoDouble(symbol, SYMBOL_POINT);
        return (spread >= pair.minSpread && spread <= pair.maxSpread);
    }
    
public:
    // Construtor
    CForexTradingSystem() {
        m_isInitialized = false;
        m_pairCount = 0;
    }
    
    // Destrutor
    ~CForexTradingSystem() {
        ArrayFree(m_pairs);
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return false;
        
        // Inicializar pares
        InitializeUSDJPY();
        InitializeEURUSD();
        
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar par
    bool AddPair(const PairConfig& pair) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_pairs);
        ArrayResize(m_pairs, size + 1);
        m_pairs[size] = pair;
        m_pairCount++;
        
        return true;
    }
    
    // Remover par
    bool RemovePair(int index) {
        if(!m_isInitialized || index < 0 || index >= m_pairCount) return false;
        
        // Remover par
        for(int i = index; i < m_pairCount - 1; i++) {
            m_pairs[i] = m_pairs[i + 1];
        }
        
        // Redimensionar array
        ArrayResize(m_pairs, m_pairCount - 1);
        m_pairCount--;
        
        return true;
    }
    
    // Obter par por símbolo
    PairConfig GetPairBySymbol(const string& symbol) {
        if(!m_isInitialized) {
            PairConfig empty;
            return empty;
        }
        
        for(int i = 0; i < m_pairCount; i++) {
            if(m_pairs[i].symbol == symbol) {
                return m_pairs[i];
            }
        }
        
        PairConfig empty;
        return empty;
    }
    
    // Verificar se par está ativo
    bool IsPairActive(const string& symbol) {
        if(!m_isInitialized) return false;
        
        PairConfig pair = GetPairBySymbol(symbol);
        if(!pair.enabled) return false;
        
        // Verificar sessão
        if(!IsSessionActive(pair.session)) return false;
        
        // Verificar volatilidade
        if(pair.volatilityFilter && !ValidateVolatility(symbol)) return false;
        
        // Verificar spread
        if(!ValidateSpread(symbol)) return false;
        
        return true;
    }
    
    // Habilitar/desabilitar par
    bool SetPairEnabled(const string& symbol, bool enabled) {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < m_pairCount; i++) {
            if(m_pairs[i].symbol == symbol) {
                m_pairs[i].enabled = enabled;
                return true;
            }
        }
        
        return false;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetPairCount() const {
        return m_pairCount;
    }
    
    PairConfig* GetPairs() {
        return m_pairs;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Forex Trading System Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Pair Count: ", m_pairCount);
        
        // Imprimir detalhes de cada par
        for(int i = 0; i < m_pairCount; i++) {
            Print("Pair ", i + 1, ":");
            Print("Symbol: ", m_pairs[i].symbol);
            Print("Session: ", m_pairs[i].session);
            Print("Strategy: ", m_pairs[i].strategy);
            Print("Volatility Filter: ", m_pairs[i].volatilityFilter);
            Print("Min Volatility: ", m_pairs[i].minVolatility);
            Print("Max Volatility: ", m_pairs[i].maxVolatility);
            Print("Min Spread: ", m_pairs[i].minSpread);
            Print("Max Spread: ", m_pairs[i].maxSpread);
            Print("Enabled: ", m_pairs[i].enabled);
            
            Print("News Sources:");
            for(int j = 0; j < ArraySize(m_pairs[i].newsSources); j++) {
                Print("  ", m_pairs[i].newsSources[j]);
            }
        }
    }
}; 