#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Incluir arquivos necessários
#include "QuantumTrader.mqh"
#include "MarketReader.mqh"
#include "RiskGuardian.mqh"
#include "StatisticalAnalysisAgent.mqh"
#include "QuantumProjectionAgent.mqh"
#include "PiCyclicAnalysis.mqh"
#include "FewShotTrainingSystem.mqh"
#include "PreTradeAnalysis.mqh"
#include "SystemMonitoring.mqh"
#include "TaskPrioritization.mqh"
#include "ScalingSystem.mqh"

// Estrutura para decisão integrada
struct IntegratedDecision {
    double statisticalWeight;    // Peso da análise estatística
    double quantumWeight;        // Peso da análise quântica
    double cyclicWeight;         // Peso da análise cíclica
    double finalDecision;        // Decisão final
    datetime timestamp;          // Timestamp da decisão
};

// Classe do Sistema de Integração
class CAgentIntegrationSystem {
private:
    // Agentes principais
    CQuantumTrader* m_quantumTrader;
    CMarketReader* m_marketReader;
    CRiskGuardian* m_riskGuardian;
    
    // Agentes de análise
    CStatisticalAnalysisAgent* m_statisticalAgent;
    CQuantumProjectionAgent* m_quantumAgent;
    CPiCyclicAnalysis* m_cyclicAgent;
    
    // Sistema de treinamento
    CFewShotTrainingSystem* m_fewShotSystem;
    
    // Sistemas de suporte
    CPreTradeAnalysis* m_preTradeSystem;
    CSystemMonitoring* m_monitoringSystem;
    CTaskPrioritization* m_taskSystem;
    CScalingSystem* m_scalingSystem;
    
    // Estado
    bool m_isInitialized;
    IntegratedDecision m_lastDecision;
    
    // Métodos privados
    bool InitializeAgents() {
        // Inicializar agentes principais
        m_quantumTrader = new CQuantumTrader();
        m_marketReader = new CMarketReader();
        m_riskGuardian = new CRiskGuardian();
        
        if(!m_quantumTrader.Initialize() ||
           !m_marketReader.Initialize() ||
           !m_riskGuardian.Initialize()) {
            return false;
        }
        
        // Inicializar agentes de análise
        m_statisticalAgent = new CStatisticalAnalysisAgent();
        m_quantumAgent = new CQuantumProjectionAgent();
        m_cyclicAgent = new CPiCyclicAnalysis();
        
        if(!m_statisticalAgent.Initialize() ||
           !m_quantumAgent.Initialize() ||
           !m_cyclicAgent.Initialize()) {
            return false;
        }
        
        // Inicializar sistema de treinamento
        m_fewShotSystem = new CFewShotTrainingSystem();
        if(!m_fewShotSystem.Initialize()) {
            return false;
        }
        
        // Inicializar sistemas de suporte
        m_preTradeSystem = new CPreTradeAnalysis();
        m_monitoringSystem = new CSystemMonitoring();
        m_taskSystem = new CTaskPrioritization();
        m_scalingSystem = new CScalingSystem();
        
        if(!m_preTradeSystem.Initialize() ||
           !m_monitoringSystem.Initialize() ||
           !m_taskSystem.Initialize() ||
           !m_scalingSystem.Initialize(1.0)) { // Volume máximo inicial de 1.0
            return false;
        }
        
        return true;
    }
    
    void ReleaseAgents() {
        // Liberar agentes principais
        delete m_quantumTrader;
        delete m_marketReader;
        delete m_riskGuardian;
        
        // Liberar agentes de análise
        delete m_statisticalAgent;
        delete m_quantumAgent;
        delete m_cyclicAgent;
        
        // Liberar sistema de treinamento
        delete m_fewShotSystem;
        
        // Liberar sistemas de suporte
        delete m_preTradeSystem;
        delete m_monitoringSystem;
        delete m_taskSystem;
        delete m_scalingSystem;
    }
    
