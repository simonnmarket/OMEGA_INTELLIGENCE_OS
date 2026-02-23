#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include <Quantum/Core/QuantumCore.mqh>
#include <Quantum/Database/TradingDatabaseSystem.mqh>
#include <Quantum/Integration/MT5IntegrationSystem.mqh>

// Estrutura para métricas de performance
struct PerformanceMetrics {
    double   winRate;
    double   profitFactor;
    double   sharpeRatio;
    double   maxDrawdown;
    double   averageWin;
    double   averageLoss;
    double   totalTrades;
    double   profitablePercent;
    datetime lastUpdate;
};

// Estrutura para alertas
struct Alert {
    string   type;
    string   message;
    datetime time;
    bool     isCritical;
    bool     isAcknowledged;
};

// Estrutura para exposição
struct Exposure {
    string   symbol;
    double   amount;
    double   percentOfEquity;
    int      positions;
    double   unrealizedPL;
};

//+------------------------------------------------------------------+
//| Classe MonitoringSystem                                            |
//+------------------------------------------------------------------+
class CMonitoringSystem {
private:
    // Objetos
    CQuantumCore*           m_core;
    CTradingDatabaseSystem* m_database;
    CMT5IntegrationSystem*  m_mt5;
    
    // Parâmetros
    double                  m_maxDrawdownLimit;
    double                  m_maxExposurePercent;
    int                     m_maxPositions;
    double                  m_minWinRate;
    
    // Cache
    PerformanceMetrics     m_metrics;
    Alert                  m_alerts[];
    Exposure               m_exposures[];
    
    // Métodos privados
    bool                    UpdateMetrics();
    bool                    CheckRiskLimits();
    void                    GenerateAlert(string type, string message, bool isCritical = false);
    double                  CalculateSharpeRatio();
    double                  CalculateDrawdown();
    
public:
                           CMonitoringSystem();
                          ~CMonitoringSystem();
    
    // Métodos principais
    bool                    Initialize(double maxDD = 20.0, double maxExp = 50.0);
    bool                    Update();
    void                    SendTelegramAlert(const Alert &alert);
    void                    SendEmailAlert(const Alert &alert);
    
    // Getters
    PerformanceMetrics     GetMetrics() const { return m_metrics; }
    Alert                  GetLastAlert();
    Exposure               GetSymbolExposure(string symbol);
    
