//+------------------------------------------------------------------+
//|                                              IActionExecutor.mqh |
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
//| Interface for trade execution modules                             |
//+------------------------------------------------------------------+
interface IActionExecutor : public IModule
{
    bool ExecuteSignal(ENUM_MARKET_SIGNAL signal);  // Execute trading signal
    bool ClosePosition();                           // Close current position
    bool ModifyPosition();                          // Modify current position
    bool ValidateExecution();                       // Validate execution
}; 