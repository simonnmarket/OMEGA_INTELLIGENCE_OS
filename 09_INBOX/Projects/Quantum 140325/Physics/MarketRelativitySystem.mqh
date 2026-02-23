#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para frame de referência temporal
struct TimeFrame {
    string   name;           // Nome do timeframe (M1, M5, M15, etc.)
    int      minutes;        // Duração em minutos
    double   latency;        // Latência média em milissegundos
    double   volatility;     // Volatilidade média
    datetime lastUpdate;     // Última atualização
};

// Estrutura para sessão de mercado
struct MarketSession {
    string   name;           // Nome da sessão (Ásia, Europa, EUA)
    int      startHour;      // Hora de início (GMT)
    int      endHour;        // Hora de fim (GMT)
    bool     isActive;       // Se a sessão está ativa
    double   avgVolatility;  // Volatilidade média da sessão
    double   avgVolume;      // Volume médio da sessão
};

// Estrutura para análise relativística
struct RelativityAnalysis {
    string   symbol;
    string   timeframe;
    datetime timestamp;
    double   temporalEffect;    // Efeito da dilatação temporal (-1 a 1)
    double   regionalEffect;    // Efeito regional (-1 a 1)
    double   sessionImpact;     // Impacto da sessão atual (0 a 1)
    string   dominantSession;   // Sessão dominante atual
    double   adjustedVolatility;// Volatilidade ajustada
    string   recommendation;    // Recomendação baseada na análise
};

//+------------------------------------------------------------------+
//| Classe MarketRelativitySystem                                      |
//+------------------------------------------------------------------+
class CMarketRelativitySystem {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    
    // Frames de referência
    TimeFrame       m_timeframes[];
    MarketSession   m_sessions[];
    
    // Cache de análises
    RelativityAnalysis m_analyses[];
    
    // Estado do sistema
    bool            m_isInitialized;
    datetime        m_lastUpdate;
    
    // Configurações
    double          m_latencyThreshold;    // Limite de latência aceitável
    double          m_volatilityWindow;    // Janela para cálculo de volatilidade
    int             m_maxAnalyses;         // Máximo de análises em cache
    
    // Métodos privados
    void            InitializeTimeFrames();
    void            InitializeSessions();
    bool            UpdateSessionStates();
    double          CalculateTemporalEffect(const string symbol, const TimeFrame &tf);
    double          CalculateRegionalEffect(const string symbol, const MarketSession &session);
    double          CalculateSessionImpact(const MarketSession &session);
    string          DetermineDominantSession();
    void            CleanupOldAnalyses();
    
public:
                    CMarketRelativitySystem();
                   ~CMarketRelativitySystem();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            Update();
    
    // Métodos de análise
    bool            AnalyzeRelativity(const string symbol, const string timeframe, RelativityAnalysis &analysis);
    bool            GetLatestAnalysis(const string symbol, const string timeframe, RelativityAnalysis &analysis);
    
    // Métodos de consulta
    bool            IsSessionActive(const string session);
    TimeFrame      *GetTimeFrames() { return m_timeframes; }
    MarketSession  *GetSessions() { return m_sessions; }
    
