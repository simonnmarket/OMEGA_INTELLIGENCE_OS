#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

//+------------------------------------------------------------------+
//| Classe VelocidadeNegocios                                         |
//+------------------------------------------------------------------+
class CVelocidadeNegocios {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    
    // Estruturas
    struct IndicatorData {
        double contracts;
        double frequency;
        double average;
        int colorIndex;
    };
    
    struct IndicatorConfig {
        int period;
        int timesAverage;
        bool enabled;
    };
    
    // Dados
    IndicatorData     m_data;
    IndicatorConfig   m_config;
    
    // Buffers
    double           m_contractsBuffer[];
    double           m_contractsColors[];
    double           m_frequencyBuffer[];
    
    // Métodos privados
    void              CalculateIndicator(int index);
    void              UpdateBuffers();
    double            CalculateAverage(int index);
    bool              ValidateData();
    
public:
                      CVelocidadeNegocios();
                     ~CVelocidadeNegocios();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Update();
    
    // Configuração
    void              SetPeriod(int period);
    void              SetTimesAverage(int times);
    void              Enable(bool enable);
    
    // Métodos de consulta
    double            GetContracts(int index);
    double            GetFrequency(int index);
    double            GetAverage(int index);
    int               GetColorIndex(int index);
    bool              IsEnabled() { return m_config.enabled; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CVelocidadeNegocios::CVelocidadeNegocios() {
    m_core = NULL;
    
    // Configurações padrão
    m_config.period = 17;
    m_config.timesAverage = 2;
    m_config.enabled = true;
    
    // Inicializa dados
    m_data.contracts = 0;
    m_data.frequency = 0;
    m_data.average = 0;
    m_data.colorIndex = 1;
    
    // Inicializa buffers
    ArrayResize(m_contractsBuffer, 1000);
    ArrayResize(m_contractsColors, 1000);
    ArrayResize(m_frequencyBuffer, 1000);
    ArrayInitialize(m_contractsBuffer, 0);
    ArrayInitialize(m_contractsColors, 1);
    ArrayInitialize(m_frequencyBuffer, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CVelocidadeNegocios::~CVelocidadeNegocios() {
    ArrayFree(m_contractsBuffer);
    ArrayFree(m_contractsColors);
    ArrayFree(m_frequencyBuffer);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CVelocidadeNegocios::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    
    m_core = core;
    
    // Verifica número de barras
    int candles = iBars(m_core.GetCurrentSymbol(), PERIOD_CURRENT);
    if(candles < m_config.period) {
        Print("Número de Barras: (", candles, ") Número de Barras Insuficientes. Mude para um timeframe Menor");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza indicador                                                 |
//+------------------------------------------------------------------+
bool CVelocidadeNegocios::Update() {
    if(!m_core || !m_config.enabled) return false;
    
    string symbol = m_core.GetCurrentSymbol();
    int total = iBars(symbol, PERIOD_CURRENT);
    
    // Calcula indicador para cada barra
    for(int i = m_config.period - 1; i < total; i++) {
        CalculateIndicator(i);
    }
    
    UpdateBuffers();
    return true;
}

//+------------------------------------------------------------------+
//| Calcula indicador                                                  |
//+------------------------------------------------------------------+
void CVelocidadeNegocios::CalculateIndicator(int index) {
    string symbol = m_core.GetCurrentSymbol();
    
    // Obtém dados da barra
    double high = iHigh(symbol, PERIOD_CURRENT, index);
    double low = iLow(symbol, PERIOD_CURRENT, index);
    long volume = iVolume(symbol, PERIOD_CURRENT, index);
    
    // Calcula frequência e contratos por ponto
    double frequency = high - low;
    double contractsPerPoint = 0;
    
    if(frequency > 0 && volume > 0) {
        contractsPerPoint = volume / frequency;
        m_frequencyBuffer[index] = contractsPerPoint;
        
        // Calcula média
        double average = CalculateAverage(index);
        m_contractsBuffer[index] = average;
        
        // Define cor
        if(contractsPerPoint > average * m_config.timesAverage) {
            m_contractsColors[index] = 0; // Vermelho
        }
        else {
            m_contractsColors[index] = 1; // Branco
        }
    }
}

//+------------------------------------------------------------------+
//| Calcula média                                                      |
//+------------------------------------------------------------------+
double CVelocidadeNegocios::CalculateAverage(int index) {
    double sum = 0;
    
    for(int j = 0; j < m_config.period; j++) {
        sum += m_frequencyBuffer[index - j];
    }
    
    return sum / m_config.period;
}

//+------------------------------------------------------------------+
//| Atualiza buffers                                                   |
//+------------------------------------------------------------------+
void CVelocidadeNegocios::UpdateBuffers() {
    // Atualiza dados atuais
    int lastIndex = ArraySize(m_contractsBuffer) - 1;
    if(lastIndex >= 0) {
        m_data.contracts = m_contractsBuffer[lastIndex];
        m_data.frequency = m_frequencyBuffer[lastIndex];
        m_data.average = m_data.contracts;
        m_data.colorIndex = (int)m_contractsColors[lastIndex];
    }
}

//+------------------------------------------------------------------+
//| Valida dados                                                       |
//+------------------------------------------------------------------+
bool CVelocidadeNegocios::ValidateData() {
    if(m_data.frequency <= 0 || m_data.contracts <= 0) {
        return false;
    }
    return true;
}

//+------------------------------------------------------------------+
//| Configurações                                                      |
//+------------------------------------------------------------------+
void CVelocidadeNegocios::SetPeriod(int period) {
    m_config.period = period;
}

void CVelocidadeNegocios::SetTimesAverage(int times) {
    m_config.timesAverage = times;
}

void CVelocidadeNegocios::Enable(bool enable) {
    m_config.enabled = enable;
}

//+------------------------------------------------------------------+
//| Métodos de consulta                                                |
//+------------------------------------------------------------------+
double CVelocidadeNegocios::GetContracts(int index) {
    if(index >= 0 && index < ArraySize(m_contractsBuffer)) {
        return m_contractsBuffer[index];
    }
    return 0;
}

double CVelocidadeNegocios::GetFrequency(int index) {
    if(index >= 0 && index < ArraySize(m_frequencyBuffer)) {
        return m_frequencyBuffer[index];
    }
    return 0;
}

double CVelocidadeNegocios::GetAverage(int index) {
    if(index >= 0 && index < ArraySize(m_contractsBuffer)) {
        return m_contractsBuffer[index];
    }
    return 0;
}

int CVelocidadeNegocios::GetColorIndex(int index) {
    if(index >= 0 && index < ArraySize(m_contractsColors)) {
        return (int)m_contractsColors[index];
    }
    return 1;
} 