//+------------------------------------------------------------------+
//|                  EXTERNAL DATA BRIDGE MODULE                     |
//|        QUANTUM OMEGA GOD MODE - PHASE 1 IMPLEMENTATION          |
//|                  VERSÃO 10.0.1 - QUANTUM-STABLE                  |
//+------------------------------------------------------------------+

#ifndef EXTERNAL_DATA_BRIDGE_MQH
#define EXTERNAL_DATA_BRIDGE_MQH

#property strict

//+------------------------------------------------------------------+
//|                  CLASSE EXTERNAL DATA BRIDGE                     |
//+------------------------------------------------------------------+
class ExternalDataBridge
{
private:
    // Cache para otimizar performance e reduzir latência
    double m_sentimentCache[5];  // Cache para 5 símbolos principais
    double m_volatilityCache;    // Cache para índice de volatilidade
    datetime m_lastSentimentUpdate[5];
    datetime m_lastVolatilityUpdate;
    int m_cacheTimeout;          // 5 minutos de cache
    bool m_isConnected;
    
public:
    //------------------------------------------------------------------
    //| Construtor                                                     |
    //------------------------------------------------------------------
    ExternalDataBridge() : m_cacheTimeout(300), m_isConnected(false)
    {
        // Inicializar cache
        ArrayInitialize(m_sentimentCache, 0.0);
        ArrayInitialize(m_lastSentimentUpdate, 0);
        m_volatilityCache = 0.0;
        m_lastVolatilityUpdate = 0;
        
        Print("🌐 EXTERNAL DATA BRIDGE INICIALIZADO");
    }
    
    //------------------------------------------------------------------
    //| Destrutor                                                      |
    //------------------------------------------------------------------
    ~ExternalDataBridge()
    {
        Print("🌐 EXTERNAL DATA BRIDGE FINALIZADO");
    }
    
    //------------------------------------------------------------------
    //| Conectar ao sistema externo                                    |
    //------------------------------------------------------------------
    void Connect()
    {
        m_isConnected = true;
        Print("🌐 EXTERNAL DATA BRIDGE CONECTADO");
    }
    
    //------------------------------------------------------------------
    //| Obtém score de sentimento de notícias para um símbolo          |
    //------------------------------------------------------------------
    double GetNewsSentimentScore(string symbol)
    {
        int symbolIndex = GetSymbolIndex(symbol);
        
        // Verificar cache
        if (TimeCurrent() - m_lastSentimentUpdate[symbolIndex] < m_cacheTimeout) {
            return m_sentimentCache[symbolIndex];
        }
        
        // Simula chamada a API externa de sentimento
        // Em ambiente real: HTTP request para serviço Python/Node.js
        double sentiment = MathRand() / 32767.0; // RAND_MAX equivalente em MQL5
        
        // Aplicar filtros de qualidade
        sentiment = NormalizeSentiment(sentiment);
        
        // Atualizar cache
        m_sentimentCache[symbolIndex] = sentiment;
        m_lastSentimentUpdate[symbolIndex] = TimeCurrent();
        
        Print("SENTIMENT ANALYSIS | ", symbol, " SCORE: ", sentiment);
        return sentiment;
    }
    
    //------------------------------------------------------------------
    //| Obtém índice de volatilidade (VIX simulado)                   |
    //------------------------------------------------------------------
    double GetVolatilityIndex()
    {
        // Verificar cache
        if (TimeCurrent() - m_lastVolatilityUpdate < m_cacheTimeout) {
            return m_volatilityCache;
        }
        
        // Simula dados de VIX entre 0 e 50
        double volatility = MathRand() / 32767.0 * 50.0; // RAND_MAX equivalente em MQL5
        
        // Aplicar filtros de qualidade
        volatility = NormalizeVolatility(volatility);
        
        // Atualizar cache
        m_volatilityCache = volatility;
        m_lastVolatilityUpdate = TimeCurrent();
        
        Print("VOLATILITY INDEX | VIX: ", volatility);
        return volatility;
    }
    
    //------------------------------------------------------------------
    //| Copia ticks para análise                                       |
    //------------------------------------------------------------------
    bool CopyTicksData(string symbol, double &ticks[])
    {
        if(!m_isConnected) {
            Print("❌ EXTERNAL DATA BRIDGE não conectado");
            return false;
        }
        
        // Simular cópia de ticks
        int tickCount = 100;
        ArrayResize(ticks, tickCount);
        
        for(int i = 0; i < tickCount; i++) {
            ticks[i] = MathRand() / 32767.0;
        }
        
        return true;
    }
    
    //------------------------------------------------------------------
    //| Normaliza score de sentimento                                 |
    //------------------------------------------------------------------
    double NormalizeSentiment(double rawSentiment)
    {
        // Aplicar filtros para evitar valores extremos
        if (rawSentiment < 0.1) rawSentiment = 0.1;
        if (rawSentiment > 0.9) rawSentiment = 0.9;
        
        return rawSentiment;
    }
    
    //------------------------------------------------------------------
    //| Normaliza índice de volatilidade                              |
    //------------------------------------------------------------------
    double NormalizeVolatility(double rawVolatility)
    {
        // Aplicar filtros para valores realistas
        if (rawVolatility < 5.0) rawVolatility = 5.0;
        if (rawVolatility > 45.0) rawVolatility = 45.0;
        
        return rawVolatility;
    }
    
