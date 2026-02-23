#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"
#include "WeisWaveAnalysis.mqh"

//+------------------------------------------------------------------+
//| Classe InstitutionalAlerts                                        |
//+------------------------------------------------------------------+
class CInstitutionalAlerts {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    CWeisWaveAnalysis* m_waveAnalysis;
    
    // Estrutura para alertas
    struct Alert {
        string message;
        double volumeSize;
        datetime time;
        ENUM_ALERT_TYPE type;
        double confidence;
        string symbol;
        double price;
        string details;
    };
    
    // Cache de dados
    vector<Alert>      m_alerts;
    
    // Configurações
    double            m_confidenceThreshold;
    int               m_maxAlerts;
    bool              m_enableNotifications;
    bool              m_enableLogging;
    
    // Métodos privados
    void              ProcessAlert(const Alert &alert);
    void              NotifyUser(const Alert &alert);
    void              LogActivity(const Alert &alert);
    double            CalculateConfidence(const Alert &alert);
    void              CleanupOldAlerts();
    
public:
                      CInstitutionalAlerts();
                     ~CInstitutionalAlerts();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core, CWeisWaveAnalysis* waveAnalysis);
    bool              Update();
    
    // Métodos de monitoramento
    void              CheckInstitutionalActivity();
    void              CheckHiddenAccumulation();
    void              CheckVolumeSpikes();
    void              CheckPriceReversals();
    
    // Métodos de consulta
    Alert*            GetLatestAlert(string symbol);
    int               GetAlertCount(string symbol);
    double            GetAverageConfidence(string symbol);
    
    // Configuração
    void              SetConfidenceThreshold(double threshold);
    void              EnableNotifications(bool enable);
    void              EnableLogging(bool enable);
    bool              IsInitialized() const { return m_core != NULL; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CInstitutionalAlerts::CInstitutionalAlerts() {
    m_core = NULL;
    m_waveAnalysis = NULL;
    
    // Configurações padrão
    m_confidenceThreshold = 0.8;
    m_maxAlerts = 1000;
    m_enableNotifications = true;
    m_enableLogging = true;
    
    // Inicializa vetor de alertas
    m_alerts.resize(0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CInstitutionalAlerts::~CInstitutionalAlerts() {
    m_alerts.clear();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CInstitutionalAlerts::Initialize(
    CQuantumCore* core,
    CWeisWaveAnalysis* waveAnalysis
) {
    if(core == NULL || waveAnalysis == NULL) return false;
    
    m_core = core;
    m_waveAnalysis = waveAnalysis;
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CInstitutionalAlerts::Update() {
    if(!m_core || !m_waveAnalysis) return false;
    
    string symbols[];
    m_core.GetSymbols(symbols);
    
    // Atualiza monitoramento para cada símbolo
    for(int i = 0; i < ArraySize(symbols); i++) {
        CheckInstitutionalActivity();
        CheckHiddenAccumulation();
        CheckVolumeSpikes();
        CheckPriceReversals();
    }
    
    CleanupOldAlerts();
    return true;
}

//+------------------------------------------------------------------+
//| Verifica atividade institucional                                  |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::CheckInstitutionalActivity() {
    if(!m_core || !m_waveAnalysis) return;
    
    if(m_waveAnalysis.AnalyzeInstitutionalFlow()) {
        Alert alert;
        alert.message = "Possível atividade institucional detectada";
        alert.volumeSize = m_waveAnalysis.GetLatestLatency(
            m_core.GetCurrentSymbol()
        ).microVolume;
        alert.time = TimeCurrent();
        alert.type = INSTITUTIONAL_ACTIVITY;
        alert.symbol = m_core.GetCurrentSymbol();
        alert.price = SymbolInfoDouble(alert.symbol, SYMBOL_LAST);
        alert.details = "Volume: " + DoubleToString(alert.volumeSize, 2);
        
        alert.confidence = CalculateConfidence(alert);
        ProcessAlert(alert);
    }
}

//+------------------------------------------------------------------+
//| Verifica acumulação oculta                                        |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::CheckHiddenAccumulation() {
    if(!m_core || !m_waveAnalysis) return;
    
    if(m_waveAnalysis.DetectHiddenAccumulation()) {
        Alert alert;
        alert.message = "Possível acumulação oculta detectada";
        alert.volumeSize = m_waveAnalysis.GetLatestPattern(
            m_core.GetCurrentSymbol()
        ).hiddenVolume;
        alert.time = TimeCurrent();
        alert.type = HIDDEN_ACCUMULATION;
        alert.symbol = m_core.GetCurrentSymbol();
        alert.price = SymbolInfoDouble(alert.symbol, SYMBOL_LAST);
        alert.details = "Volume Oculto: " + DoubleToString(alert.volumeSize, 2);
        
        alert.confidence = CalculateConfidence(alert);
        ProcessAlert(alert);
    }
}

//+------------------------------------------------------------------+
//| Verifica picos de volume                                          |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::CheckVolumeSpikes() {
    if(!m_core || !m_waveAnalysis) return;
    
    WaveData* wave = m_waveAnalysis.GetLatestWave(m_core.GetCurrentSymbol());
    if(wave != NULL && wave.isInstitutional) {
        Alert alert;
        alert.message = "Pico de volume institucional detectado";
        alert.volumeSize = wave.volume;
        alert.time = wave.time;
        alert.type = VOLUME_SPIKE;
        alert.symbol = m_core.GetCurrentSymbol();
        alert.price = wave.price;
        alert.details = "Força Delta: " + DoubleToString(wave.deltaForce, 2);
        
        alert.confidence = CalculateConfidence(alert);
        ProcessAlert(alert);
    }
}

//+------------------------------------------------------------------+
//| Verifica reversões de preço                                       |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::CheckPriceReversals() {
    if(!m_core || !m_waveAnalysis) return;
    
    WaveData* wave = m_waveAnalysis.GetLatestWave(m_core.GetCurrentSymbol());
    if(wave != NULL) {
        double currentPrice = SymbolInfoDouble(wave.symbol, SYMBOL_LAST);
        double priceChange = MathAbs(currentPrice - wave.price);
        double atr = m_core.GetAnalysis().CalculateATR(wave.symbol, 14);
        
        if(priceChange > atr * 2) {
            Alert alert;
            alert.message = "Possível reversão de preço detectada";
            alert.volumeSize = wave.volume;
            alert.time = TimeCurrent();
            alert.type = PRICE_REVERSAL;
            alert.symbol = wave.symbol;
            alert.price = currentPrice;
            alert.details = "Mudança: " + DoubleToString(priceChange, 5);
            
            alert.confidence = CalculateConfidence(alert);
            ProcessAlert(alert);
        }
    }
}

//+------------------------------------------------------------------+
//| Processa alerta                                                    |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::ProcessAlert(const Alert &alert) {
    if(alert.confidence >= m_confidenceThreshold) {
        if(m_enableNotifications) {
            NotifyUser(alert);
        }
        if(m_enableLogging) {
            LogActivity(alert);
        }
        
        // Adiciona ao histórico
        int size = m_alerts.size();
        m_alerts.resize(size + 1);
        m_alerts[size] = alert;
    }
}

