//+------------------------------------------------------------------+
//|                                             VolumeAnalysis.mqh |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

#include "../Core/MarketCore.mqh"

// Volume Analysis Parameters
struct VolumeParams
{
    int period;
    double threshold;
    bool usePrice;
    
    void Init()
    {
        period = 14;
        threshold = 2.0;
        usePrice = true;
    }
};

// Volume Analyzer Class
class CVolumeAnalyzer
{
private:
    VolumeParams m_params;
    CLogger m_logger;
    long m_volumeBuffer[];
    double m_priceBuffer[];
    
public:
    CVolumeAnalyzer()
    {
        m_params.Init();
        m_logger = CLogger("Volume");
        ArrayResize(m_volumeBuffer, m_params.period);
        ArrayResize(m_priceBuffer, m_params.period);
    }
    
    bool Init(VolumeParams &params)
    {
        m_params = params;
        ArrayResize(m_volumeBuffer, m_params.period);
        ArrayResize(m_priceBuffer, m_params.period);
        return true;
    }
    
    bool CalculateVolumeState()
    {
        if(!CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, m_params.period, m_volumeBuffer))
        {
            m_logger.Error("Failed to copy volume data");
            return false;
        }
        
        if(m_params.usePrice)
        {
            if(!CopyClose(_Symbol, PERIOD_CURRENT, 0, m_params.period, m_priceBuffer))
            {
                m_logger.Error("Failed to copy price data");
                return false;
            }
        }
        
        return true;
    }
    
    bool CheckVolumeSignal(VolumeSignal &signal)
    {
        if(!CalculateVolumeState())
            return false;
            
        double currentVolume = (double)m_volumeBuffer[0];
        double avgVolume = 0;
        double stdDev = 0;
        
        // Calculate average volume
        for(int i = 0; i < m_params.period; i++)
        {
            avgVolume += (double)m_volumeBuffer[i];
        }
        avgVolume /= m_params.period;
        
        // Calculate standard deviation
        for(int i = 0; i < m_params.period; i++)
        {
            double diff = (double)m_volumeBuffer[i] - avgVolume;
            stdDev += diff * diff;
        }
        stdDev = MathSqrt(stdDev / m_params.period);
        
        // Check for volume signals
        double zScore = (currentVolume - avgVolume) / stdDev;
        
        if(zScore > m_params.threshold)
        {
            signal.Init();
            signal.volume = currentVolume;
            signal.price = m_params.usePrice ? m_priceBuffer[0] : 0;
            signal.time = TimeCurrent();
            signal.isBuy = m_params.usePrice ? m_priceBuffer[0] > m_priceBuffer[1] : true;
            signal.isSell = m_params.usePrice ? m_priceBuffer[0] < m_priceBuffer[1] : false;
            return true;
        }
        else if(zScore < -m_params.threshold)
        {
            signal.Init();
            signal.volume = currentVolume;
            signal.price = m_params.usePrice ? m_priceBuffer[0] : 0;
            signal.time = TimeCurrent();
            signal.isBuy = m_params.usePrice ? m_priceBuffer[0] > m_priceBuffer[1] : false;
            signal.isSell = m_params.usePrice ? m_priceBuffer[0] < m_priceBuffer[1] : true;
            return true;
        }
        
        return false;
    }
    
    double GetVolumeDirection()
    {
        if(!CalculateVolumeState())
            return 0;
            
        double currentVolume = (double)m_volumeBuffer[0];
        double prevVolume = (double)m_volumeBuffer[1];
        
        return currentVolume - prevVolume;
    }
};