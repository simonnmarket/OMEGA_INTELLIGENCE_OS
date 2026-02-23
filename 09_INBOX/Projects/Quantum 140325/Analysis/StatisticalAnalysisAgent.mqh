#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para análise de volatilidade
struct VolatilityAnalysis {
    string   symbol;
    datetime timestamp;
    double   historical;    // Volatilidade histórica
    double   implied;      // Volatilidade implícita
    double   forecast;     // Previsão de volatilidade
    double   confidence;   // Nível de confiança (0-1)
};

// Estrutura para padrão de mercado
struct MarketPattern {
    string   type;         // "TREND", "REVERSAL", "CONSOLIDATION"
    datetime startTime;
    datetime endTime;
    double   startPrice;
    double   endPrice;
    double   strength;     // Força do padrão (0-1)
    double   reliability;  // Confiabilidade (0-1)
    string   description;  // Descrição detalhada
};

// Estrutura para configuração do agente
struct StatisticalConfig {
    // Configurações de movimento Browniano
    int      historyPeriod;     // Períodos para análise histórica
    int      forecastPeriod;    // Períodos para previsão
    double   confidenceLevel;    // Nível de confiança (0-1)
    bool     useGeometricBM;    // Usar movimento Browniano geométrico
    bool     useFractionalBM;   // Usar movimento Browniano fracionário
    
    // Configurações de Few-Shot Learning
    int      trainingExamples;  // Número de exemplos por classe
    double   learningRate;      // Taxa de aprendizado
    double   patternThreshold;  // Limite para detecção de padrões
};

//+------------------------------------------------------------------+
//| Classe StatisticalAnalysisAgent                                    |
//+------------------------------------------------------------------+
class CStatisticalAnalysisAgent {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    StatisticalConfig  m_config;
    
    // Cache de dados
    VolatilityAnalysis m_volatility[];
    MarketPattern      m_patterns[];
    
    // Estado do sistema
    bool              m_isInitialized;
    datetime          m_lastUpdate;
    
    // Configurações
    int               m_maxVolatilityRecords;
    int               m_maxPatterns;
    
    // Métodos privados de análise Browniana
    double            AnalyzeStandardBrownian(string symbol);
    double            AnalyzeGeometricBrownian(string symbol);
    double            AnalyzeFractionalBrownian(string symbol);
    
    // Métodos privados de volatilidade
    double            CalculateHistoricalVolatility(string symbol);
    double            CalculateImpliedVolatility(string symbol);
    double            ForecastVolatility(string symbol);
    
    // Métodos privados de padrões
    bool              DetectTrendPattern(string symbol, MarketPattern &pattern);
    bool              DetectReversalPattern(string symbol, MarketPattern &pattern);
    bool              DetectConsolidationPattern(string symbol, MarketPattern &pattern);
    double            CalculatePatternStrength(const MarketPattern &pattern);
    double            CalculatePatternReliability(const MarketPattern &pattern);
    
    // Métodos de limpeza
    void              CleanupOldData();
    
public:
                      CStatisticalAnalysisAgent();
                     ~CStatisticalAnalysisAgent();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Update();
    
    // Métodos de análise
    bool              AnalyzeVolatility(string symbol, VolatilityAnalysis &analysis);
    bool              AnalyzePattern(string symbol, MarketPattern &pattern);
    bool              PredictNextMove(string symbol, double &prediction, double &probability);
    
    // Métodos de consulta
    VolatilityAnalysis* GetLatestVolatility(string symbol);
    MarketPattern*      GetLatestPattern(string symbol);
    double             GetVolatilityForecast(string symbol);
    string             GetDominantPattern(string symbol);
    
