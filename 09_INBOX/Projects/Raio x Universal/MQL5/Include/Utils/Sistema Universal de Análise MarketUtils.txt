//+------------------------------------------------------------------+
//|                                                MarketUtils.mqh |
//|                                    Sistema Universal de Análise |
//|                                           RaioX Trading System |
//+------------------------------------------------------------------+
#property copyright "RaioX Trading System"
#property link      ""
#property version   "1.0"

#include "..\Core\MarketCore.mqh"

// Estrutura para estatísticas de mercado
struct MarketStats {
    double avgVolume;           // Volume médio
    double volStdDev;          // Desvio padrão do volume
    double avgRange;           // Range médio
    double rangeStdDev;       // Desvio padrão do range
    double momentum;           // Momentum
    double volatility;         // Volatilidade
    double correlation;        // Correlação preço/volume
    
    void Init() {
        avgVolume = 0;
        volStdDev = 0;
        avgRange = 0;
        rangeStdDev = 0;
        momentum = 0;
        volatility = 0;
        correlation = 0;
    }
};

// Estrutura para força do mercado
struct MarketStrength {
    double bullPower;          // Força dos compradores
    double bearPower;          // Força dos vendedores
    double netStrength;        // Força líquida
    double momentum;           // Momentum
    double pressure;           // Pressão do mercado
    
    void Init() {
        bullPower = 0;
        bearPower = 0;
        netStrength = 0;
        momentum = 0;
        pressure = 0;
    }
    
    bool IsBullish() const {
        return netStrength > 0 && momentum > 0;
    }
    
    bool IsBearish() const {
        return netStrength < 0 && momentum < 0;
    }
};

// Classe para cálculos estatísticos
class CStatistics {
public:
    static double Mean(const double &data[]) {
        int size = ArraySize(data);
        if(size == 0) return 0;
        
        double sum = 0;
        for(int i = 0; i < size; i++)
            sum += data[i];
            
        return sum / size;
    }
    
    static double StdDev(const double &data[], double mean = 0) {
        int size = ArraySize(data);
        if(size < 2) return 0;
        
        if(mean == 0)
            mean = Mean(data);
            
        double sum = 0;
        for(int i = 0; i < size; i++)
            sum += MathPow(data[i] - mean, 2);
            
        return MathSqrt(sum / (size - 1));
    }
    
    static double Correlation(const double &x[], const double &y[]) {
        int size = MathMin(ArraySize(x), ArraySize(y));
        if(size < 2) return 0;
        
        double sumX = 0, sumY = 0, sumXY = 0;
        double sumX2 = 0, sumY2 = 0;
        
        for(int i = 0; i < size; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
            sumY2 += y[i] * y[i];
        }
        
        double numerator = size * sumXY - sumX * sumY;
        double denominator = MathSqrt((size * sumX2 - sumX * sumX) * (size * sumY2 - sumY * sumY));
        
        return denominator != 0 ? numerator / denominator : 0;
    }
    
    static double ZScore(double value, double mean, double stdDev) {
        return stdDev != 0 ? (value - mean) / stdDev : 0;
    }
};

// Classe principal de utilidades
class CMarketUtils {
private:
    int m_period;
    
public:
    void CMarketUtils() {
        m_period = 20;
    }
    
    bool Initialize(int period = 20) {
        m_period = period;
        return true;
    }
    
    MarketStats CalculateStats(const double &prices[], const double &volumes[]) {
        MarketStats stats;
        stats.Init();
        
        if(ArraySize(prices) < m_period || ArraySize(volumes) < m_period)
            return stats;
            
        // Calcula estatísticas de volume
        stats.avgVolume = CStatistics::Mean(volumes);
        stats.volStdDev = CStatistics::StdDev(volumes, stats.avgVolume);
        
        // Calcula ranges
        double ranges[];
        ArrayResize(ranges, m_period-1);
        for(int i = 0; i < m_period-1; i++)
            ranges[i] = MathAbs(prices[i] - prices[i+1]);
            
        stats.avgRange = CStatistics::Mean(ranges);
        stats.rangeStdDev = CStatistics::StdDev(ranges, stats.avgRange);
        
        // Calcula momentum e volatilidade
        stats.momentum = CalculateMomentum(prices);
        stats.volatility = stats.rangeStdDev / stats.avgRange;
        
        // Calcula correlação
        stats.correlation = CStatistics::Correlation(prices, volumes);
        
        return stats;
    }
    
    MarketStrength AnalyzeStrength(const double &prices[], const double &volumes[]) {
        MarketStrength strength;
        strength.Init();
        
        if(ArraySize(prices) < m_period || ArraySize(volumes) < m_period)
            return strength;
            
        // Calcula forças
        for(int i = 0; i < m_period-1; i++) {
            double move = prices[i] - prices[i+1];
            double vol = volumes[i];
            
            if(move > 0)
                strength.bullPower += move * vol;
            else
                strength.bearPower += MathAbs(move) * vol;
        }
        
        // Calcula força líquida
        strength.netStrength = strength.bullPower - strength.bearPower;
        
        // Calcula momentum
        strength.momentum = CalculateMomentum(prices);
        
        // Calcula pressão do mercado
        strength.pressure = (strength.bullPower + strength.bearPower) / m_period;
        
        return strength;
    }
    
private:
    double CalculateMomentum(const double &prices[]) {
        if(ArraySize(prices) < m_period)
            return 0;
            
        return prices[0] - prices[m_period-1];
    }
};