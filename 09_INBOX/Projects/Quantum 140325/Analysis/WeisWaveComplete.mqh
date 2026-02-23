#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Enumeradores
enum ENUM_WAVE_DIRECTION {
    WAVE_UP,
    WAVE_DOWN,
    WAVE_NEUTRAL
};

enum ENUM_BEHAVIOR_TYPE {
    VOLUME_BEHAVIOR_CHANGE,
    PRICE_BEHAVIOR_CHANGE,
    MOMENTUM_BEHAVIOR_CHANGE
};

enum ENUM_SIGNAL_TYPE {
    SIGNAL_ENTRY,
    SIGNAL_EXIT,
    SIGNAL_REVERSAL
};

// Constantes
#define WAVE_STRENGTH_THRESHOLD 1.5
#define HIGH_STRENGTH_THRESHOLD 2.0

//+------------------------------------------------------------------+
//| Classe WeisWaveComplete                                           |
//+------------------------------------------------------------------+
class CWeisWaveComplete {
private:
    // Estruturas
    struct WaveStructure {
        vector<double> volumes;
        vector<double> prices;
        vector<datetime> times;
        ENUM_WAVE_DIRECTION direction;
        double cumulativeVolume;
        double waveStrength;
        bool isComplete;
    };
    
    struct BehaviorChange {
        double volumeThreshold;
        double priceChange;
        datetime timeOfChange;
        ENUM_BEHAVIOR_TYPE type;
        double significance;
    };
    
    struct WaveAnalysis {
        int waveCount;
        double averageWaveVolume;
        double largestWaveVolume;
        datetime lastWaveTime;
        bool isUptrend;
        double trendStrength;
    };
    
    // Componentes principais
    CQuantumCore*      m_core;
    
    // Dados
    WaveStructure      m_currentWave;
    vector<WaveStructure> m_historicalWaves;
    WaveAnalysis       m_analysis;
    double            m_volumeThreshold;
    
