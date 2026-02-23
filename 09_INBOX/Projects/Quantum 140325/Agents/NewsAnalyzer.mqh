#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Enumeração para impacto da notícia
enum ENUM_NEWS_IMPACT {
    NEWS_IMPACT_LOW,      // Baixo impacto
    NEWS_IMPACT_MEDIUM,   // Médio impacto
    NEWS_IMPACT_HIGH      // Alto impacto
};

// Estrutura para evento de notícia
struct NewsEvent {
    string   title;           // Título da notícia
    datetime time;           // Horário do evento
    string   currency;       // Moeda afetada
    string   description;    // Descrição do evento
    double   forecast;       // Previsão
    double   previous;       // Valor anterior
    double   actual;         // Valor atual
    ENUM_NEWS_IMPACT impact; // Impacto esperado
    bool     deviation;      // Se houve desvio significativo
};

// Estrutura para análise de notícia
struct NewsAnalysis {
    NewsEvent event;         // Evento analisado
    double    priceImpact;   // Impacto no preço (%)
    double    volumeImpact;  // Impacto no volume (%)
    double    volatility;    // Volatilidade durante o evento
    int       direction;     // Direção do movimento (-1, 0, 1)
    double    confidence;    // Confiança na análise (0-1)
    string    recommendation; // Recomendação de trading
};

//+------------------------------------------------------------------+
//| Classe NewsAnalyzer                                               |
//+------------------------------------------------------------------+
class CNewsAnalyzer {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    NewsEvent       m_events[];
    NewsAnalysis    m_analysis[];
    
    // Configurações
    int             m_lookbackMinutes;  // Minutos para análise antes/depois
    double          m_deviationThreshold; // Limite para desvio significativo
    double          m_volatilityThreshold; // Limite para volatilidade alta
    double          m_minConfidence;    // Confiança mínima para sinais
    
    // Estado do analisador
    bool            m_isActive;
    datetime        m_lastUpdate;
    string          m_currencies[];
    
    // Métodos privados
    bool            UpdateNewsEvents();
    bool            AnalyzeNewsImpact(NewsEvent &event, NewsAnalysis &analysis);
    bool            ValidateEvent(const NewsEvent &event);
    double          CalculateDeviation(const NewsEvent &event);
    string          GenerateRecommendation(const NewsAnalysis &analysis);
    void            LogNewsAnalysis(const NewsAnalysis &analysis);
    
public:
                    CNewsAnalyzer();
                   ~CNewsAnalyzer();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            AddCurrency(const string currency);
    bool            RemoveCurrency(const string currency);
    bool            UpdateAnalysis();
    
    // Métodos de consulta
    bool            GetNextEvent(NewsEvent &event);
    bool            GetLastAnalysis(const string currency, NewsAnalysis &analysis);
    bool            IsHighImpactTime(const string currency);
    
