//+------------------------------------------------------------------+
//|                                            TestRiskManager.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Risk/RiskManager.mqh"

// Instância para teste
CRiskManager* Risk = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do RiskManager...");
    
    // Inicializando o gerenciador de risco
    Risk = new CRiskManager();
    
    // Configurando parâmetros de risco
    Risk.SetMaxRiskPercent(2.0);
    Risk.SetMaxDrawdown(10.0);
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Risk != NULL) { delete Risk; Risk = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Testando funções de gerenciamento de risco
    double lotSize = Risk.CalculatePositionSize();
    bool canOpen = Risk.CanOpenPosition();
    double stopLoss = Risk.CalculateStopLoss();
    double takeProfit = Risk.CalculateTakeProfit();
    
    // Exibindo resultados
    Print("=== Teste RiskManager ===");
    Print("Tamanho do lote calculado: ", lotSize);
    Print("Pode abrir posição: ", canOpen);
    Print("Stop Loss calculado: ", stopLoss);
    Print("Take Profit calculado: ", takeProfit);
    Print("Risco atual: ", Risk.GetCurrentRisk());
    Print("Drawdown atual: ", Risk.GetCurrentDrawdown());
} 