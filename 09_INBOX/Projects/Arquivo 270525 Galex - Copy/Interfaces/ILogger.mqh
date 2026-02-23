//+------------------------------------------------------------------+
//|                                                    ILogger.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "IModule.mqh"

//+------------------------------------------------------------------+
//| Interface for logging modules                                     |
//+------------------------------------------------------------------+
interface ILogger : public IModule
{
    bool LogInfo(string message);      // Log information
    bool LogWarning(string message);   // Log warning
    bool LogError(string message);     // Log error
    bool LogTrade(string message);     // Log trade
    bool LogSignal(string message);    // Log signal
    bool ValidateLogs();               // Validate logs
}; 