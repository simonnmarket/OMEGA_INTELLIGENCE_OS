#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para evento econômico
struct EconomicEvent {
    datetime time;           // Tempo do evento
    string currency;         // Moeda afetada
    string name;            // Nome do evento
    int impact;             // Nível de impacto (1-3)
    string description;     // Descrição
    double expectedVolatility; // Volatilidade esperada
};

// Classe para gerenciamento do calendário econômico
class CEconomicCalendar {
private:
    // Arrays de dados
    EconomicEvent m_events[];
    
    // Configurações
    int m_lookAheadHours;   // Horas para frente
    int m_minImpact;        // Impacto mínimo
    
    // Estado
    bool m_isInitialized;
    datetime m_lastUpdate;
    
    // Métodos privados
    void AddEvent(const EconomicEvent& event) {
        int size = ArraySize(m_events);
        ArrayResize(m_events, size + 1);
        m_events[size] = event;
    }
    
    bool CheckHighImpactEvents() {
        datetime currentTime = TimeCurrent();
        
        for(int i = 0; i < ArraySize(m_events); i++) {
            if(m_events[i].impact >= m_minImpact &&
               m_events[i].time <= currentTime + m_lookAheadHours * 3600 &&
               m_events[i].time > currentTime) {
                return true;
            }
        }
        
        return false;
    }
    
public:
    // Construtor
    CEconomicCalendar() {
        // Configurações padrão
        m_lookAheadHours = 24;
        m_minImpact = 2;
        
        m_isInitialized = false;
        m_lastUpdate = 0;
    }
    
    // Destrutor
    ~CEconomicCalendar() {
        // Limpar array de eventos
        ArrayFree(m_events);
    }
    
    // Inicialização
    bool Initialize() {
        // Carregar eventos de exemplo
        EconomicEvent event;
        
        // Evento de exemplo 1
        event.time = TimeCurrent() + 3600; // 1 hora
        event.currency = "USD";
        event.name = "Non-Farm Payrolls";
        event.impact = 3;
        event.description = "Monthly employment report";
        event.expectedVolatility = 2.5;
        AddEvent(event);
        
        // Evento de exemplo 2
        event.time = TimeCurrent() + 7200; // 2 horas
        event.currency = "EUR";
        event.name = "ECB Interest Rate";
        event.impact = 3;
        event.description = "European Central Bank rate decision";
        event.expectedVolatility = 2.0;
        AddEvent(event);
        
        // Evento de exemplo 3
        event.time = TimeCurrent() + 10800; // 3 horas
        event.currency = "GBP";
        event.name = "GDP";
        event.impact = 2;
        event.description = "Gross Domestic Product";
        event.expectedVolatility = 1.5;
        AddEvent(event);
        
        m_isInitialized = true;
        m_lastUpdate = TimeCurrent();
        return true;
    }
    
    // Verificar eventos de alto impacto
    bool CheckHighImpactEvents() {
        if(!m_isInitialized) return false;
        return CheckHighImpactEvents();
    }
    
    // Obter próximos eventos
    EconomicEvent GetUpcomingEvents(int index) {
        EconomicEvent event = {};
        
        if(!m_isInitialized || index < 0 || index >= ArraySize(m_events)) {
            return event;
        }
        
        return m_events[index];
    }
    
    // Configurações
    void SetLookAheadHours(int hours) {
        m_lookAheadHours = hours;
    }
    
    void SetMinImpact(int impact) {
        m_minImpact = impact;
    }
    
    // Acesso
    int GetTotalEvents() const {
        return ArraySize(m_events);
    }
    
    datetime GetLastUpdate() const {
        return m_lastUpdate;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    // Métricas
    void UpdateMetrics() {
        Print("Economic Calendar Metrics:");
        Print("Total Events: ", GetTotalEvents());
        Print("Last Update: ", TimeToString(m_lastUpdate));
        Print("High Impact Events: ", HasHighImpactEvent() ? "Yes" : "No");
    }
}; 