#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Trading/AdvancedTradingSystem.mqh"
#include "../Intelligence/AdvancedAnalysis.mqh"
#include "../Data/DataCollection.mqh"
#include "../Monitoring/MonitoringSystem.mqh"
#include "../Integration/ExternalSourcesIntegration.mqh"

//+------------------------------------------------------------------+
//| Classe QuantumCore                                                 |
//+------------------------------------------------------------------+
class CQuantumCore {
private:
    // Componentes principais
    CAdvancedTradingSystem*      m_tradingSystem;
    CAdvancedAnalysis*           m_analysis;
    CDataCollection*             m_dataCollection;
    CMonitoringSystem*           m_monitoring;
    CExternalSourcesIntegration* m_externalSources;
    
    // Estado do sistema
    bool                         m_isInitialized;
    string                       m_lastError;
    
    // Configurações
    string                       m_configFile;
    
    // Métodos privados
    bool            LoadConfiguration();
    bool            ValidateComponents();
    void            LogError(string message);
    
public:
                    CQuantumCore();
                   ~CQuantumCore();
    
    // Métodos principais
    bool            Initialize();
    void            Shutdown();
    bool            Update();
    
    // Getters para componentes
    CAdvancedTradingSystem*      GetTradingSystem() { return m_tradingSystem; }
    CAdvancedAnalysis*           GetAnalysis() { return m_analysis; }
    CDataCollection*             GetDataCollection() { return m_dataCollection; }
    CMonitoringSystem*           GetMonitoring() { return m_monitoring; }
    CExternalSourcesIntegration* GetExternalSources() { return m_externalSources; }
    
    // Estado do sistema
    bool            IsInitialized() const { return m_isInitialized; }
    string          GetLastError() const { return m_lastError; }
    
    // Métodos de integração
    bool            SynchronizeComponents();
    bool            ValidateSystemState();
    void            ProcessSystemEvents();
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CQuantumCore::CQuantumCore() {
    m_tradingSystem = new CAdvancedTradingSystem();
    m_analysis = new CAdvancedAnalysis();
    m_dataCollection = new CDataCollection();
    m_monitoring = new CMonitoringSystem();
    m_externalSources = new CExternalSourcesIntegration();
    
    m_isInitialized = false;
    m_lastError = "";
    m_configFile = "config/quantum.conf";
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CQuantumCore::~CQuantumCore() {
    Shutdown();
    
    delete m_tradingSystem;
    delete m_analysis;
    delete m_dataCollection;
    delete m_monitoring;
    delete m_externalSources;
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CQuantumCore::Initialize() {
    if(m_isInitialized) return true;
    
    if(!LoadConfiguration()) {
        LogError("Failed to load configuration");
        return false;
    }
    
    // Inicializa componentes
    if(!m_tradingSystem.InitializeConnection()) {
        LogError("Failed to initialize trading system");
        return false;
    }
    
    if(!m_analysis.Initialize()) {
        LogError("Failed to initialize analysis system");
        return false;
    }
    
    if(!m_dataCollection.Initialize()) {
        LogError("Failed to initialize data collection");
        return false;
    }
    
    if(!m_monitoring.Initialize()) {
        LogError("Failed to initialize monitoring system");
        return false;
    }
    
    if(!m_externalSources.Initialize()) {
        LogError("Failed to initialize external sources");
        return false;
    }
    
    if(!ValidateComponents()) {
        LogError("Failed to validate components");
        return false;
    }
    
    m_isInitialized = true;
    return true;
}

//+------------------------------------------------------------------+
//| Desligamento                                                       |
//+------------------------------------------------------------------+
void CQuantumCore::Shutdown() {
    if(!m_isInitialized) return;
    
    m_dataCollection.StopCollection();
    m_tradingSystem.CloseAllPositions();
    
    m_isInitialized = false;
}

//+------------------------------------------------------------------+
//| Atualização                                                        |
//+------------------------------------------------------------------+
bool CQuantumCore::Update() {
    if(!m_isInitialized) {
        LogError("System not initialized");
        return false;
    }
    
    // Atualiza componentes
    if(!m_dataCollection.StartCollection()) {
        LogError("Failed to update data collection");
        return false;
    }
    
    if(!m_monitoring.Update()) {
        LogError("Failed to update monitoring system");
        return false;
    }
    
    ProcessSystemEvents();
    return true;
}

//+------------------------------------------------------------------+
//| Carrega configuração                                              |
//+------------------------------------------------------------------+
bool CQuantumCore::LoadConfiguration() {
    // Implementar carregamento de configuração
    return true;
}

//+------------------------------------------------------------------+
//| Valida componentes                                                |
//+------------------------------------------------------------------+
bool CQuantumCore::ValidateComponents() {
    if(!m_tradingSystem.IsConnected()) {
        LogError("Trading system not connected");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Registra erro                                                      |
//+------------------------------------------------------------------+
void CQuantumCore::LogError(string message) {
    m_lastError = message;
    Print("QuantumCore Error: ", message);
}

//+------------------------------------------------------------------+
//| Sincroniza componentes                                            |
//+------------------------------------------------------------------+
bool CQuantumCore::SynchronizeComponents() {
    if(!m_isInitialized) return false;
    
    // Sincroniza dados entre componentes
    AnalysisResult analysis = m_analysis.AnalyzeMarketPatterns(_Symbol, NULL, PERIOD_CURRENT);
    
    if(analysis.hasGrangerCausality) {
        // Atualiza sistema de trading com resultados da análise
        // Implementar lógica específica
    }
    
    // Processa sinais externos
    AnalysisSignal signal = m_externalSources.GetLatestSignal(_Symbol);
    if(signal.provider != "") {
        m_externalSources.ProcessSignal(signal);
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida estado do sistema                                          |
//+------------------------------------------------------------------+
bool CQuantumCore::ValidateSystemState() {
    if(!m_isInitialized) return false;
    
    // Verifica estado dos componentes
    if(!m_tradingSystem.IsConnected()) {
        LogError("Trading system connection lost");
        return false;
    }
    
    // Verifica limites de risco
    if(!m_monitoring.CheckRiskLimits()) {
        LogError("Risk limits exceeded");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Processa eventos do sistema                                        |
//+------------------------------------------------------------------+
void CQuantumCore::ProcessSystemEvents() {
    if(!m_isInitialized) return;
    
    // Processa alertas do sistema de monitoramento
    Alert alert = m_monitoring.GetLastAlert();
    if(alert.type != "" && !alert.isAcknowledged) {
        if(alert.isCritical) {
            m_monitoring.SendTelegramAlert(alert);
            m_monitoring.SendEmailAlert(alert);
        }
    }
    
    // Sincroniza componentes
    SynchronizeComponents();
    
    // Valida estado do sistema
    ValidateSystemState();
} 