    // Configurações
    void            SetLookbackPeriod(const int minutes) { m_lookbackMinutes = minutes; }
    void            SetDeviationThreshold(const double threshold) { m_deviationThreshold = threshold; }
    void            SetVolatilityThreshold(const double threshold) { m_volatilityThreshold = threshold; }
    void            SetMinConfidence(const double confidence) { m_minConfidence = confidence; }
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    int             GetEventsCount() const { return ArraySize(m_events); }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CNewsAnalyzer::CNewsAnalyzer() {
    m_core = NULL;
    m_isActive = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_lookbackMinutes = 30;       // 30 minutos antes/depois
    m_deviationThreshold = 0.5;   // 0.5 desvio padrão
    m_volatilityThreshold = 2.0;  // 2x volatilidade normal
    m_minConfidence = 0.7;        // 70% confiança mínima
    
    ArrayResize(m_events, 0);
    ArrayResize(m_analysis, 0);
    ArrayResize(m_currencies, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CNewsAnalyzer::~CNewsAnalyzer() {
    ArrayFree(m_events);
    ArrayFree(m_analysis);
    ArrayFree(m_currencies);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isActive = true;
    m_lastUpdate = TimeCurrent();
    
    // Adiciona principais moedas por padrão
    AddCurrency("USD");
    AddCurrency("EUR");
    AddCurrency("GBP");
    AddCurrency("JPY");
    
    return UpdateNewsEvents();
}

//+------------------------------------------------------------------+
//| Adiciona moeda                                                    |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::AddCurrency(const string currency) {
    // Verifica se a moeda já existe
    for(int i = 0; i < ArraySize(m_currencies); i++) {
        if(m_currencies[i] == currency) return false;
    }
    
    // Adiciona nova moeda
    int size = ArraySize(m_currencies);
    ArrayResize(m_currencies, size + 1);
    m_currencies[size] = currency;
    
    return true;
}

//+------------------------------------------------------------------+
//| Remove moeda                                                      |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::RemoveCurrency(const string currency) {
    int index = -1;
    
    // Encontra índice da moeda
    for(int i = 0; i < ArraySize(m_currencies); i++) {
        if(m_currencies[i] == currency) {
            index = i;
            break;
        }
    }
    
    if(index == -1) return false;
    
    // Remove moeda
    int size = ArraySize(m_currencies);
    for(int i = index; i < size - 1; i++) {
        m_currencies[i] = m_currencies[i + 1];
    }
    
    ArrayResize(m_currencies, size - 1);
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza análise                                                  |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::UpdateAnalysis() {
    if(!m_isActive || !m_core) return false;
    
    // Atualiza eventos
    if(!UpdateNewsEvents()) {
        Print("Failed to update news events");
        return false;
    }
    
    // Limpa análises antigas
    ArrayResize(m_analysis, 0);
    
    // Analisa cada evento
    for(int i = 0; i < ArraySize(m_events); i++) {
        if(ValidateEvent(m_events[i])) {
            NewsAnalysis analysis;
            if(AnalyzeNewsImpact(m_events[i], analysis)) {
                int size = ArraySize(m_analysis);
                ArrayResize(m_analysis, size + 1);
                m_analysis[size] = analysis;
                
                LogNewsAnalysis(analysis);
            }
        }
    }
    
    m_lastUpdate = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Obtém próximo evento                                              |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::GetNextEvent(NewsEvent &event) {
    datetime currentTime = TimeCurrent();
    datetime nextTime = D'2100.01.01';
    int nextIndex = -1;
    
    // Encontra próximo evento
    for(int i = 0; i < ArraySize(m_events); i++) {
        if(m_events[i].time > currentTime && m_events[i].time < nextTime) {
            nextTime = m_events[i].time;
            nextIndex = i;
        }
    }
    
    if(nextIndex == -1) return false;
    
    event = m_events[nextIndex];
    return true;
}

//+------------------------------------------------------------------+
//| Obtém última análise                                              |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::GetLastAnalysis(const string currency, NewsAnalysis &analysis) {
    datetime lastTime = 0;
    int lastIndex = -1;
    
    // Encontra análise mais recente para a moeda
    for(int i = 0; i < ArraySize(m_analysis); i++) {
        if(m_analysis[i].event.currency == currency && m_analysis[i].event.time > lastTime) {
            lastTime = m_analysis[i].event.time;
            lastIndex = i;
        }
    }
    
    if(lastIndex == -1) return false;
    
    analysis = m_analysis[lastIndex];
    return true;
}

//+------------------------------------------------------------------+
//| Verifica período de alto impacto                                  |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::IsHighImpactTime(const string currency) {
    datetime currentTime = TimeCurrent();
    
    for(int i = 0; i < ArraySize(m_events); i++) {
        if(m_events[i].currency == currency && m_events[i].impact == NEWS_IMPACT_HIGH) {
            datetime eventTime = m_events[i].time;
            
            // Verifica se está dentro do período de análise
            if(currentTime >= eventTime - m_lookbackMinutes * 60 &&
               currentTime <= eventTime + m_lookbackMinutes * 60) {
                return true;
            }
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Atualiza eventos                                                  |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::UpdateNewsEvents() {
    if(!m_isActive || !m_core) return false;
    
    // Limpa eventos antigos
    ArrayResize(m_events, 0);
    
    // Obtém novos eventos do calendário econômico
    MqlCalendarValue values[];
    MqlCalendarEvent events[];
    
    datetime fromDate = TimeCurrent();
    datetime toDate = fromDate + 7 * 24 * 60 * 60; // 7 dias à frente
    
    if(CalendarValueHistory(values, fromDate, toDate, m_currencies)) {
        for(int i = 0; i < ArraySize(values); i++) {
            if(CalendarEventById(events, values[i].event_id)) {
                NewsEvent event;
                event.title = events[0].name;
                event.time = values[i].time;
                event.currency = events[0].currency;
                event.description = events[0].description;
                event.forecast = values[i].forecast;
                event.previous = values[i].previous;
                event.actual = values[i].actual;
                
                // Define impacto baseado na importância do evento
                switch(events[0].importance) {
                    case CALENDAR_IMPORTANCE_LOW:    event.impact = NEWS_IMPACT_LOW; break;
                    case CALENDAR_IMPORTANCE_MEDIUM: event.impact = NEWS_IMPACT_MEDIUM; break;
                    case CALENDAR_IMPORTANCE_HIGH:   event.impact = NEWS_IMPACT_HIGH; break;
                    default: event.impact = NEWS_IMPACT_LOW;
                }
                
                // Verifica desvio
                event.deviation = (MathAbs(event.actual - event.forecast) > m_deviationThreshold);
                
                // Adiciona evento
                int size = ArraySize(m_events);
                ArrayResize(m_events, size + 1);
                m_events[size] = event;
            }
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Analisa impacto da notícia                                        |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::AnalyzeNewsImpact(NewsEvent &event, NewsAnalysis &analysis) {
    analysis.event = event;
    
    // Obtém dados do mercado
    string symbol = event.currency;
    if(symbol != "USD") symbol += "USD";
    
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    
    datetime fromTime = event.time - m_lookbackMinutes * 60;
    datetime toTime = event.time + m_lookbackMinutes * 60;
    
    if(CopyRates(symbol, PERIOD_M1, fromTime, toTime, rates) <= 0) {
        return false;
    }
    
    // Calcula impacto no preço
    double preBefore = rates[m_lookbackMinutes].close;
    double preAfter = rates[0].close;
    analysis.priceImpact = (preAfter - preBefore) / preBefore * 100;
    
    // Calcula impacto no volume
    double avgVolumeBefore = 0;
    double avgVolumeAfter = 0;
    
    for(int i = 0; i < m_lookbackMinutes; i++) {
        avgVolumeBefore += rates[m_lookbackMinutes + i].tick_volume;
        avgVolumeAfter += rates[i].tick_volume;
    }
    
    avgVolumeBefore /= m_lookbackMinutes;
    avgVolumeAfter /= m_lookbackMinutes;
    
    analysis.volumeImpact = (avgVolumeAfter - avgVolumeBefore) / avgVolumeBefore * 100;
    
    // Calcula volatilidade
    double volatility = 0;
    for(int i = 0; i < ArraySize(rates); i++) {
        volatility += (rates[i].high - rates[i].low) / rates[i].open;
    }
    analysis.volatility = volatility / ArraySize(rates);
    
    // Determina direção
    if(MathAbs(analysis.priceImpact) < 0.1) {
        analysis.direction = 0; // Lateral
    }
    else {
        analysis.direction = analysis.priceImpact > 0 ? 1 : -1;
    }
    
    // Calcula confiança
    analysis.confidence = 0.5; // Base
    
    // Ajusta confiança baseado no impacto
    if(event.impact == NEWS_IMPACT_HIGH) analysis.confidence += 0.2;
    if(event.deviation) analysis.confidence += 0.2;
    if(analysis.volatility > m_volatilityThreshold) analysis.confidence += 0.1;
    
    // Gera recomendação
    analysis.recommendation = GenerateRecommendation(analysis);
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida evento                                                     |
//+------------------------------------------------------------------+
bool CNewsAnalyzer::ValidateEvent(const NewsEvent &event) {
    if(event.time == 0) return false;
    if(event.currency == "") return false;
    
    // Verifica se a moeda está sendo monitorada
    bool validCurrency = false;
    for(int i = 0; i < ArraySize(m_currencies); i++) {
        if(event.currency == m_currencies[i]) {
            validCurrency = true;
            break;
        }
    }
    
    return validCurrency;
}

//+------------------------------------------------------------------+
//| Calcula desvio                                                    |
//+------------------------------------------------------------------+
double CNewsAnalyzer::CalculateDeviation(const NewsEvent &event) {
    if(event.forecast == 0) return 0;
    
    return (event.actual - event.forecast) / event.forecast * 100;
}

//+------------------------------------------------------------------+
//| Gera recomendação                                                 |
//+------------------------------------------------------------------+
string CNewsAnalyzer::GenerateRecommendation(const NewsAnalysis &analysis) {
    string recommendation = "";
    
    if(analysis.confidence < m_minConfidence) {
        recommendation = "Aguardar - Baixa confiança";
        return recommendation;
    }
    
    // Analisa direção e impacto
    if(analysis.direction > 0) {
        if(analysis.volatility > m_volatilityThreshold) {
            recommendation = "Compra agressiva";
        }
        else {
            recommendation = "Compra conservadora";
        }
    }
    else if(analysis.direction < 0) {
        if(analysis.volatility > m_volatilityThreshold) {
            recommendation = "Venda agressiva";
        }
        else {
            recommendation = "Venda conservadora";
        }
    }
    else {
        recommendation = "Aguardar - Mercado lateral";
    }
    
    // Adiciona avisos
    if(analysis.event.impact == NEWS_IMPACT_HIGH) {
        recommendation += " (Alto impacto)";
    }
    
    if(analysis.event.deviation) {
        recommendation += " (Desvio significativo)";
    }
    
    return recommendation;
}

//+------------------------------------------------------------------+
//| Registra análise                                                  |
//+------------------------------------------------------------------+
void CNewsAnalyzer::LogNewsAnalysis(const NewsAnalysis &analysis) {
    Print("News Analysis - Event: ", analysis.event.title,
          ", Currency: ", analysis.event.currency,
          ", Impact: ", EnumToString(analysis.event.impact),
          ", Price Impact: ", analysis.priceImpact, "%",
          ", Volume Impact: ", analysis.volumeImpact, "%",
          ", Confidence: ", analysis.confidence,
          ", Recommendation: ", analysis.recommendation);
} 