    void SynthesizeDecisions() {
        // Obter decisões dos agentes
        double statisticalDecision = m_statisticalAgent.GetDecision();
        double quantumDecision = m_quantumAgent.GetDecision();
        double cyclicDecision = m_cyclicAgent.GetDecision();
        
        // Calcular pesos baseados na confiança
        double totalConfidence = 0.0;
        double statisticalConfidence = m_statisticalAgent.GetConfidence();
        double quantumConfidence = m_quantumAgent.GetConfidence();
        double cyclicConfidence = m_cyclicAgent.GetConfidence();
        
        totalConfidence = statisticalConfidence + quantumConfidence + cyclicConfidence;
        
        if(totalConfidence > 0) {
            m_lastDecision.statisticalWeight = statisticalConfidence / totalConfidence;
            m_lastDecision.quantumWeight = quantumConfidence / totalConfidence;
            m_lastDecision.cyclicWeight = cyclicConfidence / totalConfidence;
        } else {
            m_lastDecision.statisticalWeight = 0.33;
            m_lastDecision.quantumWeight = 0.33;
            m_lastDecision.cyclicWeight = 0.34;
        }
        
        // Calcular decisão final
        m_lastDecision.finalDecision = 
            statisticalDecision * m_lastDecision.statisticalWeight +
            quantumDecision * m_lastDecision.quantumWeight +
            cyclicDecision * m_lastDecision.cyclicWeight;
            
        m_lastDecision.timestamp = TimeCurrent();
    }
    
public:
    // Construtor
    CAgentIntegrationSystem() {
        m_isInitialized = false;
    }
    
    // Destrutor
    ~CAgentIntegrationSystem() {
        ReleaseAgents();
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return true;
        
        if(!InitializeAgents()) {
            ReleaseAgents();
            return false;
        }
        
        m_isInitialized = true;
        return true;
    }
    
    // Atualização do sistema
    void Update(const double& price,
               const double& volume,
               const double& volatility,
               const double& currentBalance,
               const double& positionSize) {
        if(!m_isInitialized) return;
        
        // Atualizar agentes principais
        m_quantumTrader.Update(price, volume, volatility);
        m_marketReader.Update(price, volume);
        m_riskGuardian.Update(currentBalance, positionSize, volatility);
        
        // Atualizar agentes de análise
        m_statisticalAgent.ProcessData(price, volume, volatility);
        m_quantumAgent.ProcessData(price, volume);
        m_cyclicAgent.ProcessData(price);
        
        // Atualizar sistema de treinamento
        m_fewShotSystem.Train(price, volume, volatility);
        
        // Atualizar sistemas de suporte
        m_preTradeSystem.AnalyzePreTrade(price, volume, volatility);
        m_monitoringSystem.UpdateMetrics(0, 0, 0.0, 0.0, 0.0); // Atualizar com métricas reais
        m_scalingSystem.CalculateNextLevel(price, 1.0, ScalingLevel()); // Direção positiva
        
        // Sintetizar decisões
        SynthesizeDecisions();
    }
    
    // Obter decisão final
    IntegratedDecision GetFinalDecision() const {
        return m_lastDecision;
    }
    
    // Verificar saúde do sistema
    bool IsSystemHealthy() const {
        if(!m_isInitialized) return false;
        return m_monitoringSystem.IsSystemHealthy();
    }
    
    // Obter alertas do sistema
    void GetSystemAlerts(SystemAlert& alerts[]) {
        if(!m_isInitialized) return;
        m_monitoringSystem.GetActiveAlerts(alerts);
    }
    
    // Obter próximas tarefas
    void GetNextTasks(Task& tasks[]) {
        if(!m_isInitialized) return;
        m_taskSystem.GetPendingTasks(tasks);
    }
    
    // Obter níveis de escalonamento
    void GetScalingLevels(ScalingLevel& levels[]) {
        if(!m_isInitialized) return;
        m_scalingSystem.GetActiveLevels(levels);
    }
    
    // Métodos de acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 