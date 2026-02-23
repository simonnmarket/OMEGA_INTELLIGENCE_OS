//+------------------------------------------------------------------+
//|                                               IDataAnalyzer.mqh |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "IModule.mqh"

//+------------------------------------------------------------------+
//| Interface for market analysis modules                             |
//+------------------------------------------------------------------+
interface IDataAnalyzer : public IModule
{
    bool AnalyzeMarket();      // Analyze market conditions
    bool AnalyzeTrajectory();  // Analyze price trajectory
    bool AnalyzeVolume();      // Analyze volume patterns
    bool ValidateAnalysis();   // Validate analysis results
}; 