#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Incluir arquivo do EA
#include "SkylerEA.mqh"

// Variáveis globais
CSkylerEA* g_skylerEA = NULL;

// Parâmetros de entrada
input double InpMaxRiskPerTrade = 0.02;    // Risco Máximo por Operação (%)
input double InpMaxDailyLoss = 0.05;       // Perda Máxima Diária (%)
input int InpLeverage = 500;               // Alavancagem
input int InpRSIPeriod = 14;               // Período do RSI
input int InpMACDFastPeriod = 12;          // Período Rápido do MACD
input int InpMACDSlowPeriod = 26;          // Período Lento do MACD
input int InpMACDSignalPeriod = 9;         // Período do Sinal do MACD
input int InpBBPeriod = 20;                // Período das Bandas de Bollinger
input double InpBBDeviation = 2.0;         // Desvio Padrão das Bandas
input double InpInitialCapital = 100.0;    // Capital Inicial (EUR)
input double InpMaxPositionSize = 0.02;    // Tamanho Máximo da Posição (%)

// Função de inicialização
int OnInit() {
    // Criar instância do EA
    g_skylerEA = new CSkylerEA();
    
    // Configurar parâmetros
    EASettings settings;
    settings.maxRiskPerTrade = InpMaxRiskPerTrade;
    settings.maxDailyLoss = InpMaxDailyLoss;
    settings.leverage = InpLeverage;
    settings.rsiPeriod = InpRSIPeriod;
    settings.macdFastPeriod = InpMACDFastPeriod;
    settings.macdSlowPeriod = InpMACDSlowPeriod;
    settings.macdSignalPeriod = InpMACDSignalPeriod;
    settings.bbPeriod = InpBBPeriod;
    settings.bbDeviation = InpBBDeviation;
    settings.initialCapital = InpInitialCapital;
    settings.maxPositionSize = InpMaxPositionSize;
    
    g_skylerEA.SetSettings(settings);
    
    // Inicializar EA
    if(!g_skylerEA.Initialize()) {
        Print("Erro ao inicializar EA");
        return INIT_FAILED;
    }
    
    // Configurar alavancagem
    if(!AccountInfoInteger(ACCOUNT_LEVERAGE) == InpLeverage) {
        Print("Aviso: Alavancagem da conta diferente da configurada");
    }
    
    return INIT_SUCCEEDED;
}

// Função de desinicialização
void OnDeinit(const int reason) {
    if(g_skylerEA != NULL) {
        delete g_skylerEA;
        g_skylerEA = NULL;
    }
}

// Função de tick
void OnTick() {
    if(g_skylerEA != NULL) {
        g_skylerEA.OnTick();
    }
}

// Função de trade
void OnTrade() {
    if(g_skylerEA != NULL) {
        g_skylerEA.OnTrade();
    }
}

// Função de timer
void OnTimer() {
    // Atualizar eventos econômicos a cada minuto
    if(g_skylerEA != NULL) {
        // TODO: Implementar atualização de eventos econômicos
    }
} 