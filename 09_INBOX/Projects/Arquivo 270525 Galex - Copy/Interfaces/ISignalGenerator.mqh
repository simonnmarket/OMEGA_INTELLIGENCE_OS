//+------------------------------------------------------------------+
//|                                             ISignalGenerator.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "IModule.mqh"

//+------------------------------------------------------------------+
//| Market signal enumeration                                         |
//+------------------------------------------------------------------+
enum ENUM_MARKET_SIGNAL
{
    SIGNAL_NONE,    // No signal
    SIGNAL_BUY,     // Buy signal
    SIGNAL_SELL     // Sell signal
};

//+------------------------------------------------------------------+
//| Interface for signal generation modules                           |
//+------------------------------------------------------------------+
interface ISignalGenerator : public IModule
{
    ENUM_MARKET_SIGNAL GenerateSignal();  // Generate trading signal
    double GetSignalStrength();           // Get signal strength
    bool ValidateSignal();                // Validate signal
}; 