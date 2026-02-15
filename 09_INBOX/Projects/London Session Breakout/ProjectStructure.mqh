//+------------------------------------------------------------------+
//|                                            ProjectStructure.mqh    |
//+------------------------------------------------------------------+

// Enums para controle de documentação
enum ENUM_DOC_STATUS {
    DOC_ACTIVE,        // Documento ativo
    DOC_ANALYSIS,      // Em análise
    DOC_ARCHIVED       // Arquivado
};

enum ENUM_DOC_CATEGORY {
    DOC_STRATEGY,      // Estratégia
    DOC_INDICATOR,     // Indicador
    DOC_SYSTEM,        // Sistema
    DOC_RISK,         // Gestão de Risco
    DOC_INTEGRATION   // Integração
};

enum ENUM_MARKET_SEGMENT {
    SEGMENT_FOREX,      // Mercado Forex
    SEGMENT_STOCKS,     // Mercado de Ações
    SEGMENT_FUTURES,    // Mercado Futuros
    SEGMENT_CRYPTO      // Criptomoedas
};

// Timeframes permitidos
enum ENUM_TIMEFRAME_ALLOWED {
    TIMEFRAME_M1 = 1,
    TIMEFRAME_M5 = 5,
    TIMEFRAME_M15 = 15,
    TIMEFRAME_H1 = 60,
    TIMEFRAME_H4 = 240,
    TIMEFRAME_D1 = 1440
};

// Estrutura para controle de documentação
struct SDocumentation {
    // IDENTIFICAÇÃO
    string          docID;           
    string          version;         
    datetime        createDate;      
    datetime        updateDate;      
    ENUM_DOC_STATUS status;         
    ENUM_MARKET_SEGMENT marketSegment;
    string          targetAssets[];  
    string          responsible;     // Nome do responsável
    
    // CATEGORIZAÇÃO
    ENUM_DOC_CATEGORY category;      
    string          subcategory;    
    string          tags[];         
    
    // DESCRIÇÃO TÉCNICA
    string          strategyName;    
    string          objective;       
    ENUM_TIMEFRAME_ALLOWED timeframes[];
    
    // COMPONENTES TÉCNICOS
    struct SIndicator {
        string name;
        string config;
        string function;
        bool   isCustom;
    } indicators[];
    
    struct SParameter {
        string name;
        double defaultValue;
        double minValue;
        double maxValue;
        string description;
        bool   canOptimize;
    } parameters[];
    
    // VALIDAÇÃO
    struct SBacktest {
        datetime startPeriod;
        datetime endPeriod;
        double   netProfit;
        double   maxDrawdown;
        double   winRate;
        string   platform;
    } backtest;
    
    // GESTÃO DE RISCO
    double         riskPerTrade;    
    double         maxDrawdown;     
    string         correlations;    
    string         filters[];       
    
    // RESULTADOS
    struct SPerformance {
        double winRate;
        double profitFactor;
        double expectancy;
        double avgDrawdown;
        double sharpeRatio;
    } performance;
    
    // OBSERVAÇÕES E REFERÊNCIAS
    string         observations;    
    string         references[];    
    
    // HISTÓRICO DE ATUALIZAÇÕES
    struct SUpdateHistory {
        datetime date;
        string   version;
        string   description;
        string   responsible;
    } updates[];
    
    // Método para gerar ID único
    string GenerateDocID(string strategy, string category, int number) {
        return StringFormat("%s-%s-%04d-%d", 
                          strategy,    // Ex: LBS para London Breakout Strategy
                          category,    // Ex: ESTRATÉGIA
                          number,      // Número sequencial
                          TimeYear(TimeCurrent()));
    }
    
    // Método para atualizar documento
    void UpdateDocument(string newVersion, string updateNotes) {
        version = newVersion;
        updateDate = TimeCurrent();
        ArrayResize(references, ArraySize(references) + 1);
        references[ArraySize(references)-1] = StringFormat("%s - %s", 
                                            TimeToString(updateDate), 
                                            updateNotes);
    }
    
    // Método para adicionar ativos alvo
    void AddTargetAsset(string asset) {
        int size = ArraySize(targetAssets);
        ArrayResize(targetAssets, size + 1);
        targetAssets[size] = asset;
    }
    
    // Método para validar documento
    bool Validate() {
        if(docID == "" || version == "" || createDate == 0) return false;
        if(ArraySize(targetAssets) == 0) return false;
        return true;
    }
};

// Classe principal de estrutura do projeto
class CProjectStructure {
private:
    SDocumentation m_doc;
    
public:
    // Construtor
    CProjectStructure() {
        // Inicialização básica
    }
    
    // Métodos públicos
    string GetCurrentDate() {
        return TimeToString(TimeCurrent(), TIME_DATE);
    }
    
    bool ValidateDocument(SDocumentation &doc) {
        return doc.Validate();
    }
}; 