    //------------------------------------------------------------------
    //| Obtém índice do símbolo no cache                              |
    //------------------------------------------------------------------
    int GetSymbolIndex(string symbol)
    {
        string primarySymbols[5] = {"BTCUSD", "XAUUSD", "US500", "EURUSD", "BTCEUR"};
        
        for (int i = 0; i < 5; i++) {
            if (symbol == primarySymbols[i]) {
                return i;
            }
        }
        
        return 0; // Default para BTCUSD
    }
    
    //------------------------------------------------------------------
    //| Limpa cache para forçar atualização                           |
    //------------------------------------------------------------------
    void ClearCache()
    {
        for (int i = 0; i < 5; i++) {
            m_lastSentimentUpdate[i] = 0;
        }
        m_lastVolatilityUpdate = 0;
        Print("EXTERNAL DATA CACHE CLEARED");
    }
    
    //------------------------------------------------------------------
    //| Verifica se dados estão atualizados                           |
    //------------------------------------------------------------------
    bool IsDataFresh(string symbol)
    {
        int symbolIndex = GetSymbolIndex(symbol);
        return (TimeCurrent() - m_lastSentimentUpdate[symbolIndex] < m_cacheTimeout);
    }
    
    //------------------------------------------------------------------
    //| Verifica se está conectado                                    |
    //------------------------------------------------------------------
    bool IsConnected() const
    {
        return m_isConnected;
    }
    
    //------------------------------------------------------------------
    //| Inicialização Segura (MELHORADA)                              |
    //------------------------------------------------------------------
    bool Initialize()
    {
        m_isConnected = EstablishConnection();
        if(m_isConnected) {
            Print("✅ EXTERNAL DATA BRIDGE INICIALIZADO COM SUCESSO");
        } else {
            Print("❌ Falha na inicialização do EXTERNAL DATA BRIDGE");
        }
        return m_isConnected;
    }
    
    //------------------------------------------------------------------
    //| Estabelecer Conexão (NOVO)                                    |
    //------------------------------------------------------------------
    bool EstablishConnection()
    {
        // Simular processo de conexão
        Print("🌐 Tentando conectar ao sistema externo...");
        
        // Verificar se o sistema está disponível
        if(CheckSystemAvailability()) {
            m_isConnected = true;
            Print("🌐 Conexão estabelecida com sucesso");
            return true;
        } else {
            Print("❌ Sistema externo não disponível");
            return false;
        }
    }
    
    //------------------------------------------------------------------
    //| Verificar Disponibilidade do Sistema (NOVO)                   |
    //------------------------------------------------------------------
    bool CheckSystemAvailability()
    {
        // Simular verificação de disponibilidade
        // Em ambiente real: ping, HTTP request, etc.
        return true; // Sempre disponível em simulação
    }
    
    //------------------------------------------------------------------
    //| Copia Ticks Melhorada (MELHORADA)                             |
    //------------------------------------------------------------------
    bool CopyTicksEnhanced(const string symbol, double &ticks[])
    {
        if(!m_isConnected) {
            Print("⚠️ Ponte de dados não conectada");
            return false;
        }
        
        // Implementação segura da cópia de ticks usando array MqlTick
        MqlTick tickArray[];
        int copied = ::CopyTicks(symbol, tickArray, COPY_TICKS_ALL);
        if(copied <= 0) {
            Print("❌ Falha ao copiar ticks para ", symbol);
            return false;
        }
        
        // Converter MqlTick para double (preços)
        ArrayResize(ticks, copied);
        for(int i = 0; i < copied; i++) {
            ticks[i] = tickArray[i].bid; // Usar bid como representação
        }
        
        return true;
    }
    
    //------------------------------------------------------------------
    //| Recuperação Automática (NOVO)                                 |
    //------------------------------------------------------------------
    void AutoRecover()
    {
        if(!m_isConnected) {
            Print("⚡ Tentando reconexão automática...");
            for(int i = 0; i < 3; i++) {
                if(Initialize()) {
                    Print("✅ Conexão reestabelecida na tentativa ", i+1);
                    return;
                }
                Sleep(1000);
            }
            Print("❌ Falha na reconexão após 3 tentativas");
        }
    }
};

//+------------------------------------------------------------------+
//|                  FUNÇÕES LEGACY (COMPATIBILIDADE)                |
//+------------------------------------------------------------------+
// Instância global para compatibilidade
static ExternalDataBridge g_externalDataBridge;

//------------------------------------------------------------------
//| Funções de compatibilidade                                       |
//------------------------------------------------------------------
double GetNewsSentimentScore(string symbol) {
    return g_externalDataBridge.GetNewsSentimentScore(symbol);
}

double GetVolatilityIndex() {
    return g_externalDataBridge.GetVolatilityIndex();
}

void ClearCache() {
    g_externalDataBridge.ClearCache();
}

bool IsDataFresh(string symbol) {
    return g_externalDataBridge.IsDataFresh(symbol);
}

void Initialize() {
    g_externalDataBridge.Initialize();
}

#endif // EXTERNAL_DATA_BRIDGE_MQH 