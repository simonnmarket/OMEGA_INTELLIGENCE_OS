//+------------------------------------------------------------------+
//|                                               IRiskManager.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "IModule.mqh"
#include "ISignalGenerator.mqh"

//+------------------------------------------------------------------+
//| Interface for risk management modules                             |
//+------------------------------------------------------------------+
interface IRiskManager : public IModule
{
    bool ValidateRisk(ENUM_MARKET_SIGNAL signal);  // Validate risk for signal
    double CalculateLotSize();                     // Calculate position size
    bool CheckStopLoss();                          // Check stop loss
    bool CheckTakeProfit();                        // Check take profit
    bool ValidateRiskLevels();                     // Validate risk levels
}; 