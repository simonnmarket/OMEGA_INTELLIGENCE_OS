#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Constante Pi
#define PI 3.14159265359

// Estrutura para dados cíclicos
struct CyclicData {
    double cycleProgress;     // Progresso do ciclo
    double cycleStrength;     // Força do ciclo
    double cyclePhase;        // Fase do ciclo
    bool isValid;            // Validação
};

// Classe de Análise Cíclica Baseada em Pi
class CPiCyclicAnalysis {
private:
    // Configurações
    int m_shortTermPeriod;    // Período curto prazo (π * 24)
    int m_mediumTermPeriod;   // Período médio prazo (π * 7)
    int m_longTermPeriod;     // Período longo prazo (π * 30)
    double m_strengthThreshold; // Limiar de força
    
    // Estado
    bool m_isInitialized;
    CyclicData m_currentData;
    
    // Métodos privados
    double CalculateCycleProgress(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        // Calcular progresso baseado em π
        double progress = 0.0;
        
        for(int i = 1; i < size; i++) {
            double priceChange = prices[i-1] - prices[i];
            progress += MathSin(priceChange * PI);
        }
        
        return MathMin(MathMax(progress / size, 0.0), 1.0);
    }
    
    double CalculateCycleStrength(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        // Calcular força baseada em π
        double strength = 0.0;
        
        for(int i = 1; i < size; i++) {
            double priceChange = prices[i-1] - prices[i];
            strength += MathAbs(MathCos(priceChange * PI));
        }
        
        return MathMin(strength / size, 1.0);
    }
    
    double CalculateCyclePhase(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        // Calcular fase baseada em π
        double phase = 0.0;
        
        for(int i = 1; i < size; i++) {
            double priceChange = prices[i-1] - prices[i];
            phase += MathAtan2(priceChange, 1.0) / PI;
        }
        
        return MathMin(MathMax(phase / size, 0.0), 1.0);
    }
    
public:
    // Construtor
    CPiCyclicAnalysis() {
        m_shortTermPeriod = (int)(PI * 24);
        m_mediumTermPeriod = (int)(PI * 7);
        m_longTermPeriod = (int)(PI * 30);
        m_strengthThreshold = 0.7;
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Análise de ciclos
    void AnalyzeCycles(const double& prices[], int size) {
        if(!m_isInitialized) return;
        
        // Calcular métricas cíclicas
        m_currentData.cycleProgress = CalculateCycleProgress(prices, size);
        m_currentData.cycleStrength = CalculateCycleStrength(prices, size);
        m_currentData.cyclePhase = CalculateCyclePhase(prices, size);
        m_currentData.isValid = true;
    }
    
    // Obter decisão
    double GetDecision() const {
        if(!m_currentData.isValid) return 0.0;
        
        double decision = 0.0;
        
        // Fatores de decisão
        if(m_currentData.cycleStrength > m_strengthThreshold) {
            decision += 0.4;
        }
        if(m_currentData.cycleProgress > 0.5) {
            decision += 0.3;
        }
        if(m_currentData.cyclePhase > 0.5) {
            decision += 0.3;
        }
        
        return MathMin(MathMax(decision, -1.0), 1.0);
    }
    
    // Métodos de configuração
    void SetShortTermPeriod(int period) {
        m_shortTermPeriod = period;
    }
    
    void SetMediumTermPeriod(int period) {
        m_mediumTermPeriod = period;
    }
    
    void SetLongTermPeriod(int period) {
        m_longTermPeriod = period;
    }
    
    void SetStrengthThreshold(double threshold) {
        m_strengthThreshold = threshold;
    }
    
    // Métodos de acesso
    CyclicData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 