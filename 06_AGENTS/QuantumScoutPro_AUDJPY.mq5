//+------------------------------------------------------------------+
//|                                    QuantumScoutPro_v2.1.mq5        |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Systems"
#property version   "2.1"
#property strict

// Includes necessários
#include <Trade\Trade.mqh>
#include <Object.mqh>
#include "Indicators/MarketProfile.mqh"
#include "Indicators/OrderFlow.mqh"
#include "Indicators/VolumeAnalysis.mqh"
#include "Strategies/SatoStrategy.mqh"
#include "Strategies/TradingNutStrategy.mqh"
#include "Strategies/HybridStrategy.mqh"
#include "Core/RiskManager.mqh"
#include "Core/SignalGenerator.mqh"
#include "Core/PositionManager.mqh"
#include "Utils/Reporter.mqh"
#include "Utils/Optimizer.mqh"
#include "Utils/Monitor.mqh"

// Enums
enum ENUM_STRATEGY_TYPE {
    STRAT_SATO,
    STRAT_TRADINGNUT,
    STRAT_HYBRID
};

enum ENUM_MARKET_STATE {
    STATE_TRENDING,
    STATE_RANGING,
    STATE_VOLATILE,
    STATE_UNDEFINED
};

// Inputs
input group "Configurações Gerais"
input ENUM_STRATEGY_TYPE StrategyType = STRAT_HYBRID;    // Tipo de Estratégia
input int    TimeframeMin     = 5;                       // Timeframe (minutos)
input double RiskPercent      = 1.0;                     // Risco por operação (%)
input int    MaxDailyTrades   = 3;                       // Máximo trades diários

input group "Filtros de Volume"
input double VolumeThreshold  = 1.5;                     // Multiplicador de Volume
input int    VolumePeriod     = 20;                      // Período Volume Médio

input group "Configurações de Stop"
input int    StopLoss         = 400;                     // Stop Loss (pontos)
input int    TakeProfit       = 800;                     // Take Profit (pontos)
input bool   UseBreakEven     = true;                    // Usar Break Even
input int    BreakEvenPoints  = 300;                     // Pontos para Break Even

input group "Configurações Avançadas"
input bool   UseMarketProfile = true;                    // Usar Market Profile
input bool   UseOrderFlow     = true;                    // Usar Order Flow
input bool   UseVolumeAnalysis = true;                   // Usar Volume Analysis
input bool   UseOptimizer     = true;                    // Usar Otimizador
input bool   UseReporter      = true;                    // Usar Reporter
//+------------------------------------------------------------------+
//| Estruturas e Classes Principais                                    |
//+------------------------------------------------------------------+

// Estrutura de Setup
struct TradeSetup {
    double entry;
    double stopLoss;
    double takeProfit;
    double volume;
    ENUM_MARKET_STATE state;
    bool isValid;
    string strategy;
    double confidence;
    datetime signalTime;
};

// Estrutura de Análise de Mercado
struct MarketAnalysis {
    // Market Profile
    double valueAreaHigh;
    double valueAreaLow;
    double poc;
    bool isBalanced;
    
    // Order Flow
    double buyingPressure;
    double sellingPressure;
    double delta;
    bool hasImbalance;
    
    // Volume
    double relativeVolume;
    double volumeDelta;
    bool isVolumeValid;
    
    // Estado Geral
    ENUM_MARKET_STATE state;
    double trend;
    double momentum;
    double volatility;
};

// Classe Principal do Sistema
class CQuantumScoutPro {
private:
    // Objetos principais
    CTrade trade;
    CMarketProfile* marketProfile;
    COrderFlow* orderFlow;
    CVolumeAnalysis* volumeAnalysis;
    
    // Estratégias
    CSatoStrategy* satoStrategy;
    CTradingNutStrategy* tradingNutStrategy;
    CHybridStrategy* hybridStrategy;
    
    // Gerenciadores
    CRiskManager* riskManager;
    CSignalGenerator* signalGenerator;
    CPositionManager* positionManager;
    
    // Utilidades
    CReporter* reporter;
    COptimizer* optimizer;
    CMonitor* monitor;
    
    // Dados de mercado
    MarketAnalysis marketData;
    TradeSetup currentSetup;
    
    // Handles de indicadores
    int maHandle;
    int volumeHandle;
    int atrHandle;
    
    // Buffers
    double maBuffer[];
    double volumeBuffer[];
    double atrBuffer[];
    
public:
    // Construtor
    CQuantumScoutPro() {
        InitializeComponents();
    }
    
    // Destrutor
    ~CQuantumScoutPro() {
        CleanupComponents();
    }
    
