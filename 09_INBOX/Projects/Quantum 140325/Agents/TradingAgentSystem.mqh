#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Trading/AdvancedTradingSystem.mqh"
#include "../Data/DataCollection.mqh"

// Enumeração para tipos de agentes
enum ENUM_AGENT_TYPE {
    AGENT_FOREX_MAJOR,
    AGENT_FOREX_CROSS,
    AGENT_INDICES,
    AGENT_COMMODITIES,
    AGENT_CRYPTO
};

// Estrutura para configuração do agente
struct AgentConfig {
    string          symbol;
    ENUM_AGENT_TYPE type;
    string          sessions[];        // Sessões de trading relevantes
    string          events[];         // Eventos econômicos relevantes
    double          riskPerTrade;     // Risco por operação (%)
    double          correlationLimit; // Limite de correlação
};

// Estrutura para estado do agente
struct AgentState {
    bool     isActive;
    datetime lastUpdate;
    double   dailyPnL;
    int      totalTrades;
    double   winRate;
    double   exposure;
};

//+------------------------------------------------------------------+
//| Classe TradingAgentSystem                                         |
//+------------------------------------------------------------------+
class CTradingAgentSystem {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    AgentConfig     m_configs[];
    AgentState      m_states[];
    
    // Configurações
    int             m_maxAgents;
    double          m_maxDailyLoss;
    double          m_maxExposure;
    
    // Métodos privados
    bool            ValidateConfig(const AgentConfig &config);
    bool            UpdateAgentState(int index);
    double          CalculateCorrelation(string symbol1, string symbol2);
    bool            CheckSessionActive(const string &sessions[]);
    bool            CheckEconomicEvents(const string &events[]);
    
public:
                    CTradingAgentSystem();
                   ~CTradingAgentSystem();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            AddAgent(const AgentConfig &config);
    bool            RemoveAgent(string symbol);
    bool            UpdateAgents();
    
    // Métodos de trading
    bool            ExecuteSignal(string symbol, int direction, double volume);
    void            CloseAgentPositions(string symbol);
    void            CloseAllPositions();
    
    // Métodos de análise
    bool            AnalyzeMarket(string symbol);
    double          GetOptimalPosition(string symbol);
    bool            ValidateExposure(string symbol, double volume);
    
