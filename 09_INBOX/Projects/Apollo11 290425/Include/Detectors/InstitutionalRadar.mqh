//+------------------------------------------------------------------+
//|                                          InstitutionalRadar.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CInstitutionalRadar {
private:
    double volumeThreshold;
    double priceImpactThreshold;
    int lookbackPeriod;
    
public:
    CInstitutionalRadar() {
        volumeThreshold = 2.0;  // Volume 2x maior que a média
        priceImpactThreshold = 0.001;  // Impacto de 0.1% no preço
        lookbackPeriod = 20;  // Período de análise
    }
    
    bool DetectInstitutionalActivity() {
        // Análise de volume
        double volumeActivity = AnalyzeVolumeActivity();
        if(volumeActivity > volumeThreshold) {
            Print("Atividade institucional detectada por volume: ", volumeActivity);
            return true;
        }
        
        // Análise de impacto no preço
        double priceImpact = AnalyzePriceImpact();
        if(priceImpact > priceImpactThreshold) {
            Print("Atividade institucional detectada por impacto no preço: ", priceImpact);
            return true;
        }
        
        return false;
    }
    
    void SetVolumeThreshold(double threshold) { volumeThreshold = threshold; }
    void SetPriceImpactThreshold(double threshold) { priceImpactThreshold = threshold; }
    void SetLookbackPeriod(int period) { lookbackPeriod = period; }
    
private:
    double AnalyzeVolumeActivity() {
        long volumes[];
        ArraySetAsSeries(volumes, true);
        
        if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, lookbackPeriod, volumes) <= 0) {
            Print("Erro ao copiar volumes em AnalyzeVolumeActivity: ", GetLastError());
            return 0.0;
        }
        
        double currentVolume = (double)volumes[0];
        double avgVolume = 0.0;
        
        for(int i = 1; i < lookbackPeriod; i++) {
            avgVolume += (double)volumes[i];
        }
        avgVolume /= (lookbackPeriod - 1);
        
        return currentVolume / avgVolume;
    }
    
    double AnalyzePriceImpact() {
        double closes[];
        ArraySetAsSeries(closes, true);
        
        if(CopyClose(_Symbol, PERIOD_CURRENT, 0, lookbackPeriod, closes) <= 0) {
            Print("Erro ao copiar preços em AnalyzePriceImpact: ", GetLastError());
            return 0.0;
        }
        
        double currentClose = closes[0];
        double prevClose = closes[1];
        
        return MathAbs(currentClose - prevClose) / prevClose;
    }
}; 