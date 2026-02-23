#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

//+------------------------------------------------------------------+
//| Classe WeisWaves                                                   |
//+------------------------------------------------------------------+
class CWeisWaves {
private:
    string          m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int             m_waveCount;
    double          m_waves[];
    
    bool            CalculateWaves();
    bool            IsNewWave(int index);
    
public:
                    CWeisWaves();
                   ~CWeisWaves();
    
    bool            Initialize(string symbol, ENUM_TIMEFRAMES timeframe);
    double          GetWaveValue(int shift);
    int             GetWaveCount() const { return m_waveCount; }
    bool            Update();
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CWeisWaves::CWeisWaves() {
    m_symbol = NULL;
    m_timeframe = PERIOD_CURRENT;
    m_waveCount = 0;
    ArrayResize(m_waves, 1000);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CWeisWaves::~CWeisWaves() {
    ArrayFree(m_waves);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CWeisWaves::Initialize(string symbol, ENUM_TIMEFRAMES timeframe) {
    m_symbol = symbol;
    m_timeframe = timeframe;
    
    return CalculateWaves();
}

//+------------------------------------------------------------------+
//| Calcula as ondas                                                   |
//+------------------------------------------------------------------+
bool CWeisWaves::CalculateWaves() {
    int counted = 0;
    int limit = 1000;
    
    double high[], low[], close[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    ArraySetAsSeries(close, true);
    
    if(CopyHigh(m_symbol, m_timeframe, 0, limit, high) <= 0) return false;
    if(CopyLow(m_symbol, m_timeframe, 0, limit, low) <= 0) return false;
    if(CopyClose(m_symbol, m_timeframe, 0, limit, close) <= 0) return false;
    
    m_waveCount = 0;
    
    for(int i = limit - 1; i >= 0; i--) {
        if(IsNewWave(i)) {
            m_waves[m_waveCount] = close[i];
            m_waveCount++;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica se é uma nova onda                                        |
//+------------------------------------------------------------------+
bool CWeisWaves::IsNewWave(int index) {
    if(index >= Bars(m_symbol, m_timeframe) - 1) return false;
    
    double high[], low[], close[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    ArraySetAsSeries(close, true);
    
    if(CopyHigh(m_symbol, m_timeframe, index, 3, high) <= 0) return false;
    if(CopyLow(m_symbol, m_timeframe, index, 3, low) <= 0) return false;
    if(CopyClose(m_symbol, m_timeframe, index, 3, close) <= 0) return false;
    
    // Verifica padrão de reversão
    bool isUpWave = close[0] > close[1] && low[0] > low[1];
    bool isDownWave = close[0] < close[1] && high[0] < high[1];
    
    return isUpWave || isDownWave;
}

//+------------------------------------------------------------------+
//| Obtém valor da onda                                               |
//+------------------------------------------------------------------+
double CWeisWaves::GetWaveValue(int shift) {
    if(shift >= m_waveCount) return 0;
    return m_waves[shift];
}

//+------------------------------------------------------------------+
//| Atualiza os cálculos                                              |
//+------------------------------------------------------------------+
bool CWeisWaves::Update() {
    return CalculateWaves();
} 