    // Getters
    AgentState      GetAgentState(string symbol);
    int             GetTotalAgents() const { return ArraySize(m_configs); }
    double          GetTotalExposure();
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CTradingAgentSystem::CTradingAgentSystem() {
    m_core = NULL;
    m_maxAgents = 10;
    m_maxDailyLoss = -5.0; // 5% máximo de perda diária
    m_maxExposure = 50.0;  // 50% máximo de exposição total
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CTradingAgentSystem::~CTradingAgentSystem() {
    CloseAllPositions();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    // Configura agentes padrão
    
    // EURUSD
    AgentConfig eurusd;
    eurusd.symbol = "EURUSD";
    eurusd.type = AGENT_FOREX_MAJOR;
    ArrayResize(eurusd.sessions, 2);
    eurusd.sessions[0] = "London";
    eurusd.sessions[1] = "NewYork";
    ArrayResize(eurusd.events, 2);
    eurusd.events[0] = "ECB";
    eurusd.events[1] = "FED";
    eurusd.riskPerTrade = 2.0;
    eurusd.correlationLimit = 0.7;
    AddAgent(eurusd);
    
    // USDJPY
    AgentConfig usdjpy;
    usdjpy.symbol = "USDJPY";
    usdjpy.type = AGENT_FOREX_MAJOR;
    ArrayResize(usdjpy.sessions, 2);
    usdjpy.sessions[0] = "Tokyo";
    usdjpy.sessions[1] = "London";
    ArrayResize(usdjpy.events, 2);
    usdjpy.events[0] = "BOJ";
    usdjpy.events[1] = "FED";
    usdjpy.riskPerTrade = 2.0;
    usdjpy.correlationLimit = 0.7;
    AddAgent(usdjpy);
    
    return true;
}

//+------------------------------------------------------------------+
//| Adiciona agente                                                    |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::AddAgent(const AgentConfig &config) {
    if(!ValidateConfig(config)) return false;
    
    int size = ArraySize(m_configs);
    if(size >= m_maxAgents) return false;
    
    ArrayResize(m_configs, size + 1);
    ArrayResize(m_states, size + 1);
    
    m_configs[size] = config;
    m_states[size].isActive = true;
    m_states[size].lastUpdate = TimeCurrent();
    m_states[size].dailyPnL = 0;
    m_states[size].totalTrades = 0;
    m_states[size].winRate = 0;
    m_states[size].exposure = 0;
    
    return true;
}

//+------------------------------------------------------------------+
//| Remove agente                                                      |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::RemoveAgent(string symbol) {
    for(int i = 0; i < ArraySize(m_configs); i++) {
        if(m_configs[i].symbol == symbol) {
            CloseAgentPositions(symbol);
            
            // Remove o agente dos arrays
            for(int j = i; j < ArraySize(m_configs) - 1; j++) {
                m_configs[j] = m_configs[j + 1];
                m_states[j] = m_states[j + 1];
            }
            
            ArrayResize(m_configs, ArraySize(m_configs) - 1);
            ArrayResize(m_states, ArraySize(m_states) - 1);
            return true;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Atualiza agentes                                                  |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::UpdateAgents() {
    for(int i = 0; i < ArraySize(m_configs); i++) {
        if(!UpdateAgentState(i)) {
            Print("Failed to update agent: ", m_configs[i].symbol);
            continue;
        }
        
        if(m_states[i].isActive) {
            if(!AnalyzeMarket(m_configs[i].symbol)) {
                Print("Failed to analyze market for: ", m_configs[i].symbol);
                continue;
            }
        }
    }
    return true;
}

//+------------------------------------------------------------------+
//| Valida configuração                                               |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::ValidateConfig(const AgentConfig &config) {
    if(config.symbol == "") return false;
    if(config.riskPerTrade <= 0 || config.riskPerTrade > 5) return false;
    if(config.correlationLimit <= 0 || config.correlationLimit > 1) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza estado do agente                                         |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::UpdateAgentState(int index) {
    if(index < 0 || index >= ArraySize(m_states)) return false;
    
    // Atualiza PnL diário
    m_states[index].dailyPnL = 0; // Implementar cálculo real
    
    // Verifica sessões ativas
    m_states[index].isActive = CheckSessionActive(m_configs[index].sessions);
    
    // Verifica eventos econômicos
    if(CheckEconomicEvents(m_configs[index].events)) {
        m_states[index].isActive = false;
    }
    
    m_states[index].lastUpdate = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Verifica sessão ativa                                             |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::CheckSessionActive(const string &sessions[]) {
    datetime serverTime = TimeCurrent();
    int hour = TimeHour(serverTime);
    
    for(int i = 0; i < ArraySize(sessions); i++) {
        if(sessions[i] == "London" && hour >= 8 && hour < 16) return true;
        if(sessions[i] == "NewYork" && hour >= 13 && hour < 21) return true;
        if(sessions[i] == "Tokyo" && (hour >= 0 && hour < 8)) return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Verifica eventos econômicos                                       |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::CheckEconomicEvents(const string &events[]) {
    // Implementar verificação real de eventos
    return false;
}

//+------------------------------------------------------------------+
//| Executa sinal                                                     |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::ExecuteSignal(string symbol, int direction, double volume) {
    if(!m_core) return false;
    
    // Valida exposição
    if(!ValidateExposure(symbol, volume)) return false;
    
    // Executa ordem
    return m_core.GetTradingSystem().ExecuteOrder(
        direction > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL,
        volume
    );
}

//+------------------------------------------------------------------+
//| Fecha posições do agente                                          |
//+------------------------------------------------------------------+
void CTradingAgentSystem::CloseAgentPositions(string symbol) {
    if(!m_core) return;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) == symbol) {
            m_core.GetTradingSystem().CloseAllPositions();
        }
    }
}

//+------------------------------------------------------------------+
//| Fecha todas as posições                                           |
//+------------------------------------------------------------------+
void CTradingAgentSystem::CloseAllPositions() {
    if(!m_core) return;
    m_core.GetTradingSystem().CloseAllPositions();
}

//+------------------------------------------------------------------+
//| Analisa mercado                                                   |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::AnalyzeMarket(string symbol) {
    if(!m_core) return false;
    
    // Obtém análise do mercado
    AnalysisResult analysis = m_core.GetAnalysis().AnalyzeMarketPatterns(
        symbol,
        NULL,
        PERIOD_CURRENT
    );
    
    // Verifica sinais
    if(analysis.hasGrangerCausality && analysis.predictionAccuracy > 0.7) {
        double volume = GetOptimalPosition(symbol);
        if(volume > 0) {
            ExecuteSignal(symbol, analysis.nextPrediction > 0 ? 1 : -1, volume);
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém posição ótima                                               |
//+------------------------------------------------------------------+
double CTradingAgentSystem::GetOptimalPosition(string symbol) {
    if(!m_core) return 0;
    
    for(int i = 0; i < ArraySize(m_configs); i++) {
        if(m_configs[i].symbol == symbol) {
            double equity = AccountInfoDouble(ACCOUNT_EQUITY);
            return equity * (m_configs[i].riskPerTrade / 100.0);
        }
    }
    
    return 0;
}

//+------------------------------------------------------------------+
//| Valida exposição                                                  |
//+------------------------------------------------------------------+
bool CTradingAgentSystem::ValidateExposure(string symbol, double volume) {
    double totalExposure = GetTotalExposure();
    
    // Verifica exposição total
    if(totalExposure + volume > m_maxExposure) {
        return false;
    }
    
    // Verifica correlações
    for(int i = 0; i < ArraySize(m_configs); i++) {
        if(m_configs[i].symbol != symbol) {
            double correlation = CalculateCorrelation(symbol, m_configs[i].symbol);
            if(correlation > m_configs[i].correlationLimit) {
                return false;
            }
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula correlação                                                |
//+------------------------------------------------------------------+
double CTradingAgentSystem::CalculateCorrelation(string symbol1, string symbol2) {
    if(!m_core) return 0;
    return m_core.GetMonitoring().CalculateCorrelation(symbol1, symbol2);
}

//+------------------------------------------------------------------+
//| Obtém estado do agente                                            |
//+------------------------------------------------------------------+
AgentState CTradingAgentSystem::GetAgentState(string symbol) {
    for(int i = 0; i < ArraySize(m_configs); i++) {
        if(m_configs[i].symbol == symbol) {
            return m_states[i];
        }
    }
    
    AgentState empty = {0};
    return empty;
}

//+------------------------------------------------------------------+
//| Obtém exposição total                                             |
//+------------------------------------------------------------------+
double CTradingAgentSystem::GetTotalExposure() {
    double total = 0;
    
    for(int i = 0; i < ArraySize(m_states); i++) {
        total += m_states[i].exposure;
    }
    
    return total;
} 