//+------------------------------------------------------------------+
//| Notifica usuário                                                   |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::NotifyUser(const Alert &alert) {
    string notification = StringFormat(
        "%s - %s\nConfiança: %.2f%%\nPreço: %.5f\n%s",
        alert.symbol,
        alert.message,
        alert.confidence * 100,
        alert.price,
        alert.details
    );
    
    Alert(notification);
}

//+------------------------------------------------------------------+
//| Registra atividade                                                 |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::LogActivity(const Alert &alert) {
    string logMessage = StringFormat(
        "[%s] %s - %s (Confiança: %.2f%%, Preço: %.5f)",
        TimeToString(alert.time),
        alert.symbol,
        alert.message,
        alert.confidence * 100,
        alert.price
    );
    
    Print(logMessage);
}

//+------------------------------------------------------------------+
//| Calcula confiança do alerta                                        |
//+------------------------------------------------------------------+
double CInstitutionalAlerts::CalculateConfidence(const Alert &alert) {
    double confidence = 0.0;
    
    switch(alert.type) {
        case INSTITUTIONAL_ACTIVITY:
            confidence = MathMin(1.0, alert.volumeSize / 
                m_waveAnalysis.GetLatestLatency(alert.symbol).microVolume);
            break;
            
        case HIDDEN_ACCUMULATION:
            confidence = MathMin(1.0, alert.volumeSize / 
                m_waveAnalysis.GetLatestPattern(alert.symbol).institutionalThreshold);
            break;
            
        case VOLUME_SPIKE:
            confidence = MathMin(1.0, alert.volumeSize / 
                m_waveAnalysis.GetLatestWave(alert.symbol).volume);
            break;
            
        case PRICE_REVERSAL:
            double atr = m_core.GetAnalysis().CalculateATR(alert.symbol, 14);
            confidence = MathMin(1.0, MathAbs(alert.price - 
                m_waveAnalysis.GetLatestWave(alert.symbol).price) / (atr * 2));
            break;
    }
    
    return confidence;
}

//+------------------------------------------------------------------+
//| Obtém último alerta                                               |
//+------------------------------------------------------------------+
Alert* CInstitutionalAlerts::GetLatestAlert(string symbol) {
    for(int i = m_alerts.size() - 1; i >= 0; i--) {
        if(m_alerts[i].symbol == symbol) {
            return &m_alerts[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém contagem de alertas                                         |
//+------------------------------------------------------------------+
int CInstitutionalAlerts::GetAlertCount(string symbol) {
    int count = 0;
    for(int i = 0; i < m_alerts.size(); i++) {
        if(m_alerts[i].symbol == symbol) {
            count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Obtém confiança média                                             |
//+------------------------------------------------------------------+
double CInstitutionalAlerts::GetAverageConfidence(string symbol) {
    double sum = 0.0;
    int count = 0;
    
    for(int i = 0; i < m_alerts.size(); i++) {
        if(m_alerts[i].symbol == symbol) {
            sum += m_alerts[i].confidence;
            count++;
        }
    }
    
    return count > 0 ? sum / count : 0.0;
}

//+------------------------------------------------------------------+
//| Define threshold de confiança                                      |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::SetConfidenceThreshold(double threshold) {
    m_confidenceThreshold = MathMax(0.0, MathMin(1.0, threshold));
}

//+------------------------------------------------------------------+
//| Ativa/desativa notificações                                       |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::EnableNotifications(bool enable) {
    m_enableNotifications = enable;
}

//+------------------------------------------------------------------+
//| Ativa/desativa logging                                            |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::EnableLogging(bool enable) {
    m_enableLogging = enable;
}

//+------------------------------------------------------------------+
//| Limpa alertas antigos                                             |
//+------------------------------------------------------------------+
void CInstitutionalAlerts::CleanupOldAlerts() {
    datetime current = TimeCurrent();
    
    // Remove alertas antigos
    for(int i = m_alerts.size() - 1; i >= 0; i--) {
        if(current - m_alerts[i].time > 24 * 60 * 60) {  // 24 horas
            m_alerts.erase(i);
        }
    }
    
    // Limita tamanho do vetor
    while(m_alerts.size() > m_maxAlerts) {
        m_alerts.erase(0);
    }
} 