//+------------------------------------------------------------------+
//|                                               MarketAnalyzer.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CMarketAnalyzer {
private:
    int maFastHandle;
    int maSlowHandle;
    int rsiHandle;
    int stochHandle;
    ENUM_TIMEFRAMES analysisTimeframe;
    
public:
    CMarketAnalyzer(ENUM_TIMEFRAMES timeframe) : analysisTimeframe(timeframe) {
        maFastHandle = iMA(_Symbol, analysisTimeframe, 20, 0, MODE_EMA, PRICE_CLOSE);
        maSlowHandle = iMA(_Symbol, analysisTimeframe, 50, 0, MODE_EMA, PRICE_CLOSE);
        rsiHandle = iRSI(_Symbol, analysisTimeframe, 14, PRICE_CLOSE);
        stochHandle = iStochastic(_Symbol, analysisTimeframe, 5, 3, 3, MODE_SMA, STO_LOWHIGH);
    }
    
    ~CMarketAnalyzer() {
        if(maFastHandle != INVALID_HANDLE) IndicatorRelease(maFastHandle);
        if(maSlowHandle != INVALID_HANDLE) IndicatorRelease(maSlowHandle);
        if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
        if(stochHandle != INVALID_HANDLE) IndicatorRelease(stochHandle);
    }
    
    bool Initialize() {
        if(maFastHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar MA Fast em CMarketAnalyzer: ", GetLastError());
            return false;
        }
        if(maSlowHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar MA Slow em CMarketAnalyzer: ", GetLastError());
            return false;
        }
        if(rsiHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar RSI em CMarketAnalyzer: ", GetLastError());
            return false;
        }
        if(stochHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar Stochastic em CMarketAnalyzer: ", GetLastError());
            return false;
        }
        return true;
    }
    
    double GetTrendStrength() {
        double maFast[], maSlow[];
        ArraySetAsSeries(maFast, true);
        ArraySetAsSeries(maSlow, true);
        
        if(CopyBuffer(maFastHandle, 0, 0, 2, maFast) <= 0 || CopyBuffer(maSlowHandle, 0, 0, 2, maSlow) <= 0) {
            Print("Erro ao copiar buffers de MA em GetTrendStrength: ", GetLastError());
            return 0.0;
        }
            
        double trendStrength = (maFast[0] - maSlow[0]) / maSlow[0];
        return trendStrength;
    }
    
    double GetMarketMomentum() {
        double rsi[], stochMain[], stochSignal[];
        ArraySetAsSeries(rsi, true);
        ArraySetAsSeries(stochMain, true);
        ArraySetAsSeries(stochSignal, true);
        
        if(CopyBuffer(rsiHandle, 0, 0, 1, rsi) <= 0 || 
           CopyBuffer(stochHandle, MAIN_LINE, 0, 1, stochMain) <= 0 || 
           CopyBuffer(stochHandle, SIGNAL_LINE, 0, 1, stochSignal) <= 0) {
            Print("Erro ao copiar buffers de RSI ou Stochastic em GetMarketMomentum: ", GetLastError());
            return 0.0;
        }
            
        double rsiWeight = 0.6;
        double stochWeight = 0.4;
        
        double rsiMomentum = (rsi[0] - 50.0) / 50.0;
        double stochMomentum = (stochMain[0] - stochSignal[0]) / 100.0;
        
        return rsiWeight * rsiMomentum + stochWeight * stochMomentum;
    }
    
    bool IsVolatilityFavorable(int atrPeriod) {
        double atr[];
        ArraySetAsSeries(atr, true);
        int atrHandle = iATR(_Symbol, analysisTimeframe, atrPeriod);
        
        if(CopyBuffer(atrHandle, 0, 0, 2, atr) <= 0) {
            Print("Erro ao copiar buffer de ATR em IsVolatilityFavorable: ", GetLastError());
            IndicatorRelease(atrHandle);
            return false;
        }
        IndicatorRelease(atrHandle);
        
        double atrAvg[];
        ArraySetAsSeries(atrAvg, true);
        int atrAvgHandle = iATR(_Symbol, analysisTimeframe, 20);
        if(CopyBuffer(atrAvgHandle, 0, 0, 1, atrAvg) > 0) {
            IndicatorRelease(atrAvgHandle);
            if(atr[0] < atrAvg[0] * 0.5 || atr[0] > atrAvg[0] * 1.5) {
                Print("Volatilidade fora do intervalo aceitável: ATR=", atr[0], ", Avg=", atrAvg[0]);
                return false;
            }
        }
        return true;
    }
}; 