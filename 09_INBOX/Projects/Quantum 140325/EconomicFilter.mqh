#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para eventos econômicos
struct NewsEvent {
    datetime time;        // Horário do evento
    int importance;       // Importância (1-3)
    string currency;      // Moeda afetada
    string description;   // Descrição do evento
};

// Classe para filtro de calendário econômico
class CEconomicFilter {
private:
    // Estado
    bool m_isInitialized;
    NewsEvent m_events[];
    int m_eventCount;
    int m_timeWindow;     // Janela temporal em minutos
    
    // Métodos privados
    void SortEvents() {
        ArraySort(m_events, WHOLE_ARRAY, 0, sortEvents);
    }
    
    static int sortEvents(const void& first, const void& second) {
        const NewsEvent* e1 = (const NewsEvent*)first;
        const NewsEvent* e2 = (const NewsEvent*)second;
        
        if(e1.time < e2.time) return -1;
        if(e1.time > e2.time) return 1;
        return 0;
    }
    
    bool IsHighImpactEvent(const NewsEvent& event) {
        return event.importance >= 2; // Eventos de importância 2 ou 3
    }
    
public:
    // Construtor
    CEconomicFilter() {
        m_isInitialized = false;
        m_eventCount = 0;
        m_timeWindow = 30; // 30 minutos por padrão
    }
    
    // Destrutor
    ~CEconomicFilter() {
        ArrayFree(m_events);
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar evento
    void AddEvent(datetime time, int importance, string currency, string description) {
        if(!m_isInitialized) return;
        
        int size = ArraySize(m_events);
        if(m_eventCount >= size) {
            ArrayResize(m_events, size + 1);
        }
        
        m_events[m_eventCount].time = time;
        m_events[m_eventCount].importance = importance;
        m_events[m_eventCount].currency = currency;
        m_events[m_eventCount].description = description;
        
        m_eventCount++;
        SortEvents();
    }
    
    // Verificar se trading é permitido
    bool IsTradeAllowed(string symbol) {
        if(!m_isInitialized) return true;
        
        datetime currentTime = TimeCurrent();
        string currency = StringSubstr(symbol, 0, 3);
        
        for(int i = 0; i < m_eventCount; i++) {
            NewsEvent& event = m_events[i];
            
            // Verificar se o evento afeta a moeda do símbolo
            if(event.currency != currency) continue;
            
            // Verificar se o evento está dentro da janela temporal
            if(MathAbs(event.time - currentTime) <= m_timeWindow * 60) {
                // Se for evento de alto impacto, não permitir trading
                if(IsHighImpactEvent(event)) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    // Configurações
    void SetTimeWindow(int minutes) {
        m_timeWindow = minutes;
    }
    
    // Limpar eventos
    void ClearEvents() {
        ArrayFree(m_events);
        m_eventCount = 0;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Economic Filter Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Event Count: ", m_eventCount);
        Print("Time Window: ", m_timeWindow, " minutes");
    }
}; 