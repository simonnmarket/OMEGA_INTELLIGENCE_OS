#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Analysis/AdvancedAnalysis.mqh"
#include "../Intelligence/WeisWaves.mqh"
#include "../Intelligence/VSA.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para análise de mercado
struct MarketAnalysis {
    string   symbol;           // Símbolo analisado
    datetime timestamp;        // Timestamp da análise
    double   trend;           // Tendência (-1 a 1)
    double   momentum;        // Momentum (-1 a 1)
    double   volatility;      // Volatilidade (0 a 1)
    double   volume;          // Volume relativo (0 a 1)
    double   support;         // Nível de suporte
    double   resistance;      // Nível de resistência
    string   pattern;         // Padrão identificado
    double   confidence;      // Confiança na análise (0 a 1)
};

// Estrutura para sinal de trading
struct TradingSignal {
    string   symbol;           // Símbolo
    ENUM_ORDER_TYPE type;      // Tipo de ordem
    datetime timestamp;        // Timestamp do sinal
    double   entryPrice;      // Preço de entrada
    double   stopLoss;        // Stop loss
    double   takeProfit;      // Take profit
    double   volume;          // Volume sugerido
    double   confidence;      // Confiança no sinal (0 a 1)
    string   reason;          // Razão para o sinal
};

// Estrutura para métricas de performance
struct PerformanceMetrics {
    double   totalPnL;
    double   winRate;
    double   profitFactor;
    double   sharpeRatio;
    double   maxDrawdown;
    double   averageWin;
    double   averageLoss;
    double   expectancy;
    int      totalTrades;
    datetime lastUpdate;
};

// Estrutura para relatório
struct Report {
    string          type;
    string          content;
    datetime        timestamp;
    bool            isUrgent;
    PerformanceMetrics metrics;
};

//+------------------------------------------------------------------+
//| Classe AnalystAgent                                                |
//+------------------------------------------------------------------+
class CAnalystAgent {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    CWeisWaves*     m_weisWaves;
    CVSA*           m_vsa;
    PerformanceMetrics m_metrics;
    Report            m_reports[];
    
    // Estado do agente
    bool            m_isActive;
    datetime        m_lastUpdate;
    MarketAnalysis  m_lastAnalysis[];
    TradingSignal   m_lastSignal[];
    
    // Configurações
    int             m_period;           // Período de análise
    double          m_minConfidence;    // Confiança mínima para sinais
    double          m_correlationLimit; // Limite de correlação
    int               m_reportInterval;  // Em minutos
    int               m_maxReports;
    bool              m_autoReport;
    
    // Cache
    double            m_dailyReturns[];
    double            m_monthlyReturns[];
    
    // Métodos privados
    bool            AnalyzeMarketConditions(string symbol, MarketAnalysis &analysis);
    bool            IdentifyPatterns(string symbol, MarketAnalysis &analysis);
    bool            ValidateAnalysis(MarketAnalysis &analysis);
    bool            GenerateSignal(const MarketAnalysis &analysis, TradingSignal &signal);
    void            LogAnalysis(const MarketAnalysis &analysis);
    void              UpdateMetrics();
    void              CalculateReturns();
    double            CalculateSharpeRatio();
    double            CalculateDrawdown();
    string            GenerateReport(bool isDetailed = false);
    void              SaveReport(const Report &report);
    
public:
                    CAnalystAgent();
                   ~CAnalystAgent();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            Start();
    void            Stop();
    bool            UpdateAnalysis(string symbol);
    bool            GetLastAnalysis(string symbol, MarketAnalysis &analysis);
    bool            GetLastSignal(string symbol, TradingSignal &signal);
    
    // Métodos de configuração
    void            SetPeriod(int period) { m_period = period; }
    void            SetMinConfidence(double confidence) { m_minConfidence = confidence; }
    void            SetCorrelationLimit(double limit) { m_correlationLimit = limit; }
    
