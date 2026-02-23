//+------------------------------------------------------------------+
//|                                      TestTrajectoryAnalyzer.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Analysis/TrajectoryAnalyzer.mqh"

// Instância para teste
CTrajectoryAnalyzer* Trajectory = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do TrajectoryAnalyzer...");
    
    // Inicializando o analisador de trajetória
    Trajectory = new CTrajectoryAnalyzer();
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Trajectory != NULL) { delete Trajectory; Trajectory = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Analisando a trajetória
    Trajectory.AnalyzeTrajectory();
    
    // Exibindo resultados
    Print("=== Teste TrajectoryAnalyzer ===");
    Print("Direção: ", Trajectory.GetDirection());
    Print("Velocidade: ", Trajectory.GetVelocity());
    Print("Aceleração: ", Trajectory.GetAcceleration());
    Print("Inércia: ", Trajectory.GetInertia());
    Print("Resistência: ", Trajectory.GetResistance());
    Print("Momento: ", Trajectory.GetMomentum());
    Print("Energia: ", Trajectory.GetEnergy());
    Print("Estabilidade: ", Trajectory.GetStability());
} 