//+------------------------------------------------------------------+
//|                                              VolumeDetector.mqh |
//|                                    Sistema Universal de Análise |
//|                                           RaioX Trading System |
//+------------------------------------------------------------------+
#property copyright "RaioX Trading System"
#property link      ""
#property version   "1.0"

#include "..\Core\MarketCore.mqh"

// Classe para detecção de padrões de volume
class CVolumeDetector {
private:
    int      m_period;           // Período de análise
    double   m_threshold;        // Limiar para detecção
    double   m_volumeMA[];       // Média móvel de volume
    double   m_volumeStdDev;     // Desvio padrão do volume
    
public:
    void CVolumeDetector() {
        m_period = 20;
        m_threshold = 1.5;
        m_volumeStdDev = 0;
        ArrayResize(m_volumeMA, m_period);
        ArrayInitialize(m_volumeMA, 0);
    }
    
    bool Initialize(int period = 20, double threshold = 1.5) {
        m_period = period;
        m_threshold = threshold;
        ArrayResize(m_volumeMA, m_period);
        ArrayInitialize(m_volumeMA, 0);
        return true;
    }
    
    VolumeSignal Analyze(const double &volumes[], const double &prices[]) {
        VolumeSignal signal;
        signal.Init();
        
        if(ArraySize(volumes) < m_period || ArraySize(prices) < m_period)
            return signal;
            
        // Atualiza médias e desvio padrão
        UpdateVolumeStats(volumes);
        
        // Analisa padrões de volume
        if(IsVolumeClimax(volumes[0])) {
            signal.isValid = true;
            signal.strength = CalculateSignalStrength(volumes[0]);
            signal.time = TimeCurrent();
            
            // Determina tipo de ação do volume
            DetermineVolumeAction(volumes, prices, signal);
        }
        
        return signal;
    }
    
private:
    void UpdateVolumeStats(const double &volumes[]) {
        // Calcula média móvel
        double sum = 0;
        for(int i = 0; i < m_period; i++) {
            sum += volumes[i];
            m_volumeMA[i] = sum / (i + 1);
        }
        
        // Calcula desvio padrão
        double sumSquares = 0;
        for(int i = 0; i < m_period; i++) {
            sumSquares += MathPow(volumes[i] - m_volumeMA[0], 2);
        }
        m_volumeStdDev = MathSqrt(sumSquares / m_period);
    }
    
    bool IsVolumeClimax(double currentVolume) {
        if(m_volumeMA[0] <= 0 || m_volumeStdDev <= 0)
            return false;
            
        // Verifica se o volume atual é significativamente maior que a média
        double zScore = (currentVolume - m_volumeMA[0]) / m_volumeStdDev;
        return zScore > m_threshold;
    }
    
    double CalculateSignalStrength(double currentVolume) {
        if(m_volumeMA[0] <= 0)
            return 0;
            
        double ratio = currentVolume / m_volumeMA[0];
        return MathMin(ratio / 2, 1.0); // Normaliza entre 0 e 1
    }
    
    void DetermineVolumeAction(const double &volumes[], const double &prices[], VolumeSignal &signal) {
        // Verifica os últimos 3 períodos para determinar a ação do volume
        double priceChange = prices[0] - prices[2];
        double volumeChange = volumes[0] - volumes[2];
        
        if(priceChange > 0 && volumeChange > 0) {
            // Volume crescente com preço subindo = Absorção
            signal.isAbsorption = true;
        }
        else if(priceChange < 0 && volumeChange > 0) {
            // Volume crescente com preço caindo = Distribuição
            signal.isDistribution = true;
        }
    }
    
    bool IsVolumeBreakout(const double &volumes[], const double &prices[]) {
        if(ArraySize(volumes) < m_period || ArraySize(prices) < m_period)
            return false;
            
        // Verifica se há um aumento significativo no volume com movimento de preço
        double volumeRatio = volumes[0] / m_volumeMA[0];
        double priceChange = MathAbs(prices[0] - prices[1]);
        double avgPriceChange = CalculateAveragePriceChange(prices);
        
        return volumeRatio > m_threshold && priceChange > avgPriceChange;
    }
    
    double CalculateAveragePriceChange(const double &prices[]) {
        double sum = 0;
        for(int i = 1; i < m_period; i++) {
            sum += MathAbs(prices[i] - prices[i-1]);
        }
        return sum / (m_period - 1);
    }
    
    bool IsVolumeDivergence(const double &volumes[], const double &prices[]) {
        if(ArraySize(volumes) < m_period || ArraySize(prices) < m_period)
            return false;
            
        // Verifica divergência entre preço e volume
        double priceDirection = prices[0] - prices[m_period-1];
        double volumeDirection = volumes[0] - volumes[m_period-1];
        
        return (priceDirection > 0 && volumeDirection < 0) || 
               (priceDirection < 0 && volumeDirection > 0);
    }
};