//+------------------------------------------------------------------+
//|                                             PatternDetector.mqh |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

#include "../Core/MarketCore.mqh"

// Pattern Detection Parameters
struct PatternParams
{
    int period;
    double threshold;
    bool useVolume;
    
    void Init()
    {
        period = 14;
        threshold = 2.0;
        useVolume = true;
    }
};

// Pattern Detector Class
class CPatternDetector
{
private:
    PatternParams m_params;
    CLogger m_logger;
    double m_patternBuffer[];
    long m_volumeBuffer[];
    
public:
    CPatternDetector()
    {
        m_params.Init();
        m_logger = CLogger("Pattern");
        ArrayResize(m_patternBuffer, m_params.period);
        ArrayResize(m_volumeBuffer, m_params.period);
    }
    
    bool Init(PatternParams &params)
    {
        m_params = params;
        ArrayResize(m_patternBuffer, m_params.period);
        ArrayResize(m_volumeBuffer, m_params.period);
        return true;
    }
    
    bool DetectPattern(PatternSignal &signal)
    {
        if(!CopyClose(_Symbol, PERIOD_CURRENT, 0, m_params.period, m_patternBuffer))
        {
            m_logger.Error("Failed to copy price data");
            return false;
        }
        
        if(m_params.useVolume)
        {
            if(!CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, m_params.period, m_volumeBuffer))
            {
                m_logger.Error("Failed to copy volume data");
                return false;
            }
        }
        
        // Detect Double Top
        if(DetectDoubleTop(signal))
            return true;
            
        // Detect Double Bottom
        if(DetectDoubleBottom(signal))
            return true;
            
        // Detect Head and Shoulders
        if(DetectHeadAndShoulders(signal))
            return true;
            
        // Detect Inverse Head and Shoulders
        if(DetectInverseHeadAndShoulders(signal))
            return true;
            
        return false;
    }
    
private:
    bool DetectDoubleTop(PatternSignal &signal)
    {
        // Find two peaks with similar heights
        double peak1 = 0, peak2 = 0;
        int peak1Index = 0, peak2Index = 0;
        
        for(int i = 1; i < m_params.period - 1; i++)
        {
            if(m_patternBuffer[i] > m_patternBuffer[i-1] && m_patternBuffer[i] > m_patternBuffer[i+1])
            {
                if(peak1 == 0)
                {
                    peak1 = m_patternBuffer[i];
                    peak1Index = i;
                }
                else if(MathAbs(m_patternBuffer[i] - peak1) / peak1 < 0.01) // 1% tolerance
                {
                    peak2 = m_patternBuffer[i];
                    peak2Index = i;
                    break;
                }
            }
        }
        
        if(peak1 > 0 && peak2 > 0)
        {
            signal.Init();
            signal.pattern = "Double Top";
            signal.entryPrice = m_patternBuffer[0];
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        
        return false;
    }
    
    bool DetectDoubleBottom(PatternSignal &signal)
    {
        // Find two troughs with similar depths
        double trough1 = 0, trough2 = 0;
        int trough1Index = 0, trough2Index = 0;
        
        for(int i = 1; i < m_params.period - 1; i++)
        {
            if(m_patternBuffer[i] < m_patternBuffer[i-1] && m_patternBuffer[i] < m_patternBuffer[i+1])
            {
                if(trough1 == 0)
                {
                    trough1 = m_patternBuffer[i];
                    trough1Index = i;
                }
                else if(MathAbs(m_patternBuffer[i] - trough1) / trough1 < 0.01) // 1% tolerance
                {
                    trough2 = m_patternBuffer[i];
                    trough2Index = i;
                    break;
                }
            }
        }
        
        if(trough1 > 0 && trough2 > 0)
        {
            signal.Init();
            signal.pattern = "Double Bottom";
            signal.entryPrice = m_patternBuffer[0];
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        
        return false;
    }
    
    bool DetectHeadAndShoulders(PatternSignal &signal)
    {
        // Find three peaks: left shoulder, head, right shoulder
        double leftShoulder = 0, head = 0, rightShoulder = 0;
        int leftIndex = 0, headIndex = 0, rightIndex = 0;
        
        for(int i = 1; i < m_params.period - 1; i++)
        {
            if(m_patternBuffer[i] > m_patternBuffer[i-1] && m_patternBuffer[i] > m_patternBuffer[i+1])
            {
                if(leftShoulder == 0)
                {
                    leftShoulder = m_patternBuffer[i];
                    leftIndex = i;
                }
                else if(head == 0 && m_patternBuffer[i] > leftShoulder)
                {
                    head = m_patternBuffer[i];
                    headIndex = i;
                }
                else if(rightShoulder == 0 && m_patternBuffer[i] < head && MathAbs(m_patternBuffer[i] - leftShoulder) / leftShoulder < 0.01)
                {
                    rightShoulder = m_patternBuffer[i];
                    rightIndex = i;
                    break;
                }
            }
        }
        
        if(leftShoulder > 0 && head > 0 && rightShoulder > 0)
        {
            signal.Init();
            signal.pattern = "Head and Shoulders";
            signal.entryPrice = m_patternBuffer[0];
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        
        return false;
    }
    
    bool DetectInverseHeadAndShoulders(PatternSignal &signal)
    {
        // Find three troughs: left shoulder, head, right shoulder
        double leftShoulder = 0, head = 0, rightShoulder = 0;
        int leftIndex = 0, headIndex = 0, rightIndex = 0;
        
        for(int i = 1; i < m_params.period - 1; i++)
        {
            if(m_patternBuffer[i] < m_patternBuffer[i-1] && m_patternBuffer[i] < m_patternBuffer[i+1])
            {
                if(leftShoulder == 0)
                {
                    leftShoulder = m_patternBuffer[i];
                    leftIndex = i;
                }
                else if(head == 0 && m_patternBuffer[i] < leftShoulder)
                {
                    head = m_patternBuffer[i];
                    headIndex = i;
                }
                else if(rightShoulder == 0 && m_patternBuffer[i] > head && MathAbs(m_patternBuffer[i] - leftShoulder) / leftShoulder < 0.01)
                {
                    rightShoulder = m_patternBuffer[i];
                    rightIndex = i;
                    break;
                }
            }
        }
        
        if(leftShoulder > 0 && head > 0 && rightShoulder > 0)
        {
            signal.Init();
            signal.pattern = "Inverse Head and Shoulders";
            signal.entryPrice = m_patternBuffer[0];
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        
        return false;
    }
};