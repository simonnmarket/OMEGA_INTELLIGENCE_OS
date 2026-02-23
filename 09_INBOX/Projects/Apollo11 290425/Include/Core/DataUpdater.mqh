//+------------------------------------------------------------------+
//|                                                  DataUpdater.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CDataUpdater {
private:
    double volumeForce;
    double gravForce;
    double sphereEnergy;
    double POC;
    double sphereEnergyLast;
    double monthlyHigh;
    double monthlyLow;
    double weeklyHigh;
    double weeklyLow;
    datetime lastTime;
    datetime lastResetTime;
    int plotCounter;
    int rotationFactor;
    
public:
    CDataUpdater() {
        volumeForce = 0.0;
        gravForce = 0.0;
        sphereEnergy = 0.0;
        POC = 0.0;
        sphereEnergyLast = 0.0;
        monthlyHigh = 0.0;
        monthlyLow = 0.0;
        weeklyHigh = 0.0;
        weeklyLow = 0.0;
        lastTime = 0;
        lastResetTime = 0;
        plotCounter = 0;
        rotationFactor = 0;
    }
    
    void UpdateMarketData() {
        long volumeArray[];
        ArraySetAsSeries(volumeArray, true);
        if(CopyTickVolume(_Symbol, 0, 0, 10, volumeArray) > 0) {
            double volumeAvg = 0;
            for(int i = 0; i < 10; i++) volumeAvg += (double)volumeArray[i];
            volumeAvg /= 10.0;
            double currentVolume = (double)volumeArray[0];
            volumeForce = currentVolume / volumeAvg;
            Print("volumeForce atualizado: ", volumeForce);
        } else {
            Print("Erro ao copiar volume de ticks em UpdateMarketData: ", GetLastError());
        }
    }
    
    void CalculatePhysics() {
        gravForce = volumeForce * (rotationFactor != 0 ? MathAbs(rotationFactor) * 1000 : 1000);
        sphereEnergy = volumeForce * 2.0;
        POC = iClose(_Symbol, PERIOD_CURRENT, 1);
        Print("Physics: gravForce=", gravForce, " sphereEnergy=", sphereEnergy);
    }
    
    void UpdateRotationFactor(string resetInterval) {
        datetime currentResetTime = iTime(_Symbol, StringToPeriod(resetInterval), 0);
        if(currentResetTime == 0) {
            Print("Erro ao obter tempo para reset em UpdateRotationFactor: ", GetLastError());
            return;
        }
        bool reset = currentResetTime != lastResetTime;
        lastResetTime = currentResetTime;

        double high = iHigh(_Symbol, PERIOD_CURRENT, 0);
        double low = iLow(_Symbol, PERIOD_CURRENT, 0);
        double highPrev = iHigh(_Symbol, PERIOD_CURRENT, 1);
        double lowPrev = iLow(_Symbol, PERIOD_CURRENT, 1);

        int one = (high > highPrev && low > lowPrev) ? 2 : 0;
        int two = (high < highPrev && low < lowPrev) ? -2 : 0;
        int three = (high > highPrev && low < lowPrev) ? 0 : 0;
        int four = (high < highPrev && low > lowPrev) ? 0 : 0;
        int five = (high == highPrev && low > lowPrev) ? 1 : 0;
        int six = (high > highPrev && low == lowPrev) ? 1 : 0;
        int seven = (high < highPrev && low == lowPrev) ? -1 : 0;
        int eight = (high == highPrev && low < lowPrev) ? -1 : 0;

        if (reset) rotationFactor = one + two + three + four + five + six + seven + eight;
        else rotationFactor += one + two + three + four + five + six + seven + eight;

        Print("Rotation Factor atualizado: ", rotationFactor);
    }
    
    void CalculateMonthlyChannel() {
        monthlyHigh = iHigh(_Symbol, PERIOD_MN1, 1);
        monthlyLow = iLow(_Symbol, PERIOD_MN1, 1);
    }
    
    void CalculateWeeklyChannel() {
        weeklyHigh = iHigh(_Symbol, PERIOD_W1, 1);
        weeklyLow = iLow(_Symbol, PERIOD_W1, 1);
    }
    
    double GetVolumeForce() const { return volumeForce; }
    double GetGravForce() const { return gravForce; }
    double GetSphereEnergy() const { return sphereEnergy; }
    double GetPOC() const { return POC; }
    int GetRotationFactor() const { return rotationFactor; }
    
private:
    ENUM_TIMEFRAMES StringToPeriod(string timeframeStr) {
        if(timeframeStr == "D1") return PERIOD_D1;
        if(timeframeStr == "H4") return PERIOD_H4;
        if(timeframeStr == "H1") return PERIOD_H1;
        if(timeframeStr == "M15") return PERIOD_M15;
        if(timeframeStr == "M5") return PERIOD_M5;
        if(timeframeStr == "M1") return PERIOD_M1;
        return PERIOD_CURRENT;
    }
}; 