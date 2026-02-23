#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Monitoring/MonitoringSystem.mqh"

// Estrutura para limites de risco
struct RiskLimits {
    double   maxDrawdown;      // Máximo drawdown permitido (%)
    double   maxExposure;      // Máxima exposição total (%)
    double   maxPositionSize;  // Tamanho máximo por posição (%)
    double   maxCorrelation;   // Correlação máxima entre ativos
    double   minMarginLevel;   // Nível mínimo de margem (%)
    int      maxOpenPositions; // Número máximo de posições abertas
    double   maxDailyLoss;     // Perda máxima diária (%)
    double   maxWeeklyLoss;    // Perda máxima semanal (%)
};

// Estrutura para métricas de risco
struct RiskMetrics {
    double   currentDrawdown;   // Drawdown atual (%)
    double   totalExposure;    // Exposição total atual (%)
    double   marginLevel;      // Nível de margem atual (%)
    int      openPositions;    // Número de posições abertas
    double   dailyPnL;        // Lucro/Perda diário (%)
    double   weeklyPnL;       // Lucro/Perda semanal (%)
    double   volatility;      // Volatilidade atual
    double   correlation;     // Correlação média entre ativos
};

//+------------------------------------------------------------------+
//| Classe RiskManager                                                 |
//+------------------------------------------------------------------+
class CRiskManager {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    RiskLimits      m_limits;
    RiskMetrics     m_metrics;
    
    // Estado do gerenciador
    bool            m_isActive;
    datetime        m_lastUpdate;
    double          m_initialBalance;
    double          m_lastDayBalance;
    double          m_lastWeekBalance;
    
    // Cache de correlações
    double          m_correlationMatrix[][100];
    string          m_symbols[];
    
    // Métodos privados
    bool            UpdateMetrics();
    bool            ValidatePosition(const string symbol, const double volume);
    bool            CheckCorrelation(const string symbol1, const string symbol2);
    double          CalculateOptimalPosition(const string symbol);
    void            LogRiskStatus();
    
public:
                    CRiskManager();
                   ~CRiskManager();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            SetRiskLimits(const RiskLimits &limits);
    bool            ValidateOrder(const string symbol, const double volume);
    double          GetOptimalPositionSize(const string symbol);
    bool            CheckRiskLevels();
    
