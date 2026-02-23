#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Enumeradores
enum ENUM_WAVE_TYPE {
    UP_WAVE,
    DOWN_WAVE,
    NEUTRAL_WAVE
};

enum ENUM_ALERT_TYPE {
    INSTITUTIONAL_ACTIVITY,
    HIDDEN_ACCUMULATION,
    VOLUME_SPIKE,
    PRICE_REVERSAL
};

//+------------------------------------------------------------------+
//| Classe WeisWaveAnalysis                                           |
//+------------------------------------------------------------------+
class CWeisWaveAnalysis {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    
    // Estruturas de dados
    struct WaveData {
        double volume;
        double price;
        datetime time;
        ENUM_WAVE_TYPE type;  // UP_WAVE, DOWN_WAVE
        bool isInstitutional;
        double deltaForce;
    };
    
    struct VolumePattern {
        double accumulationVolume;
        double distributionVolume;
        double hiddenVolume;    // Volume fracionado
        double institutionalThreshold;
        vector<double> waveSizes;
    };
    
    struct LowLatencyDetection {
        double microVolume;     // Volumes fracionados em microssegundos
        int frequency;          // Frequência das operações
        double averageSize;     // Tamanho médio das operações
        bool isAlgorithmic;     // Identificador de operações algorítmicas
    };
    
    // Cache de dados
    vector<WaveData>   m_waves;
    vector<VolumePattern> m_patterns;
    vector<LowLatencyDetection> m_latencyData;
    
    // Configurações
    double            m_threshold;
    int              m_minFrequency;
    double           m_institutionalThreshold;
    int              m_maxWaves;
    int              m_maxPatterns;
    
    // Métodos privados
    void              UpdateVolumeProfile();
    double            CalculateDeltaForce(const WaveData &wave);
    bool              IsAlgorithmicPattern(const LowLatencyDetection &latency);
    void              CleanupOldData();
    
public:
                      CWeisWaveAnalysis();
                     ~CWeisWaveAnalysis();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Update();
    
    // Métodos de análise
    bool              AnalyzeInstitutionalFlow();
    bool              DetectHiddenAccumulation();
    bool              AnalyzeWavePattern(string symbol);
    
    // Métodos de consulta
    WaveData*         GetLatestWave(string symbol);
    VolumePattern*    GetLatestPattern(string symbol);
    LowLatencyDetection* GetLatestLatency(string symbol);
    
