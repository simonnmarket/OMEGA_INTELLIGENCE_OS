#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"
#include "../Analysis/AdvancedAnalysis.mqh"

// Estrutura para recomendação
struct Recommendation {
    string   symbol;
    string   type;           // "ENTRY", "EXIT", "ADJUST"
    string   direction;      // "LONG", "SHORT", "NEUTRAL"
    datetime timestamp;
    double   price;
    double   stopLoss;
    double   takeProfit;
    double   confidence;     // 0-1
    string   reason;
    string   timeframe;
    bool     isUrgent;
};

// Estrutura para análise de mercado
struct MarketInsight {
    string   symbol;
    string   timeframe;
    datetime timestamp;
    string   trend;          // "BULLISH", "BEARISH", "NEUTRAL"
    double   strength;       // 0-1
    string   pattern;
    string   support[];
    string   resistance[];
    string   events[];
    string   analysis;
};

// Estrutura para configuração do consultor
struct ConsultantConfig {
    string   symbols[];
    string   timeframes[];
    double   minConfidence;
    int      maxRecommendations;
    bool     useML;
    bool     useFundamental;
    bool     useTechnical;
    bool     useMarketSentiment;
};

//+------------------------------------------------------------------+
//| Classe ConsultantAgent                                            |
//+------------------------------------------------------------------+
class CConsultantAgent {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    ConsultantConfig   m_config;
    
    // Cache de dados
    Recommendation     m_recommendations[];
    MarketInsight     m_insights[];
    
    // Estado do agente
    bool              m_isActive;
    datetime          m_lastUpdate;
    
    // Métodos privados
    bool              ValidateRecommendation(const Recommendation &rec);
    bool              ValidateInsight(const MarketInsight &insight);
    bool              AnalyzeMarket(string symbol, string timeframe, MarketInsight &insight);
    bool              GenerateRecommendation(const MarketInsight &insight, Recommendation &rec);
    void              UpdateCache();
    void              CleanupOldData();
    double            CalculateConfidence(const MarketInsight &insight);
    string            DeterminePattern(string symbol, string timeframe);
    
public:
                      CConsultantAgent();
                     ~CConsultantAgent();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Start();
    void              Stop();
    
    // Métodos de análise
    bool              UpdateAnalysis();
    bool              GetRecommendation(string symbol, Recommendation &rec);
    bool              GetMarketInsight(string symbol, MarketInsight &insight);
    
    // Métodos de configuração
    void              SetConfig(const ConsultantConfig &config);
    void              AddSymbol(string symbol);
    void              RemoveSymbol(string symbol);
    
    // Métodos de consulta
    Recommendation   *GetActiveRecommendations();
    MarketInsight   *GetLatestInsights();
    string           GetMarketSummary();
    
