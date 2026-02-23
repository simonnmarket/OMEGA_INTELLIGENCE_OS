#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para sinais de insights
struct InsightSignal {
    string categoryName;      // Nome da categoria
    string signalName;       // Nome do sinal
    double strength;         // Força do sinal (0-1)
    double confidence;       // Confiança (0-1)
    datetime timestamp;      // Momento da geração
    string description;      // Descrição detalhada
    bool isValid;           // Validação do sinal
    
    // Metadados para integração
    int priority;           // Prioridade do sinal
    double impact;          // Impacto esperado
    string correlations[];  // Correlações com outras categorias
    
    void Reset() {
        categoryName = "";
        signalName = "";
        strength = 0.0;
        confidence = 0.0;
        timestamp = 0;
        description = "";
        isValid = false;
        priority = 0;
        impact = 0.0;
        ArrayFree(correlations);
    }
};

// Interface base para todas as categorias
interface IInsightCategory {
public:
    bool Initialize();
    bool Update();
    bool Validate();
    string GetCategoryName();
    double GetInsightScore();
    bool GetSignals(InsightSignal &signals[]);
};

// Classe base para todas as categorias
class CBaseCategoryAnalyzer : public IInsightCategory {
protected:
    string          m_categoryName;
    InsightSignal   m_signals[];
    
    struct CategoryMetrics {
        double accuracy;
        double reliability;
        double adaptability;
        datetime lastUpdate;
        
        void Reset() {
            accuracy = 0.0;
            reliability = 0.0;
            adaptability = 0.0;
            lastUpdate = 0;
        }
    } m_metrics;
    
    struct CategoryState {
        bool isInitialized;
        bool isActive;
        bool needsUpdate;
        int signalCount;
        
        void Reset() {
            isInitialized = false;
            isActive = false;
            needsUpdate = true;
            signalCount = 0;
        }
    } m_state;

public:
    // Construtor padrão
    CBaseCategoryAnalyzer(string categoryName) {
        m_categoryName = categoryName;
        InitializeBase();
    }
    
    // Métodos da interface
    virtual bool Initialize() {
        if(m_state.isInitialized) return true;
        
        if(!ValidateCategory()) {
            LogError("Falha na validação da categoria: " + m_categoryName);
            return false;
        }
        
        m_state.isInitialized = true;
        m_state.isActive = true;
        return true;
    }
    
    virtual bool Update() {
        if(!m_state.isInitialized || !m_state.isActive) return false;
        
        if(!ProcessCategory()) {
            LogError("Falha ao processar categoria: " + m_categoryName);
            return false;
        }
        
        m_metrics.lastUpdate = TimeCurrent();
        return true;
    }
    
    virtual bool Validate() {
        return m_state.isInitialized && m_state.isActive;
    }
    
    virtual string GetCategoryName() { return m_categoryName; }
    
    virtual double GetInsightScore() {
        return CalculateCategoryScore();
    }
    
    virtual bool GetSignals(InsightSignal &signals[]) {
        if(!ValidateSignals()) return false;
        
        ArrayResize(signals, ArraySize(m_signals));
        ArrayCopy(signals, m_signals);
        return true;
    }

protected:
    // Métodos auxiliares base
    virtual void InitializeBase() {
        m_state.Reset();
        m_metrics.Reset();
        ArrayFree(m_signals);
    }
    
    virtual bool ValidateCategory() {
        return !m_categoryName.empty();
    }
    
    virtual bool ValidateSignals() {
        return m_state.isInitialized && m_state.isActive;
    }
    
    virtual double CalculateCategoryScore() {
        return (m_metrics.accuracy + 
                m_metrics.reliability + 
                m_metrics.adaptability) / 3.0;
    }
    
    virtual bool ProcessCategory() {
        return true; // Implementação padrão
    }
    
    void LogError(string message) {
        Print("Erro [" + m_categoryName + "]: " + message);
    }
    
    void AddSignal(InsightSignal &signal) {
        int size = ArraySize(m_signals);
        ArrayResize(m_signals, size + 1);
        m_signals[size] = signal;
        m_state.signalCount++;
    }
};

// Gerenciador central de categorias
class CCategoryManager {
private:
    IInsightCategory* m_categories[];
    
public:
    CCategoryManager() {
        ArrayResize(m_categories, 0);
    }
    
    ~CCategoryManager() {
        for(int i = 0; i < ArraySize(m_categories); i++) {
            if(m_categories[i] != NULL) {
                delete m_categories[i];
            }
        }
        ArrayFree(m_categories);
    }
    
    bool RegisterCategory(IInsightCategory* category) {
        if(category == NULL) return false;
        
        string categoryName = category.GetCategoryName();
        if(categoryName.empty()) return false;
        
        if(!category.Initialize()) {
            Print("Falha ao inicializar categoria: " + categoryName);
            return false;
        }
        
        int size = ArraySize(m_categories);
        ArrayResize(m_categories, size + 1);
        m_categories[size] = category;
        return true;
    }
    
    IInsightCategory* GetCategory(string categoryName) {
        for(int i = 0; i < ArraySize(m_categories); i++) {
            if(m_categories[i] != NULL && m_categories[i].GetCategoryName() == categoryName) {
                return m_categories[i];
            }
        }
        return NULL;
    }
    
    bool UpdateAllCategories() {
        bool success = true;
        for(int i = 0; i < ArraySize(m_categories); i++) {
            if(m_categories[i] != NULL) {
                if(!m_categories[i].Update()) {
                    success = false;
                }
            }
        }
        return success;
    }
    
    void GetAllSignals(InsightSignal &signals[]) {
        ArrayResize(signals, 0);
        
        for(int i = 0; i < ArraySize(m_categories); i++) {
            if(m_categories[i] != NULL) {
                InsightSignal categorySignals[];
                if(m_categories[i].GetSignals(categorySignals)) {
                    int currentSize = ArraySize(signals);
                    ArrayResize(signals, currentSize + ArraySize(categorySignals));
                    ArrayCopy(signals, categorySignals, currentSize);
                }
            }
        }
    }
    
    int GetCategoryCount() {
        return ArraySize(m_categories);
    }
    
    bool IsCategoryRegistered(string categoryName) {
        return GetCategory(categoryName) != NULL;
    }
}; 