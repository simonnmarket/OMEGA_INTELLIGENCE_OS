//+------------------------------------------------------------------+
//|                                         EA_RaioX_Universal.mq5 |
//|                                    Sistema Universal de Análise |
//|                                           RaioX Trading System |
//+------------------------------------------------------------------+
#property copyright "RaioX Trading System"
#property link      ""
#property version   "1.0"

// Inclusão dos módulos
#include <Trade\Trade.mqh>
#include "..\Include\Core\MarketCore.mqh"
#include "..\Include\Physics\QuantumMarket.mqh"
#include "..\Include\Analysis\WaveAnalysis.mqh"
#include "..\Include\Analysis\VolumeAnalysis.mqh"
#include "..\Include\Risk\RiskManager.mqh"
#include "..\Include\Utils\MarketUtils.mqh"
#include "..\Include\Detectors\VolumeDetector.mqh"
#include "..\Include\Detectors\WaveDetector.mqh"
#include "..\Include\Detectors\PatternDetector.mqh"

// Objetos globais
CTrade          trade;
CRiskManager    riskManager;
CMarketUtils    marketUtils;
CVolumeAnalyzer volumeAnalyzer;
CWaveAnalyzer   waveAnalyzer;
CQuantumAnalyzer quantumAnalyzer;
CVolumeDetector volumeDetector;
CWaveDetector   waveDetector;
CPatternDetector patternDetector;
CLogger         logger;

// Buffers para dados de mercado
double priceBuffer[];
long volumeBuffer[];

// Parâmetros de entrada
input double   InpInitialLots = 0.1;      // Lote inicial
input double   InpMaxLots = 1.0;          // Lote máximo
input int      InpScalingSteps = 3;       // Passos de escalonamento
input double   InpMaxRiskPercent = 2.0;   // Risco máximo por operação (%)
input int      InpATRPeriod = 14;         // Período do ATR
input double   InpATRMultiplier = 1.5;    // Multiplicador do ATR
input bool     InpEnableQuantum = true;   // Habilitar análise quântica
input bool     InpDebugMode = false;      // Modo debug

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    // Inicializa arrays
    ArraySetAsSeries(priceBuffer, true);
    ArraySetAsSeries(volumeBuffer, true);
    
    // Inicializa logger
    logger.Initialize(InpDebugMode);
    logger.Log("Iniciando EA RaioX Universal...");
    
    // Inicializa gerenciador de risco
    if(!riskManager.Initialize(InpInitialLots, InpMaxLots, InpScalingSteps, 
                             InpMaxRiskPercent, InpATRPeriod, InpATRMultiplier)) {
        logger.LogError("Erro ao inicializar gerenciador de risco");
        return INIT_FAILED;
    }
    
    // Inicializa utilidades de mercado
    if(!marketUtils.Initialize(InpATRPeriod)) {
        logger.LogError("Erro ao inicializar utilidades de mercado");
        return INIT_FAILED;
    }
    
    // Inicializa analisadores
    if(!InitializeAnalyzers()) {
        logger.LogError("Erro ao inicializar analisadores");
        return INIT_FAILED;
    }
    
    // Inicializa detectores
    if(!InitializeDetectors()) {
        logger.LogError("Erro ao inicializar detectores");
        return INIT_FAILED;
    }
    
    logger.Log("EA inicializado com sucesso");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    logger.Log("EA finalizado. Razão: " + string(reason));
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Atualiza dados de mercado
    if(!UpdateMarketData()) {
        logger.LogError("Erro ao atualizar dados de mercado");
        return;
    }
    
    // Converte volume para double para análise
    double volumeDoubleBuffer[];
    ArrayResize(volumeDoubleBuffer, ArraySize(volumeBuffer));
    for(int i = 0; i < ArraySize(volumeBuffer); i++) {
        volumeDoubleBuffer[i] = (double)volumeBuffer[i];
    }
    
    // Analisa mercado
    AnalyzeMarket(volumeDoubleBuffer);
    
    // Gerencia posições existentes
    ManagePositions();
    
    // Verifica novas oportunidades
    if(CanOpenNewPosition()) {
        CheckNewTradeOpportunities(volumeDoubleBuffer);
    }
}

//+------------------------------------------------------------------+
//| Funções auxiliares                                              |
//+------------------------------------------------------------------+
bool InitializeAnalyzers() {
    if(!volumeAnalyzer.Initialize(InpATRPeriod)) {
        logger.LogError("Erro ao inicializar analisador de volume");
        return false;
    }
    
    if(!waveAnalyzer.Initialize(InpATRPeriod)) {
        logger.LogError("Erro ao inicializar analisador de ondas");
        return false;
    }
    
    if(InpEnableQuantum) {
        if(!quantumAnalyzer.Initialize(InpATRPeriod)) {
            logger.LogError("Erro ao inicializar analisador quântico");
            return false;
        }
    }
    
    return true;
}

bool InitializeDetectors() {
    if(!volumeDetector.Initialize(20, 1.5)) {
        logger.LogError("Erro ao inicializar detector de volume");
        return false;
    }
    
    if(!waveDetector.Initialize(20, 5.0)) {
        logger.LogError("Erro ao inicializar detector de ondas");
        return false;
    }
    
    if(!patternDetector.Initialize(20, 0.5, 0.7)) {
        logger.LogError("Erro ao inicializar detector de padrões");
        return false;
    }
    
    return true;
}

