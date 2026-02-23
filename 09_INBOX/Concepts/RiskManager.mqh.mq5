//+------------------------------------------------------------------+
//|                                               RiskManager.mqh |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

#include "..\Core\MarketCore.mqh"

// Risk Management Parameters
struct RiskParams
{
    double initialLot;
    double maxLot;
    int scalingSteps;
    int atrPeriod;
    double riskPercent;
    
    void Init()
    {
        initialLot = 0.1;
        maxLot = 1.0;
        scalingSteps = 3;
        atrPeriod = 14;
        riskPercent = 1.0;
    }
};

// Risk Management Class
class CRiskManager
{
private:
    RiskParams m_params;
    CLogger m_logger;
    int m_atrHandle;
    double m_atrBuffer[];
    
public:
    CRiskManager(RiskParams &params, bool debugMode = false)
    {
        m_params = params;
        m_logger = CLogger("Risk", debugMode);
        m_atrHandle = INVALID_HANDLE;
        ArrayResize(m_atrBuffer, m_params.atrPeriod);
    }
    
    bool Init()
    {
        m_atrHandle = iATR(_Symbol, PERIOD_CURRENT, m_params.atrPeriod);
        if(m_atrHandle == INVALID_HANDLE)
        {
            m_logger.Error("Failed to create ATR indicator");
            return false;
        }
        return true;
    }
    
    void Deinit()
    {
        if(m_atrHandle != INVALID_HANDLE)
        {
            IndicatorRelease(m_atrHandle);
            m_atrHandle = INVALID_HANDLE;
        }
    }
    
    double CalculatePositionSize(int step)
    {
        if(step < 0 || step >= m_params.scalingSteps)
        {
            m_logger.Error("Invalid scaling step");
            return 0;
        }
        
        double lotStep = (m_params.maxLot - m_params.initialLot) / (m_params.scalingSteps - 1);
        return m_params.initialLot + (lotStep * step);
    }
    
    double CalculateStopLoss(double entryPrice, bool isBuy)
    {
        if(m_atrHandle == INVALID_HANDLE)
        {
            m_logger.Error("ATR indicator not initialized");
            return 0;
        }
        
        if(CopyBuffer(m_atrHandle, 0, 0, 1, m_atrBuffer) <= 0)
        {
            m_logger.Error("Failed to copy ATR data");
            return 0;
        }
        
        double atr = m_atrBuffer[0];
        return isBuy ? entryPrice - (atr * 2) : entryPrice + (atr * 2);
    }
    
    double CalculateTakeProfit(double entryPrice, double stopLoss, bool isBuy)
    {
        double risk = MathAbs(entryPrice - stopLoss);
        return isBuy ? entryPrice + (risk * 2) : entryPrice - (risk * 2);
    }
};