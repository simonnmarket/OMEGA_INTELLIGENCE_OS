#property copyright "Integration Manager System"
#property strict

#include "RiskManager.mqh"
#include "MarketAnalysis.mqh"
#include "PositionManager.mqh"

class CIntegrationManager {
private:
    CRiskManager* riskManager;
    CMarketAnalysis* marketAnalysis;
    CPositionManager* positionManager;
    
    // Configurações
    double minConfidence;
    double minVolume;
    int maxPositions;
    
    // Estado
    bool isInitialized;
    datetime lastAnalysisTime;
    
public:
    CIntegrationManager() {
        riskManager = new CRiskManager();
        marketAnalysis = new CMarketAnalysis();
        positionManager = new CPositionManager();
        
        minConfidence = 0.7;
        minVolume = 1.0;
        maxPositions = 3;
        
        isInitialized = false;
        lastAnalysisTime = 0;
    }
    
    ~CIntegrationManager() {
        delete riskManager;
        delete marketAnalysis;
        delete positionManager;
    }
    
    bool Initialize() {
        if(!riskManager.Initialize()) {
            Print("Erro ao inicializar Risk Manager");
            return false;
        }
        
        if(!marketAnalysis.Initialize()) {
            Print("Erro ao inicializar Market Analysis");
            return false;
        }
        
        isInitialized = true;
        Print("Sistema integrado inicializado com sucesso");
        return true;
    }
    
    void Process() {
        if(!isInitialized) {
            Print("Sistema não inicializado");
            return;
        }
        
        // Verifica se é hora de fazer nova análise
        datetime currentTime = TimeCurrent();
        if(currentTime - lastAnalysisTime < 60) { // Analisa a cada minuto
            return;
        }
        lastAnalysisTime = currentTime;
        
        // Processa análise de mercado
        marketAnalysis.Process();
        
        // Verifica condições de entrada
        if(CheckEntryConditions()) {
            // Calcula tamanho da posição
            double lotSize = riskManager.CalculatePositionSize();
            
            // Determina direção da posição
            ENUM_POSITION_TYPE posType = DeterminePositionType();
            
            // Abre posição
            if(posType != WRONG_VALUE) {
                positionManager.OpenPosition(posType, lotSize);
            }
        }
        
        // Gerencia posições abertas
        ManageOpenPositions();
    }
    
    bool CheckEntryConditions() {
        // Verifica número máximo de posições
        if(riskManager.GetOpenPositionsCount() >= maxPositions) {
            return false;
        }
        
        // Verifica confiança mínima
        if(marketAnalysis.GetConfidence() < minConfidence) {
            return false;
        }
        
        // Verifica volume mínimo
        if(marketAnalysis.GetVolume() < minVolume) {
            return false;
        }
        
        // Verifica condições de risco
        if(!riskManager.IsTradeAllowed()) {
            return false;
        }
        
        return true;
    }
    
    ENUM_POSITION_TYPE DeterminePositionType() {
        double trendStrength = marketAnalysis.GetTrendStrength();
        double momentum = marketAnalysis.GetMomentum();
        double volatility = marketAnalysis.GetVolatility();
        
        // Lógica de decisão baseada em múltiplos fatores
        if(trendStrength > 0.7 && momentum > 0.6 && volatility < 0.3) {
            return POSITION_TYPE_BUY;
        }
        else if(trendStrength < -0.7 && momentum < -0.6 && volatility < 0.3) {
            return POSITION_TYPE_SELL;
        }
        
        return WRONG_VALUE;
    }
    
    void ManageOpenPositions() {
        // Atualiza trailing stops e break even
        positionManager.ManagePosition();
        
        // Verifica drawdown e outras métricas de risco
        riskManager.CheckRiskMetrics();
    }
    
    void PrintStatus() {
        if(!isInitialized) {
            Print("Sistema não inicializado");
            return;
        }
        
        Print("\n=== Status do Sistema Integrado ===");
        Print("Posições Abertas: ", riskManager.GetOpenPositionsCount());
        Print("Confiança: ", marketAnalysis.GetConfidence());
        Print("Volume: ", marketAnalysis.GetVolume());
        Print("Drawdown: ", riskManager.GetDrawdown());
        Print("Equity: ", riskManager.GetEquity());
        Print("===============================\n");
    }
}; 