    // Inicialização
    bool Initialize() {
        if(!InitializeIndicators()) return false;
        if(!InitializeStrategies()) return false;
        if(!InitializeManagers()) return false;
        
        return true;
    }
    
    // Processamento principal
    void ProcessTick() {
        if(!IsMarketReady()) return;
        
        UpdateMarketData();
        
        if(CanTrade()) {
            AnalyzeMarket();
            GenerateSignals();
            ExecuteTrades();
        }
        
        ManagePositions();
        UpdateReports();
        OptimizeSystem();
    }
    
private:
    // Inicialização de componentes
    void InitializeComponents() {
        marketProfile = new CMarketProfile();
        orderFlow = new COrderFlow();
        volumeAnalysis = new CVolumeAnalysis();
        
        satoStrategy = new CSatoStrategy();
        tradingNutStrategy = new CTradingNutStrategy();
        hybridStrategy = new CHybridStrategy();
        
        riskManager = new CRiskManager();
        signalGenerator = new CSignalGenerator();
        positionManager = new CPositionManager();
        
        reporter = new CReporter();
        optimizer = new COptimizer();
        monitor = new CMonitor();
    }
    
    // Limpeza de componentes
    void CleanupComponents() {
        delete marketProfile;
        delete orderFlow;
        delete volumeAnalysis;
        
        delete satoStrategy;
        delete tradingNutStrategy;
        delete hybridStrategy;
        
        delete riskManager;
        delete signalGenerator;
        delete positionManager;
        
        delete reporter;
        delete optimizer;
        delete monitor;
    }
    // Inicialização de indicadores
    bool InitializeIndicators() {
        // Handles principais
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_EMA, PRICE_CLOSE);
        volumeHandle = iVolumes(_Symbol, PERIOD_CURRENT, VOLUME_TICK);
        atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
        
        if(maHandle == INVALID_HANDLE || volumeHandle == INVALID_HANDLE || atrHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores!");
            return false;
        }
        
        // Inicializar buffers
        ArraySetAsSeries(maBuffer, true);
        ArraySetAsSeries(volumeBuffer, true);
        ArraySetAsSeries(atrBuffer, true);
        
        // Inicializar componentes avançados
        if(UseMarketProfile && !marketProfile.Initialize()) return false;
        if(UseOrderFlow && !orderFlow.Initialize()) return false;
        if(UseVolumeAnalysis && !volumeAnalysis.Initialize()) return false;
        