    // Métodos privados
    void              ResetWaveStructure();
    void              InitializeAnalysis();
    bool              IsValidTick(const MqlTick& tick);
    void              UpdateCurrentWave(const MqlTick& tick);
    void              UpdateWaveDirection(const MqlTick& tick);
    bool              IsWaveComplete();
    bool              HasDirectionChanged();
    bool              IsVolumeSignificant();
    void              CompleteCurrentWave();
    double            CalculateWaveStrength();
    bool              ValidateTrendStrength();
    void              UpdateAnalysis();
    bool              IsUptrendConfirmed();
    double            CalculateTrendStrength();
    void              UpdateCumulativeVolume(const MqlTick& tick);
    
public:
                      CWeisWaveComplete();
                     ~CWeisWaveComplete();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core, double threshold = 1000.0);
    bool              ProcessNewTick(const MqlTick& tick);
    BehaviorChange    AnalyzeWaveBehavior();
    double            GetWaveStrength();
    bool              IsTrendConfirmed();
    
    // Métodos de consulta
    WaveStructure*    GetCurrentWave() { return &m_currentWave; }
    WaveAnalysis*     GetAnalysis() { return &m_analysis; }
    int               GetHistoricalWavesCount() { return m_historicalWaves.size(); }
    WaveStructure*    GetHistoricalWave(int index);
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CWeisWaveComplete::CWeisWaveComplete() {
    m_core = NULL;
    m_volumeThreshold = 1000.0;
    ResetWaveStructure();
    InitializeAnalysis();
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CWeisWaveComplete::~CWeisWaveComplete() {
    m_historicalWaves.clear();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::Initialize(CQuantumCore* core, double threshold) {
    if(core == NULL) return false;
    
    m_core = core;
    m_volumeThreshold = threshold;
    ResetWaveStructure();
    InitializeAnalysis();
    
    return true;
}

//+------------------------------------------------------------------+
//| Reseta estrutura de onda                                          |
//+------------------------------------------------------------------+
void CWeisWaveComplete::ResetWaveStructure() {
    m_currentWave.volumes.clear();
    m_currentWave.prices.clear();
    m_currentWave.times.clear();
    m_currentWave.direction = WAVE_NEUTRAL;
    m_currentWave.cumulativeVolume = 0;
    m_currentWave.waveStrength = 0;
    m_currentWave.isComplete = false;
}

//+------------------------------------------------------------------+
//| Inicializa análise                                                 |
//+------------------------------------------------------------------+
void CWeisWaveComplete::InitializeAnalysis() {
    m_analysis.waveCount = 0;
    m_analysis.averageWaveVolume = 0;
    m_analysis.largestWaveVolume = 0;
    m_analysis.lastWaveTime = 0;
    m_analysis.isUptrend = false;
    m_analysis.trendStrength = 0;
}

//+------------------------------------------------------------------+
//| Verifica tick válido                                               |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::IsValidTick(const MqlTick& tick) {
    return tick.volume > 0 && tick.last > 0;
}

//+------------------------------------------------------------------+
//| Processa novo tick                                                 |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::ProcessNewTick(const MqlTick& tick) {
    if(!IsValidTick(tick)) return false;
    
    UpdateCurrentWave(tick);
    
    if(IsWaveComplete()) {
        CompleteCurrentWave();
        ResetWaveStructure();
        UpdateCurrentWave(tick);
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Atualiza onda atual                                                |
//+------------------------------------------------------------------+
void CWeisWaveComplete::UpdateCurrentWave(const MqlTick& tick) {
    m_currentWave.volumes.push_back(tick.volume);
    m_currentWave.prices.push_back(tick.last);
    m_currentWave.times.push_back(tick.time);
    
    UpdateWaveDirection(tick);
    UpdateCumulativeVolume(tick);
}

//+------------------------------------------------------------------+
//| Atualiza direção da onda                                           |
//+------------------------------------------------------------------+
void CWeisWaveComplete::UpdateWaveDirection(const MqlTick& tick) {
    if(m_currentWave.volumes.size() < 2) return;
    
    double currentPrice = tick.last;
    double previousPrice = m_currentWave.prices[m_currentWave.prices.size() - 2];
    
    if(currentPrice > previousPrice) {
        m_currentWave.direction = WAVE_UP;
    }
    else if(currentPrice < previousPrice) {
        m_currentWave.direction = WAVE_DOWN;
    }
}

//+------------------------------------------------------------------+
//| Atualiza volume cumulativo                                         |
//+------------------------------------------------------------------+
void CWeisWaveComplete::UpdateCumulativeVolume(const MqlTick& tick) {
    m_currentWave.cumulativeVolume += tick.volume;
}

//+------------------------------------------------------------------+
//| Verifica se onda está completa                                     |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::IsWaveComplete() {
    if(m_currentWave.volumes.size() < 2) return false;
    
    if(HasDirectionChanged()) return true;
    if(IsVolumeSignificant()) return true;
    
    return false;
}

//+------------------------------------------------------------------+
//| Verifica mudança de direção                                        |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::HasDirectionChanged() {
    if(m_currentWave.volumes.size() < 3) return false;
    
    double currentPrice = m_currentWave.prices.back();
    double previousPrice = m_currentWave.prices[m_currentWave.prices.size() - 2];
    double prePreviousPrice = m_currentWave.prices[m_currentWave.prices.size() - 3];
    
    bool wasUp = prePreviousPrice < previousPrice;
    bool isUp = previousPrice < currentPrice;
    
    return wasUp != isUp;
}

//+------------------------------------------------------------------+
//| Verifica volume significativo                                      |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::IsVolumeSignificant() {
    double currentVolume = m_currentWave.volumes.back();
    return currentVolume > m_volumeThreshold;
}

//+------------------------------------------------------------------+
//| Completa onda atual                                                |
//+------------------------------------------------------------------+
void CWeisWaveComplete::CompleteCurrentWave() {
    m_currentWave.isComplete = true;
    m_currentWave.waveStrength = CalculateWaveStrength();
    
    m_historicalWaves.push_back(m_currentWave);
    UpdateAnalysis();
}

