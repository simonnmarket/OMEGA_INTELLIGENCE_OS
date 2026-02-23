#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados estatísticos
struct StatisticalData {
    double brownianMotion;     // Movimento browniano
    double volatility;         // Volatilidade
    double patternConfidence;  // Confiança do padrão
    bool isValid;             // Validação
};

// Classe do Agente de Análise Estatística
class CStatisticalAnalysisAgent {
private:
    // Configurações
    int m_lookbackPeriod;      // Período de análise
    double m_volatilityThreshold; // Limiar de volatilidade
    double m_patternThreshold;    // Limiar de padrão
    
    // Estado
    bool m_isInitialized;
    StatisticalData m_currentData;
    
    // Métodos privados
    double CalculateBrownianMotion(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        double sum = 0.0;
        for(int i = 1; i < size; i++) {
            double diff = prices[i-1] - prices[i];
            sum += diff * diff;
        }
        
        return MathSqrt(sum / (size - 1));
    }
    
    double CalculateVolatility(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        double mean = 0.0;
        for(int i = 0; i < size; i++) {
            mean += prices[i];
        }
        mean /= size;
        
        double sumSquaredDiff = 0.0;
        for(int i = 0; i < size; i++) {
            double diff = prices[i] - mean;
            sumSquaredDiff += diff * diff;
        }
        
        return MathSqrt(sumSquaredDiff / size);
    }
    
    double CalculatePatternConfidence(const VolumeMetrics& metrics) {
        double confidence = 0.0;
        
        // Fatores de confiança
        confidence += MathAbs(metrics.trendStrength) * 0.4;
        confidence += MathAbs(metrics.momentum) * 0.3;
        confidence += (metrics.skewness * metrics.kurtosis) * 0.3;
        
        return MathMin(MathMax(confidence, 0.0), 1.0);
    }
    
public:
    // Construtor
    CStatisticalAnalysisAgent() {
        m_lookbackPeriod = 20;
        m_volatilityThreshold = 0.0001;
        m_patternThreshold = 0.7;
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Processamento de dados
    void ProcessData(const VolumeMetrics& metrics) {
        if(!m_isInitialized) return;
        
        // Calcular métricas estatísticas
        m_currentData.brownianMotion = CalculateBrownianMotion(metrics.prices, m_lookbackPeriod);
        m_currentData.volatility = CalculateVolatility(metrics.prices, m_lookbackPeriod);
        m_currentData.patternConfidence = CalculatePatternConfidence(metrics);
        m_currentData.isValid = true;
    }
    
    // Obter decisão
    double GetDecision() const {
        if(!m_currentData.isValid) return 0.0;
        
        double decision = 0.0;
        
        // Fatores de decisão
        if(m_currentData.volatility > m_volatilityThreshold) {
            decision += 0.4;
        }
        if(m_currentData.patternConfidence > m_patternThreshold) {
            decision += 0.4;
        }
        if(m_currentData.brownianMotion > 0) {
            decision += 0.2;
        }
        
        return MathMin(MathMax(decision, -1.0), 1.0);
    }
    
    // Métodos de configuração
    void SetLookbackPeriod(int period) {
        m_lookbackPeriod = period;
    }
    
    void SetVolatilityThreshold(double threshold) {
        m_volatilityThreshold = threshold;
    }
    
    void SetPatternThreshold(double threshold) {
        m_patternThreshold = threshold;
    }
    
    // Métodos de acesso
    StatisticalData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 