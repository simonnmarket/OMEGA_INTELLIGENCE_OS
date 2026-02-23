//+------------------------------------------------------------------+
//|                                                TestMarketSignal.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Core/MarketSignal.mqh"
#include "Include/Core/SensorySystems.mqh"

// Instâncias para teste
CQuantumVisionSystem* Vision = NULL;
CMarketHearingSystem* Hearing = NULL;
CMarketTouchSystem* Touch = NULL;
CRiskSmellingSystem* Smell = NULL;
CMarketTasteSystem* Taste = NULL;
CSensoryIntegration* SensorySystem = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do MarketSignal...");
    
    // Inicializando os sistemas sensoriais
    Vision = new CQuantumVisionSystem();
    Hearing = new CMarketHearingSystem();
    Touch = new CMarketTouchSystem();
    Smell = new CRiskSmellingSystem();
    Taste = new CMarketTasteSystem();
    SensorySystem = new CSensoryIntegration();
    
    // Inicializando os sistemas
    if(!Vision.Initialize() || !Hearing.Initialize() || !Touch.Initialize() ||
       !Smell.Initialize() || !Taste.Initialize()) {
        Print("Erro na inicialização dos sistemas sensoriais");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Vision != NULL) { delete Vision; Vision = NULL; }
    if(Hearing != NULL) { delete Hearing; Hearing = NULL; }
    if(Touch != NULL) { delete Touch; Touch = NULL; }
    if(Smell != NULL) { delete Smell; Smell = NULL; }
    if(Taste != NULL) { delete Taste; Taste = NULL; }
    if(SensorySystem != NULL) { delete SensorySystem; SensorySystem = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Processando cada sistema sensorial
    Vision.Process();
    Hearing.Process();
    Touch.Process();
    Smell.Process();
    Taste.Process();
    
    // Integrando as percepções
    SensorySystem.ProcessSensoryInput(Vision, Hearing, Touch, Smell, Taste);
    IntegratedSensoryData perception = SensorySystem.GetCurrentPerception();
    
    // Exibindo resultados
    Print("=== Teste MarketSignal ===");
    Print("Confiança Visual: ", perception.visualConfidence);
    Print("Confiança Auditiva: ", perception.auditoryConfidence);
    Print("Confiança Tátil: ", perception.tactileConfidence);
    Print("Confiança Olfativa: ", perception.olfactoryConfidence);
    Print("Confiança Gustativa: ", perception.gustatoryConfidence);
    Print("Percepção Geral: ", perception.overallPerception);
    Print("Coerência Sensorial: ", perception.sensoryCoherence);
    Print("Força do Mercado: ", perception.marketStrength);
    Print("Força da Tendência: ", perception.trendStrength);
    Print("Força Gravitacional: ", perception.gravForce);
    Print("Fator de Rotação: ", perception.rotationFactor);
} 