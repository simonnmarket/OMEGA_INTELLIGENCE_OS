//+------------------------------------------------------------------+
//|                                               MarketUtils.mq5 |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

#include "..\Core\MarketCore.mqh"

// Market Statistics Structure
struct MarketStats
{
    double avgVolume;
    double volumeStdDev;
    double avgRange;
    double rangeStdDev;
    double momentum;
    double volatility;
    double correlation;
    
    void Init()
    {
        avgVolume = 0;
        volumeStdDev = 0;
        avgRange = 0;
        rangeStdDev = 0;
        momentum = 0;
        volatility = 0;
        correlation = 0;
    }
};

// Market Strength Structure
struct MarketStrength
{
    double bullPower;
    double bearPower;
    double netStrength;
    double momentum;
    double marketPressure;
    
    bool IsBullish() { return netStrength > 0; }
    bool IsBearish() { return netStrength < 0; }
    
    void Init()
    {
        bullPower = 0;
        bearPower = 0;
        netStrength = 0;
        momentum = 0;
        marketPressure = 0;
    }
};

// Statistics Class
class CStatistics
{
public:
    static double Mean(const double &data[])
    {
        if(ArraySize(data) == 0) return 0;
        
        double sum = 0;
        for(int i = 0; i < ArraySize(data); i++)
        {
            sum += data[i];
        }
        return sum / ArraySize(data);
    }
    
    static double StdDev(const double &data[])
    {
        if(ArraySize(data) == 0) return 0;
        
        double mean = Mean(data);
        double sumSqDiff = 0;
        
        for(int i = 0; i < ArraySize(data); i++)
        {
            double diff = data[i] - mean;
            sumSqDiff += diff * diff;
        }
        
        return MathSqrt(sumSqDiff / ArraySize(data));
    }
    
    static double Correlation(const double &data1[], const double &data2[])
    {
        if(ArraySize(data1) != ArraySize(data2)) return 0;
        if(ArraySize(data1) == 0) return 0;
        
        double mean1 = Mean(data1);
        double mean2 = Mean(data2);
        double sumProdDiff = 0;
        double sumSqDiff1 = 0;
        double sumSqDiff2 = 0;
        
        for(int i = 0; i < ArraySize(data1); i++)
        {
            double diff1 = data1[i] - mean1;
            double diff2 = data2[i] - mean2;
            sumProdDiff += diff1 * diff2;
            sumSqDiff1 += diff1 * diff1;
            sumSqDiff2 += diff2 * diff2;
        }
        
        if(sumSqDiff1 == 0 || sumSqDiff2 == 0) return 0;
        return sumProdDiff / MathSqrt(sumSqDiff1 * sumSqDiff2);
    }
    
    static double ZScore(double value, const double &data[])
    {
        if(ArraySize(data) == 0) return 0;
        
        double mean = Mean(data);
        double stdDev = StdDev(data);
        
        if(stdDev == 0) return 0;
        return (value - mean) / stdDev;
    }
};

// Market Utilities Class
class CMarketUtils
{
private:
    CLogger m_logger;
    
public:
    CMarketUtils()
    {
        m_logger = CLogger("Market");
    }
    
    bool CalculateMarketStats(MarketStats &stats)
    {
        double close[], high[], low[];
        long volume[];
        ArraySetAsSeries(close, true);
        ArraySetAsSeries(high, true);
        ArraySetAsSeries(low, true);
        ArraySetAsSeries(volume, true);
        
        int period = 14;
        
        if(!CopyClose(_Symbol, PERIOD_CURRENT, 0, period, close) ||
           !CopyHigh(_Symbol, PERIOD_CURRENT, 0, period, high) ||
           !CopyLow(_Symbol, PERIOD_CURRENT, 0, period, low) ||
           !CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, period, volume))
        {
            m_logger.Error("Failed to copy market data");
            return false;
        }
        
        // Convert volume to double for calculations
        double volumeDouble[];
        ArrayResize(volumeDouble, period);
        for(int i = 0; i < period; i++)
        {
            volumeDouble[i] = (double)volume[i];
        }
        
        // Calculate volume statistics
        stats.avgVolume = CStatistics::Mean(volumeDouble);
        stats.volumeStdDev = CStatistics::StdDev(volumeDouble);
        
        // Calculate range statistics
        double ranges[];
        ArrayResize(ranges, period);
        for(int i = 0; i < period; i++)
        {
            ranges[i] = high[i] - low[i];
        }
        stats.avgRange = CStatistics::Mean(ranges);
        stats.rangeStdDev = CStatistics::StdDev(ranges);
        
        // Calculate momentum
        stats.momentum = close[0] - close[period-1];
        
        // Calculate volatility
        stats.volatility = stats.rangeStdDev / stats.avgRange;
        
        // Calculate correlation between price and volume
        stats.correlation = CStatistics::Correlation(close, volumeDouble);
        
        return true;
    }
    
    bool AnalyzeMarketStrength(MarketStrength &strength)
    {
        double close[];
        long volume[];
        ArraySetAsSeries(close, true);
        ArraySetAsSeries(volume, true);
        
        int period = 14;
        
        if(!CopyClose(_Symbol, PERIOD_CURRENT, 0, period, close) ||
           !CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, period, volume))
        {
            m_logger.Error("Failed to copy market data");
            return false;
        }
        
        // Convert volume to double for calculations
        double volumeDouble[];
        ArrayResize(volumeDouble, period);
        for(int i = 0; i < period; i++)
        {
            volumeDouble[i] = (double)volume[i];
        }
        
        // Calculate bull and bear power
        strength.bullPower = 0;
        strength.bearPower = 0;
        
        for(int i = 0; i < period-1; i++)
        {
            if(close[i] > close[i+1])
            {
                strength.bullPower += (close[i] - close[i+1]) * volumeDouble[i];
            }
            else
            {
                strength.bearPower += (close[i+1] - close[i]) * volumeDouble[i];
            }
        }
        
        // Calculate net strength
        strength.netStrength = strength.bullPower - strength.bearPower;
        
        // Calculate momentum
        strength.momentum = close[0] - close[period-1];
        
        // Calculate market pressure
        strength.marketPressure = CStatistics::Correlation(close, volumeDouble);
        
        return true;
    }
}; 