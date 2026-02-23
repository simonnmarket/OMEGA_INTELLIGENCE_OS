#property copyright "Apollo11 Quantum Trading System"
#property version   "5.0"
#property strict

#include "NeuralNetwork.mqh"
#include "QuantumCorrelationManager.mqh"

// Classe para rastrear grandes players
class CBigPlayerTracker {
private:
    double volumeThreshold;
    double orderFlowThreshold;
    double correlationThreshold;
    double neuralThreshold;
    
    double volumeRatio;
    double orderFlow;
    double correlation;
    double neuralConfidence;
    
    int volumeHandle;
    int maHandle;
    int rsiHandle;
    
    CNeuralNetwork* neuralNetwork;
    CQuantumCorrelationManager* correlationManager;
    
public:
    CBigPlayerTracker(double volThresh = 2.0, double flowThresh = 0.7, 
                     double corrThresh = 0.8, double neuralThresh = 0.6) {
        volumeThreshold = volThresh;
        orderFlowThreshold = flowThresh;
        correlationThreshold = corrThresh;
        neuralThreshold = neuralThresh;
        
        volumeRatio = 0.0;
        orderFlow = 0.0;
        correlation = 0.0;
        neuralConfidence = 0.0;
        
        volumeHandle = iVolumes(_Symbol, PERIOD_CURRENT, VOLUME_TICK);
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
        rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
        
        neuralNetwork = new CNeuralNetwork();
        correlationManager = new CQuantumCorrelationManager();
    }
    
    ~CBigPlayerTracker() {
        if(volumeHandle != INVALID_HANDLE) IndicatorRelease(volumeHandle);
        if(maHandle != INVALID_HANDLE) IndicatorRelease(maHandle);
        if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
        if(neuralNetwork != NULL) delete neuralNetwork;
        if(correlationManager != NULL) delete correlationManager;
    }
    
    bool Initialize() {
        if(volumeHandle == INVALID_HANDLE || 
           maHandle == INVALID_HANDLE || 
           rsiHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores em CBigPlayerTracker");
            return false;
        }
        return correlationManager.Initialize();
    }
    
    void Process() {
        CalculateVolumeRatio();
        CalculateOrderFlow();
        CalculateCorrelation();
        CalculateNeuralConfidence();
    }
    
    bool IsBigPlayerDetected() {
        return (volumeRatio >= volumeThreshold && 
                MathAbs(orderFlow) >= orderFlowThreshold && 
                correlation >= correlationThreshold && 
                neuralConfidence >= neuralThreshold);
    }
    
    void GetMetrics(double &volRatio, double &flow, double &corr, double &neural) {
        volRatio = volumeRatio;
        flow = orderFlow;
        corr = correlation;
        neural = neuralConfidence;
    }
    
private:
    void CalculateVolumeRatio() {
        double volume[];
        ArraySetAsSeries(volume, true);
        if(CopyBuffer(volumeHandle, 0, 0, 20, volume) <= 0) return;
        
        double avgVolume = 0.0;
        for(int i = 0; i < 20; i++) {
            avgVolume += volume[i];
        }
        avgVolume /= 20.0;
        
        volumeRatio = volume[0] / avgVolume;
    }
    
    void CalculateOrderFlow() {
        MqlTick lastTick;
        SymbolInfoTick(_Symbol, lastTick);
        
        if(lastTick.volume > 0) {
            orderFlow = (lastTick.ask - lastTick.bid) / lastTick.volume;
        }
    }
    
    void CalculateCorrelation() {
        correlation = correlationManager.GetCorrelation(_Symbol);
    }
    
    void CalculateNeuralConfidence() {
        double inputs[3];
        inputs[0] = volumeRatio;
        inputs[1] = orderFlow;
        inputs[2] = correlation;
        
        neuralConfidence = neuralNetwork.Predict(inputs);
    }
}; 