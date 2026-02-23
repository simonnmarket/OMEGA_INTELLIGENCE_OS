//+------------------------------------------------------------------+
//|                                        TestInstitutionalRadar.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Detectors/InstitutionalRadar.mqh"

// Instância para teste
CInstitutionalRadar* Radar = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do InstitutionalRadar...");
    
    // Inicializando o radar institucional
    Radar = new CInstitutionalRadar();
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Radar != NULL) { delete Radar; Radar = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Detectando atividade institucional
    bool hasInstitutionalActivity = Radar.DetectInstitutionalActivity();
    
    // Exibindo resultados
    Print("=== Teste InstitutionalRadar ===");
    Print("Atividade Institucional Detectada: ", hasInstitutionalActivity ? "Sim" : "Não");
    Print("Volume Atividade: ", Radar.GetVolumeActivity());
    Print("Impacto de Preço: ", Radar.GetPriceImpact());
    Print("Período de Análise: ", Radar.GetLookbackPeriod());
} 