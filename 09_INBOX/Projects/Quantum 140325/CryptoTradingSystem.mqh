#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Tipos de criptomoeda
enum CryptoType {
    CRYPTO_BTC,      // Bitcoin
    CRYPTO_ETH,      // Ethereum
    CRYPTO_SOL,      // Solana
    CRYPTO_ALT       // Altcoins
};

// Estrutura para configuração de criptomoeda
struct CryptoConfig {
    string symbol;              // Símbolo
    CryptoType type;           // Tipo
    double maxPositionSize;     // Tamanho máximo da posição
    bool dynamicStops;         // Stops dinâmicos
    bool flashCrashProtection; // Proteção contra flash crash
    string[] sentimentSources; // Fontes de sentimento
    double sentimentThreshold; // Limiar de sentimento
    double minVolume;          // Volume mínimo
    double maxSpread;          // Spread máximo
    bool enabled;              // Habilitado
};

// Classe para sistema de trading de criptomoedas
class CCryptoTradingSystem {
private:
    // Estado
    bool m_isInitialized;
    CryptoConfig m_cryptos[];
    int m_cryptoCount;
    
    // Métodos privados
    void InitializeBitcoin() {
        CryptoConfig crypto;
        crypto.symbol = "BTCUSD";
        crypto.type = CRYPTO_BTC;
        crypto.maxPositionSize = 0.02;  // 2% do capital
        crypto.dynamicStops = true;
        crypto.flashCrashProtection = true;
        crypto.sentimentThreshold = 0.7;
        crypto.minVolume = 1000000;     // 1M USD
        crypto.maxSpread = 0.5;         // 0.5%
        crypto.enabled = true;
        
        // Configurar fontes de sentimento
        ArrayResize(crypto.sentimentSources, 3);
        crypto.sentimentSources[0] = "Twitter";
        crypto.sentimentSources[1] = "Reddit";
        crypto.sentimentSources[2] = "Discord";
        
        AddCrypto(crypto);
    }
    
    void InitializeEthereum() {
        CryptoConfig crypto;
        crypto.symbol = "ETHUSD";
        crypto.type = CRYPTO_ETH;
        crypto.maxPositionSize = 0.02;  // 2% do capital
        crypto.dynamicStops = true;
        crypto.flashCrashProtection = true;
        crypto.sentimentThreshold = 0.7;
        crypto.minVolume = 500000;      // 500K USD
        crypto.maxSpread = 0.5;         // 0.5%
        crypto.enabled = true;
        
        // Configurar fontes de sentimento
        ArrayResize(crypto.sentimentSources, 3);
        crypto.sentimentSources[0] = "Twitter";
        crypto.sentimentSources[1] = "Reddit";
        crypto.sentimentSources[2] = "Discord";
        
        AddCrypto(crypto);
    }
    
    bool ValidateVolume(const string& symbol) {
        CryptoConfig crypto = GetCryptoBySymbol(symbol);
        if(!crypto.enabled) return false;
        
        double volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME);
        return (volume >= crypto.minVolume);
    }
    
    bool ValidateSpread(const string& symbol) {
        CryptoConfig crypto = GetCryptoBySymbol(symbol);
        if(!crypto.enabled) return false;
        
        double spread = SymbolInfoInteger(symbol, SYMBOL_SPREAD) * SymbolInfoDouble(symbol, SYMBOL_POINT);
        return (spread <= crypto.maxSpread);
    }
    
    bool CheckFlashCrash(const string& symbol) {
        CryptoConfig crypto = GetCryptoBySymbol(symbol);
        if(!crypto.enabled || !crypto.flashCrashProtection) return true;
        
        // Verificar queda brusca de preço
        double currentPrice = SymbolInfoDouble(symbol, SYMBOL_BID);
        double prevPrice = SymbolInfoDouble(symbol, SYMBOL_PREV_BID);
        double priceChange = MathAbs(currentPrice - prevPrice) / prevPrice;
        
        // Se queda maior que 5% em 1 minuto, considerar flash crash
        return (priceChange <= 0.05);
    }
    
public:
    // Construtor
    CCryptoTradingSystem() {
        m_isInitialized = false;
        m_cryptoCount = 0;
    }
    
    // Destrutor
    ~CCryptoTradingSystem() {
        ArrayFree(m_cryptos);
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return false;
        
        // Inicializar criptomoedas
        InitializeBitcoin();
        InitializeEthereum();
        
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar criptomoeda
    bool AddCrypto(const CryptoConfig& crypto) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_cryptos);
        ArrayResize(m_cryptos, size + 1);
        m_cryptos[size] = crypto;
        m_cryptoCount++;
        
        return true;
    }
    
    // Remover criptomoeda
    bool RemoveCrypto(int index) {
        if(!m_isInitialized || index < 0 || index >= m_cryptoCount) return false;
        
        // Remover criptomoeda
        for(int i = index; i < m_cryptoCount - 1; i++) {
            m_cryptos[i] = m_cryptos[i + 1];
        }
        
        // Redimensionar array
        ArrayResize(m_cryptos, m_cryptoCount - 1);
        m_cryptoCount--;
        
        return true;
    }
    
    // Obter criptomoeda por símbolo
    CryptoConfig GetCryptoBySymbol(const string& symbol) {
        if(!m_isInitialized) {
            CryptoConfig empty;
            return empty;
        }
        
        for(int i = 0; i < m_cryptoCount; i++) {
            if(m_cryptos[i].symbol == symbol) {
                return m_cryptos[i];
            }
        }
        
        CryptoConfig empty;
        return empty;
    }
    
    // Verificar se criptomoeda está ativa
    bool IsCryptoActive(const string& symbol) {
        if(!m_isInitialized) return false;
        
        CryptoConfig crypto = GetCryptoBySymbol(symbol);
        if(!crypto.enabled) return false;
        
        // Verificar volume
        if(!ValidateVolume(symbol)) return false;
        
        // Verificar spread
        if(!ValidateSpread(symbol)) return false;
        
        // Verificar flash crash
        if(!CheckFlashCrash(symbol)) return false;
        
        return true;
    }
    
    // Habilitar/desabilitar criptomoeda
    bool SetCryptoEnabled(const string& symbol, bool enabled) {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < m_cryptoCount; i++) {
            if(m_cryptos[i].symbol == symbol) {
                m_cryptos[i].enabled = enabled;
                return true;
            }
        }
        
        return false;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetCryptoCount() const {
        return m_cryptoCount;
    }
    
    CryptoConfig* GetCryptos() {
        return m_cryptos;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Crypto Trading System Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Crypto Count: ", m_cryptoCount);
        
        // Imprimir detalhes de cada criptomoeda
        for(int i = 0; i < m_cryptoCount; i++) {
            Print("Crypto ", i + 1, ":");
            Print("Symbol: ", m_cryptos[i].symbol);
            Print("Type: ", m_cryptos[i].type);
            Print("Max Position Size: ", m_cryptos[i].maxPositionSize);
            Print("Dynamic Stops: ", m_cryptos[i].dynamicStops);
            Print("Flash Crash Protection: ", m_cryptos[i].flashCrashProtection);
            Print("Sentiment Threshold: ", m_cryptos[i].sentimentThreshold);
            Print("Min Volume: ", m_cryptos[i].minVolume);
            Print("Max Spread: ", m_cryptos[i].maxSpread);
            Print("Enabled: ", m_cryptos[i].enabled);
            
            Print("Sentiment Sources:");
            for(int j = 0; j < ArraySize(m_cryptos[i].sentimentSources); j++) {
                Print("  ", m_cryptos[i].sentimentSources[j]);
            }
        }
    }
}; 