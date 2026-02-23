#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para métricas do sistema
struct SystemMetrics {
    double successRate;        // Taxa de sucesso das operações
    double currentDrawdown;    // Drawdown atual
    double profitFactor;       // Fator de lucro
    double systemHealth;       // Saúde do sistema (0-1)
    double performanceScore;   // Pontuação de desempenho
    bool isValid;             // Validação
};

// Estrutura para alertas
struct SystemAlert {
    string message;           // Mensagem do alerta
    datetime timestamp;       // Timestamp do alerta
    int severity;            // Severidade (1-3)
    bool isActive;          // Status do alerta
};

// Classe do Sistema de Monitoramento
class CSystemMonitoring {
private:
    // Configurações
    double m_minSuccessRate;    // Taxa mínima de sucesso
    double m_maxDrawdown;       // Drawdown máximo permitido
    double m_minProfitFactor;   // Fator de lucro mínimo
    double m_healthThreshold;   // Limiar de saúde do sistema
    
    // Estado
    bool m_isInitialized;
    SystemMetrics m_currentMetrics;
    SystemAlert m_alerts[];
    
    // Métodos privados
    double CalculateSuccessRate(const int& totalTrades,
                               const int& successfulTrades) {
        if(totalTrades == 0) return 0.0;
        return (double)successfulTrades / totalTrades;
    }
    
    double CalculateProfitFactor(const double& grossProfit,
                                const double& grossLoss) {
        if(grossLoss == 0) return 0.0;
        return grossProfit / grossLoss;
    }
    
    double CalculateSystemHealth() {
        double health = 0.0;
        
        // Fatores de saúde
        health += (m_currentMetrics.successRate >= m_minSuccessRate ? 1.0 : 0.0) * 0.3;
        health += (m_currentMetrics.currentDrawdown <= m_maxDrawdown ? 1.0 : 0.0) * 0.3;
        health += (m_currentMetrics.profitFactor >= m_minProfitFactor ? 1.0 : 0.0) * 0.4;
        
        return health;
    }
    
    double CalculatePerformanceScore() {
        double score = 0.0;
        
        // Fatores de desempenho
        score += m_currentMetrics.successRate * 0.4;
        score += (1.0 - m_currentMetrics.currentDrawdown) * 0.3;
        score += MathMin(m_currentMetrics.profitFactor / 2.0, 1.0) * 0.3;
        
        return score;
    }
    
    void CheckAlerts() {
        // Limpar alertas antigos
        ArrayFree(m_alerts);
        
        // Verificar taxa de sucesso
        if(m_currentMetrics.successRate < m_minSuccessRate) {
            AddAlert("Taxa de sucesso abaixo do mínimo", 2);
        }
        
        // Verificar drawdown
        if(m_currentMetrics.currentDrawdown > m_maxDrawdown) {
            AddAlert("Drawdown excedeu o limite máximo", 3);
        }
        
        // Verificar fator de lucro
        if(m_currentMetrics.profitFactor < m_minProfitFactor) {
            AddAlert("Fator de lucro abaixo do mínimo", 2);
        }
        
        // Verificar saúde do sistema
        if(m_currentMetrics.systemHealth < m_healthThreshold) {
            AddAlert("Saúde do sistema comprometida", 3);
        }
    }
    
    void AddAlert(const string& message, const int& severity) {
        int size = ArraySize(m_alerts);
        ArrayResize(m_alerts, size + 1);
        
        m_alerts[size].message = message;
        m_alerts[size].timestamp = TimeCurrent();
        m_alerts[size].severity = severity;
        m_alerts[size].isActive = true;
    }
    
public:
    // Construtor
    CSystemMonitoring() {
        m_minSuccessRate = 0.55;    // 55% mínimo
        m_maxDrawdown = 0.1;        // 10% máximo
        m_minProfitFactor = 1.5;    // 1.5 mínimo
        m_healthThreshold = 0.7;    // 70% mínimo
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Atualização de métricas
    void UpdateMetrics(const int& totalTrades,
                      const int& successfulTrades,
                      const double& currentDrawdown,
                      const double& grossProfit,
                      const double& grossLoss) {
        if(!m_isInitialized) return;
        
        // Calcular métricas
        m_currentMetrics.successRate = CalculateSuccessRate(totalTrades, successfulTrades);
        m_currentMetrics.currentDrawdown = currentDrawdown;
        m_currentMetrics.profitFactor = CalculateProfitFactor(grossProfit, grossLoss);
        m_currentMetrics.systemHealth = CalculateSystemHealth();
        m_currentMetrics.performanceScore = CalculatePerformanceScore();
        m_currentMetrics.isValid = true;
        
        // Verificar alertas
        CheckAlerts();
    }
    
    // Verificar saúde do sistema
    bool IsSystemHealthy() const {
        if(!m_isInitialized) return false;
        return m_currentMetrics.systemHealth >= m_healthThreshold;
    }
    
    // Obter alertas ativos
    void GetActiveAlerts(SystemAlert& alerts[]) {
        ArrayFree(alerts);
        
        for(int i = 0; i < ArraySize(m_alerts); i++) {
            if(m_alerts[i].isActive) {
                int size = ArraySize(alerts);
                ArrayResize(alerts, size + 1);
                alerts[size] = m_alerts[i];
            }
        }
    }
    
    // Métodos de configuração
    void SetMinSuccessRate(double rate) {
        m_minSuccessRate = rate;
    }
    
    void SetMaxDrawdown(double drawdown) {
        m_maxDrawdown = drawdown;
    }
    
    void SetMinProfitFactor(double factor) {
        m_minProfitFactor = factor;
    }
    
    void SetHealthThreshold(double threshold) {
        m_healthThreshold = threshold;
    }
    
    // Métodos de acesso
    SystemMetrics GetMetrics() const {
        return m_currentMetrics;
    }
    
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 