    // Métodos de atualização
    bool            UpdateCorrelations();
    bool            UpdateDailyStats();
    bool            UpdateWeeklyStats();
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    RiskMetrics     GetMetrics() const { return m_metrics; }
    RiskLimits      GetLimits() const { return m_limits; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CRiskManager::CRiskManager() {
    m_core = NULL;
    m_isActive = false;
    m_lastUpdate = 0;
    m_initialBalance = 0;
    m_lastDayBalance = 0;
    m_lastWeekBalance = 0;
    
    // Configura limites padrão
    m_limits.maxDrawdown = 2.0;      // 2%
    m_limits.maxExposure = 20.0;     // 20%
    m_limits.maxPositionSize = 5.0;  // 5%
    m_limits.maxCorrelation = 0.7;   // 0.7
    m_limits.minMarginLevel = 200.0; // 200%
    m_limits.maxOpenPositions = 10;  // 10 posições
    m_limits.maxDailyLoss = 1.0;     // 1%
    m_limits.maxWeeklyLoss = 3.0;    // 3%
    
    ArrayResize(m_symbols, 0);
    ArrayResize(m_correlationMatrix, 0, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CRiskManager::~CRiskManager() {
    ArrayFree(m_symbols);
    ArrayFree(m_correlationMatrix);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CRiskManager::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isActive = true;
    m_lastUpdate = TimeCurrent();
    m_initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    m_lastDayBalance = m_initialBalance;
    m_lastWeekBalance = m_initialBalance;
    
    if(!UpdateMetrics()) {
        Print("Failed to initialize risk metrics");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Define limites de risco                                           |
//+------------------------------------------------------------------+
bool CRiskManager::SetRiskLimits(const RiskLimits &limits) {
    // Valida limites
    if(limits.maxDrawdown <= 0 || limits.maxDrawdown > 10) return false;
    if(limits.maxExposure <= 0 || limits.maxExposure > 100) return false;
    if(limits.maxPositionSize <= 0 || limits.maxPositionSize > 20) return false;
    if(limits.maxCorrelation <= 0 || limits.maxCorrelation > 1) return false;
    if(limits.minMarginLevel < 100) return false;
    if(limits.maxOpenPositions <= 0) return false;
    if(limits.maxDailyLoss <= 0 || limits.maxDailyLoss > 5) return false;
    if(limits.maxWeeklyLoss <= 0 || limits.maxWeeklyLoss > 10) return false;
    
    m_limits = limits;
    return true;
}

//+------------------------------------------------------------------+
//| Valida ordem                                                      |
//+------------------------------------------------------------------+
bool CRiskManager::ValidateOrder(const string symbol, const double volume) {
    if(!m_isActive || !m_core) return false;
    
    // Atualiza métricas
    if(!UpdateMetrics()) return false;
    
    // Verifica limites gerais
    if(m_metrics.currentDrawdown >= m_limits.maxDrawdown) {
        Print("Maximum drawdown limit reached");
        return false;
    }
    
    if(m_metrics.totalExposure >= m_limits.maxExposure) {
        Print("Maximum exposure limit reached");
        return false;
    }
    
    if(m_metrics.marginLevel <= m_limits.minMarginLevel) {
        Print("Margin level too low");
        return false;
    }
    
    if(m_metrics.openPositions >= m_limits.maxOpenPositions) {
        Print("Maximum number of positions reached");
        return false;
    }
    
    if(m_metrics.dailyPnL <= -m_limits.maxDailyLoss) {
        Print("Maximum daily loss reached");
        return false;
    }
    
    if(m_metrics.weeklyPnL <= -m_limits.maxWeeklyLoss) {
        Print("Maximum weekly loss reached");
        return false;
    }
    
    // Valida posição específica
    return ValidatePosition(symbol, volume);
}

//+------------------------------------------------------------------+
//| Obtém tamanho ótimo da posição                                    |
//+------------------------------------------------------------------+
double CRiskManager::GetOptimalPositionSize(const string symbol) {
    if(!m_isActive || !m_core) return 0;
    
    return CalculateOptimalPosition(symbol);
}

//+------------------------------------------------------------------+
//| Verifica níveis de risco                                          |
//+------------------------------------------------------------------+
bool CRiskManager::CheckRiskLevels() {
    if(!m_isActive || !m_core) return false;
    
    if(!UpdateMetrics()) return false;
    
    bool result = true;
    
    // Verifica todos os limites
    if(m_metrics.currentDrawdown >= m_limits.maxDrawdown) {
        Print("WARNING: Maximum drawdown limit exceeded");
        result = false;
    }
    
    if(m_metrics.totalExposure >= m_limits.maxExposure) {
        Print("WARNING: Maximum exposure limit exceeded");
        result = false;
    }
    
    if(m_metrics.marginLevel <= m_limits.minMarginLevel) {
        Print("WARNING: Margin level below minimum");
        result = false;
    }
    
    if(m_metrics.dailyPnL <= -m_limits.maxDailyLoss) {
        Print("WARNING: Maximum daily loss exceeded");
        result = false;
    }
    
    if(m_metrics.weeklyPnL <= -m_limits.maxWeeklyLoss) {
        Print("WARNING: Maximum weekly loss exceeded");
        result = false;
    }
    
    LogRiskStatus();
    
    return result;
}

//+------------------------------------------------------------------+
//| Atualiza correlações                                              |
//+------------------------------------------------------------------+
bool CRiskManager::UpdateCorrelations() {
    if(!m_isActive || !m_core) return false;
    
    int totalSymbols = ArraySize(m_symbols);
    if(totalSymbols == 0) return true;
    
    // Redimensiona matriz de correlação
    ArrayResize(m_correlationMatrix, totalSymbols);
    for(int i = 0; i < totalSymbols; i++) {
        ArrayResize(m_correlationMatrix[i], totalSymbols);
    }
    
    // Calcula correlações
    for(int i = 0; i < totalSymbols; i++) {
        for(int j = i; j < totalSymbols; j++) {
            if(i == j) {
                m_correlationMatrix[i][j] = 1.0;
                continue;
            }
            
            double correlation = m_core.GetMonitoring().CalculateCorrelation(m_symbols[i], m_symbols[j]);
            m_correlationMatrix[i][j] = correlation;
            m_correlationMatrix[j][i] = correlation;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza estatísticas diárias                                     |
//+------------------------------------------------------------------+
bool CRiskManager::UpdateDailyStats() {
    if(!m_isActive || !m_core) return false;
    
    static datetime lastDay = 0;
    datetime currentTime = TimeCurrent();
    
    MqlDateTime time;
    TimeToStruct(currentTime, time);
    
    // Verifica se é um novo dia
    if(time.day != TimeToStruct(lastDay, time).day) {
        m_lastDayBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        lastDay = currentTime;
    }
    
    // Calcula P&L diário
    double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    m_metrics.dailyPnL = (currentBalance - m_lastDayBalance) / m_lastDayBalance * 100;
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza estatísticas semanais                                    |
//+------------------------------------------------------------------+
bool CRiskManager::UpdateWeeklyStats() {
    if(!m_isActive || !m_core) return false;
    
    static datetime lastWeek = 0;
    datetime currentTime = TimeCurrent();
    
    MqlDateTime time;
    TimeToStruct(currentTime, time);
    
    // Verifica se é uma nova semana
    if(time.day_of_week < TimeToStruct(lastWeek, time).day_of_week) {
        m_lastWeekBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        lastWeek = currentTime;
    }
    
    // Calcula P&L semanal
    double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    m_metrics.weeklyPnL = (currentBalance - m_lastWeekBalance) / m_lastWeekBalance * 100;
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza métricas                                                 |
//+------------------------------------------------------------------+
bool CRiskManager::UpdateMetrics() {
    if(!m_isActive || !m_core) return false;
    
    // Atualiza drawdown
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    m_metrics.currentDrawdown = (balance - equity) / balance * 100;
    
    // Atualiza exposição total
    m_metrics.totalExposure = 0;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket)) {
            double positionValue = PositionGetDouble(POSITION_VOLUME) * PositionGetDouble(POSITION_PRICE_CURRENT);
            m_metrics.totalExposure += positionValue / equity * 100;
        }
    }
    
    // Atualiza nível de margem
    m_metrics.marginLevel = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
    
    // Atualiza número de posições
    m_metrics.openPositions = PositionsTotal();
    
    // Atualiza estatísticas
    UpdateDailyStats();
    UpdateWeeklyStats();
    
    // Atualiza volatilidade
    m_metrics.volatility = m_core.GetMonitoring().CalculateVolatility();
    
    // Atualiza correlação média
    UpdateCorrelations();
    m_metrics.correlation = 0;
    int count = 0;
    for(int i = 0; i < ArraySize(m_correlationMatrix); i++) {
        for(int j = i + 1; j < ArraySize(m_correlationMatrix[i]); j++) {
            m_metrics.correlation += MathAbs(m_correlationMatrix[i][j]);
            count++;
        }
    }
    if(count > 0) m_metrics.correlation /= count;
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida posição                                                    |
//+------------------------------------------------------------------+
bool CRiskManager::ValidatePosition(const string symbol, const double volume) {
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double positionValue = volume * SymbolInfoDouble(symbol, SYMBOL_ASK);
    
    // Verifica tamanho da posição
    if(positionValue / equity * 100 > m_limits.maxPositionSize) {
        Print("Position size exceeds maximum allowed");
        return false;
    }
    
    // Verifica correlações
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket)) {
            string posSymbol = PositionGetString(POSITION_SYMBOL);
            if(posSymbol != symbol && !CheckCorrelation(symbol, posSymbol)) {
                Print("Correlation limit exceeded with ", posSymbol);
                return false;
            }
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica correlação                                               |
//+------------------------------------------------------------------+
bool CRiskManager::CheckCorrelation(const string symbol1, const string symbol2) {
    int index1 = -1, index2 = -1;
    
    // Encontra índices dos símbolos
    for(int i = 0; i < ArraySize(m_symbols); i++) {
        if(m_symbols[i] == symbol1) index1 = i;
        if(m_symbols[i] == symbol2) index2 = i;
    }
    
    // Se algum símbolo não foi encontrado, retorna true
    if(index1 == -1 || index2 == -1) return true;
    
    return MathAbs(m_correlationMatrix[index1][index2]) <= m_limits.maxCorrelation;
}

//+------------------------------------------------------------------+
//| Calcula tamanho ótimo da posição                                  |
//+------------------------------------------------------------------+
double CRiskManager::CalculateOptimalPosition(const string symbol) {
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double availableRisk = equity * (m_limits.maxPositionSize / 100);
    
    double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    
    if(tickValue == 0 || tickSize == 0) return 0;
    
    // Ajusta pelo nível de volatilidade
    double volatilityAdjustment = 1.0;
    if(m_metrics.volatility > 0) {
        volatilityAdjustment = 1.0 / m_metrics.volatility;
    }
    
    return NormalizeDouble(availableRisk * volatilityAdjustment / (tickValue / tickSize), 2);
}

//+------------------------------------------------------------------+
//| Registra status de risco                                          |
//+------------------------------------------------------------------+
void CRiskManager::LogRiskStatus() {
    Print("Risk Status - Drawdown: ", m_metrics.currentDrawdown, "%",
          ", Exposure: ", m_metrics.totalExposure, "%",
          ", Margin Level: ", m_metrics.marginLevel, "%",
          ", Daily P&L: ", m_metrics.dailyPnL, "%",
          ", Weekly P&L: ", m_metrics.weeklyPnL, "%",
          ", Positions: ", m_metrics.openPositions);
} 