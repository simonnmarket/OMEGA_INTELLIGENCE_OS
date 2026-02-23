#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para níveis de escalonamento
struct ScalingLevel {
    double price;          // Preço do nível
    double volume;         // Volume para este nível
    double risk;           // Risco associado
    bool isActive;         // Status do nível
};

// Estrutura para métricas de escalonamento
struct ScalingMetrics {
    double currentVolume;  // Volume atual
    double maxVolume;      // Volume máximo permitido
    double avgEntryPrice;  // Preço médio de entrada
    double totalRisk;      // Risco total
    bool isValid;         // Validação
};

// Classe do Sistema de Escalonamento
class CScalingSystem {
private:
    // Configurações
    double m_maxRiskPerTrade;    // Risco máximo por operação
    double m_maxTotalRisk;       // Risco total máximo
    double m_volumeStep;         // Passo de volume
    double m_priceStep;          // Passo de preço
    
    // Estado
    bool m_isInitialized;
    ScalingLevel m_levels[];
    ScalingMetrics m_metrics;
    
    // Métodos privados
    bool ValidateLevel(const ScalingLevel& level) {
        // Validar preço
        if(level.price <= 0) return false;
        
        // Validar volume
        if(level.volume <= 0 || level.volume > m_metrics.maxVolume) return false;
        
        // Validar risco
        if(level.risk <= 0 || level.risk > m_maxRiskPerTrade) return false;
        
        return true;
    }
    
    double CalculateTotalRisk() {
        double totalRisk = 0.0;
        
        for(int i = 0; i < ArraySize(m_levels); i++) {
            if(m_levels[i].isActive) {
                totalRisk += m_levels[i].risk;
            }
        }
        
        return totalRisk;
    }
    
    double CalculateAvgEntryPrice() {
        double totalVolume = 0.0;
        double weightedPrice = 0.0;
        
        for(int i = 0; i < ArraySize(m_levels); i++) {
            if(m_levels[i].isActive) {
                totalVolume += m_levels[i].volume;
                weightedPrice += m_levels[i].price * m_levels[i].volume;
            }
        }
        
        if(totalVolume == 0) return 0.0;
        return weightedPrice / totalVolume;
    }
    
    void UpdateMetrics() {
        m_metrics.currentVolume = 0.0;
        
        for(int i = 0; i < ArraySize(m_levels); i++) {
            if(m_levels[i].isActive) {
                m_metrics.currentVolume += m_levels[i].volume;
            }
        }
        
        m_metrics.avgEntryPrice = CalculateAvgEntryPrice();
        m_metrics.totalRisk = CalculateTotalRisk();
        m_metrics.isValid = true;
    }
    
public:
    // Construtor
    CScalingSystem() {
        m_maxRiskPerTrade = 0.02;    // 2% por nível
        m_maxTotalRisk = 0.1;        // 10% total
        m_volumeStep = 0.1;          // 10% do volume base
        m_priceStep = 0.001;         // 0.1% do preço
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize(const double& maxVolume) {
        if(maxVolume <= 0) return false;
        
        m_metrics.maxVolume = maxVolume;
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar nível de escalonamento
    bool AddLevel(const double& price,
                 const double& volume,
                 const double& risk) {
        if(!m_isInitialized) return false;
        
        ScalingLevel level;
        level.price = price;
        level.volume = volume;
        level.risk = risk;
        level.isActive = true;
        
        if(!ValidateLevel(level)) return false;
        
        // Verificar risco total
        double newTotalRisk = m_metrics.totalRisk + risk;
        if(newTotalRisk > m_maxTotalRisk) return false;
        
        int size = ArraySize(m_levels);
        ArrayResize(m_levels, size + 1);
        m_levels[size] = level;
        
        UpdateMetrics();
        return true;
    }
    
    // Remover nível de escalonamento
    bool RemoveLevel(const int& index) {
        if(!m_isInitialized || index < 0 || index >= ArraySize(m_levels)) {
            return false;
        }
        
        m_levels[index].isActive = false;
        UpdateMetrics();
        return true;
    }
    
    // Calcular próximo nível
    bool CalculateNextLevel(const double& currentPrice,
                          const double& direction,
                          ScalingLevel& nextLevel) {
        if(!m_isInitialized) return false;
        
        // Calcular preço do próximo nível
        double priceStep = m_priceStep * currentPrice;
        double nextPrice = currentPrice + (direction * priceStep);
        
        // Calcular volume do próximo nível
        double nextVolume = m_volumeStep * m_metrics.maxVolume;
        
        // Calcular risco do próximo nível
        double nextRisk = m_maxRiskPerTrade;
        
        // Criar nível
        nextLevel.price = nextPrice;
        nextLevel.volume = nextVolume;
        nextLevel.risk = nextRisk;
        nextLevel.isActive = true;
        
        return ValidateLevel(nextLevel);
    }
    
    // Obter métricas atuais
    ScalingMetrics GetMetrics() const {
        return m_metrics;
    }
    
    // Obter níveis ativos
    void GetActiveLevels(ScalingLevel& levels[]) {
        ArrayFree(levels);
        
        for(int i = 0; i < ArraySize(m_levels); i++) {
            if(m_levels[i].isActive) {
                int size = ArraySize(levels);
                ArrayResize(levels, size + 1);
                levels[size] = m_levels[i];
            }
        }
    }
    
    // Métodos de configuração
    void SetMaxRiskPerTrade(double risk) {
        m_maxRiskPerTrade = risk;
    }
    
    void SetMaxTotalRisk(double risk) {
        m_maxTotalRisk = risk;
    }
    
    void SetVolumeStep(double step) {
        m_volumeStep = step;
    }
    
    void SetPriceStep(double step) {
        m_priceStep = step;
    }
    
    // Métodos de acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 