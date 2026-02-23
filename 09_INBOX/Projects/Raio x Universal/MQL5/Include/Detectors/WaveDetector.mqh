//+------------------------------------------------------------------+
//|                                                WaveDetector.mqh |
//|                                    Sistema Universal de Análise |
//|                                           RaioX Trading System |
//+------------------------------------------------------------------+
#property copyright "RaioX Trading System"
#property link      ""
#property version   "1.0"

#include "..\Core\MarketCore.mqh"

// Estrutura para sinal de onda
struct WaveSignal {
    bool isValid;           // Sinal válido
    WAVE_TYPE type;        // Tipo de onda
    double strength;       // Força da onda (0-1)
    double momentum;       // Momentum da onda
    double support;        // Nível de suporte
    double resistance;     // Nível de resistência
    datetime startTime;    // Início da onda
    
    void Init() {
        isValid = false;
        type = WAVE_TYPE_NONE;
        strength = 0;
        momentum = 0;
        support = 0;
        resistance = 0;
        startTime = 0;
    }
};

// Classe para detecção de ondas
class CWaveDetector {
private:
    int      m_period;          // Período de análise
    double   m_minStrength;     // Força mínima para detecção
    double   m_priceBuffer[];   // Buffer de preços
    double   m_momentumBuffer[];// Buffer de momentum
    
public:
    void CWaveDetector() {
        m_period = 20;
        m_minStrength = 5.0;
        ArrayResize(m_priceBuffer, m_period);
        ArrayResize(m_momentumBuffer, m_period);
        ArrayInitialize(m_priceBuffer, 0);
        ArrayInitialize(m_momentumBuffer, 0);
    }
    
    bool Initialize(int period = 20, double minStrength = 5.0) {
        m_period = period;
        m_minStrength = minStrength;
        ArrayResize(m_priceBuffer, m_period);
        ArrayResize(m_momentumBuffer, m_period);
        ArrayInitialize(m_priceBuffer, 0);
        ArrayInitialize(m_momentumBuffer, 0);
        return true;
    }
    
    WaveSignal Analyze(const double &prices[], const double &volumes[]) {
        WaveSignal signal;
        signal.Init();
        
        if(ArraySize(prices) < m_period || ArraySize(volumes) < m_period)
            return signal;
            
        // Atualiza buffers
        UpdateBuffers(prices);
        
        // Calcula características da onda
        signal.strength = CalculateWaveStrength();
        signal.momentum = CalculateWaveMomentum(volumes);
        
        // Identifica pontos importantes
        IdentifyKeyLevels(signal);
        
        // Determina tipo de onda
        if(DetermineWaveType(signal)) {
            signal.isValid = true;
            signal.startTime = TimeCurrent();
        }
        
        return signal;
    }
    
private:
    void UpdateBuffers(const double &prices[]) {
        ArrayCopy(m_priceBuffer, prices);
        
        // Calcula momentum para cada ponto
        for(int i = 0; i < m_period-1; i++) {
            m_momentumBuffer[i] = prices[i] - prices[i+1];
        }
    }
    
    double CalculateWaveStrength() {
        double strength = 0;
        double maxMove = 0;
        
        for(int i = 0; i < m_period-1; i++) {
            double move = MathAbs(m_priceBuffer[i] - m_priceBuffer[i+1]);
            strength += move;
            maxMove = MathMax(maxMove, move);
        }
        
        return maxMove > 0 ? MathMin(strength / (maxMove * m_period), 1.0) : 0;
    }
    
    double CalculateWaveMomentum(const double &volumes[]) {
        double momentum = 0;
        double volumeSum = 0;
        
        for(int i = 0; i < m_period-1; i++) {
            momentum += m_momentumBuffer[i] * volumes[i];
            volumeSum += volumes[i];
        }
        
        return volumeSum > 0 ? momentum / volumeSum : 0;
    }
    
    void IdentifyKeyLevels(WaveSignal &signal) {
        double high = m_priceBuffer[ArrayMaximum(m_priceBuffer, 0, m_period)];
        double low = m_priceBuffer[ArrayMinimum(m_priceBuffer, 0, m_period)];
        
        signal.resistance = high;
        signal.support = low;
    }
    
    bool DetermineWaveType(WaveSignal &signal) {
        if(signal.strength < m_minStrength / 10.0)
            return false;
            
        // Analisa padrão da onda
        if(IsTsunami(signal)) {
            signal.type = WAVE_TYPE_TSUNAMI;
            return true;
        }
        
        if(IsImpulse(signal)) {
            signal.type = WAVE_TYPE_IMPULSE;
            return true;
        }
        
        if(IsCorrection(signal)) {
            signal.type = WAVE_TYPE_CORRECTION;
            return true;
        }
        
        return false;
    }
    
    bool IsTsunami(const WaveSignal &signal) {
        // Verifica características de tsunami
        return signal.strength > 0.8 && MathAbs(signal.momentum) > m_minStrength;
    }
    
    bool IsImpulse(const WaveSignal &signal) {
        // Verifica características de onda de impulso
        return signal.momentum > 0 && signal.strength > 0.5;
    }
    
    bool IsCorrection(const WaveSignal &signal) {
        // Verifica características de onda corretiva
        return signal.momentum < 0 && signal.strength > 0.3;
    }
    
    bool IsWaveComplete(const WaveSignal &signal) {
        double currentPrice = m_priceBuffer[0];
        
        switch(signal.type) {
            case WAVE_TYPE_IMPULSE:
                return currentPrice >= signal.resistance;
                
            case WAVE_TYPE_CORRECTION:
                return currentPrice <= signal.support;
                
            case WAVE_TYPE_TSUNAMI:
                return signal.strength >= 0.9;
                
            default:
                return false;
        }
    }
    
    bool HasDivergence(const double &volumes[]) {
        double priceSlope = CalculateSlope(m_priceBuffer);
        double volumeSlope = CalculateSlope(volumes);
        
        return (priceSlope > 0 && volumeSlope < 0) || 
               (priceSlope < 0 && volumeSlope > 0);
    }
    
    double CalculateSlope(const double &data[]) {
        if(ArraySize(data) < 2)
            return 0;
            
        return (data[0] - data[ArraySize(data)-1]) / (ArraySize(data)-1);
    }
};