#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados estratégicos
struct StrategyData {
    double entrySignal;       // Sinal de entrada (-1 a 1)
    double exitSignal;        // Sinal de saída (-1 a 1)
    double takeProfitLevel;   // Nível de Take Profit
    double stopLossLevel;     // Nível de Stop Loss
    bool isValid;            // Validação
};

// Classe do Agente Estratégico
class CQuantumTrader {
private:
    // Configurações
    double m_tpMultiplier;    // Multiplicador do Take Profit
    double m_slMultiplier;    // Multiplicador do Stop Loss
    double m_signalThreshold; // Limiar de sinal
    
    // Estado
    bool m_isInitialized;
    StrategyData m_currentData;
    
    // Métodos privados
    double CalculateEntrySignal(const VolumeMetrics& metrics,
                               const StatisticalData& stats,
                               const QuantumData& quantum) {
        double signal = 0.0;
        
        // Fatores de entrada
        signal += metrics.trendStrength * 0.3;
        signal += stats.patternConfidence * 0.2;
        signal += quantum.entanglement * 0.2;
        signal += (metrics.volumeImbalance > 0 ? 1 : -1) * 0.3;
        
        return MathMin(MathMax(signal, -1.0), 1.0);
    }
    
    double CalculateExitSignal(const VolumeMetrics& metrics,
                              const StatisticalData& stats,
                              const QuantumData& quantum) {
        double signal = 0.0;
        
        // Fatores de saída
        signal += (metrics.trendStrength < 0 ? 1 : -1) * 0.3;
        signal += (1.0 - stats.patternConfidence) * 0.2;
        signal += (1.0 - quantum.entanglement) * 0.2;
        signal += (metrics.volumeImbalance < 0 ? 1 : -1) * 0.3;
        
        return MathMin(MathMax(signal, -1.0), 1.0);
    }
    
    double CalculateTakeProfit(const double& currentPrice,
                              const double& entryPrice,
                              const double& atr) {
        double direction = (currentPrice > entryPrice) ? 1.0 : -1.0;
        return currentPrice + (atr * m_tpMultiplier * direction);
    }
    
    double CalculateStopLoss(const double& currentPrice,
                            const double& entryPrice,
                            const double& atr) {
        double direction = (currentPrice > entryPrice) ? 1.0 : -1.0;
        return currentPrice - (atr * m_slMultiplier * direction);
    }
    
public:
    // Construtor
    CQuantumTrader() {
        m_tpMultiplier = 2.0;
        m_slMultiplier = 1.0;
        m_signalThreshold = 0.7;
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Análise de mercado
    void AnalyzeMarket(const VolumeMetrics& metrics,
                      const StatisticalData& stats,
                      const QuantumData& quantum,
                      const double& currentPrice,
                      const double& entryPrice,
                      const double& atr) {
        if(!m_isInitialized) return;
        
        // Calcular sinais
        m_currentData.entrySignal = CalculateEntrySignal(metrics, stats, quantum);
        m_currentData.exitSignal = CalculateExitSignal(metrics, stats, quantum);
        
        // Calcular níveis
        m_currentData.takeProfitLevel = CalculateTakeProfit(currentPrice, entryPrice, atr);
        m_currentData.stopLossLevel = CalculateStopLoss(currentPrice, entryPrice, atr);
        
        m_currentData.isValid = true;
    }
    
    // Obter decisão
    double GetDecision() const {
        if(!m_currentData.isValid) return 0.0;
        
        // Combinar sinais
        double decision = (m_currentData.entrySignal + m_currentData.exitSignal) / 2.0;
        
        // Aplicar limiar
        if(MathAbs(decision) < m_signalThreshold) {
            decision = 0.0;
        }
        
        return decision;
    }
    
    // Métodos de configuração
    void SetTPMultiplier(double multiplier) {
        m_tpMultiplier = multiplier;
    }
    
    void SetSLMultiplier(double multiplier) {
        m_slMultiplier = multiplier;
    }
    
    void SetSignalThreshold(double threshold) {
        m_signalThreshold = threshold;
    }
    
    // Métodos de acesso
    StrategyData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 