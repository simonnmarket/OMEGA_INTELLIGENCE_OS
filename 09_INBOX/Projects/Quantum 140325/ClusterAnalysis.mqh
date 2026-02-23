#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para análise de volume
struct VolumeAnalysis {
    double price;           // Preço
    double volume;          // Volume
    double delta;           // Delta de volume
    datetime timestamp;     // Timestamp
};

// Estrutura para perfil de mercado
struct MarketProfile {
    double valueAreaHigh;   // Área de valor superior
    double valueAreaLow;    // Área de valor inferior
    double poc;             // Ponto de controle
    double volumeProfile[]; // Perfil de volume
};

// Classe para análise de cluster
class CClusterAnalysis {
private:
    // Estado
    bool m_isInitialized;
    VolumeAnalysis m_volumeData[];
    MarketProfile m_profile;
    int m_dataSize;
    
    // Métodos privados
    void CalculateVolumeDelta(const string& symbol, const ENUM_TIMEFRAME& timeframe, int period) {
        if(!m_isInitialized) return;
        
        // Limpar dados antigos
        ArrayFree(m_volumeData);
        m_dataSize = 0;
        
        // Coletar dados
        for(int i = 0; i < period; i++) {
            double close = iClose(symbol, timeframe, i);
            double volume = iVolume(symbol, timeframe, i);
            double open = iOpen(symbol, timeframe, i);
            
            // Calcular delta
            double delta = (close > open) ? volume : -volume;
            
            // Adicionar ao array
            int size = ArraySize(m_volumeData);
            ArrayResize(m_volumeData, size + 1);
            m_volumeData[size].price = close;
            m_volumeData[size].volume = volume;
            m_volumeData[size].delta = delta;
            m_volumeData[size].timestamp = iTime(symbol, timeframe, i);
            m_dataSize++;
        }
    }
    
    void CalculateMarketProfile(const string& symbol, const ENUM_TIMEFRAME& timeframe, int period) {
        if(!m_isInitialized) return;
        
        // Calcular preço médio
        double sumPrice = 0;
        double sumVolume = 0;
        for(int i = 0; i < m_dataSize; i++) {
            sumPrice += m_volumeData[i].price * m_volumeData[i].volume;
            sumVolume += m_volumeData[i].volume;
        }
        
        if(sumVolume > 0) {
            m_profile.poc = sumPrice / sumVolume;
        }
        
        // Calcular áreas de valor
        double stdDev = 0;
        for(int i = 0; i < m_dataSize; i++) {
            stdDev += MathPow(m_volumeData[i].price - m_profile.poc, 2) * m_volumeData[i].volume;
        }
        stdDev = MathSqrt(stdDev / sumVolume);
        
        m_profile.valueAreaHigh = m_profile.poc + stdDev;
        m_profile.valueAreaLow = m_profile.poc - stdDev;
        
        // Criar perfil de volume
        ArrayResize(m_profile.volumeProfile, 100);
        double priceStep = (m_profile.valueAreaHigh - m_profile.valueAreaLow) / 100;
        
        for(int i = 0; i < 100; i++) {
            double priceLevel = m_profile.valueAreaLow + i * priceStep;
            double volume = 0;
            
            for(int j = 0; j < m_dataSize; j++) {
                if(m_volumeData[j].price >= priceLevel && 
                   m_volumeData[j].price < priceLevel + priceStep) {
                    volume += m_volumeData[j].volume;
                }
            }
            
            m_profile.volumeProfile[i] = volume;
        }
    }
    
public:
    // Construtor
    CClusterAnalysis() {
        m_isInitialized = false;
        m_dataSize = 0;
    }
    
    // Destrutor
    ~CClusterAnalysis() {
        ArrayFree(m_volumeData);
        ArrayFree(m_profile.volumeProfile);
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Analisar volume e perfil
    bool AnalyzeCluster(const string& symbol, const ENUM_TIMEFRAME& timeframe, int period) {
        if(!m_isInitialized) return false;
        
        CalculateVolumeDelta(symbol, timeframe, period);
        CalculateMarketProfile(symbol, timeframe, period);
        
        return true;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetDataSize() const {
        return m_dataSize;
    }
    
    MarketProfile GetMarketProfile() const {
        return m_profile;
    }
    
    VolumeAnalysis* GetVolumeData() {
        return m_volumeData;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Cluster Analysis Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Data Size: ", m_dataSize);
        Print("POC: ", m_profile.poc);
        Print("Value Area High: ", m_profile.valueAreaHigh);
        Print("Value Area Low: ", m_profile.valueAreaLow);
    }
}; 