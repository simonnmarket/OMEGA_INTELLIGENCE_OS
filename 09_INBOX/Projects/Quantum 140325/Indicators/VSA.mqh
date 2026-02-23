#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Enumeração para sinais VSA
enum VSASignal {
    VSA_NO_SIGNAL,
    VSA_BUYING_CLIMAX,
    VSA_SELLING_CLIMAX,
    VSA_HIGH_VOLUME_UP,
    VSA_HIGH_VOLUME_DOWN,
    VSA_LOW_VOLUME_UP,
    VSA_LOW_VOLUME_DOWN,
    VSA_NO_DEMAND,
    VSA_NO_SUPPLY,
    VSA_STOPPING_VOLUME
};

//+------------------------------------------------------------------+
//| Classe VSA                                                         |
//+------------------------------------------------------------------+
class CVSA {
private:
    string          m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int             m_period;
    
    double          m_volumeMA[];
    double          m_spreadMA[];
    
    bool            CalculateMA();
    bool            IsHighVolume(int index);
    bool            IsLowVolume(int index);
    bool            IsWideSpread(int index);
    bool            IsNarrowSpread(int index);
    bool            IsUpBar(int index);
    bool            IsDownBar(int index);
    
public:
                    CVSA();
                   ~CVSA();
    
    bool            Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int period = 14);
    VSASignal       GetSignal(int shift);
    bool            Update();
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CVSA::CVSA() {
    m_symbol = NULL;
    m_timeframe = PERIOD_CURRENT;
    m_period = 14;
    ArrayResize(m_volumeMA, 1000);
    ArrayResize(m_spreadMA, 1000);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CVSA::~CVSA() {
    ArrayFree(m_volumeMA);
    ArrayFree(m_spreadMA);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CVSA::Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int period = 14) {
    m_symbol = symbol;
    m_timeframe = timeframe;
    m_period = period;
    
    return CalculateMA();
}

//+------------------------------------------------------------------+
//| Calcula médias móveis                                             |
//+------------------------------------------------------------------+
bool CVSA::CalculateMA() {
    double volume[], high[], low[];
    ArraySetAsSeries(volume, true);
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyTickVolume(m_symbol, m_timeframe, 0, 1000, volume) <= 0) return false;
    if(CopyHigh(m_symbol, m_timeframe, 0, 1000, high) <= 0) return false;
    if(CopyLow(m_symbol, m_timeframe, 0, 1000, low) <= 0) return false;
    
    // Calcula média móvel do volume
    for(int i = 999; i >= m_period; i--) {
        double sum = 0;
        for(int j = 0; j < m_period; j++) {
            sum += volume[i-j];
        }
        m_volumeMA[i] = sum / m_period;
        
        // Calcula média móvel do spread
        sum = 0;
        for(int j = 0; j < m_period; j++) {
            sum += (high[i-j] - low[i-j]);
        }
        m_spreadMA[i] = sum / m_period;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica volume alto                                              |
//+------------------------------------------------------------------+
bool CVSA::IsHighVolume(int index) {
    double volume[];
    ArraySetAsSeries(volume, true);
    if(CopyTickVolume(m_symbol, m_timeframe, index, 1, volume) <= 0) return false;
    
    return volume[0] > m_volumeMA[index] * 1.5;
}

//+------------------------------------------------------------------+
//| Verifica volume baixo                                             |
//+------------------------------------------------------------------+
bool CVSA::IsLowVolume(int index) {
    double volume[];
    ArraySetAsSeries(volume, true);
    if(CopyTickVolume(m_symbol, m_timeframe, index, 1, volume) <= 0) return false;
    
    return volume[0] < m_volumeMA[index] * 0.5;
}

//+------------------------------------------------------------------+
//| Verifica spread amplo                                             |
//+------------------------------------------------------------------+
bool CVSA::IsWideSpread(int index) {
    double high[], low[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyHigh(m_symbol, m_timeframe, index, 1, high) <= 0) return false;
    if(CopyLow(m_symbol, m_timeframe, index, 1, low) <= 0) return false;
    
    double spread = high[0] - low[0];
    return spread > m_spreadMA[index] * 1.5;
}

//+------------------------------------------------------------------+
//| Verifica spread estreito                                          |
//+------------------------------------------------------------------+
bool CVSA::IsNarrowSpread(int index) {
    double high[], low[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyHigh(m_symbol, m_timeframe, index, 1, high) <= 0) return false;
    if(CopyLow(m_symbol, m_timeframe, index, 1, low) <= 0) return false;
    
    double spread = high[0] - low[0];
    return spread < m_spreadMA[index] * 0.5;
}

//+------------------------------------------------------------------+
//| Verifica barra de alta                                            |
//+------------------------------------------------------------------+
bool CVSA::IsUpBar(int index) {
    double open[], close[];
    ArraySetAsSeries(open, true);
    ArraySetAsSeries(close, true);
    
    if(CopyOpen(m_symbol, m_timeframe, index, 1, open) <= 0) return false;
    if(CopyClose(m_symbol, m_timeframe, index, 1, close) <= 0) return false;
    
    return close[0] > open[0];
}

//+------------------------------------------------------------------+
//| Verifica barra de baixa                                           |
//+------------------------------------------------------------------+
bool CVSA::IsDownBar(int index) {
    double open[], close[];
    ArraySetAsSeries(open, true);
    ArraySetAsSeries(close, true);
    
    if(CopyOpen(m_symbol, m_timeframe, index, 1, open) <= 0) return false;
    if(CopyClose(m_symbol, m_timeframe, index, 1, close) <= 0) return false;
    
    return close[0] < open[0];
}

//+------------------------------------------------------------------+
//| Obtém sinal VSA                                                   |
//+------------------------------------------------------------------+
VSASignal CVSA::GetSignal(int shift) {
    if(IsHighVolume(shift)) {
        if(IsWideSpread(shift)) {
            if(IsUpBar(shift)) return VSA_BUYING_CLIMAX;
            if(IsDownBar(shift)) return VSA_SELLING_CLIMAX;
        }
        if(IsUpBar(shift)) return VSA_HIGH_VOLUME_UP;
        if(IsDownBar(shift)) return VSA_HIGH_VOLUME_DOWN;
    }
    
    if(IsLowVolume(shift)) {
        if(IsUpBar(shift)) return VSA_NO_DEMAND;
        if(IsDownBar(shift)) return VSA_NO_SUPPLY;
    }
    
    if(IsWideSpread(shift) && IsDownBar(shift) && IsHighVolume(shift))
        return VSA_STOPPING_VOLUME;
    
    return VSA_NO_SIGNAL;
}

//+------------------------------------------------------------------+
//| Atualiza os cálculos                                              |
//+------------------------------------------------------------------+
bool CVSA::Update() {
    return CalculateMA();
} 