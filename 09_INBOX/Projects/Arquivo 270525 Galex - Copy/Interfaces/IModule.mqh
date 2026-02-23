//+------------------------------------------------------------------+
//|                                                      IModule.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Interface for all modules                                         |
//+------------------------------------------------------------------+
interface IModule
{
    bool Init();           // Initialize module
    void Update();         // Update module state
    bool Validate();       // Validate module state
    void Cleanup();        // Cleanup resources
}; 