    // Getters
    bool             IsActive() const { return m_isActive; }
    ConsultantConfig GetConfig() const { return m_config; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CConsultantAgent::CConsultantAgent() {
    m_core = NULL;
    m_isActive = false;
    m_lastUpdate = 0;
    
    // Configuração padrão
    ArrayResize(m_config.symbols, 3);
    m_config.symbols[0] = "EURUSD";
    m_config.symbols[1] = "USDJPY";
    m_config.symbols[2] = "GBPUSD";
    
    ArrayResize(m_config.timeframes, 4);
    m_config.timeframes[0] = "M15";
    m_config.timeframes[1] = "H1";
    m_config.timeframes[2] = "H4";
    m_config.timeframes[3] = "D1";
    
    m_config.minConfidence = 0.7;
    m_config.maxRecommendations = 50;
    m_config.useML = true;
    m_config.useFundamental = true;
    m_config.useTechnical = true;
    m_config.useMarketSentiment = true;
    
    ArrayResize(m_recommendations, 0);
    ArrayResize(m_insights, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CConsultantAgent::~CConsultantAgent() {
    Stop();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CConsultantAgent::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicia o agente                                                    |
//+------------------------------------------------------------------+
bool CConsultantAgent::Start() {
    if(!m_core) return false;
    
    m_isActive = true;
    m_lastUpdate = TimeCurrent();
    
    // Análise inicial
    UpdateAnalysis();
    
    return true;
}

//+------------------------------------------------------------------+
//| Para o agente                                                      |
//+------------------------------------------------------------------+
void CConsultantAgent::Stop() {
    if(!m_isActive) return;
    
    // Limpa recomendações ativas
    ArrayResize(m_recommendations, 0);
    ArrayResize(m_insights, 0);
    
    m_isActive = false;
}

//+------------------------------------------------------------------+
//| Atualiza análise                                                  |
//+------------------------------------------------------------------+
bool CConsultantAgent::UpdateAnalysis() {
    if(!m_isActive || !m_core) return false;
    
    // Limpa dados antigos
    CleanupOldData();
    
    // Analisa cada símbolo em cada timeframe
    for(int i = 0; i < ArraySize(m_config.symbols); i++) {
        for(int j = 0; j < ArraySize(m_config.timeframes); j++) {
            MarketInsight insight;
            if(AnalyzeMarket(m_config.symbols[i], m_config.timeframes[j], insight)) {
                // Gera recomendação se necessário
                if(insight.strength >= m_config.minConfidence) {
                    Recommendation rec;
                    if(GenerateRecommendation(insight, rec)) {
                        if(ValidateRecommendation(rec)) {
                            int size = ArraySize(m_recommendations);
                            ArrayResize(m_recommendations, size + 1);
                            m_recommendations[size] = rec;
                        }
                    }
                }
                
                // Armazena insight
                if(ValidateInsight(insight)) {
                    int size = ArraySize(m_insights);
                    ArrayResize(m_insights, size + 1);
                    m_insights[size] = insight;
                }
            }
        }
    }
    
    m_lastUpdate = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Analisa mercado                                                   |
//+------------------------------------------------------------------+
bool CConsultantAgent::AnalyzeMarket(string symbol, string timeframe, MarketInsight &insight) {
    if(!m_core) return false;
    
    insight.symbol = symbol;
    insight.timeframe = timeframe;
    insight.timestamp = TimeCurrent();
    
    // Análise técnica
    if(m_config.useTechnical) {
        // Obtém análise do mercado
        AnalysisResult analysis = m_core.GetAnalysis().AnalyzeMarketPatterns(
            symbol,
            NULL,
            StringToTimeFrame(timeframe)
        );
        
        insight.trend = analysis.nextPrediction > 0 ? "BULLISH" : "BEARISH";
        insight.strength = analysis.predictionAccuracy;
        insight.pattern = DeterminePattern(symbol, timeframe);
    }
    
    // Análise fundamental
    if(m_config.useFundamental) {
        // Obtém notícias e eventos
        NewsData news = m_core.GetDataCollection().GetLatestNews(symbol);
        ArrayResize(insight.events, 1);
        insight.events[0] = StringFormat("%s (Impact: %s)", news.title, news.impact);
    }
    
    // Análise de sentimento
    if(m_config.useMarketSentiment) {
        SentimentData sentiment = m_core.GetDataCollection().GetLatestSentiment(symbol);
        insight.analysis += StringFormat("\nSentiment: %.2f%%", sentiment.bullishPercentage);
    }
    
    // Machine Learning
    if(m_config.useML) {
        MLPrediction prediction = m_core.GetAnalysis().GetMLPrediction(symbol, timeframe);
        insight.analysis += StringFormat("\nML Prediction: %s (Confidence: %.2f%%)",
            prediction.direction > 0 ? "UP" : "DOWN",
            prediction.confidence * 100
        );
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Gera recomendação                                                 |
//+------------------------------------------------------------------+
bool CConsultantAgent::GenerateRecommendation(const MarketInsight &insight, Recommendation &rec) {
    rec.symbol = insight.symbol;
    rec.timestamp = insight.timestamp;
    rec.confidence = insight.strength;
    rec.timeframe = insight.timeframe;
    
    // Determina tipo e direção
    if(insight.trend == "BULLISH" && insight.strength > m_config.minConfidence) {
        rec.type = "ENTRY";
        rec.direction = "LONG";
    }
    else if(insight.trend == "BEARISH" && insight.strength > m_config.minConfidence) {
        rec.type = "ENTRY";
        rec.direction = "SHORT";
    }
    else {
        rec.type = "ADJUST";
        rec.direction = "NEUTRAL";
    }
    
    // Define preços
    MqlTick tick;
    if(!SymbolInfoTick(rec.symbol, tick)) return false;
    
    rec.price = tick.ask;
    
    // Calcula stops baseado na volatilidade
    double atr = iATR(rec.symbol, StringToTimeFrame(rec.timeframe), 14, 0);
    if(rec.direction == "LONG") {
        rec.stopLoss = rec.price - atr * 2;
        rec.takeProfit = rec.price + atr * 3;
    }
    else if(rec.direction == "SHORT") {
        rec.stopLoss = rec.price + atr * 2;
        rec.takeProfit = rec.price - atr * 3;
    }
    
    // Define razão
    rec.reason = StringFormat("Based on %s pattern with %.2f%% confidence. %s",
        insight.pattern,
        insight.strength * 100,
        insight.analysis
    );
    
    // Define urgência
    rec.isUrgent = insight.strength > 0.9;
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém recomendação                                                |
//+------------------------------------------------------------------+
bool CConsultantAgent::GetRecommendation(string symbol, Recommendation &rec) {
    for(int i = ArraySize(m_recommendations) - 1; i >= 0; i--) {
        if(m_recommendations[i].symbol == symbol) {
            rec = m_recommendations[i];
            return true;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Obtém insight de mercado                                          |
//+------------------------------------------------------------------+
bool CConsultantAgent::GetMarketInsight(string symbol, MarketInsight &insight) {
    for(int i = ArraySize(m_insights) - 1; i >= 0; i--) {
        if(m_insights[i].symbol == symbol) {
            insight = m_insights[i];
            return true;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Define configuração                                               |
//+------------------------------------------------------------------+
void CConsultantAgent::SetConfig(const ConsultantConfig &config) {
    m_config = config;
    UpdateAnalysis();
}

//+------------------------------------------------------------------+
//| Adiciona símbolo                                                  |
//+------------------------------------------------------------------+
void CConsultantAgent::AddSymbol(string symbol) {
    // Verifica se já existe
    for(int i = 0; i < ArraySize(m_config.symbols); i++) {
        if(m_config.symbols[i] == symbol) return;
    }
    
    // Adiciona novo símbolo
    int size = ArraySize(m_config.symbols);
    ArrayResize(m_config.symbols, size + 1);
    m_config.symbols[size] = symbol;
    
    // Atualiza análise para o novo símbolo
    if(m_isActive) {
        for(int i = 0; i < ArraySize(m_config.timeframes); i++) {
            MarketInsight insight;
            if(AnalyzeMarket(symbol, m_config.timeframes[i], insight)) {
                if(ValidateInsight(insight)) {
                    int insightSize = ArraySize(m_insights);
                    ArrayResize(m_insights, insightSize + 1);
                    m_insights[insightSize] = insight;
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Remove símbolo                                                    |
//+------------------------------------------------------------------+
void CConsultantAgent::RemoveSymbol(string symbol) {
    for(int i = 0; i < ArraySize(m_config.symbols); i++) {
        if(m_config.symbols[i] == symbol) {
            // Remove símbolo
            for(int j = i; j < ArraySize(m_config.symbols) - 1; j++) {
                m_config.symbols[j] = m_config.symbols[j + 1];
            }
            ArrayResize(m_config.symbols, ArraySize(m_config.symbols) - 1);
            
            // Remove insights e recomendações relacionadas
            CleanupOldData();
            break;
        }
    }
}

//+------------------------------------------------------------------+
//| Obtém recomendações ativas                                        |
//+------------------------------------------------------------------+
Recommendation *CConsultantAgent::GetActiveRecommendations() {
    static Recommendation activeRecs[];
    ArrayResize(activeRecs, 0);
    
    datetime current = TimeCurrent();
    
    for(int i = 0; i < ArraySize(m_recommendations); i++) {
        // Considera recomendações das últimas 24 horas
        if(current - m_recommendations[i].timestamp <= 24 * 3600) {
            int size = ArraySize(activeRecs);
            ArrayResize(activeRecs, size + 1);
            activeRecs[size] = m_recommendations[i];
        }
    }
    
    return activeRecs;
}

//+------------------------------------------------------------------+
//| Obtém últimos insights                                            |
//+------------------------------------------------------------------+
MarketInsight *CConsultantAgent::GetLatestInsights() {
    return m_insights;
}

//+------------------------------------------------------------------+
//| Obtém resumo do mercado                                           |
//+------------------------------------------------------------------+
string CConsultantAgent::GetMarketSummary() {
    string summary = "Market Summary\n";
    summary += "---------------\n\n";
    
    for(int i = 0; i < ArraySize(m_config.symbols); i++) {
        MarketInsight insight;
        if(GetMarketInsight(m_config.symbols[i], insight)) {
            summary += StringFormat("%s (%s):\n", insight.symbol, insight.timeframe);
            summary += StringFormat("Trend: %s (Strength: %.2f%%)\n", 
                insight.trend, insight.strength * 100);
            summary += StringFormat("Pattern: %s\n", insight.pattern);
            
            if(ArraySize(insight.events) > 0) {
                summary += "Events:\n";
                for(int j = 0; j < ArraySize(insight.events); j++) {
                    summary += StringFormat("  - %s\n", insight.events[j]);
                }
            }
            
            summary += insight.analysis + "\n\n";
        }
    }
    
    return summary;
}

//+------------------------------------------------------------------+
//| Valida recomendação                                               |
//+------------------------------------------------------------------+
bool CConsultantAgent::ValidateRecommendation(const Recommendation &rec) {
    if(rec.symbol == "") return false;
    if(rec.timestamp == 0) return false;
    if(rec.confidence <= 0 || rec.confidence > 1) return false;
    if(rec.price <= 0) return false;
    
    if(rec.type == "ENTRY") {
        if(rec.stopLoss <= 0 || rec.takeProfit <= 0) return false;
        if(rec.direction != "LONG" && rec.direction != "SHORT") return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida insight                                                    |
//+------------------------------------------------------------------+
bool CConsultantAgent::ValidateInsight(const MarketInsight &insight) {
    if(insight.symbol == "") return false;
    if(insight.timestamp == 0) return false;
    if(insight.strength <= 0 || insight.strength > 1) return false;
    if(insight.trend == "") return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Limpa dados antigos                                               |
//+------------------------------------------------------------------+
void CConsultantAgent::CleanupOldData() {
    datetime current = TimeCurrent();
    
    // Limpa recomendações antigas (mais de 24 horas)
    for(int i = ArraySize(m_recommendations) - 1; i >= 0; i--) {
        if(current - m_recommendations[i].timestamp > 24 * 3600) {
            for(int j = i; j < ArraySize(m_recommendations) - 1; j++) {
                m_recommendations[j] = m_recommendations[j + 1];
            }
            ArrayResize(m_recommendations, ArraySize(m_recommendations) - 1);
        }
    }
    
    // Mantém apenas os insights mais recentes por símbolo/timeframe
    for(int i = ArraySize(m_insights) - 1; i >= 0; i--) {
        for(int j = i - 1; j >= 0; j--) {
            if(m_insights[i].symbol == m_insights[j].symbol &&
               m_insights[i].timeframe == m_insights[j].timeframe) {
                for(int k = j; k < ArraySize(m_insights) - 1; k++) {
                    m_insights[k] = m_insights[k + 1];
                }
                ArrayResize(m_insights, ArraySize(m_insights) - 1);
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Calcula confiança                                                 |
//+------------------------------------------------------------------+
double CConsultantAgent::CalculateConfidence(const MarketInsight &insight) {
    double confidence = 0;
    int factors = 0;
    
    // Análise técnica
    if(m_config.useTechnical) {
        confidence += insight.strength;
        factors++;
    }
    
    // Análise fundamental
    if(m_config.useFundamental && ArraySize(insight.events) > 0) {
        confidence += 0.8; // Peso para eventos significativos
        factors++;
    }
    
    // Machine Learning
    if(m_config.useML) {
        MLPrediction prediction = m_core.GetAnalysis().GetMLPrediction(
            insight.symbol,
            insight.timeframe
        );
        confidence += prediction.confidence;
        factors++;
    }
    
    return factors > 0 ? confidence / factors : 0;
}

//+------------------------------------------------------------------+
//| Determina padrão                                                  |
//+------------------------------------------------------------------+
string CConsultantAgent::DeterminePattern(string symbol, string timeframe) {
    // Obtém dados do mercado
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    
    int bars = 20; // Número de barras para análise
    if(CopyRates(symbol, StringToTimeFrame(timeframe), 0, bars, rates) != bars) {
        return "Unknown";
    }
    
    // Identifica padrões comuns
    bool isUptrend = true;
    bool isDowntrend = true;
    bool hasReversal = false;
    
    for(int i = 1; i < bars - 1; i++) {
        if(rates[i].close <= rates[i+1].close) isUptrend = false;
        if(rates[i].close >= rates[i+1].close) isDowntrend = false;
        
        if(i < bars - 2) {
            // Verifica padrão de reversão
            if(rates[i].close > rates[i+1].close && rates[i+1].close < rates[i+2].close ||
               rates[i].close < rates[i+1].close && rates[i+1].close > rates[i+2].close) {
                hasReversal = true;
            }
        }
    }
    
    // Determina padrão
    if(isUptrend) return "Strong Uptrend";
    if(isDowntrend) return "Strong Downtrend";
    if(hasReversal) return "Potential Reversal";
    
    return "Consolidation";
} 