        return true;
    }
    
    // Inicialização de estratégias
    bool InitializeStrategies() {
        switch(StrategyType) {
            case STRAT_SATO:
                if(!satoStrategy.Initialize()) return false;
                break;
                
            case STRAT_TRADINGNUT:
                if(!tradingNutStrategy.Initialize()) return false;
                break;
                
            case STRAT_HYBRID:
                if(!hybridStrategy.Initialize()) return false;
                break;
        }
        
        return true;
    }
    
    // Inicialização de gerenciadores
    bool InitializeManagers() {
        if(!riskManager.Initialize(RiskPercent, MaxDailyTrades)) return false;
        if(!signalGenerator.Initialize()) return false;
        if(!positionManager.Initialize(UseBreakEven, BreakEvenPoints)) return false;
        
        if(UseReporter && !reporter.Initialize()) return false;
        if(UseOptimizer && !optimizer.Initialize()) return false;
        
        return true;
    }
    
    // Atualização de dados de mercado
    void UpdateMarketData() {
        // Atualizar buffers
        CopyBuffer(maHandle, 0, 0, 3, maBuffer);
        CopyBuffer(volumeHandle, 0, 0, 3, volumeBuffer);
        CopyBuffer(atrHandle, 0, 0, 3, atrBuffer);
        
        // Atualizar Market Profile
        if(UseMarketProfile) {
            marketProfile.Update();
            marketData.valueAreaHigh = marketProfile.GetValueAreaHigh();
            marketData.valueAreaLow = marketProfile.GetValueAreaLow();
            marketData.poc = marketProfile.GetPOC();
            marketData.isBalanced = marketProfile.IsBalanced();
        }
        
        // Atualizar Order Flow
        if(UseOrderFlow) {
            orderFlow.Update();
            marketData.buyingPressure = orderFlow.GetBuyingPressure();
            marketData.sellingPressure = orderFlow.GetSellingPressure();
            marketData.delta = orderFlow.GetDelta();
            marketData.hasImbalance = orderFlow.HasImbalance();
        }
        
        // Atualizar Volume Analysis
        if(UseVolumeAnalysis) {
            volumeAnalysis.Update();
            marketData.relativeVolume = volumeAnalysis.GetRelativeVolume();
            marketData.volumeDelta = volumeAnalysis.GetVolumeDelta();
            marketData.isVolumeValid = volumeAnalysis.IsVolumeValid();
        }
        
        // Atualizar estado geral do mercado
        UpdateMarketState();
    }
    
    // Análise de mercado
    void AnalyzeMarket() {
        switch(StrategyType) {
            case STRAT_SATO:
                currentSetup = satoStrategy.Analyze(marketData);
                break;
                
            case STRAT_TRADINGNUT:
                currentSetup = tradingNutStrategy.Analyze(marketData);
                break;
                
            case STRAT_HYBRID:
                currentSetup = hybridStrategy.Analyze(marketData);
                break;
        }
    }
    // Geração de sinais
    void GenerateSignals() {
        if(!currentSetup.isValid) return;
        
        // Validar setup com gerenciador de sinais
        if(!signalGenerator.ValidateSignal(currentSetup)) {
            currentSetup.isValid = false;
            return;
        }
        
        // Validar risco
        if(!riskManager.ValidateRisk(currentSetup)) {
            currentSetup.isValid = false;
            return;
        }
        
        // Calcular volume final
        currentSetup.volume = riskManager.CalculatePosition(currentSetup);
    }
    
    // Execução de trades
    void ExecuteTrades() {
        if(!currentSetup.isValid) return;
        
        // Executar ordem
        bool result = trade.Buy(
            currentSetup.volume,
            _Symbol,
            currentSetup.entry,
            currentSetup.stopLoss,
            currentSetup.takeProfit,
            "Quantum Scout Pro v2.1 - " + currentSetup.strategy
        );
        
        // Registrar resultado
        if(result) {
            monitor.RegisterTrade(currentSetup);
            reporter.UpdateStats(currentSetup);
        }
    }
    
    // Gestão de posições
    void ManagePositions() {
        if(!PositionSelect(_Symbol)) return;
        
        // Atualizar stops
        positionManager.UpdateStops();
        
        // Verificar break even
        if(UseBreakEven) {
            positionManager.CheckBreakEven();
        }
        
        // Trailing stop
        positionManager.UpdateTrailingStop();
    }
    
    // Atualização de relatórios
    void UpdateReports() {
        if(!UseReporter) return;
        
        reporter.UpdatePerformance();
        reporter.GenerateReport();
        
        if(reporter.ShouldSendReport()) {
            reporter.SendReport();
        }
    }
    
    // Otimização do sistema
    void OptimizeSystem() {
        if(!UseOptimizer) return;
        
        if(optimizer.ShouldOptimize()) {
            optimizer.OptimizeParameters();
            optimizer.ApplyOptimization();
        }
    }
    
    // Validação de mercado
    bool IsMarketReady() {
        if(!IsMarketOpen()) return false;
        if(IsHighSpread()) return false;
        if(!HasSufficientVolume()) return false;
        
        return true;
    }
    
    // Verificação de trading
    bool CanTrade() {
        if(PositionsTotal() >= MaxDailyTrades) return false;
        if(!riskManager.CheckDailyLimit()) return false;
        return true;
    }
    
    // Atualização do estado do mercado
    void UpdateMarketState() {
        if(IsTrending()) {
            marketData.state = STATE_TRENDING;
        }
        else if(IsRanging()) {
            marketData.state = STATE_RANGING;
        }
        else if(IsVolatile()) {
            marketData.state = STATE_VOLATILE;
        }
        else {
            marketData.state = STATE_UNDEFINED;
        }
        
        marketData.trend = CalculateTrend();
        marketData.momentum = CalculateMomentum();
        marketData.volatility = CalculateVolatility();
    }
    
    // Funções auxiliares de análise
    bool IsTrending() {
        return (
            maBuffer[0] > maBuffer[1] &&
            maBuffer[1] > maBuffer[2] &&
            marketData.momentum > 0
        );
    }
    
    bool IsRanging() {
        return (
            MathAbs(marketData.trend) < 0.2 &&
            marketData.volatility < atrBuffer[0]
        );
    }
    
    bool IsVolatile() {
        return (
            marketData.volatility > atrBuffer[0] * 1.5 &&
            marketData.momentum > 0.5
        );
    }
    
    double CalculateTrend() {
        return (maBuffer[0] - maBuffer[2]) / maBuffer[2];
    }
    
    double CalculateMomentum() {
        return (Close[0] - Close[1]) / Close[1];
    }
    
    double CalculateVolatility() {
        return atrBuffer[0];
    }
};

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
CQuantumScoutPro* Scout;

int OnInit() {
    Scout = new CQuantumScoutPro();
    
    if(!Scout.Initialize()) {
        Print("Erro ao inicializar Quantum Scout Pro!");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    delete Scout;
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick() {
    Scout.ProcessTick();
}

