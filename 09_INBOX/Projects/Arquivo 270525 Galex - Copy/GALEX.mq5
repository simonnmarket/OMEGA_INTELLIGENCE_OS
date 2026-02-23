//+------------------------------------------------------------------+
//|                                                      GALEX.mq5 |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "3.00"
#property strict

// Include necessary files
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include "..\Include\Core\MarketSignal\MarketSignal.mqh"
#include "..\Include\Core\TradeExecutor\TradeExecutor.mqh"
#include "..\Include\Core\DataUpdater\DataUpdater.mqh"
#include "..\Include\Physics\PhysicsEngine.mqh"
#include "..\Include\Analysis\MarketAnalyzer.mqh"
#include "..\Include\Analysis\TrajectoryAnalyzer.mqh"
#include "..\Include\Risk\RiskManager.mqh"
#include "..\Include\Utils\Statistics.mqh"
#include "..\Include\Utils\Logger.mqh"
#include "..\Include\Detectors\InstitutionalRadar.mqh"

// Input parameters
input double LotSize = 0.1;           // Lot size
input int MagicNumber = 123456;       // Magic number
input int StopLoss = 100;             // Stop loss in points
input int TakeProfit = 200;           // Take profit in points
input ENUM_TIMEFRAMES Timeframe = PERIOD_M15;  // Timeframe
input int BarsToProcess = 1000;       // Number of bars to process

// Global variables
CTrade trade;
CPositionInfo positionInfo;
CMarketSignal marketSignal;
CTradeExecutor tradeExecutor;
CDataUpdater dataUpdater;
CPhysicsEngine physicsEngine;
CMarketAnalyzer marketAnalyzer;
CTrajectoryAnalyzer trajectoryAnalyzer;
CRiskManager riskManager;
CStatistics statistics;
CLogger logger;
CInstitutionalRadar institutionalRadar;

// Arrays for data
double priceData[];
double volumeData[];
double processedData[];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Initialize trade settings
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(_Symbol);
    trade.SetDeviationInPoints(10);
    
    // Initialize modules
    if(!marketSignal.Init()) return INIT_FAILED;
    if(!tradeExecutor.Init()) return INIT_FAILED;
    if(!dataUpdater.Init()) return INIT_FAILED;
    if(!physicsEngine.Init()) return INIT_FAILED;
    if(!marketAnalyzer.Init()) return INIT_FAILED;
    if(!trajectoryAnalyzer.Init()) return INIT_FAILED;
    if(!riskManager.Init()) return INIT_FAILED;
    if(!statistics.Init()) return INIT_FAILED;
    if(!logger.Init()) return INIT_FAILED;
    if(!institutionalRadar.Init()) return INIT_FAILED;
    
    // Configure arrays
    ArrayResize(priceData, BarsToProcess);
    ArrayResize(volumeData, BarsToProcess);
    ArrayResize(processedData, 5);
    
    Print("GALEX Trading System initialized successfully!");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Cleanup modules
    marketSignal.Cleanup();
    tradeExecutor.Cleanup();
    dataUpdater.Cleanup();
    physicsEngine.Cleanup();
    marketAnalyzer.Cleanup();
    trajectoryAnalyzer.Cleanup();
    riskManager.Cleanup();
    statistics.Cleanup();
    logger.Cleanup();
    institutionalRadar.Cleanup();
    Print("GALEX Trading System finalized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Update data
    if(!dataUpdater.UpdateData()) return;
    
    // Process data
    if(!dataUpdater.ProcessData()) return;
    
    // Analyze market
    if(!marketAnalyzer.AnalyzeMarket()) return;
    if(!trajectoryAnalyzer.AnalyzeTrajectory()) return;
    if(!institutionalRadar.Update()) return;
    
    // Generate signal
    ENUM_MARKET_SIGNAL signal = marketSignal.GenerateSignal();
    
    // Validate signal
    if(!marketSignal.ValidateSignal()) return;
    
    // Check risk
    if(!riskManager.ValidateRisk(signal)) return;
    
    // Execute trade
    if(signal != SIGNAL_NONE)
    {
        if(!tradeExecutor.ExecuteSignal(signal)) return;
    }
    
    // Update statistics
    statistics.Update();
    
    // Log information
    logger.LogInfo("Tick processed successfully");
}

//+------------------------------------------------------------------+
//| Custom functions                                                  |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Check if we can open a new position                              |
//+------------------------------------------------------------------+
bool CanOpenPosition()
{
    if(PositionSelect(_Symbol)) return false;
    return true;
}

//+------------------------------------------------------------------+
//| Check if we can close a position                                 |
//+------------------------------------------------------------------+
bool CanClosePosition()
{
    if(!PositionSelect(_Symbol)) return false;
    return true;
}

//+------------------------------------------------------------------+
//| Check if we can modify a position                                |
//+------------------------------------------------------------------+
bool CanModifyPosition()
{
    if(!PositionSelect(_Symbol)) return false;
    return true;
}

//+------------------------------------------------------------------+
//| Calculate position size based on risk                            |
//+------------------------------------------------------------------+
double CalculatePositionSize()
{
    double risk = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01; // 1% risk
    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double stop_loss_points = StopLoss;
    
    return NormalizeDouble(risk / (stop_loss_points * tick_value), 2);
}

//+------------------------------------------------------------------+
//| Calculate stop loss level                                        |
//+------------------------------------------------------------------+
double CalculateStopLoss(ENUM_MARKET_SIGNAL signal)
{
    double current_price = signal == SIGNAL_BUY ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    return signal == SIGNAL_BUY ? current_price - StopLoss * _Point : current_price + StopLoss * _Point;
}

//+------------------------------------------------------------------+
//| Calculate take profit level                                      |
//+------------------------------------------------------------------+
double CalculateTakeProfit(ENUM_MARKET_SIGNAL signal)
{
    double current_price = signal == SIGNAL_BUY ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    return signal == SIGNAL_BUY ? current_price + TakeProfit * _Point : current_price - TakeProfit * _Point;
} 