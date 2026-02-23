//+------------------------------------------------------------------+
//|                                          TestPhysicsEngine.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Physics/PhysicsEngine.mqh"

// Instância para teste
CPhysicsEngine* Physics = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do PhysicsEngine...");
    
    // Inicializando o motor de física
    Physics = new CPhysicsEngine();
    
    if(!Physics.Initialize()) {
        Print("Erro na inicialização do PhysicsEngine");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Physics != NULL) { delete Physics; Physics = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Processando simulação física
    Physics.Process();
    
    // Exibindo resultados
    Print("=== Teste PhysicsEngine ===");
    Print("Força Resultante: ", Physics.GetResultantForce());
    Print("Momento Linear: ", Physics.GetLinearMomentum());
    Print("Momento Angular: ", Physics.GetAngularMomentum());
    Print("Energia Cinética: ", Physics.GetKineticEnergy());
    Print("Energia Potencial: ", Physics.GetPotentialEnergy());
    Print("Energia Total: ", Physics.GetTotalEnergy());
    Print("Torque: ", Physics.GetTorque());
    Print("Inércia: ", Physics.GetInertia());
    Print("Centro de Massa: ", Physics.GetCenterOfMass());
    Print("Estado Quântico: ", Physics.GetQuantumState());
} 