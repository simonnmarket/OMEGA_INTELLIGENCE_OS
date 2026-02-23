//+------------------------------------------------------------------+
//|                                               WaveAnalysis.mqh |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

#include "../Core/MarketCore.mqh"

// Wave Analysis Parameters
struct WaveParams
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

// Wave Analyzer Class
class CWaveAnalyzer
{
private:
    WaveParams m_params;
    CLogger m_logger;
    double m_waveBuffer[];
    long m_volumeBuffer[];
    
public:
    CWaveAnalyzer()
    {
        m_params.Init();
        m_logger = CLogger("Wave");
        ArrayResize(m_waveBuffer, m_params.period);
        ArrayResize(m_volumeBuffer, m_params.period);
    }
    
    bool Init(WaveParams &params)
    {
        m_params = params;
        ArrayResize(m_waveBuffer, m_params.period);
        ArrayResize(m_volumeBuffer, m_params.period);
        return true;
    }
    
    bool CalculateWaveState()
    {
        if(!CopyClose(_Symbol, PERIOD_CURRENT, 0, m_params.period, m_waveBuffer))
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
        
        return true;
    }
    
    bool CheckWaveSignal(PatternSignal &signal)
    {
        if(!CalculateWaveState())
            return false;
            
        double currentPrice = m_waveBuffer[0];
        double avgPrice = 0;
        double stdDev = 0;
        
        // Calculate average price
        for(int i = 0; i < m_params.period; i++)
        {
            avgPrice += m_waveBuffer[i];
        }
        avgPrice /= m_params.period;
        
        // Calculate standard deviation
        for(int i = 0; i < m_params.period; i++)
        {
            double diff = m_waveBuffer[i] - avgPrice;
            stdDev += diff * diff;
        }
        stdDev = MathSqrt(stdDev / m_params.period);
        
        // Check for wave signals
        double zScore = (currentPrice - avgPrice) / stdDev;
        
        if(zScore > m_params.threshold)
        {
            signal.Init();
            signal.pattern = "Wave Up";
            signal.entryPrice = currentPrice;
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        else if(zScore < -m_params.threshold)
        {
            signal.Init();
            signal.pattern = "Wave Down";
            signal.entryPrice = currentPrice;
            signal.time = TimeCurrent();
            signal.isActive = true;
            return true;
        }
        
        return false;
    }
    
    ENUM_WAVE_TYPE GetWaveDirection()
    {
        if(!CalculateWaveState())
            return WAVE_TERMINATION;
            
        double currentPrice = m_waveBuffer[0];
        double prevPrice = m_waveBuffer[1];
        
        if(currentPrice > prevPrice)
            return WAVE_IMPULSE;
        else if(currentPrice < prevPrice)
            return WAVE_CORRECTIVE;
        else
            return WAVE_TERMINATION;
    }
};