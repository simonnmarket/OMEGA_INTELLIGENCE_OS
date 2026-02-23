#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Analysis/AdvancedAnalysis.mqh"
#include "../Monitoring/MonitoringSystem.mqh"

// Estrutura para ativo do portfólio
struct PortfolioAsset {
    string   symbol;           // Símbolo do ativo
    double   weight;          // Peso no portfólio (%)
    double   expectedReturn;  // Retorno esperado (%)
    double   volatility;     // Volatilidade (%)
    double   correlation[];  // Correlações com outros ativos
    double   sharpeRatio;    // Índice de Sharpe
    double   maxDrawdown;    // Máximo drawdown (%)
    bool     isActive;       // Se está ativo no portfólio
};

// Estrutura para métricas do portfólio
struct PortfolioMetrics {
    double   totalReturn;     // Retorno total (%)
    double   volatility;      // Volatilidade total (%)
    double   sharpeRatio;     // Índice de Sharpe do portfólio
    double   maxDrawdown;     // Máximo drawdown do portfólio (%)
    double   correlation;     // Correlação média entre ativos
    double   diversification; // Índice de diversificação (0-1)
    double   turnover;       // Taxa de turnover do portfólio (%)
    double   riskContribution[]; // Contribuição de risco por ativo
};

//+------------------------------------------------------------------+
//| Classe PortfolioOptimizer                                         |
//+------------------------------------------------------------------+
class CPortfolioOptimizer {
private:
    // Componentes principais
    CQuantumCore*    m_core;
    PortfolioAsset   m_assets[];
    PortfolioMetrics m_metrics;
    
    // Configurações
    int             m_lookbackPeriod;   // Período de análise histórica
    double          m_riskFreeRate;     // Taxa livre de risco (%)
    double          m_targetReturn;     // Retorno alvo (%)
    double          m_maxWeight;        // Peso máximo por ativo (%)
    double          m_minWeight;        // Peso mínimo por ativo (%)
    double          m_rebalancePct;    // Percentual para rebalanceamento
    
    // Estado do otimizador
    bool            m_isActive;
    datetime        m_lastOptimization;
    datetime        m_lastRebalance;
    
    // Métodos privados
    bool            CalculateReturns();
    bool            CalculateVolatilities();
    bool            CalculateCorrelations();
    bool            CalculateWeights();
    bool            ValidatePortfolio();
    void            LogPortfolioStatus();
    
public:
                    CPortfolioOptimizer();
                   ~CPortfolioOptimizer();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            AddAsset(const string symbol);
    bool            RemoveAsset(const string symbol);
    bool            OptimizePortfolio();
    bool            RebalancePortfolio();
    
    // Métodos de análise
    bool            AnalyzePortfolio();
    double          GetOptimalWeight(const string symbol);
    bool            NeedsRebalancing();
    
