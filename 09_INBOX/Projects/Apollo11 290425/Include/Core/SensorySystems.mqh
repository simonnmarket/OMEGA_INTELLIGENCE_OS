//+------------------------------------------------------------------+
//|                                            SensorySystems.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

#include "MarketSignal.mqh"

class CQuantumVisionSystem : public CSensoryBase {
public:
    CQuantumVisionSystem() : CSensoryBase() {}
    virtual void Process() override {
        // Análise visual do mercado
        double maFast[], maSlow[];
        ArraySetAsSeries(maFast, true);
        ArraySetAsSeries(maSlow, true);
        
        int maFastHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_EMA, PRICE_CLOSE);
        int maSlowHandle = iMA(_Symbol, PERIOD_CURRENT, 50, 0, MODE_EMA, PRICE_CLOSE);
        
        if(CopyBuffer(maFastHandle, 0, 0, 2, maFast) > 0 && 
           CopyBuffer(maSlowHandle, 0, 0, 2, maSlow) > 0) {
            double trend = (maFast[0] - maSlow[0]) / maSlow[0];
            confidence = MathAbs(trend);
        }
        
        IndicatorRelease(maFastHandle);
        IndicatorRelease(maSlowHandle);
    }
};

class CMarketHearingSystem : public CSensoryBase {
public:
    CMarketHearingSystem() : CSensoryBase() {}
    virtual void Process() override {
        // Análise de volume e ruído do mercado
        long volumes[];
        ArraySetAsSeries(volumes, true);
        
        if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, 10, volumes) > 0) {
            double currentVolume = (double)volumes[0];
            double avgVolume = 0.0;
            
            for(int i = 1; i < 10; i++) {
                avgVolume += (double)volumes[i];
            }
            avgVolume /= 9.0;
            
            confidence = currentVolume / avgVolume;
        }
    }
};

class CMarketTouchSystem : public CSensoryBase {
public:
    CMarketTouchSystem() : CSensoryBase() {}
    virtual void Process() override {
        // Análise de volatilidade e pressão do mercado
        double atr[];
        ArraySetAsSeries(atr, true);
        int atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
        
        if(CopyBuffer(atrHandle, 0, 0, 2, atr) > 0) {
            double currentATR = atr[0];
            double prevATR = atr[1];
            confidence = currentATR / prevATR;
        }
        
        IndicatorRelease(atrHandle);
    }
};

class CRiskSmellingSystem : public CSensoryBase {
public:
    CRiskSmellingSystem() : CSensoryBase() {}
    virtual void Process() override {
        // Análise de risco e perigo
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double drawdown = (balance - equity) / balance * 100.0;
        
        confidence = 1.0 - (drawdown / 100.0);
    }
};

class CMarketTasteSystem : public CSensoryBase {
public:
    CMarketTasteSystem() : CSensoryBase() {}
    virtual void Process() override {
        // Análise de tendência e sabor do mercado
        double rsi[];
        ArraySetAsSeries(rsi, true);
        int rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
        
        if(CopyBuffer(rsiHandle, 0, 0, 1, rsi) > 0) {
            confidence = MathAbs(rsi[0] - 50.0) / 50.0;
        }
        
        IndicatorRelease(rsiHandle);
    }
};

class CSensoryIntegration {
private:
    IntegratedSensoryData currentPerception;
    
public:
    CSensoryIntegration() {
        currentPerception.Clear();
    }
    
    void ProcessSensoryInput(CQuantumVisionSystem* vision, 
                           CMarketHearingSystem* hearing,
                           CMarketTouchSystem* touch,
                           CRiskSmellingSystem* smell,
                           CMarketTasteSystem* taste) {
        currentPerception.visualConfidence = vision.GetConfidence();
        currentPerception.auditoryConfidence = hearing.GetConfidence();
        currentPerception.tactileConfidence = touch.GetConfidence();
        currentPerception.olfactoryConfidence = smell.GetConfidence();
        currentPerception.gustatoryConfidence = taste.GetConfidence();
        
        // Cálculo da percepção geral
        currentPerception.overallPerception = (
            currentPerception.visualConfidence +
            currentPerception.auditoryConfidence +
            currentPerception.tactileConfidence +
            currentPerception.olfactoryConfidence +
            currentPerception.gustatoryConfidence
        ) / 5.0;
        
        // Cálculo da coerência sensorial
        double mean = currentPerception.overallPerception;
        double variance = 0.0;
        
        variance += MathPow(currentPerception.visualConfidence - mean, 2);
        variance += MathPow(currentPerception.auditoryConfidence - mean, 2);
        variance += MathPow(currentPerception.tactileConfidence - mean, 2);
        variance += MathPow(currentPerception.olfactoryConfidence - mean, 2);
        variance += MathPow(currentPerception.gustatoryConfidence - mean, 2);
        
        currentPerception.sensoryCoherence = 1.0 - MathSqrt(variance / 5.0);
    }
    
    IntegratedSensoryData GetCurrentPerception() const {
        return currentPerception;
    }
}; 