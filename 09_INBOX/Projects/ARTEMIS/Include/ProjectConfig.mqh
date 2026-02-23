//+------------------------------------------------------------------+
//| ProjectConfig.mqh - Central Configuration File                    |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

#include "DirectoryConfig.mqh"

// Standard Library Includes
#include <Trade\\Trade.mqh>
#include <Arrays\\ArrayObj.mqh>
#include <Trade\\HistoryOrderInfo.mqh>

// Forward declarations
class CLogger;
class CRiskManager;
class CQuantumMarketPhysics;
class CStatistics;
class CNeuralPredictor;
class CVolatilityQuantum;
class CVolatilityMetrics;
class CAnalysisModule;
class CFractalAnalysis;
class CHash;

// Core Module Includes
#include "Utils\\CLogger.mqh"                // Unified logging system
#include "Math\\CStatistics.mqh"             // Statistical analysis
#include "Quantum\\CVolatilityQuantum.mqh"   // Quantum volatility
#include "Quantum\\VolatilityMetrics.mqh"    // Volatility metrics
#include "Analysis\\CAnalysisModule.mqh"     // Analysis module
#include "Core\\FractalAnalysis.mqh"         // Fractal analysis

// Math Module Includes
#include "Math\\Stat\\Math.mqh"               // Statistical functions
#include "Math\\Alglib\\alglib.mqh"           // Advanced math library

// Trade Module Includes
#include "Trade\\HistoryOrderInfo.mqh"       // Order history management

// Utility Includes
#include "Utils\\Crypt\\CHash.mqh"            // Cryptographic functions 