    // Configurações
    void            SetLookbackPeriod(const int period) { m_lookbackPeriod = period; }
    void            SetRiskFreeRate(const double rate) { m_riskFreeRate = rate; }
    void            SetTargetReturn(const double target) { m_targetReturn = target; }
    void            SetWeightLimits(const double min, const double max);
    void            SetRebalanceThreshold(const double threshold) { m_rebalancePct = threshold; }
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    PortfolioMetrics GetMetrics() const { return m_metrics; }
    int             GetAssetsCount() const { return ArraySize(m_assets); }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CPortfolioOptimizer::CPortfolioOptimizer() {
    m_core = NULL;
    m_isActive = false;
    m_lastOptimization = 0;
    m_lastRebalance = 0;
    
    // Configurações padrão
    m_lookbackPeriod = 252;    // 1 ano de trading
    m_riskFreeRate = 2.0;      // 2% ao ano
    m_targetReturn = 10.0;     // 10% ao ano
    m_maxWeight = 20.0;        // 20% máximo por ativo
    m_minWeight = 1.0;         // 1% mínimo por ativo
    m_rebalancePct = 5.0;      // 5% para rebalanceamento
    
    ArrayResize(m_assets, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CPortfolioOptimizer::~CPortfolioOptimizer() {
    ArrayFree(m_assets);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isActive = true;
    m_lastOptimization = TimeCurrent();
    m_lastRebalance = m_lastOptimization;
    
    return true;
}

//+------------------------------------------------------------------+
//| Adiciona ativo                                                    |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::AddAsset(const string symbol) {
    // Verifica se o ativo já existe
    for(int i = 0; i < ArraySize(m_assets); i++) {
        if(m_assets[i].symbol == symbol) return false;
    }
    
    // Adiciona novo ativo
    int size = ArraySize(m_assets);
    ArrayResize(m_assets, size + 1);
    
    m_assets[size].symbol = symbol;
    m_assets[size].weight = 0;
    m_assets[size].expectedReturn = 0;
    m_assets[size].volatility = 0;
    m_assets[size].sharpeRatio = 0;
    m_assets[size].maxDrawdown = 0;
    m_assets[size].isActive = true;
    
    ArrayResize(m_assets[size].correlation, size + 1);
    for(int i = 0; i <= size; i++) {
        m_assets[size].correlation[i] = (i == size) ? 1.0 : 0.0;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Remove ativo                                                      |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::RemoveAsset(const string symbol) {
    int index = -1;
    
    // Encontra índice do ativo
    for(int i = 0; i < ArraySize(m_assets); i++) {
        if(m_assets[i].symbol == symbol) {
            index = i;
            break;
        }
    }
    
    if(index == -1) return false;
    
    // Remove ativo e ajusta correlações
    int size = ArraySize(m_assets);
    for(int i = index; i < size - 1; i++) {
        m_assets[i] = m_assets[i + 1];
        ArrayResize(m_assets[i].correlation, size - 1);
    }
    
    ArrayResize(m_assets, size - 1);
    
    return true;
}

//+------------------------------------------------------------------+
//| Otimiza portfólio                                                 |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::OptimizePortfolio() {
    if(!m_isActive || !m_core) return false;
    
    // Calcula métricas dos ativos
    if(!CalculateReturns() || !CalculateVolatilities() || !CalculateCorrelations()) {
        Print("Failed to calculate portfolio metrics");
        return false;
    }
    
    // Calcula pesos ótimos
    if(!CalculateWeights()) {
        Print("Failed to calculate optimal weights");
        return false;
    }
    
    // Valida portfólio
    if(!ValidatePortfolio()) {
        Print("Portfolio validation failed");
        return false;
    }
    
    m_lastOptimization = TimeCurrent();
    LogPortfolioStatus();
    
    return true;
}

//+------------------------------------------------------------------+
//| Rebalanceia portfólio                                            |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::RebalancePortfolio() {
    if(!m_isActive || !m_core) return false;
    
    if(!NeedsRebalancing()) return true;
    
    // Obtém pesos atuais
    double currentWeights[];
    ArrayResize(currentWeights, ArraySize(m_assets));
    
    double totalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    for(int i = 0; i < ArraySize(m_assets); i++) {
        double positionValue = 0;
        for(int j = PositionsTotal() - 1; j >= 0; j--) {
            if(PositionSelectByTicket(PositionGetTicket(j))) {
                if(PositionGetString(POSITION_SYMBOL) == m_assets[i].symbol) {
                    positionValue += PositionGetDouble(POSITION_VOLUME) * PositionGetDouble(POSITION_PRICE_CURRENT);
                }
            }
        }
        currentWeights[i] = positionValue / totalEquity * 100;
    }
    
    // Verifica desvios e ajusta posições
    for(int i = 0; i < ArraySize(m_assets); i++) {
        double deviation = MathAbs(currentWeights[i] - m_assets[i].weight);
        if(deviation > m_rebalancePct) {
            // Calcula volume necessário para ajuste
            double targetValue = totalEquity * m_assets[i].weight / 100;
            double currentValue = totalEquity * currentWeights[i] / 100;
            double adjustmentValue = targetValue - currentValue;
            
            if(adjustmentValue > 0) {
                // Compra mais
                double volume = adjustmentValue / SymbolInfoDouble(m_assets[i].symbol, SYMBOL_ASK);
                m_core.GetTradingSystem().ExecuteOrder(ORDER_TYPE_BUY, volume);
            }
            else if(adjustmentValue < 0) {
                // Vende excesso
                double volume = MathAbs(adjustmentValue) / SymbolInfoDouble(m_assets[i].symbol, SYMBOL_BID);
                m_core.GetTradingSystem().ExecuteOrder(ORDER_TYPE_SELL, volume);
            }
        }
    }
    
    m_lastRebalance = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Analisa portfólio                                                 |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::AnalyzePortfolio() {
    if(!m_isActive || !m_core) return false;
    
    // Calcula métricas do portfólio
    m_metrics.totalReturn = 0;
    m_metrics.volatility = 0;
    m_metrics.maxDrawdown = 0;
    m_metrics.correlation = 0;
    m_metrics.diversification = 0;
    m_metrics.turnover = 0;
    
    // Calcula retorno e volatilidade do portfólio
    for(int i = 0; i < ArraySize(m_assets); i++) {
        m_metrics.totalReturn += m_assets[i].weight * m_assets[i].expectedReturn;
        
        for(int j = 0; j < ArraySize(m_assets); j++) {
            m_metrics.volatility += m_assets[i].weight * m_assets[j].weight * 
                                  m_assets[i].volatility * m_assets[j].volatility * 
                                  m_assets[i].correlation[j];
        }
    }
    
    m_metrics.volatility = MathSqrt(m_metrics.volatility);
    
    // Calcula Sharpe Ratio
    if(m_metrics.volatility > 0) {
        m_metrics.sharpeRatio = (m_metrics.totalReturn - m_riskFreeRate) / m_metrics.volatility;
    }
    
    // Calcula correlação média
    int correlationCount = 0;
    for(int i = 0; i < ArraySize(m_assets); i++) {
        for(int j = i + 1; j < ArraySize(m_assets); j++) {
            m_metrics.correlation += MathAbs(m_assets[i].correlation[j]);
            correlationCount++;
        }
    }
    if(correlationCount > 0) m_metrics.correlation /= correlationCount;
    
    // Calcula índice de diversificação
    double totalWeight = 0;
    for(int i = 0; i < ArraySize(m_assets); i++) {
        totalWeight += m_assets[i].weight;
    }
    if(totalWeight > 0) {
        double equalWeight = 1.0 / ArraySize(m_assets);
        double weightDeviation = 0;
        for(int i = 0; i < ArraySize(m_assets); i++) {
            weightDeviation += MathPow(m_assets[i].weight / totalWeight - equalWeight, 2);
        }
        m_metrics.diversification = 1.0 - MathSqrt(weightDeviation / ArraySize(m_assets));
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém peso ótimo                                                  |
//+------------------------------------------------------------------+
double CPortfolioOptimizer::GetOptimalWeight(const string symbol) {
    for(int i = 0; i < ArraySize(m_assets); i++) {
        if(m_assets[i].symbol == symbol) {
            return m_assets[i].weight;
        }
    }
    return 0;
}

//+------------------------------------------------------------------+
//| Verifica necessidade de rebalanceamento                           |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::NeedsRebalancing() {
    if(!m_isActive || !m_core) return false;
    
    double totalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    for(int i = 0; i < ArraySize(m_assets); i++) {
        double positionValue = 0;
        for(int j = PositionsTotal() - 1; j >= 0; j--) {
            if(PositionSelectByTicket(PositionGetTicket(j))) {
                if(PositionGetString(POSITION_SYMBOL) == m_assets[i].symbol) {
                    positionValue += PositionGetDouble(POSITION_VOLUME) * PositionGetDouble(POSITION_PRICE_CURRENT);
                }
            }
        }
        
        double currentWeight = positionValue / totalEquity * 100;
        if(MathAbs(currentWeight - m_assets[i].weight) > m_rebalancePct) {
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Define limites de peso                                            |
//+------------------------------------------------------------------+
void CPortfolioOptimizer::SetWeightLimits(const double min, const double max) {
    if(min >= 0 && max > min && max <= 100) {
        m_minWeight = min;
        m_maxWeight = max;
    }
}

//+------------------------------------------------------------------+
//| Calcula retornos                                                  |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::CalculateReturns() {
    for(int i = 0; i < ArraySize(m_assets); i++) {
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyRates(m_assets[i].symbol, PERIOD_D1, 0, m_lookbackPeriod, rates) != m_lookbackPeriod) {
            return false;
        }
        
        double returns = 0;
        for(int j = 1; j < m_lookbackPeriod; j++) {
            returns += (rates[j-1].close - rates[j].close) / rates[j].close;
        }
        
        m_assets[i].expectedReturn = (returns / (m_lookbackPeriod - 1)) * 252 * 100; // Anualizado
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula volatilidades                                             |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::CalculateVolatilities() {
    for(int i = 0; i < ArraySize(m_assets); i++) {
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyRates(m_assets[i].symbol, PERIOD_D1, 0, m_lookbackPeriod, rates) != m_lookbackPeriod) {
            return false;
        }
        
        double returns[];
        ArrayResize(returns, m_lookbackPeriod - 1);
        double meanReturn = 0;
        
        for(int j = 0; j < m_lookbackPeriod - 1; j++) {
            returns[j] = (rates[j].close - rates[j+1].close) / rates[j+1].close;
            meanReturn += returns[j];
        }
        meanReturn /= (m_lookbackPeriod - 1);
        
        double variance = 0;
        for(int j = 0; j < m_lookbackPeriod - 1; j++) {
            variance += MathPow(returns[j] - meanReturn, 2);
        }
        variance /= (m_lookbackPeriod - 2);
        
        m_assets[i].volatility = MathSqrt(variance * 252) * 100; // Anualizada
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula correlações                                               |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::CalculateCorrelations() {
    int size = ArraySize(m_assets);
    
    for(int i = 0; i < size; i++) {
        for(int j = i; j < size; j++) {
            if(i == j) {
                m_assets[i].correlation[j] = 1.0;
                continue;
            }
            
            MqlRates rates1[], rates2[];
            ArraySetAsSeries(rates1, true);
            ArraySetAsSeries(rates2, true);
            
            if(CopyRates(m_assets[i].symbol, PERIOD_D1, 0, m_lookbackPeriod, rates1) != m_lookbackPeriod ||
               CopyRates(m_assets[j].symbol, PERIOD_D1, 0, m_lookbackPeriod, rates2) != m_lookbackPeriod) {
                return false;
            }
            
            double correlation = m_core.GetMonitoring().CalculateCorrelation(m_assets[i].symbol, m_assets[j].symbol);
            
            m_assets[i].correlation[j] = correlation;
            m_assets[j].correlation[i] = correlation;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula pesos                                                     |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::CalculateWeights() {
    int size = ArraySize(m_assets);
    if(size == 0) return false;
    
    // Implementa otimização de média-variância
    double totalWeight = 0;
    double totalReturn = 0;
    double minVolatility = DBL_MAX;
    
    // Encontra ativo com menor volatilidade
    for(int i = 0; i < size; i++) {
        if(m_assets[i].volatility < minVolatility) {
            minVolatility = m_assets[i].volatility;
        }
    }
    
    // Atribui pesos inversamente proporcionais à volatilidade
    for(int i = 0; i < size; i++) {
        if(m_assets[i].volatility > 0) {
            m_assets[i].weight = minVolatility / m_assets[i].volatility;
            totalWeight += m_assets[i].weight;
        }
    }
    
    // Normaliza pesos
    for(int i = 0; i < size; i++) {
        m_assets[i].weight = (m_assets[i].weight / totalWeight) * 100;
        
        // Aplica limites
        if(m_assets[i].weight < m_minWeight) m_assets[i].weight = m_minWeight;
        if(m_assets[i].weight > m_maxWeight) m_assets[i].weight = m_maxWeight;
        
        totalReturn += m_assets[i].weight * m_assets[i].expectedReturn;
    }
    
    // Ajusta pesos se necessário para atingir retorno alvo
    if(totalReturn < m_targetReturn) {
        double adjustment = (m_targetReturn - totalReturn) / size;
        for(int i = 0; i < size; i++) {
            m_assets[i].weight += adjustment;
            if(m_assets[i].weight > m_maxWeight) m_assets[i].weight = m_maxWeight;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida portfólio                                                  |
//+------------------------------------------------------------------+
bool CPortfolioOptimizer::ValidatePortfolio() {
    double totalWeight = 0;
    
    for(int i = 0; i < ArraySize(m_assets); i++) {
        if(m_assets[i].weight < 0 || m_assets[i].weight > 100) return false;
        totalWeight += m_assets[i].weight;
    }
    
    return MathAbs(totalWeight - 100.0) < 0.01;
}

//+------------------------------------------------------------------+
//| Registra status do portfólio                                      |
//+------------------------------------------------------------------+
void CPortfolioOptimizer::LogPortfolioStatus() {
    Print("Portfolio Status - Return: ", m_metrics.totalReturn, "%",
          ", Volatility: ", m_metrics.volatility, "%",
          ", Sharpe: ", m_metrics.sharpeRatio,
          ", Diversification: ", m_metrics.diversification);
    
    for(int i = 0; i < ArraySize(m_assets); i++) {
        Print("Asset: ", m_assets[i].symbol,
              ", Weight: ", m_assets[i].weight, "%",
              ", Return: ", m_assets[i].expectedReturn, "%",
              ", Volatility: ", m_assets[i].volatility, "%");
    }
} 