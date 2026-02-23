#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para condições de mercado
struct MarketConditions {
    bool isTradingTime;     // Horário de negociação
    bool hasHighImpactEvent; // Evento de alto impacto
    double rsiValue;        // Valor do RSI
    double macdValue;       // Valor do MACD
    double macdSignal;      // Sinal do MACD
    double bbUpper;         // Banda superior de Bollinger
    double bbMiddle;        // Banda média de Bollinger
    double bbLower;         // Banda inferior de Bollinger
    bool hasHammerPattern;  // Padrão de martelo
    double volatility;      // Volatilidade
};

// Classe para análise de mercado
class CMarketAnalyzer {
private:
    // Handles dos indicadores
    int m_rsiHandle;
    int m_macdHandle;
    int m_bbHandle;
    
    // Configurações
    int m_rsiPeriod;
    int m_macdFastPeriod;
    int m_macdSlowPeriod;
    int m_macdSignalPeriod;
    int m_bbPeriod;
    double m_bbDeviation;
    
    // Buffers
    double m_rsiBuffer[];
    double m_macdBuffer[];
    double m_macdSignalBuffer[];
    double m_bbUpperBuffer[];
    double m_bbMiddleBuffer[];
    double m_bbLowerBuffer[];
    
    // Estado
    bool m_isInitialized;
    
    // Métodos privados
    bool InitializeIndicators() {
        // Inicializar RSI
        m_rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, m_rsiPeriod, PRICE_CLOSE);
        if(m_rsiHandle == INVALID_HANDLE) return false;
        
        // Inicializar MACD
        m_macdHandle = iMACD(_Symbol, PERIOD_CURRENT, m_macdFastPeriod,
                            m_macdSlowPeriod, m_macdSignalPeriod, PRICE_CLOSE);
        if(m_macdHandle == INVALID_HANDLE) return false;
        
        // Inicializar Bollinger Bands
        m_bbHandle = iBands(_Symbol, PERIOD_CURRENT, m_bbPeriod, 0,
                          m_bbDeviation, PRICE_CLOSE);
        if(m_bbHandle == INVALID_HANDLE) return false;
        
        return true;
    }
    
    bool CheckTradingTime() {
        datetime currentTime = TimeCurrent();
        MqlDateTime dt;
        TimeToStruct(currentTime, dt);
        
        // Verificar horário de negociação (exemplo: 9:00-16:00)
        return dt.hour >= 9 && dt.hour < 16;
    }
    
    bool DetectHammerPattern() {
        double open[], high[], low[], close[];
        ArraySetAsSeries(open, true);
        ArraySetAsSeries(high, true);
        ArraySetAsSeries(low, true);
        ArraySetAsSeries(close, true);
        
        CopyOpen(_Symbol, PERIOD_CURRENT, 0, 3, open);
        CopyHigh(_Symbol, PERIOD_CURRENT, 0, 3, high);
        CopyLow(_Symbol, PERIOD_CURRENT, 0, 3, low);
        CopyClose(_Symbol, PERIOD_CURRENT, 0, 3, close);
        
        // Detectar padrão de martelo
        double bodySize = MathAbs(close[0] - open[0]);
        double lowerWick = MathMin(open[0], close[0]) - low[0];
        double upperWick = high[0] - MathMax(open[0], close[0]);
        
        return lowerWick > 2 * bodySize && upperWick < bodySize;
    }
    
    void UpdateIndicators() {
        // Atualizar RSI
        CopyBuffer(m_rsiHandle, 0, 0, 1, m_rsiBuffer);
        
        // Atualizar MACD
        CopyBuffer(m_macdHandle, 0, 0, 1, m_macdBuffer);
        CopyBuffer(m_macdHandle, 1, 0, 1, m_macdSignalBuffer);
        
        // Atualizar Bollinger Bands
        CopyBuffer(m_bbHandle, 1, 0, 1, m_bbUpperBuffer);
        CopyBuffer(m_bbHandle, 0, 0, 1, m_bbMiddleBuffer);
        CopyBuffer(m_bbHandle, 2, 0, 1, m_bbLowerBuffer);
    }
    
public:
    // Construtor
    CMarketAnalyzer() {
        // Configurações padrão
        m_rsiPeriod = 14;
        m_macdFastPeriod = 12;
        m_macdSlowPeriod = 26;
        m_macdSignalPeriod = 9;
        m_bbPeriod = 20;
        m_bbDeviation = 2.0;
        
        m_isInitialized = false;
        m_rsiHandle = INVALID_HANDLE;
        m_macdHandle = INVALID_HANDLE;
        m_bbHandle = INVALID_HANDLE;
    }
    
    // Destrutor
    ~CMarketAnalyzer() {
        // Liberar handles dos indicadores
        IndicatorRelease(m_rsiHandle);
        IndicatorRelease(m_macdHandle);
        IndicatorRelease(m_bbHandle);
    }
    
    // Inicialização
    bool Initialize() {
        if(!InitializeIndicators()) return false;
        m_isInitialized = true;
        return true;
    }
    
    // Analisar condições de mercado
    MarketConditions AnalyzeMarketConditions() {
        MarketConditions conditions = {};
        
        if(!m_isInitialized) return conditions;
        
        // Atualizar indicadores
        UpdateIndicators();
        
        // Verificar horário de negociação
        conditions.isTradingTime = CheckTradingTime();
        
        // Verificar evento de alto impacto
        conditions.hasHighImpactEvent = false; // Implementar verificação de eventos
        
        // Atualizar valores dos indicadores
        conditions.rsiValue = m_rsiBuffer[0];
        conditions.macdValue = m_macdBuffer[0];
        conditions.macdSignal = m_macdSignalBuffer[0];
        conditions.bbUpper = m_bbUpperBuffer[0];
        conditions.bbMiddle = m_bbMiddleBuffer[0];
        conditions.bbLower = m_bbLowerBuffer[0];
        
        // Detectar padrão de martelo
        conditions.hasHammerPattern = DetectHammerPattern();
        
        // Calcular volatilidade
        double high[], low[];
        ArraySetAsSeries(high, true);
        ArraySetAsSeries(low, true);
        
        CopyHigh(_Symbol, PERIOD_CURRENT, 0, 20, high);
        CopyLow(_Symbol, PERIOD_CURRENT, 0, 20, low);
        
        double sumRange = 0;
        for(int i = 0; i < 20; i++) {
            sumRange += high[i] - low[i];
        }
        conditions.volatility = sumRange / 20;
        
        return conditions;
    }
    
    // Configurações
    void SetRSIPeriod(int period) {
        m_rsiPeriod = period;
        if(m_isInitialized) {
            IndicatorRelease(m_rsiHandle);
            InitializeIndicators();
        }
    }
    
    void SetMACDPeriods(int fast, int slow, int signal) {
        m_macdFastPeriod = fast;
        m_macdSlowPeriod = slow;
        m_macdSignalPeriod = signal;
        if(m_isInitialized) {
            IndicatorRelease(m_macdHandle);
            InitializeIndicators();
        }
    }
    
    void SetBBPeriods(int period, double deviation) {
        m_bbPeriod = period;
        m_bbDeviation = deviation;
        if(m_isInitialized) {
            IndicatorRelease(m_bbHandle);
            InitializeIndicators();
        }
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 