    // Configuração
    void              SetThresholds(double threshold, int minFreq, double instThreshold);
    bool              IsInitialized() const { return m_core != NULL; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CWeisWaveAnalysis::CWeisWaveAnalysis() {
    m_core = NULL;
    
    // Configurações padrão
    m_threshold = 1000.0;  // Volume mínimo para detecção
    m_minFrequency = 5;    // Frequência mínima de operações
    m_institutionalThreshold = 5000.0;  // Limite para atividade institucional
    m_maxWaves = 1000;
    m_maxPatterns = 500;
    
    // Inicializa vetores
    m_waves.resize(0);
    m_patterns.resize(0);
    m_latencyData.resize(0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CWeisWaveAnalysis::~CWeisWaveAnalysis() {
    m_waves.clear();
    m_patterns.clear();
    m_latencyData.clear();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::Update() {
    if(!m_core) return false;
    
    string symbols[];
    m_core.GetSymbols(symbols);
    
    // Atualiza análises para cada símbolo
    for(int i = 0; i < ArraySize(symbols); i++) {
        AnalyzeWavePattern(symbols[i]);
        AnalyzeInstitutionalFlow();
        DetectHiddenAccumulation();
    }
    
    CleanupOldData();
    return true;
}

//+------------------------------------------------------------------+
//| Analisa fluxo institucional                                       |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::AnalyzeInstitutionalFlow() {
    if(!m_core) return false;
    
    LowLatencyDetection latency;
    latency.microVolume = CalculateMicroVolume();
    latency.frequency = GetOperationFrequency();
    latency.averageSize = CalculateAverageSize();
    latency.isAlgorithmic = IsAlgorithmicPattern(latency);
    
    if(IsInstitutionalPattern(latency)) {
        UpdateVolumeProfile();
        
        // Adiciona ao histórico
        int size = m_latencyData.size();
        m_latencyData.resize(size + 1);
        m_latencyData[size] = latency;
        
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Detecta acumulação oculta                                         |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::DetectHiddenAccumulation() {
    if(!m_core) return false;
    
    VolumePattern pattern;
    pattern.hiddenVolume = GetFractionatedVolume();
    pattern.institutionalThreshold = m_institutionalThreshold;
    
    if(pattern.hiddenVolume > pattern.institutionalThreshold) {
        if(IsAccumulationPattern()) {
            // Adiciona ao histórico
            int size = m_patterns.size();
            m_patterns.resize(size + 1);
            m_patterns[size] = pattern;
            
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Analisa padrão de ondas                                           |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::AnalyzeWavePattern(string symbol) {
    if(!m_core) return false;
    
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, 100, rates);
    
    if(copied < 100) return false;
    
    // Identifica ondas
    for(int i = 1; i < copied - 1; i++) {
        WaveData wave;
        wave.time = rates[i].time;
        wave.price = rates[i].close;
        wave.volume = rates[i].tick_volume;
        
        // Determina tipo de onda
        if(rates[i].close > rates[i-1].close && 
           rates[i].close > rates[i+1].close) {
            wave.type = UP_WAVE;
        }
        else if(rates[i].close < rates[i-1].close && 
                rates[i].close < rates[i+1].close) {
            wave.type = DOWN_WAVE;
        }
        else {
            wave.type = NEUTRAL_WAVE;
        }
        
        // Calcula força delta
        wave.deltaForce = CalculateDeltaForce(wave);
        
        // Verifica se é institucional
        wave.isInstitutional = wave.volume > m_institutionalThreshold;
        
        // Adiciona ao histórico
        int size = m_waves.size();
        m_waves.resize(size + 1);
        m_waves[size] = wave;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula volume em microssegundos                                  |
//+------------------------------------------------------------------+
double CWeisWaveAnalysis::CalculateMicroVolume() {
    if(!m_core) return 0.0;
    
    // Obtém dados de ticks recentes
    MqlTick ticks[];
    ArraySetAsSeries(ticks, true);
    int copied = CopyTicks(m_core.GetCurrentSymbol(), ticks, 0, 1000);
    
    if(copied < 1000) return 0.0;
    
    // Calcula volume em microssegundos
    double microVolume = 0;
    datetime lastTime = ticks[0].time;
    
    for(int i = 1; i < copied; i++) {
        if(ticks[i].time == lastTime) {
            microVolume += ticks[i].volume;
        }
        else {
            lastTime = ticks[i].time;
        }
    }
    
    return microVolume;
}

//+------------------------------------------------------------------+
//| Obtém frequência de operações                                     |
//+------------------------------------------------------------------+
int CWeisWaveAnalysis::GetOperationFrequency() {
    if(!m_core) return 0;
    
    // Obtém dados de ticks recentes
    MqlTick ticks[];
    ArraySetAsSeries(ticks, true);
    int copied = CopyTicks(m_core.GetCurrentSymbol(), ticks, 0, 1000);
    
    if(copied < 1000) return 0;
    
    // Calcula frequência
    int frequency = 0;
    datetime lastTime = ticks[0].time;
    
    for(int i = 1; i < copied; i++) {
        if(ticks[i].time != lastTime) {
            frequency++;
            lastTime = ticks[i].time;
        }
    }
    
    return frequency;
}

//+------------------------------------------------------------------+
//| Verifica padrão institucional                                     |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::IsInstitutionalPattern(
    const LowLatencyDetection &latency
) {
    return (latency.microVolume > m_threshold && 
            latency.frequency > m_minFrequency);
}

//+------------------------------------------------------------------+
//| Calcula volume fracionado                                         |
//+------------------------------------------------------------------+
double CWeisWaveAnalysis::GetFractionatedVolume() {
    if(!m_core) return 0.0;
    
    // Obtém dados de ticks recentes
    MqlTick ticks[];
    ArraySetAsSeries(ticks, true);
    int copied = CopyTicks(m_core.GetCurrentSymbol(), ticks, 0, 1000);
    
    if(copied < 1000) return 0.0;
    
    // Calcula volume fracionado
    double fractionatedVolume = 0;
    double totalVolume = 0;
    
    for(int i = 0; i < copied; i++) {
        totalVolume += ticks[i].volume;
        if(ticks[i].volume < m_threshold) {
            fractionatedVolume += ticks[i].volume;
        }
    }
    
    return fractionatedVolume / totalVolume;
}

//+------------------------------------------------------------------+
//| Verifica padrão de acumulação                                     |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::IsAccumulationPattern() {
    if(!m_core) return false;
    
    // Obtém dados recentes
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(m_core.GetCurrentSymbol(), PERIOD_CURRENT, 0, 20, rates);
    
    if(copied < 20) return false;
    
    // Analisa padrão de acumulação
    double volumeSum = 0;
    double priceRange = 0;
    
    for(int i = 0; i < copied; i++) {
        volumeSum += rates[i].tick_volume;
        priceRange = MathMax(priceRange, 
                           MathAbs(rates[i].high - rates[i].low));
    }
    
    // Verifica condições de acumulação
    bool hasHighVolume = volumeSum > m_institutionalThreshold;
    bool hasLowRange = priceRange < m_core.GetAnalysis().CalculateATR(
        m_core.GetCurrentSymbol(),
        14
    ) * 0.5;
    
    return hasHighVolume && hasLowRange;
}

//+------------------------------------------------------------------+
//| Atualiza perfil de volume                                         |
//+------------------------------------------------------------------+
void CWeisWaveAnalysis::UpdateVolumeProfile() {
    if(!m_core) return;
    
    // Obtém dados recentes
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(m_core.GetCurrentSymbol(), PERIOD_CURRENT, 0, 100, rates);
    
    if(copied < 100) return;
    
    // Atualiza padrões de volume
    VolumePattern pattern;
    pattern.accumulationVolume = 0;
    pattern.distributionVolume = 0;
    pattern.hiddenVolume = GetFractionatedVolume();
    
    for(int i = 0; i < copied; i++) {
        if(rates[i].close > rates[i].open) {
            pattern.accumulationVolume += rates[i].tick_volume;
        }
        else {
            pattern.distributionVolume += rates[i].tick_volume;
        }
    }
    
    // Adiciona ao histórico
    int size = m_patterns.size();
    m_patterns.resize(size + 1);
    m_patterns[size] = pattern;
}

//+------------------------------------------------------------------+
//| Calcula força delta                                               |
//+------------------------------------------------------------------+
double CWeisWaveAnalysis::CalculateDeltaForce(const WaveData &wave) {
    if(!m_core) return 0.0;
    
    // Calcula força baseada no volume e direção
    double force = wave.volume;
    if(wave.type == UP_WAVE) {
        force *= 1.0;
    }
    else if(wave.type == DOWN_WAVE) {
        force *= -1.0;
    }
    
    return force;
}

//+------------------------------------------------------------------+
//| Verifica padrão algorítmico                                       |
//+------------------------------------------------------------------+
bool CWeisWaveAnalysis::IsAlgorithmicPattern(
    const LowLatencyDetection &latency
) {
    // Verifica características de operações algorítmicas
    bool hasHighFrequency = latency.frequency > m_minFrequency * 2;
    bool hasConsistentSize = latency.averageSize > 0 && 
                            latency.averageSize < m_threshold;
    
    return hasHighFrequency && hasConsistentSize;
}

//+------------------------------------------------------------------+
//| Calcula tamanho médio das operações                               |
//+------------------------------------------------------------------+
double CWeisWaveAnalysis::CalculateAverageSize() {
    if(!m_core) return 0.0;
    
    // Obtém dados de ticks recentes
    MqlTick ticks[];
    ArraySetAsSeries(ticks, true);
    int copied = CopyTicks(m_core.GetCurrentSymbol(), ticks, 0, 1000);
    
    if(copied < 1000) return 0.0;
    
    // Calcula tamanho médio
    double totalSize = 0;
    int count = 0;
    
    for(int i = 0; i < copied; i++) {
        if(ticks[i].volume > 0) {
            totalSize += ticks[i].volume;
            count++;
        }
    }
    
    return count > 0 ? totalSize / count : 0.0;
}

//+------------------------------------------------------------------+
//| Obtém última onda                                                 |
//+------------------------------------------------------------------+
WaveData* CWeisWaveAnalysis::GetLatestWave(string symbol) {
    for(int i = m_waves.size() - 1; i >= 0; i--) {
        if(m_waves[i].time > 0) {  // Verifica se é uma onda válida
            return &m_waves[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém último padrão                                               |
//+------------------------------------------------------------------+
VolumePattern* CWeisWaveAnalysis::GetLatestPattern(string symbol) {
    if(m_patterns.size() > 0) {
        return &m_patterns[m_patterns.size() - 1];
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém última detecção de latência                                 |
//+------------------------------------------------------------------+
LowLatencyDetection* CWeisWaveAnalysis::GetLatestLatency(string symbol) {
    if(m_latencyData.size() > 0) {
        return &m_latencyData[m_latencyData.size() - 1];
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Define thresholds                                                  |
//+------------------------------------------------------------------+
void CWeisWaveAnalysis::SetThresholds(
    double threshold,
    int minFreq,
    double instThreshold
) {
    m_threshold = threshold;
    m_minFrequency = minFreq;
    m_institutionalThreshold = instThreshold;
}

//+------------------------------------------------------------------+
//| Limpa dados antigos                                               |
//+------------------------------------------------------------------+
void CWeisWaveAnalysis::CleanupOldData() {
    datetime current = TimeCurrent();
    
    // Remove ondas antigas
    for(int i = m_waves.size() - 1; i >= 0; i--) {
        if(current - m_waves[i].time > 24 * 60 * 60) {  // 24 horas
            m_waves.erase(i);
        }
    }
    
    // Remove padrões antigos
    while(m_patterns.size() > m_maxPatterns) {
        m_patterns.erase(0);
    }
    
    // Remove dados de latência antigos
    while(m_latencyData.size() > m_maxWaves) {
        m_latencyData.erase(0);
    }
} 