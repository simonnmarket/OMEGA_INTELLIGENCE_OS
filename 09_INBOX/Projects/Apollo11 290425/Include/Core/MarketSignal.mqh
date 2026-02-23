//+------------------------------------------------------------------+
//|                                                  MarketSignal.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

// Estrutura para dados sensoriais integrados
struct IntegratedSensoryData {
    double visualConfidence;
    double auditoryConfidence;
    double tactileConfidence;
    double olfactoryConfidence;
    double gustatoryConfidence;
    double overallPerception;
    double sensoryCoherence;
    double marketStrength;
    double trendStrength;
    double gravForce;
    int rotationFactor;
    
    void Clear() {
        visualConfidence = 0.0;
        auditoryConfidence = 0.0;
        tactileConfidence = 0.0;
        olfactoryConfidence = 0.0;
        gustatoryConfidence = 0.0;
        overallPerception = 0.0;
        sensoryCoherence = 0.0;
        marketStrength = 0.0;
        trendStrength = 0.0;
        gravForce = 0.0;
        rotationFactor = 0;
    }
};

// Classe base para sistemas sensoriais
class CSensoryBase {
protected:
    double confidence;
    bool isInitialized;
    
public:
    CSensoryBase() : confidence(0.0), isInitialized(false) {}
    virtual ~CSensoryBase() {}
    virtual bool Initialize() { isInitialized = true; return true; }
    virtual void Process() = 0;
    double GetConfidence() const { return confidence; }
    bool IsInitialized() const { return isInitialized; }
}; 