//+------------------------------------------------------------------+
//| Common.mqh                                                        |
//| Central header file for managing common dependencies              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024"
#property link      ""
#property version   "1.00"
#property strict

// Standard includes
#include <Trade\Trade.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>
#include "..\Trade\HistoryOrderInfo.mqh"
#include <Object.mqh>
#include <StdLibErr.mqh>
#include <Arrays\ArrayObj.mqh>

// Core class forward declarations
class CTimeframeHierarchy;
class CVolatilityAnalysis;
class CStatistics;
class CLogger;
class CWinInet;

// Forward declarations
class CQuantumMarketPhysics;
class CVolatilityQuantum;
class CAnalysisModule;
class CFractalAnalysis;
class CHash;

// Common structures
struct VolatilityMetrics;  // Forward declaration, defined in VolatilityMetrics.mqh

// Common enums
enum ERROR_SEVERITY {
    SEVERITY_LOW = 0,
    SEVERITY_MEDIUM = 1,
    SEVERITY_HIGH = 2,
    SEVERITY_CRITICAL = 3
};

// Common constants
#define MAX_RETRIES 3
#define DEFAULT_TIMEOUT 5000
#define MIN_DATA_POINTS 30 