    // Configuração
    void              SetConfig(const StatisticalConfig &config);
    StatisticalConfig GetConfig() const { return m_config; }
    bool              IsInitialized() const { return m_isInitialized; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CStatisticalAnalysisAgent::CStatisticalAnalysisAgent() {
    m_core = NULL;
    m_isInitialized = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_config.historyPeriod = 1000;
    m_config.forecastPeriod = 100;
    m_config.confidenceLevel = 0.95;
    m_config.useGeometricBM = true;
    m_config.useFractionalBM = true;
    m_config.trainingExamples = 5;
    m_config.learningRate = 0.01;
    m_config.patternThreshold = 0.7;
    
    m_maxVolatilityRecords = 5000;
    m_maxPatterns = 1000;
    
    ArrayResize(m_volatility, 0);
    ArrayResize(m_patterns, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CStatisticalAnalysisAgent::~CStatisticalAnalysisAgent() {
    ArrayFree(m_volatility);
    ArrayFree(m_patterns);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isInitialized = true;
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::Update() {
    if(!m_isInitialized || !m_core) return false;
    
    string symbols[];
    m_core.GetSymbols(symbols);
    
    // Atualiza análises para cada símbolo
    for(int i = 0; i < ArraySize(symbols); i++) {
        VolatilityAnalysis volAnalysis;
        MarketPattern pattern;
        
        if(AnalyzeVolatility(symbols[i], volAnalysis)) {
            int size = ArraySize(m_volatility);
            ArrayResize(m_volatility, size + 1);
            m_volatility[size] = volAnalysis;
        }
        
        if(AnalyzePattern(symbols[i], pattern)) {
            int size = ArraySize(m_patterns);
            ArrayResize(m_patterns, size + 1);
            m_patterns[size] = pattern;
        }
    }
    
    CleanupOldData();
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Analisa volatilidade                                              |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::AnalyzeVolatility(
    string symbol,
    VolatilityAnalysis &analysis
) {
    if(!m_core) return false;
    
    // Preenche dados básicos
    analysis.symbol = symbol;
    analysis.timestamp = TimeCurrent();
    
    // Calcula diferentes tipos de volatilidade
    analysis.historical = CalculateHistoricalVolatility(symbol);
    analysis.implied = CalculateImpliedVolatility(symbol);
    analysis.forecast = ForecastVolatility(symbol);
    
    // Calcula nível de confiança
    double stdDev = m_core.GetAnalysis().CalculateStdDev(symbol);
    double avgStdDev = m_core.GetAnalysis().CalculateAverageStdDev(
        symbol,
        m_config.historyPeriod
    );
    
    if(avgStdDev > 0) {
        analysis.confidence = MathMin(1.0, stdDev / avgStdDev);
    }
    else {
        analysis.confidence = 0.5;  // Valor neutro
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Analisa padrões                                                   |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::AnalyzePattern(
    string symbol,
    MarketPattern &pattern
) {
    // Tenta detectar diferentes tipos de padrões
    if(DetectTrendPattern(symbol, pattern)) {
        pattern.type = "TREND";
    }
    else if(DetectReversalPattern(symbol, pattern)) {
        pattern.type = "REVERSAL";
    }
    else if(DetectConsolidationPattern(symbol, pattern)) {
        pattern.type = "CONSOLIDATION";
    }
    else {
        return false;
    }
    
    // Calcula métricas do padrão
    pattern.strength = CalculatePatternStrength(pattern);
    pattern.reliability = CalculatePatternReliability(pattern);
    
    return true;
}

//+------------------------------------------------------------------+
//| Prediz próximo movimento                                          |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::PredictNextMove(
    string symbol,
    double &prediction,
    double &probability
) {
    if(!m_core) return false;
    
    // Obtém última análise de volatilidade
    VolatilityAnalysis* vol = GetLatestVolatility(symbol);
    if(vol == NULL) return false;
    
    // Calcula previsão usando diferentes modelos Brownianos
    double stdPred = AnalyzeStandardBrownian(symbol);
    double geoPred = m_config.useGeometricBM ? 
                    AnalyzeGeometricBrownian(symbol) : 0;
    double fracPred = m_config.useFractionalBM ? 
                     AnalyzeFractionalBrownian(symbol) : 0;
    
    // Combina previsões com pesos baseados na confiança
    double totalWeight = 1.0;  // Peso do modelo padrão
    double weightedPred = stdPred;
    
    if(m_config.useGeometricBM) {
        totalWeight += 1.2;  // Peso maior para GBM
        weightedPred += 1.2 * geoPred;
    }
    
    if(m_config.useFractionalBM) {
        totalWeight += 0.8;  // Peso menor para FBM
        weightedPred += 0.8 * fracPred;
    }
    
    prediction = weightedPred / totalWeight;
    
    // Calcula probabilidade baseada na volatilidade e confiança
    probability = vol.confidence * (1.0 - vol.forecast / vol.historical);
    probability = MathMax(0.1, MathMin(0.9, probability));  // Limita entre 0.1 e 0.9
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém última volatilidade                                         |
//+------------------------------------------------------------------+
VolatilityAnalysis* CStatisticalAnalysisAgent::GetLatestVolatility(string symbol) {
    for(int i = ArraySize(m_volatility) - 1; i >= 0; i--) {
        if(m_volatility[i].symbol == symbol) {
            return &m_volatility[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém último padrão                                               |
//+------------------------------------------------------------------+
MarketPattern* CStatisticalAnalysisAgent::GetLatestPattern(string symbol) {
    for(int i = ArraySize(m_patterns) - 1; i >= 0; i--) {
        if(m_patterns[i].startPrice > 0 && // Verifica se é um padrão válido
           m_patterns[i].endPrice > 0) {
            return &m_patterns[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém previsão de volatilidade                                    |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::GetVolatilityForecast(string symbol) {
    VolatilityAnalysis* vol = GetLatestVolatility(symbol);
    if(vol != NULL) {
        return vol.forecast;
    }
    return 0.0;
}

//+------------------------------------------------------------------+
//| Obtém padrão dominante                                            |
//+------------------------------------------------------------------+
string CStatisticalAnalysisAgent::GetDominantPattern(string symbol) {
    MarketPattern* pattern = GetLatestPattern(symbol);
    if(pattern != NULL && pattern.strength >= m_config.patternThreshold) {
        return pattern.type;
    }
    return "NONE";
}

//+------------------------------------------------------------------+
//| Define configuração                                               |
//+------------------------------------------------------------------+
void CStatisticalAnalysisAgent::SetConfig(const StatisticalConfig &config) {
    m_config = config;
}

//+------------------------------------------------------------------+
//| Analisa movimento Browniano padrão                                |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::AnalyzeStandardBrownian(string symbol) {
    if(!m_core) return 0.0;
    
    // Obtém dados históricos
    double prices[];
    ArraySetAsSeries(prices, true);
    int copied = CopyClose(symbol, PERIOD_CURRENT, 0, m_config.historyPeriod, prices);
    
    if(copied != m_config.historyPeriod) return 0.0;
    
    // Calcula parâmetros do movimento Browniano
    double drift = 0;
    double diffusion = 0;
    
    for(int i = 1; i < copied; i++) {
        double change = prices[i-1] - prices[i];
        drift += change;
        diffusion += change * change;
    }
    
    drift /= copied - 1;
    diffusion = MathSqrt(diffusion / (copied - 1));
    
    // Retorna previsão
    return prices[0] + drift + diffusion * MathRandomNormal(0.0, 1.0);
}

//+------------------------------------------------------------------+
//| Analisa movimento Browniano geométrico                            |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::AnalyzeGeometricBrownian(string symbol) {
    if(!m_core) return 0.0;
    
    // Obtém dados históricos
    double prices[];
    ArraySetAsSeries(prices, true);
    int copied = CopyClose(symbol, PERIOD_CURRENT, 0, m_config.historyPeriod, prices);
    
    if(copied != m_config.historyPeriod) return 0.0;
    
    // Calcula retornos logarítmicos
    double returns[];
    ArrayResize(returns, copied - 1);
    
    for(int i = 1; i < copied; i++) {
        returns[i-1] = MathLog(prices[i-1] / prices[i]);
    }
    
    // Calcula parâmetros do GBM
    double mu = 0;
    double sigma = 0;
    
    for(int i = 0; i < ArraySize(returns); i++) {
        mu += returns[i];
        sigma += returns[i] * returns[i];
    }
    
    mu /= ArraySize(returns);
    sigma = MathSqrt(sigma / ArraySize(returns) - mu * mu);
    
    // Retorna previsão
    double dt = 1.0;  // Intervalo de tempo
    double drift = (mu - 0.5 * sigma * sigma) * dt;
    double diffusion = sigma * MathSqrt(dt) * MathRandomNormal(0.0, 1.0);
    
    return prices[0] * MathExp(drift + diffusion);
}

//+------------------------------------------------------------------+
//| Analisa movimento Browniano fracionário                           |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::AnalyzeFractionalBrownian(string symbol) {
    if(!m_core) return 0.0;
    
    // Obtém dados históricos
    double prices[];
    ArraySetAsSeries(prices, true);
    int copied = CopyClose(symbol, PERIOD_CURRENT, 0, m_config.historyPeriod, prices);
    
    if(copied != m_config.historyPeriod) return 0.0;
    
    // Calcula expoente de Hurst
    double hurst = m_core.GetAnalysis().CalculateHurstExponent(symbol);
    
    // Ajusta parâmetros baseado no expoente de Hurst
    double drift = 0;
    double diffusion = 0;
    
    for(int i = 1; i < copied; i++) {
        double change = prices[i-1] - prices[i];
        drift += change;
        diffusion += MathPow(MathAbs(change), 2 * hurst);
    }
    
    drift /= copied - 1;
    diffusion = MathPow(diffusion / (copied - 1), 1.0 / (2 * hurst));
    
    // Retorna previsão
    return prices[0] + drift + diffusion * MathRandomNormal(0.0, 1.0);
}

//+------------------------------------------------------------------+
//| Calcula volatilidade histórica                                    |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::CalculateHistoricalVolatility(string symbol) {
    if(!m_core) return 0.0;
    
    return m_core.GetAnalysis().CalculateVolatility(
        symbol,
        m_config.historyPeriod
    );
}

//+------------------------------------------------------------------+
//| Calcula volatilidade implícita                                    |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::CalculateImpliedVolatility(string symbol) {
    if(!m_core) return 0.0;
    
    // Implementação simplificada - em um sistema real,
    // isso seria calculado usando dados de opções
    return m_core.GetAnalysis().CalculateATR(symbol, 14) /
           SymbolInfoDouble(symbol, SYMBOL_LAST);
}

//+------------------------------------------------------------------+
//| Prevê volatilidade                                                |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::ForecastVolatility(string symbol) {
    if(!m_core) return 0.0;
    
    // Obtém volatilidades históricas
    double historical = CalculateHistoricalVolatility(symbol);
    double implied = CalculateImpliedVolatility(symbol);
    
    // Usa média ponderada com mais peso para volatilidade implícita
    return (historical + 2 * implied) / 3;
}

//+------------------------------------------------------------------+
//| Detecta padrão de tendência                                       |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::DetectTrendPattern(
    string symbol,
    MarketPattern &pattern
) {
    if(!m_core) return false;
    
    // Obtém dados históricos
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, m_config.historyPeriod, rates);
    
    if(copied < 30) return false;  // Precisa de pelo menos 30 barras
    
    // Analisa tendência usando regressão linear
    double slope = m_core.GetAnalysis().CalculateLinearRegression(symbol);
    double r2 = m_core.GetAnalysis().CalculateR2(symbol);
    
    // Verifica se há tendência significativa
    if(MathAbs(slope) > m_config.patternThreshold && r2 > 0.7) {
        pattern.startTime = rates[copied-1].time;
        pattern.endTime = rates[0].time;
        pattern.startPrice = rates[copied-1].close;
        pattern.endPrice = rates[0].close;
        pattern.strength = MathAbs(slope);
        pattern.reliability = r2;
        pattern.description = slope > 0 ? "Uptrend" : "Downtrend";
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Detecta padrão de reversão                                        |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::DetectReversalPattern(
    string symbol,
    MarketPattern &pattern
) {
    if(!m_core) return false;
    
    // Obtém dados históricos
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, 30, rates);
    
    if(copied < 30) return false;
    
    // Analisa indicadores de reversão
    double rsi = m_core.GetAnalysis().CalculateRSI(symbol, 14);
    double stoch = m_core.GetAnalysis().CalculateStochastic(symbol);
    
    // Verifica condições de reversão
    bool isOverbought = (rsi > 70 && stoch > 80);
    bool isOversold = (rsi < 30 && stoch < 20);
    
    if(isOverbought || isOversold) {
        pattern.startTime = rates[29].time;
        pattern.endTime = rates[0].time;
        pattern.startPrice = rates[29].close;
        pattern.endPrice = rates[0].close;
        pattern.strength = MathAbs(70 - rsi) / 30.0;
        pattern.reliability = 0.7;  // Valor base para reversões
        pattern.description = isOverbought ? "Bearish Reversal" : "Bullish Reversal";
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Detecta padrão de consolidação                                    |
//+------------------------------------------------------------------+
bool CStatisticalAnalysisAgent::DetectConsolidationPattern(
    string symbol,
    MarketPattern &pattern
) {
    if(!m_core) return false;
    
    // Obtém dados históricos
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, 20, rates);
    
    if(copied < 20) return false;
    
    // Calcula volatilidade e range médio
    double volatility = m_core.GetAnalysis().CalculateVolatility(symbol);
    double avgVolatility = m_core.GetAnalysis().CalculateAverageVolatility(
        symbol,
        m_config.historyPeriod
    );
    
    // Verifica se está em consolidação
    if(volatility < avgVolatility * 0.5) {
        pattern.startTime = rates[19].time;
        pattern.endTime = rates[0].time;
        pattern.startPrice = rates[19].close;
        pattern.endPrice = rates[0].close;
        pattern.strength = 1.0 - (volatility / avgVolatility);
        pattern.reliability = 0.8;  // Alta confiabilidade para consolidações
        pattern.description = "Price Consolidation";
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Calcula força do padrão                                          |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::CalculatePatternStrength(
    const MarketPattern &pattern
) {
    // Calcula baseado na magnitude do movimento e tempo
    double priceChange = MathAbs(pattern.endPrice - pattern.startPrice);
    double timeChange = (double)(pattern.endTime - pattern.startTime);
    
    if(timeChange <= 0) return 0.0;
    
    return MathMin(1.0, priceChange / (timeChange * 0.1));
}

//+------------------------------------------------------------------+
//| Calcula confiabilidade do padrão                                 |
//+------------------------------------------------------------------+
double CStatisticalAnalysisAgent::CalculatePatternReliability(
    const MarketPattern &pattern
) {
    // Usa histórico de padrões similares
    int similarPatterns = 0;
    int successfulPatterns = 0;
    
    for(int i = 0; i < ArraySize(m_patterns); i++) {
        if(m_patterns[i].type == pattern.type) {
            similarPatterns++;
            if(m_patterns[i].strength >= pattern.strength) {
                successfulPatterns++;
            }
        }
    }
    
    if(similarPatterns > 0) {
        return (double)successfulPatterns / similarPatterns;
    }
    
    return 0.5;  // Valor neutro se não houver histórico
}

//+------------------------------------------------------------------+
//| Limpa dados antigos                                               |
//+------------------------------------------------------------------+
void CStatisticalAnalysisAgent::CleanupOldData() {
    datetime current = TimeCurrent();
    
    // Remove registros de volatilidade antigos
    for(int i = ArraySize(m_volatility) - 1; i >= 0; i--) {
        if(current - m_volatility[i].timestamp > m_config.historyPeriod * 60) {
            for(int j = i; j < ArraySize(m_volatility) - 1; j++) {
                m_volatility[j] = m_volatility[j + 1];
            }
            ArrayResize(m_volatility, ArraySize(m_volatility) - 1);
        }
    }
    
    // Remove padrões antigos
    for(int i = ArraySize(m_patterns) - 1; i >= 0; i--) {
        if(current - m_patterns[i].endTime > m_config.historyPeriod * 60) {
            for(int j = i; j < ArraySize(m_patterns) - 1; j++) {
                m_patterns[j] = m_patterns[j + 1];
            }
            ArrayResize(m_patterns, ArraySize(m_patterns) - 1);
        }
    }
    
    // Limita tamanho dos arrays
    while(ArraySize(m_volatility) > m_maxVolatilityRecords) {
        for(int i = 0; i < ArraySize(m_volatility) - 1; i++) {
            m_volatility[i] = m_volatility[i + 1];
        }
        ArrayResize(m_volatility, ArraySize(m_volatility) - 1);
    }
    
    while(ArraySize(m_patterns) > m_maxPatterns) {
        for(int i = 0; i < ArraySize(m_patterns) - 1; i++) {
            m_patterns[i] = m_patterns[i + 1];
        }
        ArrayResize(m_patterns, ArraySize(m_patterns) - 1);
    }
} 