//+------------------------------------------------------------------+
//|                                               IDataProcessor.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "IModule.mqh"

//+------------------------------------------------------------------+
//| Interface for data processing modules                             |
//+------------------------------------------------------------------+
interface IDataProcessor : public IModule
{
    bool ProcessData();    // Process market data
    bool UpdateData();     // Update market data
    bool ValidateData();   // Validate market data
}; 