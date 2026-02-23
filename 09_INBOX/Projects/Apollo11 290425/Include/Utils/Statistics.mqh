//+------------------------------------------------------------------+
//|                                                Statistics.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CStatistics {
public:
    static double Mean(const double &array[]) {
        double sum = 0.0;
        for(int i = 0; i < ArraySize(array); i++) sum += array[i];
        return sum / ArraySize(array);
    }
    
    static double StdDev(const double &array[]) {
        double mean = Mean(array);
        double sum = 0.0;
        for(int i = 0; i < ArraySize(array); i++) sum += MathPow(array[i] - mean, 2);
        return MathSqrt(sum / ArraySize(array));
    }
    
    static double Correlation(const double &array1[], const double &array2[]) {
        if(ArraySize(array1) != ArraySize(array2)) return 0.0;
        
        double mean1 = Mean(array1);
        double mean2 = Mean(array2);
        double sum = 0.0;
        double sum1 = 0.0;
        double sum2 = 0.0;
        
        for(int i = 0; i < ArraySize(array1); i++) {
            sum += (array1[i] - mean1) * (array2[i] - mean2);
            sum1 += MathPow(array1[i] - mean1, 2);
            sum2 += MathPow(array2[i] - mean2, 2);
        }
        
        return sum / MathSqrt(sum1 * sum2);
    }
    
    static double ZScore(const double &array[], double value) {
        double mean = Mean(array);
        double stddev = StdDev(array);
        if(stddev == 0) return 0.0;
        return (value - mean) / stddev;
    }
    
    static double Normalize(const double &array[], double value) {
        double min = array[ArrayMinimum(array)];
        double max = array[ArrayMaximum(array)];
        if(max == min) return 0.0;
        return (value - min) / (max - min);
    }
    
    static double ExponentialMovingAverage(const double &array[], int period) {
        if(ArraySize(array) < period) return 0.0;
        
        double k = 2.0 / (period + 1);
        double ema = array[0];
        
        for(int i = 1; i < ArraySize(array); i++) {
            ema = array[i] * k + ema * (1 - k);
        }
        
        return ema;
    }
}; 