//+------------------------------------------------------------------+
//| Calcula força da onda                                              |
//+------------------------------------------------------------------+
double CWeisWaveComplete::CalculateWaveStrength() {
    if(m_currentWave.volumes.empty()) return 0;
    
    double volumeStrength = m_currentWave.cumulativeVolume / m_analysis.averageWaveVolume;
    double priceChange = MathAbs(m_currentWave.prices.back() - m_currentWave.prices[0]);
    
    return volumeStrength * priceChange;
}

//+------------------------------------------------------------------+
//| Valida força da tendência                                          |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::ValidateTrendStrength() {
    if(m_historicalWaves.size() < 3) return false;
    
    int consecutiveWaves = 0;
    ENUM_WAVE_DIRECTION lastDirection = m_historicalWaves.back().direction;
    
    for(int i = m_historicalWaves.size() - 1; i >= 0; i--) {
        if(m_historicalWaves[i].direction == lastDirection) {
            consecutiveWaves++;
        }
        else {
            break;
        }
    }
    
    return consecutiveWaves >= 3;
}

//+------------------------------------------------------------------+
//| Atualiza análise                                                   |
//+------------------------------------------------------------------+
void CWeisWaveComplete::UpdateAnalysis() {
    m_analysis.waveCount++;
    m_analysis.lastWaveTime = TimeCurrent();
    
    // Atualiza média do volume das ondas
    double totalVolume = 0;
    for(uint i = 0; i < m_historicalWaves.size(); i++) {
        totalVolume += m_historicalWaves[i].cumulativeVolume;
    }
    m_analysis.averageWaveVolume = totalVolume / m_historicalWaves.size();
    
    // Atualiza maior volume de onda
    m_analysis.largestWaveVolume = 0;
    for(uint i = 0; i < m_historicalWaves.size(); i++) {
        if(m_historicalWaves[i].cumulativeVolume > m_analysis.largestWaveVolume) {
            m_analysis.largestWaveVolume = m_historicalWaves[i].cumulativeVolume;
        }
    }
    
    // Atualiza tendência
    if(m_historicalWaves.size() >= 3) {
        m_analysis.isUptrend = IsUptrendConfirmed();
        m_analysis.trendStrength = CalculateTrendStrength();
    }
}

//+------------------------------------------------------------------+
//| Verifica confirmação de tendência de alta                          |
//+------------------------------------------------------------------+
bool CWeisWaveComplete::IsUptrendConfirmed() {
    if(m_historicalWaves.size() < 3) return false;
    
    int upWaves = 0;
    int downWaves = 0;
    
    for(int i = m_historicalWaves.size() - 1; 
        i >= MathMax(0, m_historicalWaves.size() - 3); i--) {
        if(m_historicalWaves[i].direction == WAVE_UP) {
            upWaves++;
        }
        else {
            downWaves++;
        }
    }
    
    return upWaves > downWaves;
}

//+------------------------------------------------------------------+
//| Calcula força da tendência                                         |
//+------------------------------------------------------------------+
double CWeisWaveComplete::CalculateTrendStrength() {
    if(m_historicalWaves.size() < 3) return 0;
    
    double strength = 0;
    for(int i = m_historicalWaves.size() - 1; 
        i >= MathMax(0, m_historicalWaves.size() - 3); i--) {
        if(m_historicalWaves[i].direction == 
           (m_analysis.isUptrend ? WAVE_UP : WAVE_DOWN)) {
            strength += m_historicalWaves[i].waveStrength;
        }
    }
    
    return strength;
}

//+------------------------------------------------------------------+
//| Analisa comportamento da onda                                      |
//+------------------------------------------------------------------+
BehaviorChange CWeisWaveComplete::AnalyzeWaveBehavior() {
    BehaviorChange behavior;
    behavior.timeOfChange = TimeCurrent();
    
    if(IsVolumeSignificant()) {
        behavior.type = VOLUME_BEHAVIOR_CHANGE;
        behavior.volumeThreshold = m_volumeThreshold;
        behavior.significance = m_currentWave.cumulativeVolume / 
                              m_analysis.averageWaveVolume;
    }
    
    return behavior;
}

