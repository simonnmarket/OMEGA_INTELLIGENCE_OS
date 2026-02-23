#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados de validação
struct ValidationData {
    bool supportResistanceValid;  // Validação de suporte/resistência
    bool volumeProfileValid;      // Validação do perfil de volume
    bool priceEquilibriumValid;   // Validação do equilíbrio de preço
    bool riskMetricsValid;        // Validação das métricas de risco
    double rewardRiskRatio;       // Razão recompensa/risco
    double potentialLoss;         // Perda potencial
    double marketExposure;        // Exposição ao mercado
    bool isValid;                // Validação geral
};

// Classe do Sistema de Testes Pré-Operação
class CPreTradeAnalysis {
private:
    // Configurações
    double m_minRewardRiskRatio;  // Razão mínima recompensa/risco
    double m_maxPotentialLoss;    // Perda máxima permitida
    double m_maxMarketExposure;   // Exposição máxima ao mercado
    
    // Estado
    bool m_isInitialized;
    ValidationData m_currentData;
    
    // Métodos privados
    bool ValidateSupportResistance(const double& currentPrice,
                                 const double& nearestSupport,
                                 const double& nearestResistance) {
        // Verificar distância aos níveis
        double supportDistance = MathAbs(currentPrice - nearestSupport);
        double resistanceDistance = MathAbs(nearestResistance - currentPrice);
        
        // Requer distância mínima dos níveis
        return (supportDistance > 0.0001 && resistanceDistance > 0.0001);
    }
    
    bool ValidateVolumeProfile(const VolumeMetrics& metrics) {
        // Verificar força do volume
        return (MathAbs(metrics.volumeImbalance) > 0.1 &&
                metrics.trendStrength > 0.5);
    }
    
    bool ValidatePriceEquilibrium(const double& currentPrice,
                                const double& equilibriumPrice) {
        // Verificar distância do equilíbrio
        double distance = MathAbs(currentPrice - equilibriumPrice);
        return (distance < 0.001);
    }
    
    double CalculateRewardRiskRatio(const double& takeProfit,
                                   const double& stopLoss,
                                   const double& currentPrice) {
        double reward = MathAbs(takeProfit - currentPrice);
        double risk = MathAbs(currentPrice - stopLoss);
        
        if(risk == 0) return 0.0;
        return reward / risk;
    }
    
    double CalculatePotentialLoss(const double& positionSize,
                                 const double& stopLoss,
                                 const double& currentPrice) {
        return positionSize * MathAbs(currentPrice - stopLoss);
    }
    
    double CalculateMarketExposure(const double& positionSize,
                                  const double& accountBalance) {
        return positionSize / accountBalance;
    }
    
public:
    // Construtor
    CPreTradeAnalysis() {
        m_minRewardRiskRatio = 1.5;  // 1:1.5
        m_maxPotentialLoss = 0.02;   // 2% do capital
        m_maxMarketExposure = 0.5;   // 50% do capital
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Análise pré-operação
    void AnalyzePreTrade(const double& currentPrice,
                        const double& takeProfit,
                        const double& stopLoss,
                        const double& nearestSupport,
                        const double& nearestResistance,
                        const double& equilibriumPrice,
                        const VolumeMetrics& metrics,
                        const double& positionSize,
                        const double& accountBalance) {
        if(!m_isInitialized) return;
        
        // Validar níveis
        m_currentData.supportResistanceValid = ValidateSupportResistance(
            currentPrice, nearestSupport, nearestResistance);
        
        // Validar volume
        m_currentData.volumeProfileValid = ValidateVolumeProfile(metrics);
        
        // Validar equilíbrio
        m_currentData.priceEquilibriumValid = ValidatePriceEquilibrium(
            currentPrice, equilibriumPrice);
        
        // Calcular métricas de risco
        m_currentData.rewardRiskRatio = CalculateRewardRiskRatio(
            takeProfit, stopLoss, currentPrice);
        
        m_currentData.potentialLoss = CalculatePotentialLoss(
            positionSize, stopLoss, currentPrice);
        
        m_currentData.marketExposure = CalculateMarketExposure(
            positionSize, accountBalance);
        
        // Validar métricas de risco
        m_currentData.riskMetricsValid = (
            m_currentData.rewardRiskRatio >= m_minRewardRiskRatio &&
            m_currentData.potentialLoss <= m_maxPotentialLoss &&
            m_currentData.marketExposure <= m_maxMarketExposure
        );
        
        // Validar geral
        m_currentData.isValid = (
            m_currentData.supportResistanceValid &&
            m_currentData.volumeProfileValid &&
            m_currentData.priceEquilibriumValid &&
            m_currentData.riskMetricsValid
        );
    }
    
    // Verificar aprovação
    bool IsApproved() const {
        if(!m_isInitialized) return false;
        return m_currentData.isValid;
    }
    
    // Métodos de configuração
    void SetMinRewardRiskRatio(double ratio) {
        m_minRewardRiskRatio = ratio;
    }
    
    void SetMaxPotentialLoss(double loss) {
        m_maxPotentialLoss = loss;
    }
    
    void SetMaxMarketExposure(double exposure) {
        m_maxMarketExposure = exposure;
    }
    
    // Métodos de acesso
    ValidationData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 