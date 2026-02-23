#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para dados de mercado
struct MarketData {
    double supportLevels[];    // Níveis de suporte
    double resistanceLevels[]; // Níveis de resistência
    double priceEquilibrium;   // Equilíbrio de preço
    double supplyDemandRatio;  // Razão oferta/demanda
    bool isValid;             // Validação
};

// Classe do Agente de Análise de Mercado
class CMarketReader {
private:
    // Configurações
    int m_lookbackPeriod;      // Período de análise
    int m_maxLevels;           // Máximo de níveis
    double m_levelThreshold;   // Limiar para níveis
    
    // Estado
    bool m_isInitialized;
    MarketData m_currentData;
    
    // Métodos privados
    void FindSupportResistance(const double& prices[], int size) {
        // Limpar arrays
        ArrayFree(m_currentData.supportLevels);
        ArrayFree(m_currentData.resistanceLevels);
        
        // Encontrar níveis
        for(int i = 2; i < size-2; i++) {
            // Suporte
            if(prices[i] < prices[i-1] && prices[i] < prices[i-2] &&
               prices[i] < prices[i+1] && prices[i] < prices[i+2]) {
                ArrayResize(m_currentData.supportLevels, ArraySize(m_currentData.supportLevels) + 1);
                m_currentData.supportLevels[ArraySize(m_currentData.supportLevels)-1] = prices[i];
            }
            
            // Resistência
            if(prices[i] > prices[i-1] && prices[i] > prices[i-2] &&
               prices[i] > prices[i+1] && prices[i] > prices[i+2]) {
                ArrayResize(m_currentData.resistanceLevels, ArraySize(m_currentData.resistanceLevels) + 1);
                m_currentData.resistanceLevels[ArraySize(m_currentData.resistanceLevels)-1] = prices[i];
            }
        }
        
        // Limitar número de níveis
        if(ArraySize(m_currentData.supportLevels) > m_maxLevels) {
            ArrayResize(m_currentData.supportLevels, m_maxLevels);
        }
        if(ArraySize(m_currentData.resistanceLevels) > m_maxLevels) {
            ArrayResize(m_currentData.resistanceLevels, m_maxLevels);
        }
    }
    
    double CalculatePriceEquilibrium(const double& prices[], int size) {
        if(size < 2) return 0.0;
        
        double sum = 0.0;
        for(int i = 0; i < size; i++) {
            sum += prices[i];
        }
        
        return sum / size;
    }
    
    double CalculateSupplyDemandRatio(const VolumeMetrics& metrics) {
        double ratio = 0.0;
        
        // Calcular razão baseada em volume e preço
        if(metrics.volumeImbalance != 0) {
            ratio = metrics.volumeImbalance / MathAbs(metrics.volumeImbalance);
        }
        
        return ratio;
    }
    
public:
    // Construtor
    CMarketReader() {
        m_lookbackPeriod = 20;
        m_maxLevels = 5;
        m_levelThreshold = 0.0001;
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Análise de mercado
    void AnalyzeMarket(const double& prices[], int size,
                      const VolumeMetrics& metrics) {
        if(!m_isInitialized) return;
        
        // Encontrar níveis
        FindSupportResistance(prices, size);
        
        // Calcular equilíbrio
        m_currentData.priceEquilibrium = CalculatePriceEquilibrium(prices, size);
        
        // Calcular razão oferta/demanda
        m_currentData.supplyDemandRatio = CalculateSupplyDemandRatio(metrics);
        
        m_currentData.isValid = true;
    }
    
    // Obter níveis mais próximos
    void GetNearestLevels(const double& currentPrice,
                         double& nearestSupport,
                         double& nearestResistance) {
        if(!m_currentData.isValid) return;
        
        // Encontrar suporte mais próximo
        nearestSupport = currentPrice;
        for(int i = 0; i < ArraySize(m_currentData.supportLevels); i++) {
            if(m_currentData.supportLevels[i] < currentPrice &&
               m_currentData.supportLevels[i] > nearestSupport) {
                nearestSupport = m_currentData.supportLevels[i];
            }
        }
        
        // Encontrar resistência mais próxima
        nearestResistance = currentPrice;
        for(int i = 0; i < ArraySize(m_currentData.resistanceLevels); i++) {
            if(m_currentData.resistanceLevels[i] > currentPrice &&
               m_currentData.resistanceLevels[i] < nearestResistance) {
                nearestResistance = m_currentData.resistanceLevels[i];
            }
        }
    }
    
    // Métodos de configuração
    void SetLookbackPeriod(int period) {
        m_lookbackPeriod = period;
    }
    
    void SetMaxLevels(int max) {
        m_maxLevels = max;
    }
    
    void SetLevelThreshold(double threshold) {
        m_levelThreshold = threshold;
    }
    
    // Métodos de acesso
    MarketData GetData() const {
        return m_currentData;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 