    // Getters/Setters
    void            SetLatencyThreshold(double threshold) { m_latencyThreshold = threshold; }
    void            SetVolatilityWindow(double window) { m_volatilityWindow = window; }
    bool            IsInitialized() const { return m_isInitialized; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CMarketRelativitySystem::CMarketRelativitySystem() {
    m_core = NULL;
    m_isInitialized = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_latencyThreshold = 100.0;  // 100ms
    m_volatilityWindow = 20;     // 20 períodos
    m_maxAnalyses = 1000;
    
    ArrayResize(m_analyses, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CMarketRelativitySystem::~CMarketRelativitySystem() {
    ArrayFree(m_timeframes);
    ArrayFree(m_sessions);
    ArrayFree(m_analyses);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    // Inicializa frames de referência
    InitializeTimeFrames();
    InitializeSessions();
    
    m_isInitialized = true;
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicializa timeframes                                             |
//+------------------------------------------------------------------+
void CMarketRelativitySystem::InitializeTimeFrames() {
    // Define timeframes padrão
    TimeFrame frames[] = {
        {"M1",  1,  50, 0.0, 0},
        {"M5",  5,  50, 0.0, 0},
        {"M15", 15, 50, 0.0, 0},
        {"H1",  60, 50, 0.0, 0},
        {"H4",  240,50, 0.0, 0},
        {"D1",  1440,50,0.0, 0}
    };
    
    int size = ArraySize(frames);
    ArrayResize(m_timeframes, size);
    ArrayCopy(m_timeframes, frames);
}

//+------------------------------------------------------------------+
//| Inicializa sessões                                                |
//+------------------------------------------------------------------+
void CMarketRelativitySystem::InitializeSessions() {
    // Define sessões padrão (horários em GMT)
    MarketSession sessions[] = {
        {"Asia",    0,  8, false, 0.0, 0.0},
        {"Europe",  8, 16, false, 0.0, 0.0},
        {"US",     13, 21, false, 0.0, 0.0}
    };
    
    int size = ArraySize(sessions);
    ArrayResize(m_sessions, size);
    ArrayCopy(m_sessions, sessions);
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::Update() {
    if(!m_isInitialized || !m_core) return false;
    
    // Atualiza estado das sessões
    UpdateSessionStates();
    
    // Limpa análises antigas
    CleanupOldAnalyses();
    
    m_lastUpdate = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza estados das sessões                                      |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::UpdateSessionStates() {
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    
    // Ajusta hora local para GMT
    int gmtOffset = 0; // Deve ser configurado conforme o servidor
    int currentHour = (dt.hour + gmtOffset) % 24;
    
    // Atualiza estado de cada sessão
    for(int i = 0; i < ArraySize(m_sessions); i++) {
        if(currentHour >= m_sessions[i].startHour && currentHour < m_sessions[i].endHour) {
            m_sessions[i].isActive = true;
            
            // Atualiza métricas da sessão
            if(m_core != NULL) {
                // Calcula volatilidade média da sessão
                m_sessions[i].avgVolatility = m_core.GetAnalysis().CalculateSessionVolatility(
                    m_sessions[i].name,
                    m_sessions[i].startHour,
                    m_sessions[i].endHour
                );
                
                // Calcula volume médio da sessão
                m_sessions[i].avgVolume = m_core.GetAnalysis().CalculateSessionVolume(
                    m_sessions[i].name,
                    m_sessions[i].startHour,
                    m_sessions[i].endHour
                );
            }
        }
        else {
            m_sessions[i].isActive = false;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Analisa relatividade                                              |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::AnalyzeRelativity(
    const string symbol,
    const string timeframe,
    RelativityAnalysis &analysis
) {
    if(!m_isInitialized || !m_core) return false;
    
    // Encontra timeframe correspondente
    TimeFrame* tf = NULL;
    for(int i = 0; i < ArraySize(m_timeframes); i++) {
        if(m_timeframes[i].name == timeframe) {
            tf = &m_timeframes[i];
            break;
        }
    }
    if(tf == NULL) return false;
    
    // Prepara análise
    analysis.symbol = symbol;
    analysis.timeframe = timeframe;
    analysis.timestamp = TimeCurrent();
    
    // Calcula efeitos
    analysis.temporalEffect = CalculateTemporalEffect(symbol, *tf);
    analysis.dominantSession = DetermineDominantSession();
    
    // Encontra sessão atual
    MarketSession* currentSession = NULL;
    for(int i = 0; i < ArraySize(m_sessions); i++) {
        if(m_sessions[i].isActive) {
            currentSession = &m_sessions[i];
            break;
        }
    }
    
    if(currentSession != NULL) {
        analysis.regionalEffect = CalculateRegionalEffect(symbol, *currentSession);
        analysis.sessionImpact = CalculateSessionImpact(*currentSession);
    }
    
    // Ajusta volatilidade
    analysis.adjustedVolatility = m_core.GetAnalysis().CalculateVolatility(
        symbol,
        StringToTimeFrame(timeframe)
    ) * (1 + analysis.temporalEffect) * (1 + analysis.regionalEffect);
    
    // Gera recomendação
    if(analysis.temporalEffect > 0.5 && analysis.regionalEffect > 0.5) {
        analysis.recommendation = "Strong Trading Conditions";
    }
    else if(analysis.temporalEffect < -0.5 || analysis.regionalEffect < -0.5) {
        analysis.recommendation = "Weak Trading Conditions";
    }
    else {
        analysis.recommendation = "Neutral Trading Conditions";
    }
    
    // Armazena análise
    int size = ArraySize(m_analyses);
    if(size >= m_maxAnalyses) {
        CleanupOldAnalyses();
        size = ArraySize(m_analyses);
    }
    
    ArrayResize(m_analyses, size + 1);
    m_analyses[size] = analysis;
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula efeito temporal                                           |
//+------------------------------------------------------------------+
double CMarketRelativitySystem::CalculateTemporalEffect(
    const string symbol,
    const TimeFrame &tf
) {
    if(!m_core) return 0.0;
    
    // Calcula latência média
    double currentLatency = m_core.GetMonitoring().GetLatency(symbol);
    double latencyEffect = (currentLatency <= m_latencyThreshold) ? 1.0 : 
                          -1.0 * (currentLatency - m_latencyThreshold) / m_latencyThreshold;
    
    // Calcula efeito da volatilidade
    double currentVolatility = m_core.GetAnalysis().CalculateVolatility(
        symbol,
        StringToTimeFrame(tf.name)
    );
    
    double volatilityEffect = (currentVolatility - tf.volatility) / 
                             (tf.volatility > 0 ? tf.volatility : 1);
    
    // Combina efeitos
    return MathMax(-1.0, MathMin(1.0, (latencyEffect + volatilityEffect) / 2));
}

//+------------------------------------------------------------------+
//| Calcula efeito regional                                           |
//+------------------------------------------------------------------+
double CMarketRelativitySystem::CalculateRegionalEffect(
    const string symbol,
    const MarketSession &session
) {
    if(!m_core) return 0.0;
    
    // Calcula efeito do volume
    double currentVolume = m_core.GetAnalysis().CalculateVolume(symbol);
    double volumeEffect = (currentVolume - session.avgVolume) / 
                         (session.avgVolume > 0 ? session.avgVolume : 1);
    
    // Calcula efeito da volatilidade
    double currentVolatility = m_core.GetAnalysis().CalculateVolatility(symbol);
    double volatilityEffect = (currentVolatility - session.avgVolatility) /
                             (session.avgVolatility > 0 ? session.avgVolatility : 1);
    
    // Combina efeitos
    return MathMax(-1.0, MathMin(1.0, (volumeEffect + volatilityEffect) / 2));
}

//+------------------------------------------------------------------+
//| Calcula impacto da sessão                                         |
//+------------------------------------------------------------------+
double CMarketRelativitySystem::CalculateSessionImpact(
    const MarketSession &session
) {
    if(!session.isActive) return 0.0;
    
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    
    // Calcula posição relativa na sessão
    int sessionLength = session.endHour - session.startHour;
    int currentHour = (dt.hour - session.startHour + 24) % 24;
    
    // Retorna valor entre 0 e 1 baseado na posição na sessão
    return (double)currentHour / sessionLength;
}

//+------------------------------------------------------------------+
//| Determina sessão dominante                                        |
//+------------------------------------------------------------------+
string CMarketRelativitySystem::DetermineDominantSession() {
    string dominant = "None";
    double maxImpact = 0;
    
    for(int i = 0; i < ArraySize(m_sessions); i++) {
        if(m_sessions[i].isActive) {
            double impact = CalculateSessionImpact(m_sessions[i]);
            if(impact > maxImpact) {
                maxImpact = impact;
                dominant = m_sessions[i].name;
            }
        }
    }
    
    return dominant;
}

//+------------------------------------------------------------------+
//| Obtém última análise                                              |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::GetLatestAnalysis(
    const string symbol,
    const string timeframe,
    RelativityAnalysis &analysis
) {
    for(int i = ArraySize(m_analyses) - 1; i >= 0; i--) {
        if(m_analyses[i].symbol == symbol && m_analyses[i].timeframe == timeframe) {
            analysis = m_analyses[i];
            return true;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Verifica se sessão está ativa                                     |
//+------------------------------------------------------------------+
bool CMarketRelativitySystem::IsSessionActive(const string session) {
    for(int i = 0; i < ArraySize(m_sessions); i++) {
        if(m_sessions[i].name == session) {
            return m_sessions[i].isActive;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Limpa análises antigas                                            |
//+------------------------------------------------------------------+
void CMarketRelativitySystem::CleanupOldAnalyses() {
    datetime current = TimeCurrent();
    
    // Remove análises com mais de 24 horas
    for(int i = ArraySize(m_analyses) - 1; i >= 0; i--) {
        if(current - m_analyses[i].timestamp > 24 * 3600) {
            for(int j = i; j < ArraySize(m_analyses) - 1; j++) {
                m_analyses[j] = m_analyses[j + 1];
            }
            ArrayResize(m_analyses, ArraySize(m_analyses) - 1);
        }
    }
    
    // Se ainda exceder o máximo, remove as mais antigas
    while(ArraySize(m_analyses) > m_maxAnalyses) {
        for(int i = 0; i < ArraySize(m_analyses) - 1; i++) {
            m_analyses[i] = m_analyses[i + 1];
        }
        ArrayResize(m_analyses, ArraySize(m_analyses) - 1);
    }
} 