#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Classe para análise de padrões de candlestick
class CCandlePatternAnalyzer {
private:
    // Estado
    bool m_isInitialized;
    double m_bodyToWickRatio;
    double m_minCandleSize;
    
    // Métodos privados
    double GetBodySize(int shift) {
        return MathAbs(iClose(_Symbol, PERIOD_CURRENT, shift) - iOpen(_Symbol, PERIOD_CURRENT, shift));
    }
    
    double GetUpperWickSize(int shift) {
        double high = iHigh(_Symbol, PERIOD_CURRENT, shift);
        double open = iOpen(_Symbol, PERIOD_CURRENT, shift);
        double close = iClose(_Symbol, PERIOD_CURRENT, shift);
        
        return high - MathMax(open, close);
    }
    
    double GetLowerWickSize(int shift) {
        double low = iLow(_Symbol, PERIOD_CURRENT, shift);
        double open = iOpen(_Symbol, PERIOD_CURRENT, shift);
        double close = iClose(_Symbol, PERIOD_CURRENT, shift);
        
        return MathMin(open, close) - low;
    }
    
    double GetTotalSize(int shift) {
        return iHigh(_Symbol, PERIOD_CURRENT, shift) - iLow(_Symbol, PERIOD_CURRENT, shift);
    }
    
public:
    // Construtor
    CCandlePatternAnalyzer() {
        m_isInitialized = false;
        m_bodyToWickRatio = 0.3;  // 30% do tamanho total
        m_minCandleSize = 0.0001; // Tamanho mínimo em pontos
    }
    
    // Destrutor
    ~CCandlePatternAnalyzer() {
        // Limpar recursos
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Verificar padrão de martelo
    bool IsHammerPattern(int shift) {
        if(!m_isInitialized) return false;
        
        double bodySize = GetBodySize(shift);
        double upperWick = GetUpperWickSize(shift);
        double lowerWick = GetLowerWickSize(shift);
        double totalSize = GetTotalSize(shift);
        
        // Verificar tamanho mínimo
        if(totalSize < m_minCandleSize) return false;
        
        // Verificar proporção corpo/mecha
        if(bodySize > totalSize * m_bodyToWickRatio) return false;
        
        // Verificar mecha inferior (deve ser pelo menos 2x o corpo)
        if(lowerWick < bodySize * 2) return false;
        
        // Verificar mecha superior (deve ser pequena)
        if(upperWick > bodySize) return false;
        
        return true;
    }
    
    // Verificar padrão de estrela cadente
    bool IsShootingStarPattern(int shift) {
        if(!m_isInitialized) return false;
        
        double bodySize = GetBodySize(shift);
        double upperWick = GetUpperWickSize(shift);
        double lowerWick = GetLowerWickSize(shift);
        double totalSize = GetTotalSize(shift);
        
        // Verificar tamanho mínimo
        if(totalSize < m_minCandleSize) return false;
        
        // Verificar proporção corpo/mecha
        if(bodySize > totalSize * m_bodyToWickRatio) return false;
        
        // Verificar mecha superior (deve ser pelo menos 2x o corpo)
        if(upperWick < bodySize * 2) return false;
        
        // Verificar mecha inferior (deve ser pequena)
        if(lowerWick > bodySize) return false;
        
        return true;
    }
    
    // Verificar padrão de doji
    bool IsDojiPattern(int shift) {
        if(!m_isInitialized) return false;
        
        double bodySize = GetBodySize(shift);
        double totalSize = GetTotalSize(shift);
        
        // Verificar tamanho mínimo
        if(totalSize < m_minCandleSize) return false;
        
        // Verificar proporção corpo/mecha (corpo deve ser muito pequeno)
        if(bodySize > totalSize * 0.1) return false;
        
        return true;
    }
    
    // Verificar padrão de engolfo de alta
    bool IsBullishEngulfingPattern(int shift) {
        if(!m_isInitialized) return false;
        
        // Verificar se o candle atual é de alta
        if(iClose(_Symbol, PERIOD_CURRENT, shift) <= iOpen(_Symbol, PERIOD_CURRENT, shift)) return false;
        
        // Verificar se o candle anterior é de baixa
        if(iClose(_Symbol, PERIOD_CURRENT, shift+1) >= iOpen(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        
        // Verificar se o corpo do candle atual engole o corpo do candle anterior
        if(iOpen(_Symbol, PERIOD_CURRENT, shift) > iClose(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        if(iClose(_Symbol, PERIOD_CURRENT, shift) < iOpen(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        
        return true;
    }
    
    // Verificar padrão de engolfo de baixa
    bool IsBearishEngulfingPattern(int shift) {
        if(!m_isInitialized) return false;
        
        // Verificar se o candle atual é de baixa
        if(iClose(_Symbol, PERIOD_CURRENT, shift) >= iOpen(_Symbol, PERIOD_CURRENT, shift)) return false;
        
        // Verificar se o candle anterior é de alta
        if(iClose(_Symbol, PERIOD_CURRENT, shift+1) <= iOpen(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        
        // Verificar se o corpo do candle atual engole o corpo do candle anterior
        if(iOpen(_Symbol, PERIOD_CURRENT, shift) < iClose(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        if(iClose(_Symbol, PERIOD_CURRENT, shift) > iOpen(_Symbol, PERIOD_CURRENT, shift+1)) return false;
        
        return true;
    }
    
    // Configurações
    void SetBodyToWickRatio(double ratio) {
        m_bodyToWickRatio = ratio;
    }
    
    void SetMinCandleSize(double size) {
        m_minCandleSize = size;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Candle Pattern Analyzer Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Body to Wick Ratio: ", m_bodyToWickRatio);
        Print("Minimum Candle Size: ", m_minCandleSize);
    }
}; 