    // Análise de risco
    bool                    ValidateNewPosition(string symbol, double volume);
    double                  GetOptimalPositionSize(string symbol);
    double                  CalculateCorrelation(string symbol1, string symbol2);
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CMonitoringSystem::CMonitoringSystem() {
    m_core = new CQuantumCore();
    m_database = new CTradingDatabaseSystem();
    m_mt5 = new CMT5IntegrationSystem();
    
    m_maxDrawdownLimit = 20.0;
    m_maxExposurePercent = 50.0;
    m_maxPositions = 10;
    m_minWinRate = 50.0;
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CMonitoringSystem::~CMonitoringSystem() {
    delete m_core;
    delete m_database;
    delete m_mt5;
    ArrayFree(m_alerts);
    ArrayFree(m_exposures);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CMonitoringSystem::Initialize(double maxDD = 20.0, double maxExp = 50.0) {
    m_maxDrawdownLimit = maxDD;
    m_maxExposurePercent = maxExp;
    
    if(!UpdateMetrics()) {
        Print("Failed to update initial metrics");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza métricas                                                 |
//+------------------------------------------------------------------+
bool CMonitoringSystem::UpdateMetrics() {
    // Calcula win rate
    int totalTrades = (int)HistoryDealsTotal();
    int winTrades = 0;
    double totalProfit = 0;
    double totalLoss = 0;
    
    for(int i = 0; i < totalTrades; i++) {
        ulong ticket = HistoryDealGetTicket(i);
        if(ticket == 0) continue;
        
        double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
        if(profit > 0) {
            winTrades++;
            totalProfit += profit;
        } else if(profit < 0) {
            totalLoss += MathAbs(profit);
        }
    }
    
    m_metrics.winRate = totalTrades > 0 ? (double)winTrades / totalTrades * 100 : 0;
    m_metrics.profitFactor = totalLoss > 0 ? totalProfit / totalLoss : 0;
    m_metrics.sharpeRatio = CalculateSharpeRatio();
    m_metrics.maxDrawdown = CalculateDrawdown();
    m_metrics.averageWin = winTrades > 0 ? totalProfit / winTrades : 0;
    m_metrics.averageLoss = (totalTrades - winTrades) > 0 ? totalLoss / (totalTrades - winTrades) : 0;
    m_metrics.totalTrades = totalTrades;
    m_metrics.profitablePercent = totalTrades > 0 ? (double)winTrades / totalTrades * 100 : 0;
    m_metrics.lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica limites de risco                                         |
//+------------------------------------------------------------------+
bool CMonitoringSystem::CheckRiskLimits() {
    // Verifica drawdown
    if(m_metrics.maxDrawdown > m_maxDrawdownLimit) {
        GenerateAlert("Risk", "Maximum drawdown limit exceeded", true);
        return false;
    }
    
    // Verifica exposição total
    double totalExposure = 0;
    for(int i = 0; i < ArraySize(m_exposures); i++) {
        totalExposure += m_exposures[i].percentOfEquity;
    }
    
    if(totalExposure > m_maxExposurePercent) {
        GenerateAlert("Risk", "Maximum exposure limit exceeded", true);
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Gera alerta                                                       |
//+------------------------------------------------------------------+
void CMonitoringSystem::GenerateAlert(string type, string message, bool isCritical = false) {
    Alert alert;
    alert.type = type;
    alert.message = message;
    alert.time = TimeCurrent();
    alert.isCritical = isCritical;
    alert.isAcknowledged = false;
    
    int size = ArraySize(m_alerts);
    ArrayResize(m_alerts, size + 1);
    m_alerts[size] = alert;
    
    if(isCritical) {
        SendTelegramAlert(alert);
        SendEmailAlert(alert);
    }
}

//+------------------------------------------------------------------+
//| Calcula Sharpe Ratio                                              |
//+------------------------------------------------------------------+
double CMonitoringSystem::CalculateSharpeRatio() {
    double returns[];
    ArrayResize(returns, 30); // 30 dias
    
    // Calcula retornos diários
    for(int i = 0; i < 30; i++) {
        returns[i] = 0; // Implementar cálculo real
    }
    
    double meanReturn = 0;
    double stdDev = 0;
    
    // Calcula média
    for(int i = 0; i < 30; i++) {
        meanReturn += returns[i];
    }
    meanReturn /= 30;
    
    // Calcula desvio padrão
    for(int i = 0; i < 30; i++) {
        stdDev += MathPow(returns[i] - meanReturn, 2);
    }
    stdDev = MathSqrt(stdDev / 29);
    
    // Taxa livre de risco (assumindo 2% ao ano)
    double riskFreeRate = 0.02 / 252; // Taxa diária
    
    return stdDev != 0 ? (meanReturn - riskFreeRate) / stdDev : 0;
}

//+------------------------------------------------------------------+
//| Calcula drawdown                                                  |
//+------------------------------------------------------------------+
double CMonitoringSystem::CalculateDrawdown() {
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    return balance > 0 ? (balance - equity) / balance * 100 : 0;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                  |
//+------------------------------------------------------------------+
bool CMonitoringSystem::Update() {
    if(!UpdateMetrics()) return false;
    if(!CheckRiskLimits()) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Envia alerta Telegram                                             |
//+------------------------------------------------------------------+
void CMonitoringSystem::SendTelegramAlert(const Alert &alert) {
    // Implementar integração com Telegram
    Print("Telegram Alert: ", alert.message);
}

//+------------------------------------------------------------------+
//| Envia alerta Email                                                |
//+------------------------------------------------------------------+
void CMonitoringSystem::SendEmailAlert(const Alert &alert) {
    // Implementar envio de email
    Print("Email Alert: ", alert.message);
}

//+------------------------------------------------------------------+
//| Obtém último alerta                                               |
//+------------------------------------------------------------------+
Alert CMonitoringSystem::GetLastAlert() {
    int size = ArraySize(m_alerts);
    if(size > 0) {
        return m_alerts[size - 1];
    }
    
    Alert empty = {0};
    return empty;
}

//+------------------------------------------------------------------+
//| Obtém exposição do símbolo                                        |
//+------------------------------------------------------------------+
Exposure CMonitoringSystem::GetSymbolExposure(string symbol) {
    for(int i = 0; i < ArraySize(m_exposures); i++) {
        if(m_exposures[i].symbol == symbol) {
            return m_exposures[i];
        }
    }
    
    Exposure empty = {0};
    return empty;
}

//+------------------------------------------------------------------+
//| Valida nova posição                                               |
//+------------------------------------------------------------------+
bool CMonitoringSystem::ValidateNewPosition(string symbol, double volume) {
    Exposure exposure = GetSymbolExposure(symbol);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // Verifica limite de posições
    if(PositionsTotal() >= m_maxPositions) {
        GenerateAlert("Position", "Maximum positions limit reached", false);
        return false;
    }
    
    // Verifica exposição do símbolo
    double newExposure = (exposure.amount + volume) / equity * 100;
    if(newExposure > m_maxExposurePercent) {
        GenerateAlert("Exposure", "Symbol exposure limit exceeded", false);
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula tamanho ótimo da posição                                 |
//+------------------------------------------------------------------+
double CMonitoringSystem::GetOptimalPositionSize(string symbol) {
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double riskPerTrade = 0.02; // 2% por trade
    
    double atr = iATR(symbol, PERIOD_D1, 14, 0);
    double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    
    if(atr == 0 || tickValue == 0) return 0;
    
    double riskAmount = equity * riskPerTrade;
    double positionSize = riskAmount / (atr * tickValue);
    
    return NormalizeDouble(positionSize, 2);
}

//+------------------------------------------------------------------+
//| Calcula correlação entre símbolos                                 |
//+------------------------------------------------------------------+
double CMonitoringSystem::CalculateCorrelation(string symbol1, string symbol2) {
    int period = 100;
    double data1[], data2[];
    ArrayResize(data1, period);
    ArrayResize(data2, period);
    
    // Obtém dados históricos
    for(int i = 0; i < period; i++) {
        data1[i] = iClose(symbol1, PERIOD_D1, i);
        data2[i] = iClose(symbol2, PERIOD_D1, i);
    }
    
    // Calcula correlação
    double sum1 = 0, sum2 = 0, sum12 = 0;
    double sum1Sq = 0, sum2Sq = 0;
    
    for(int i = 0; i < period; i++) {
        sum1 += data1[i];
        sum2 += data2[i];
        sum12 += data1[i] * data2[i];
        sum1Sq += data1[i] * data1[i];
        sum2Sq += data2[i] * data2[i];
    }
    
    double numerator = period * sum12 - sum1 * sum2;
    double denominator = MathSqrt((period * sum1Sq - sum1 * sum1) * (period * sum2Sq - sum2 * sum2));
    
    return denominator != 0 ? numerator / denominator : 0;
} 