    // Métodos de análise
    bool            AnalyzePerformance();
    bool            GeneratePerformanceReport(bool isDetailed = false);
    bool            GenerateRiskReport();
    bool            GenerateMarketReport();
    
    // Métodos de alerta
    void            CheckAlerts();
    void            SendAlert(string message, bool isUrgent = false);
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    int             GetPeriod() const { return m_period; }
    double          GetMinConfidence() const { return m_minConfidence; }
    PerformanceMetrics GetMetrics() const { return m_metrics; }
    Report            GetLastReport();
    Report           *GetReports() { return m_reports; }
    int               GetReportCount() const { return ArraySize(m_reports); }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CAnalystAgent::CAnalystAgent() {
    m_core = NULL;
    m_weisWaves = NULL;
    m_vsa = NULL;
    m_isActive = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_period = 14;
    m_minConfidence = 0.7;
    m_correlationLimit = 0.7;
    m_reportInterval = 60;  // 60 minutos
    m_maxReports = 100;
    m_autoReport = true;
    
    ArrayResize(m_lastAnalysis, 0);
    ArrayResize(m_lastSignal, 0);
    ArrayResize(m_dailyReturns, 0);
    ArrayResize(m_monthlyReturns, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CAnalystAgent::~CAnalystAgent() {
    if(m_weisWaves != NULL) delete m_weisWaves;
    if(m_vsa != NULL) delete m_vsa;
    
    ArrayFree(m_lastAnalysis);
    ArrayFree(m_lastSignal);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CAnalystAgent::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    // Inicializa componentes
    m_weisWaves = new CWeisWaves();
    m_vsa = new CVSA();
    
    if(!m_weisWaves.Initialize() || !m_vsa.Initialize()) {
        Print("Failed to initialize analysis components");
        return false;
    }
    
    m_isActive = true;
    m_lastUpdate = TimeCurrent();
    
    // Inicializa métricas
    m_metrics.totalPnL = 0;
    m_metrics.winRate = 0;
    m_metrics.profitFactor = 0;
    m_metrics.sharpeRatio = 0;
    m_metrics.maxDrawdown = 0;
    m_metrics.averageWin = 0;
    m_metrics.averageLoss = 0;
    m_metrics.expectancy = 0;
    m_metrics.totalTrades = 0;
    m_metrics.lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicia o agente                                                    |
//+------------------------------------------------------------------+
bool CAnalystAgent::Start() {
    if(!m_core) return false;
    
    // Atualiza métricas iniciais
    UpdateMetrics();
    
    // Gera relatório inicial
    GeneratePerformanceReport(true);
    
    return true;
}

//+------------------------------------------------------------------+
//| Para o agente                                                      |
//+------------------------------------------------------------------+
void CAnalystAgent::Stop() {
    // Gera relatório final
    GeneratePerformanceReport(true);
}

//+------------------------------------------------------------------+
//| Atualiza análise                                                  |
//+------------------------------------------------------------------+
bool CAnalystAgent::UpdateAnalysis(string symbol) {
    if(!m_isActive || !m_core) return false;
    
    MarketAnalysis analysis;
    analysis.symbol = symbol;
    analysis.timestamp = TimeCurrent();
    
    // Analisa condições de mercado
    if(!AnalyzeMarketConditions(symbol, analysis)) {
        Print("Failed to analyze market conditions for ", symbol);
        return false;
    }
    
    // Identifica padrões
    if(!IdentifyPatterns(symbol, analysis)) {
        Print("Failed to identify patterns for ", symbol);
        return false;
    }
    
    // Valida análise
    if(!ValidateAnalysis(analysis)) {
        Print("Analysis validation failed for ", symbol);
        return false;
    }
    
    // Gera sinal se a confiança for suficiente
    if(analysis.confidence >= m_minConfidence) {
        TradingSignal signal;
        if(GenerateSignal(analysis, signal)) {
            int size = ArraySize(m_lastSignal);
            ArrayResize(m_lastSignal, size + 1);
            m_lastSignal[size] = signal;
        }
    }
    
    // Armazena análise
    int size = ArraySize(m_lastAnalysis);
    ArrayResize(m_lastAnalysis, size + 1);
    m_lastAnalysis[size] = analysis;
    
    LogAnalysis(analysis);
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém última análise                                              |
//+------------------------------------------------------------------+
bool CAnalystAgent::GetLastAnalysis(string symbol, MarketAnalysis &analysis) {
    int size = ArraySize(m_lastAnalysis);
    if(size == 0) return false;
    
    for(int i = size - 1; i >= 0; i--) {
        if(m_lastAnalysis[i].symbol == symbol) {
            analysis = m_lastAnalysis[i];
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Obtém último sinal                                                |
//+------------------------------------------------------------------+
bool CAnalystAgent::GetLastSignal(string symbol, TradingSignal &signal) {
    int size = ArraySize(m_lastSignal);
    if(size == 0) return false;
    
    for(int i = size - 1; i >= 0; i--) {
        if(m_lastSignal[i].symbol == symbol) {
            signal = m_lastSignal[i];
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Analisa condições de mercado                                      |
//+------------------------------------------------------------------+
bool CAnalystAgent::AnalyzeMarketConditions(string symbol, MarketAnalysis &analysis) {
    // Obtém dados do mercado
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    if(CopyRates(symbol, PERIOD_CURRENT, 0, m_period, rates) != m_period) {
        return false;
    }
    
    // Calcula tendência
    double trend = 0;
    for(int i = 1; i < m_period; i++) {
        trend += rates[i].close > rates[i].open ? 1 : -1;
    }
    analysis.trend = trend / m_period;
    
    // Calcula momentum
    double momentum = (rates[0].close - rates[m_period-1].close) / rates[m_period-1].close;
    analysis.momentum = MathMin(MathMax(momentum, -1), 1);
    
    // Calcula volatilidade
    double volatility = 0;
    for(int i = 0; i < m_period; i++) {
        volatility += (rates[i].high - rates[i].low) / rates[i].open;
    }
    analysis.volatility = volatility / m_period;
    
    // Calcula volume relativo
    double avgVolume = 0;
    for(int i = 0; i < m_period; i++) {
        avgVolume += rates[i].tick_volume;
    }
    avgVolume /= m_period;
    analysis.volume = rates[0].tick_volume / avgVolume;
    
    // Calcula suporte e resistência
    double high = rates[0].high, low = rates[0].low;
    for(int i = 1; i < m_period; i++) {
        high = MathMax(high, rates[i].high);
        low = MathMin(low, rates[i].low);
    }
    analysis.resistance = high;
    analysis.support = low;
    
    return true;
}

//+------------------------------------------------------------------+
//| Identifica padrões                                                |
//+------------------------------------------------------------------+
bool CAnalystAgent::IdentifyPatterns(string symbol, MarketAnalysis &analysis) {
    // Analisa padrões Weis Waves
    int wave = m_weisWaves.GetCurrentWave(symbol);
    string wavePattern = "";
    
    switch(wave) {
        case 1: wavePattern = "Wave 1 - Início de tendência"; break;
        case 2: wavePattern = "Wave 2 - Retração"; break;
        case 3: wavePattern = "Wave 3 - Impulso principal"; break;
        case 4: wavePattern = "Wave 4 - Consolidação"; break;
        case 5: wavePattern = "Wave 5 - Fim de tendência"; break;
    }
    
    // Analisa padrões VSA
    ENUM_VSA_SIGNAL vsaSignal = m_vsa.GetSignal(symbol);
    string vsaPattern = "";
    
    switch(vsaSignal) {
        case VSA_SIGNAL_BUYING_CLIMAX: vsaPattern = "Buying Climax"; break;
        case VSA_SIGNAL_SELLING_CLIMAX: vsaPattern = "Selling Climax"; break;
        case VSA_SIGNAL_HIGH_VOLUME_UP: vsaPattern = "Alto Volume Up"; break;
        case VSA_SIGNAL_HIGH_VOLUME_DOWN: vsaPattern = "Alto Volume Down"; break;
        case VSA_SIGNAL_NO_DEMAND: vsaPattern = "No Demand"; break;
        case VSA_SIGNAL_NO_SUPPLY: vsaPattern = "No Supply"; break;
    }
    
    // Combina padrões
    analysis.pattern = wavePattern + " | " + vsaPattern;
    
    // Calcula confiança baseada na concordância dos padrões
    bool waveBullish = (wave == 1 || wave == 3 || wave == 5);
    bool vsaBullish = (vsaSignal == VSA_SIGNAL_BUYING_CLIMAX || 
                      vsaSignal == VSA_SIGNAL_HIGH_VOLUME_UP ||
                      vsaSignal == VSA_SIGNAL_NO_SUPPLY);
                      
    analysis.confidence = waveBullish == vsaBullish ? 0.8 : 0.5;
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida análise                                                    |
//+------------------------------------------------------------------+
bool CAnalystAgent::ValidateAnalysis(MarketAnalysis &analysis) {
    // Verifica timestamp
    if(analysis.timestamp == 0) return false;
    
    // Verifica valores dentro dos limites
    if(analysis.trend < -1 || analysis.trend > 1) return false;
    if(analysis.momentum < -1 || analysis.momentum > 1) return false;
    if(analysis.volatility < 0 || analysis.volatility > 1) return false;
    if(analysis.volume < 0) return false;
    if(analysis.confidence < 0 || analysis.confidence > 1) return false;
    
    // Verifica níveis de suporte e resistência
    if(analysis.support >= analysis.resistance) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Gera sinal                                                        |
//+------------------------------------------------------------------+
bool CAnalystAgent::GenerateSignal(const MarketAnalysis &analysis, TradingSignal &signal) {
    signal.symbol = analysis.symbol;
    signal.timestamp = analysis.timestamp;
    signal.confidence = analysis.confidence;
    
    // Determina direção do sinal
    if(analysis.trend > 0 && analysis.momentum > 0) {
        signal.type = ORDER_TYPE_BUY;
        signal.entryPrice = analysis.support + (analysis.resistance - analysis.support) * 0.382;
        signal.stopLoss = analysis.support;
        signal.takeProfit = analysis.resistance;
    }
    else if(analysis.trend < 0 && analysis.momentum < 0) {
        signal.type = ORDER_TYPE_SELL;
        signal.entryPrice = analysis.resistance - (analysis.resistance - analysis.support) * 0.382;
        signal.stopLoss = analysis.resistance;
        signal.takeProfit = analysis.support;
    }
    else {
        return false;
    }
    
    // Calcula volume baseado na volatilidade e confiança
    signal.volume = analysis.volatility * analysis.confidence;
    
    // Define razão para o sinal
    signal.reason = "Sinal gerado baseado em: " + analysis.pattern;
    
    return true;
}

//+------------------------------------------------------------------+
//| Registra análise                                                  |
//+------------------------------------------------------------------+
void CAnalystAgent::LogAnalysis(const MarketAnalysis &analysis) {
    Print("Market Analysis - Symbol: ", analysis.symbol,
          ", Trend: ", analysis.trend,
          ", Momentum: ", analysis.momentum,
          ", Volatility: ", analysis.volatility,
          ", Volume: ", analysis.volume,
          ", Pattern: ", analysis.pattern,
          ", Confidence: ", analysis.confidence);
}

//+------------------------------------------------------------------+
//| Atualiza métricas                                                 |
//+------------------------------------------------------------------+
void CAnalystAgent::UpdateMetrics() {
    if(!m_core) return;
    
    // Atualiza PnL total
    m_metrics.totalPnL = 0;
    double totalWins = 0;
    double totalLosses = 0;
    int wins = 0;
    int losses = 0;
    
    // Analisa histórico de trades
    for(int i = OrdersHistoryTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) {
            double profit = OrderProfit() + OrderSwap() + OrderCommission();
            m_metrics.totalPnL += profit;
            
            if(profit > 0) {
                totalWins += profit;
                wins++;
                m_metrics.averageWin = totalWins / wins;
            }
            else if(profit < 0) {
                totalLosses += MathAbs(profit);
                losses++;
                m_metrics.averageLoss = totalLosses / losses;
            }
        }
    }
    
    // Calcula métricas
    m_metrics.totalTrades = wins + losses;
    m_metrics.winRate = m_metrics.totalTrades > 0 ? (double)wins / m_metrics.totalTrades * 100 : 0;
    m_metrics.profitFactor = totalLosses > 0 ? totalWins / totalLosses : 0;
    m_metrics.expectancy = (m_metrics.winRate/100 * m_metrics.averageWin) - 
                          ((1-m_metrics.winRate/100) * m_metrics.averageLoss);
    
    // Calcula retornos e métricas avançadas
    CalculateReturns();
    m_metrics.sharpeRatio = CalculateSharpeRatio();
    m_metrics.maxDrawdown = CalculateDrawdown();
    
    m_metrics.lastUpdate = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Calcula retornos                                                  |
//+------------------------------------------------------------------+
void CAnalystAgent::CalculateReturns() {
    // Calcula retornos diários
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    int daysInMonth = 30;
    
    ArrayResize(m_dailyReturns, daysInMonth);
    ArrayInitialize(m_dailyReturns, 0);
    
    for(int i = OrdersHistoryTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) {
            MqlDateTime orderDt;
            TimeToStruct(OrderCloseTime(), orderDt);
            
            if(orderDt.mon == dt.mon && orderDt.year == dt.year) {
                m_dailyReturns[orderDt.day-1] += OrderProfit() + OrderSwap() + OrderCommission();
            }
        }
    }
    
    // Calcula retornos mensais
    ArrayResize(m_monthlyReturns, 12);
    ArrayInitialize(m_monthlyReturns, 0);
    
    for(int i = OrdersHistoryTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) {
            MqlDateTime orderDt;
            TimeToStruct(OrderCloseTime(), orderDt);
            
            if(orderDt.year == dt.year) {
                m_monthlyReturns[orderDt.mon-1] += OrderProfit() + OrderSwap() + OrderCommission();
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Calcula Sharpe Ratio                                              |
//+------------------------------------------------------------------+
double CAnalystAgent::CalculateSharpeRatio() {
    double mean = 0;
    double variance = 0;
    int count = 0;
    
    // Calcula média dos retornos diários
    for(int i = 0; i < ArraySize(m_dailyReturns); i++) {
        if(m_dailyReturns[i] != 0) {
            mean += m_dailyReturns[i];
            count++;
        }
    }
    
    if(count == 0) return 0;
    mean /= count;
    
    // Calcula variância
    for(int i = 0; i < ArraySize(m_dailyReturns); i++) {
        if(m_dailyReturns[i] != 0) {
            variance += MathPow(m_dailyReturns[i] - mean, 2);
        }
    }
    
    variance /= count;
    double stdDev = MathSqrt(variance);
    
    // Taxa livre de risco (assumindo 2% ao ano)
    double riskFreeRate = 0.02 / 252;
    
    return stdDev != 0 ? (mean - riskFreeRate) / stdDev : 0;
}

//+------------------------------------------------------------------+
//| Calcula Drawdown                                                   |
//+------------------------------------------------------------------+
double CAnalystAgent::CalculateDrawdown() {
    double maxDrawdown = 0;
    double peak = 0;
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    for(int i = OrdersHistoryTotal() - 1; i >= 0; i--) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) {
            equity += OrderProfit() + OrderSwap() + OrderCommission();
            
            if(equity > peak) {
                peak = equity;
            }
            
            double drawdown = (peak - equity) / peak * 100;
            if(drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }
    }
    
    return maxDrawdown;
}

//+------------------------------------------------------------------+
//| Analisa performance                                               |
//+------------------------------------------------------------------+
bool CAnalystAgent::AnalyzePerformance() {
    UpdateMetrics();
    
    // Verifica alertas
    CheckAlerts();
    
    // Gera relatório se necessário
    if(m_autoReport) {
        datetime lastReportTime = 0;
        if(ArraySize(m_reports) > 0) {
            lastReportTime = m_reports[ArraySize(m_reports)-1].timestamp;
        }
        
        if(TimeCurrent() - lastReportTime >= m_reportInterval * 60) {
            GeneratePerformanceReport();
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Gera relatório de performance                                     |
//+------------------------------------------------------------------+
bool CAnalystAgent::GeneratePerformanceReport(bool isDetailed = false) {
    string content = GenerateReport(isDetailed);
    
    Report report;
    report.type = "Performance";
    report.content = content;
    report.timestamp = TimeCurrent();
    report.isUrgent = false;
    report.metrics = m_metrics;
    
    SaveReport(report);
    return true;
}

//+------------------------------------------------------------------+
//| Gera relatório de risco                                          |
//+------------------------------------------------------------------+
bool CAnalystAgent::GenerateRiskReport() {
    if(!m_core) return false;
    
    string content = "Risk Analysis Report\n";
    content += "-------------------\n\n";
    
    // Análise de exposição
    content += "Current Exposure:\n";
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionSelectByTicket(PositionGetTicket(i))) {
            content += StringFormat("  %s: %.2f lots\n",
                PositionGetString(POSITION_SYMBOL),
                PositionGetDouble(POSITION_VOLUME)
            );
        }
    }
    
    // Análise de correlação
    content += "\nCorrelation Analysis:\n";
    string symbols[] = {"EURUSD", "USDJPY", "GBPUSD"};
    for(int i = 0; i < ArraySize(symbols); i++) {
        for(int j = i + 1; j < ArraySize(symbols); j++) {
            double correlation = m_core.GetMonitoring().CalculateCorrelation(
                symbols[i],
                symbols[j]
            );
            content += StringFormat("  %s-%s: %.2f\n",
                symbols[i],
                symbols[j],
                correlation
            );
        }
    }
    
    Report report;
    report.type = "Risk";
    report.content = content;
    report.timestamp = TimeCurrent();
    report.isUrgent = false;
    report.metrics = m_metrics;
    
    SaveReport(report);
    return true;
}

//+------------------------------------------------------------------+
//| Gera relatório de mercado                                        |
//+------------------------------------------------------------------+
bool CAnalystAgent::GenerateMarketReport() {
    if(!m_core) return false;
    
    string content = "Market Analysis Report\n";
    content += "--------------------\n\n";
    
    // Análise técnica
    content += "Technical Analysis:\n";
    string symbols[] = {"EURUSD", "USDJPY", "GBPUSD"};
    for(int i = 0; i < ArraySize(symbols); i++) {
        AnalysisResult analysis = m_core.GetAnalysis().AnalyzeMarketPatterns(
            symbols[i],
            NULL,
            PERIOD_H1
        );
        
        content += StringFormat("  %s: %s (Accuracy: %.2f%%)\n",
            symbols[i],
            analysis.nextPrediction > 0 ? "Bullish" : "Bearish",
            analysis.predictionAccuracy * 100
        );
    }
    
    // Análise fundamental
    content += "\nFundamental Analysis:\n";
    NewsData news = m_core.GetDataCollection().GetLatestNews("");
    content += StringFormat("  Latest News: %s\n  Impact: %s\n",
        news.title,
        news.impact
    );
    
    Report report;
    report.type = "Market";
    report.content = content;
    report.timestamp = TimeCurrent();
    report.isUrgent = false;
    report.metrics = m_metrics;
    
    SaveReport(report);
    return true;
}

//+------------------------------------------------------------------+
//| Verifica alertas                                                  |
//+------------------------------------------------------------------+
void CAnalystAgent::CheckAlerts() {
    // Verifica drawdown
    if(m_metrics.maxDrawdown > 10) {
        SendAlert("High drawdown alert: " + DoubleToString(m_metrics.maxDrawdown, 2) + "%", true);
    }
    
    // Verifica win rate
    if(m_metrics.winRate < 40) {
        SendAlert("Low win rate alert: " + DoubleToString(m_metrics.winRate, 2) + "%", true);
    }
    
    // Verifica profit factor
    if(m_metrics.profitFactor < 1.2) {
        SendAlert("Low profit factor alert: " + DoubleToString(m_metrics.profitFactor, 2), false);
    }
}

//+------------------------------------------------------------------+
//| Envia alerta                                                      |
//+------------------------------------------------------------------+
void CAnalystAgent::SendAlert(string message, bool isUrgent = false) {
    if(!m_core) return;
    
    // Cria relatório de alerta
    Report report;
    report.type = "Alert";
    report.content = message;
    report.timestamp = TimeCurrent();
    report.isUrgent = isUrgent;
    report.metrics = m_metrics;
    
    SaveReport(report);
    
    // Envia alerta via Telegram se urgente
    if(isUrgent) {
        m_core.GetMonitoring().SendTelegramAlert(message);
    }
}

//+------------------------------------------------------------------+
//| Gera relatório                                                    |
//+------------------------------------------------------------------+
string CAnalystAgent::GenerateReport(bool isDetailed = false) {
    string content = "Performance Report\n";
    content += "-----------------\n\n";
    
    // Métricas básicas
    content += StringFormat("Total P&L: %.2f\n", m_metrics.totalPnL);
    content += StringFormat("Win Rate: %.2f%%\n", m_metrics.winRate);
    content += StringFormat("Profit Factor: %.2f\n", m_metrics.profitFactor);
    content += StringFormat("Total Trades: %d\n", m_metrics.totalTrades);
    content += StringFormat("Max Drawdown: %.2f%%\n", m_metrics.maxDrawdown);
    
    if(isDetailed) {
        // Métricas avançadas
        content += "\nAdvanced Metrics:\n";
        content += StringFormat("Sharpe Ratio: %.2f\n", m_metrics.sharpeRatio);
        content += StringFormat("Average Win: %.2f\n", m_metrics.averageWin);
        content += StringFormat("Average Loss: %.2f\n", m_metrics.averageLoss);
        content += StringFormat("Expectancy: %.2f\n", m_metrics.expectancy);
        
        // Análise de retornos
        content += "\nMonthly Returns:\n";
        for(int i = 0; i < ArraySize(m_monthlyReturns); i++) {
            if(m_monthlyReturns[i] != 0) {
                content += StringFormat("  Month %d: %.2f\n", i+1, m_monthlyReturns[i]);
            }
        }
    }
    
    return content;
}

//+------------------------------------------------------------------+
//| Salva relatório                                                   |
//+------------------------------------------------------------------+
void CAnalystAgent::SaveReport(const Report &report) {
    // Mantém número máximo de relatórios
    if(ArraySize(m_reports) >= m_maxReports) {
        for(int i = 0; i < ArraySize(m_reports) - 1; i++) {
            m_reports[i] = m_reports[i + 1];
        }
        ArrayResize(m_reports, m_maxReports);
    }
    else {
        ArrayResize(m_reports, ArraySize(m_reports) + 1);
    }
    
    m_reports[ArraySize(m_reports) - 1] = report;
}

//+------------------------------------------------------------------+
//| Obtém último relatório                                            |
//+------------------------------------------------------------------+
Report CAnalystAgent::GetLastReport() {
    if(ArraySize(m_reports) > 0) {
        return m_reports[ArraySize(m_reports) - 1];
    }
    
    Report empty;
    ZeroMemory(empty);
    return empty;
} 