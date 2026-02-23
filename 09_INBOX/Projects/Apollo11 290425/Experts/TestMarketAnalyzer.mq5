//+------------------------------------------------------------------+
//|                                          TestMarketAnalyzer.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "Include/Analysis/MarketAnalyzer.mqh"

// Instância para teste
CMarketAnalyzer* Market = NULL;

// Função de inicialização
int OnInit() {
    Print("Iniciando teste do MarketAnalyzer...");
    
    // Inicializando o analisador de mercado
    Market = new CMarketAnalyzer();
    
    // Configurando parâmetros de análise
    Market.SetTimeframe(PERIOD_CURRENT);
    Market.SetLookbackPeriod(20);
    
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Market != NULL) { delete Market; Market = NULL; }
}

// Função principal de teste
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Testando funções de análise de mercado
    double trend = Market.AnalyzeTrend();
    double volatility = Market.CalculateVolatility();
    double momentum = Market.CalculateMomentum();
    double volume = Market.AnalyzeVolume();
    double support = Market.FindSupport();
    double resistance = Market.FindResistance();
    
    // Exibindo resultados
    Print("=== Teste MarketAnalyzer ===");
    Print("Tendência: ", trend);
    Print("Volatilidade: ", volatility);
    Print("Momentum: ", momentum);
    Print("Volume: ", volume);
    Print("Suporte: ", support);
    Print("Resistência: ", resistance);
    Print("Estado do Mercado: ", Market.GetMarketState());
    Print("Força da Tendência: ", Market.GetTrendStrength());
} 