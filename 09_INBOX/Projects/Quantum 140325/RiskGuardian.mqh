#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados de risco
struct RiskData {
    double maxDrawdown;        // Máximo drawdown
    double currentDrawdown;    // Drawdown atual
    double riskExposure;       // Exposição ao risco
    double riskScore;          // Pontuação de risco
    bool isValid;             // Validação
};

// Classe do Agente de Gestão de Risco
class CRiskGuardian {
private:
    // Configurações
    double m_maxRiskPerTrade;  // Risco máximo por operação
    double m_maxDrawdownLimit; // Limite máximo de drawdown
    double m_maxExposure;      // Exposição máxima permitida
    
    // Estado
    bool m_isInitialized;
    RiskData m_currentData;
    double m_peakBalance;      // Saldo máximo histórico
    
    // Métodos privados
    double CalculateDrawdown(const double& currentBalance) {
        if(currentBalance > m_peakBalance) {
            m_peakBalance = currentBalance;
        }
        
        return (m_peakBalance - currentBalance) / m_peakBalance;
    }
    
    double CalculateRiskExposure(const double& positionSize,
                                const double& accountBalance) {
        return positionSize / accountBalance;
    }
    
    double CalculateRiskScore(const double& currentDrawdown,
                             const double& riskExposure,
                             const double& volatility) {
        double score = 0.0;
        
        // Fatores de risco
        score += currentDrawdown * 0.4;
        score += riskExposure * 0.3;
        score += volatility * 0.3;
        
        return MathMin(MathMax(score, 0.0), 1.0);
    }
    
public:
    // Construtor
    CRiskGuardian() {
        m_maxRiskPerTrade = 0.02;  // 2% por operação
        m_maxDrawdownLimit = 0.1;   // 10% máximo
        m_maxExposure = 0.5;        // 50% máximo
        m_peakBalance = 0.0;
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Análise de risco
    void AnalyzeRisk(const double& currentBalance,
                    const double& positionSize,
                    const double& volatility) {
        if(!m_isInitialized) return;
        
        // Calcular métricas de risco
        m_currentData.currentDrawdown = CalculateDrawdown(currentBalance);
        m_currentData.riskExposure = CalculateRiskExposure(positionSize, currentBalance);
        m_currentData.riskScore = CalculateRiskScore(
            m_currentData.currentDrawdown,
            m_currentData.riskExposure,
            volatility
        );
        
        // Atualizar máximo drawdown
        if(m_currentData.currentDrawdown > m_currentData.maxDrawdown) {
            m_currentData.maxDrawdown = m_currentData.currentDrawdown;
        }
        
        m_currentData.isValid = true;
    }
    
    // Verificar limites de risco
    bool CheckRiskLimits() const {
        if(!m_currentData.isValid) return false;
        
        // Verificar drawdown
        if(m_currentData.currentDrawdown > m_maxDrawdownLimit) {
            return false;
        }
        
        // Verificar exposição
        if(m_currentData.riskExposure > m_maxExposure) {
            return false;
        }
        
        // Verificar pontuação de risco
        if(m_currentData.riskScore > 0.8) {
            return false;
        }
        
        return true;
    }
    
    // Calcular tamanho de posição seguro
    double CalculateSafePositionSize(const double& accountBalance,
                                   const double& currentPrice,
                                   const double& stopLoss) {
        double riskAmount = accountBalance * m_maxRiskPerTrade;
        double priceRisk = MathAbs(currentPrice - stopLoss);
        
        if(priceRisk == 0) return 0.0;
        
        return riskAmount / priceRisk;
    }
    
    // Métodos de configuração
    void SetMaxRiskPerTrade(double risk) {
        m_maxRiskPerTrade = risk;
    }
    
    void SetMaxDrawdownLimit(double limit) {
        m_maxDrawdownLimit = limit;
    }
    
    void SetMaxExposure(double exposure) {
        m_maxExposure = exposure;
    }
    
    // Métodos de acesso
    RiskData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 