//+------------------------------------------------------------------+
//| Obtém força da onda                                                |
//+------------------------------------------------------------------+
double CWeisWaveComplete::GetWaveStrength() {
    return CalculateWaveStrength();
}

//+------------------------------------------------------------------+
//| Obtém onda histórica                                               |
//+------------------------------------------------------------------+
WaveStructure* CWeisWaveComplete::GetHistoricalWave(int index) {
    if(index >= 0 && index < m_historicalWaves.size()) {
        return &m_historicalWaves[index];
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Classe WeisSignals                                                 |
//+------------------------------------------------------------------+
class CWeisSignals {
private:
    // Estrutura para sinais
    struct Signal {
        ENUM_SIGNAL_TYPE type;
        double price;
        datetime time;
        double strength;
        string description;
    };
    
    // Componentes principais
    CQuantumCore*      m_core;
    CWeisWaveComplete* m_waveAnalyzer;
    
    // Dados
    vector<Signal>     m_signals;
    
    // Métodos privados
    bool              IsEntrySignal(Signal& signal);
    void              NotifySignal(const Signal& signal);
    
public:
                      CWeisSignals();
                     ~CWeisSignals();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core, CWeisWaveComplete* analyzer);
    bool              CheckForSignals();
    
    // Métodos de consulta
    Signal*           GetLatestSignal();
    int               GetSignalCount();
    double            GetAverageSignalStrength();
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CWeisSignals::CWeisSignals() {
    m_core = NULL;
    m_waveAnalyzer = NULL;
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CWeisSignals::~CWeisSignals() {
    m_signals.clear();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CWeisSignals::Initialize(
    CQuantumCore* core,
    CWeisWaveComplete* analyzer
) {
    if(core == NULL || analyzer == NULL) return false;
    
    m_core = core;
    m_waveAnalyzer = analyzer;
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica sinais                                                    |
//+------------------------------------------------------------------+
bool CWeisSignals::CheckForSignals() {
    if(!m_waveAnalyzer.IsTrendConfirmed()) return false;
    
    Signal signal;
    
    if(IsEntrySignal(signal)) {
        m_signals.push_back(signal);
        NotifySignal(signal);
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Verifica sinal de entrada                                          |
//+------------------------------------------------------------------+
bool CWeisSignals::IsEntrySignal(Signal& signal) {
    double waveStrength = m_waveAnalyzer.GetWaveStrength();
    
    if(waveStrength > WAVE_STRENGTH_THRESHOLD) {
        signal.type = SIGNAL_ENTRY;
        signal.price = SymbolInfoDouble(Symbol(), SYMBOL_BID);
        signal.time = TimeCurrent();
        signal.strength = waveStrength;
        signal.description = "Forte sinal de entrada baseado em onda Weis";
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Notifica sinal                                                     |
//+------------------------------------------------------------------+
void CWeisSignals::NotifySignal(const Signal& signal) {
    string message = StringFormat(
        "Sinal Weis Wave\nTipo: %s\nPreço: %f\nForça: %f\nDescrição: %s",
        EnumToString(signal.type),
        signal.price,
        signal.strength,
        signal.description
    );
    
    Print(message);
    if(signal.strength > HIGH_STRENGTH_THRESHOLD) {
        SendNotification(message);
    }
}

//+------------------------------------------------------------------+
//| Obtém último sinal                                                 |
//+------------------------------------------------------------------+
Signal* CWeisSignals::GetLatestSignal() {
    if(m_signals.size() > 0) {
        return &m_signals[m_signals.size() - 1];
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém contagem de sinais                                           |
//+------------------------------------------------------------------+
int CWeisSignals::GetSignalCount() {
    return m_signals.size();
}

//+------------------------------------------------------------------+
//| Obtém força média dos sinais                                       |
//+------------------------------------------------------------------+
double CWeisSignals::GetAverageSignalStrength() {
    if(m_signals.size() == 0) return 0;
    
    double sum = 0;
    for(uint i = 0; i < m_signals.size(); i++) {
        sum += m_signals[i].strength;
    }
    
    return sum / m_signals.size();
} 