bool UpdateMarketData() {
    if(CopyClose(_Symbol, PERIOD_CURRENT, 0, 50, priceBuffer) <= 0) {
        logger.LogError("Erro ao copiar preços");
        return false;
    }
        
    if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, 50, volumeBuffer) <= 0) {
        logger.LogError("Erro ao copiar volumes");
        return false;
    }
        
    return true;
}

void AnalyzeMarket(const double &volumes[]) {
    // Análise de volume
    VolumeProfile volProfile = volumeAnalyzer.AnalyzeVolume(priceBuffer, volumes);
    
    // Análise de ondas
    WaveData waveData = waveAnalyzer.AnalyzeWaves(priceBuffer, volumes);
    
    // Análise quântica
    if(InpEnableQuantum) {
        QuantumState qState = quantumAnalyzer.AnalyzeMarket(priceBuffer, volumes);
        if(qState.isSingularity) {
            logger.Log("Singularidade detectada!");
        }
    }
    
    // Análise de força do mercado
    MarketStrength strength = marketUtils.AnalyzeStrength(priceBuffer, volumes);
    
    // Log de análises importantes
    if(InpDebugMode) {
        LogMarketAnalysis(volProfile, waveData, strength);
    }
}

void ManagePositions() {
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(ticket <= 0) continue;
        
        if(PositionGetString(POSITION_SYMBOL) == _Symbol) {
            // Atualiza stops dinâmicos
            riskManager.UpdateDynamicStops(ticket);
            
            // Verifica condições de saída
            CheckExitConditions(ticket);
        }
    }
}

void CheckExitConditions(const ulong ticket) {
    if(!PositionSelectByTicket(ticket))
        return;
        
    bool isLong = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
    double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);
    double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
    
    // Converte volume para double para análise
    double volumeDoubleBuffer[];
    ArrayResize(volumeDoubleBuffer, ArraySize(volumeBuffer));
    for(int i = 0; i < ArraySize(volumeBuffer); i++) {
        volumeDoubleBuffer[i] = (double)volumeBuffer[i];
    }
    
    // Verifica sinais dos detectores
    VolumeSignal volSignal = volumeDetector.Analyze(volumeDoubleBuffer, priceBuffer);
    WaveSignal waveSignal = waveDetector.Analyze(priceBuffer, volumeDoubleBuffer);
    
    // Condições de saída baseadas em sinais
    if((isLong && volSignal.isDistribution) || (!isLong && volSignal.isAbsorption)) {
        if(waveSignal.strength > 0.7) {
            trade.PositionClose(ticket);
            logger.Log("Posição fechada por sinal de volume e onda");
        }
    }
}

bool CanOpenNewPosition() {
    return PositionsTotal() < InpScalingSteps;
}

void CheckNewTradeOpportunities(const double &volumes[]) {
    // Analisa sinais dos detectores
    VolumeSignal volSignal = volumeDetector.Analyze(volumes, priceBuffer);
    WaveSignal waveSignal = waveDetector.Analyze(priceBuffer, volumes);
    PatternSignal patternSignal = patternDetector.Analyze(priceBuffer, volumes);
    
    // Verifica condições de entrada
    if(patternSignal.isValid && patternSignal.reliability >= 0.8) {
        if(volSignal.isValid && waveSignal.isValid) {
            ExecuteNewPosition(patternSignal, volSignal, waveSignal);
        }
    }
}

void ExecuteNewPosition(const PatternSignal &pattern, const VolumeSignal &volume, const WaveSignal &wave) {
    double stopLoss = riskManager.CalculateATRStop(pattern.targetPrice > SymbolInfoDouble(_Symbol, SYMBOL_ASK));
    if(stopLoss == 0) return;
    
    double lots = riskManager.CalculatePositionSize(MathAbs(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - stopLoss));
    if(lots <= 0) return;
    
    ENUM_ORDER_TYPE orderType = pattern.targetPrice > SymbolInfoDouble(_Symbol, SYMBOL_ASK) ? 
                               ORDER_TYPE_BUY : ORDER_TYPE_SELL;
                               
    double price = orderType == ORDER_TYPE_BUY ? 
                  SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                  SymbolInfoDouble(_Symbol, SYMBOL_BID);
                  
    if(trade.PositionOpen(_Symbol, orderType, lots, price, stopLoss, pattern.targetPrice)) {
        logger.Log(StringFormat("Nova posição aberta: %s %.2f lotes", 
                              EnumToString(orderType), lots));
    }
}

void LogMarketAnalysis(const VolumeProfile &vol, const WaveData &wave, const MarketStrength &strength) {
    string analysis = StringFormat(
        "Análise de Mercado:\n" +
        "Volume Force: %.2f\n" +
        "Wave Strength: %.2f\n" +
        "Market Strength: %.2f\n" +
        "Momentum: %.2f",
        vol.volumeForce,
        wave.strength,
        strength.netStrength,
        strength.momentum
    );
    
    logger.Log(analysis);
}