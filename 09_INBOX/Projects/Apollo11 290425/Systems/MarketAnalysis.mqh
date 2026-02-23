#property copyright "Market Analysis System"
#property strict

class CMarketAnalysis {
private:
    // Handles para indicadores
    int maHandle;
    int rsiHandle;
    int macdHandle;
    int bbandsHandle;
    
    // Configurações
    int maPeriod;
    int rsiPeriod;
    int macdFast;
    int macdSlow;
    int macdSignal;
    int bbandsPeriod;
    double bbandsDeviation;
    
    // Métricas
    double trendStrength;
    double momentum;
    double volatility;
    double marketBias;
    
public:
    CMarketAnalysis(int maPer = 20, int rsiPer = 14, 
                   int macdF = 12, int macdS = 26, int macdSig = 9,
                   int bbandsPer = 20, double bbandsDev = 2.0) {
        maPeriod = maPer;
        rsiPeriod = rsiPer;
        macdFast = macdF;
        macdSlow = macdS;
        macdSignal = macdSig;
        bbandsPeriod = bbandsPer;
        bbandsDeviation = bbandsDev;
        
        // Inicializa indicadores
        maHandle = iMA(_Symbol, PERIOD_CURRENT, maPeriod, 0, MODE_SMA, PRICE_CLOSE);
        rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, rsiPeriod, PRICE_CLOSE);
        macdHandle = iMACD(_Symbol, PERIOD_CURRENT, macdFast, macdSlow, macdSignal, PRICE_CLOSE);
        bbandsHandle = iBands(_Symbol, PERIOD_CURRENT, bbandsPeriod, 0, bbandsDeviation, PRICE_CLOSE);
    }
    
    ~CMarketAnalysis() {
        if(maHandle != INVALID_HANDLE) IndicatorRelease(maHandle);
        if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
        if(macdHandle != INVALID_HANDLE) IndicatorRelease(macdHandle);
        if(bbandsHandle != INVALID_HANDLE) IndicatorRelease(bbandsHandle);
    }
    
    bool Initialize() {
        if(maHandle == INVALID_HANDLE || rsiHandle == INVALID_HANDLE ||
           macdHandle == INVALID_HANDLE || bbandsHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores em CMarketAnalysis");
            return false;
        }
        return true;
    }
    
    void Process() {
        // Calcula força da tendência
        CalculateTrendStrength();
        
        // Calcula momentum
        CalculateMomentum();
        
        // Calcula volatilidade
        CalculateVolatility();
        
        // Calcula viés do mercado
        CalculateMarketBias();
        
        Print("Análise de Mercado:",
              "\nForça da Tendência: ", trendStrength,
              "\nMomentum: ", momentum,
              "\nVolatilidade: ", volatility,
              "\nViés do Mercado: ", marketBias);
    }
    
    void CalculateTrendStrength() {
        double ma[];
        ArraySetAsSeries(ma, true);
        if(CopyBuffer(maHandle, 0, 0, 2, ma) <= 0) return;
        
        double close[];
        ArraySetAsSeries(close, true);
        if(CopyBuffer(maHandle, 0, 0, 2, close) <= 0) return;
        
        // Calcula força baseada na distância do preço à média móvel
        trendStrength = MathAbs(close[0] - ma[0]) / ma[0] * 100.0;
    }
    
    void CalculateMomentum() {
        double rsi[];
        ArraySetAsSeries(rsi, true);
        if(CopyBuffer(rsiHandle, 0, 0, 2, rsi) <= 0) return;
        
        // Normaliza o RSI para um valor entre -1 e 1
        momentum = (rsi[0] - 50.0) / 50.0;
    }
    
    void CalculateVolatility() {
        double upper[], lower[];
        ArraySetAsSeries(upper, true);
        ArraySetAsSeries(lower, true);
        
        if(CopyBuffer(bbandsHandle, 1, 0, 1, upper) <= 0) return;
        if(CopyBuffer(bbandsHandle, 2, 0, 1, lower) <= 0) return;
        
        // Calcula volatilidade baseada na largura das bandas
        volatility = (upper[0] - lower[0]) / lower[0] * 100.0;
    }
    
    void CalculateMarketBias() {
        double macd[], signal[];
        ArraySetAsSeries(macd, true);
        ArraySetAsSeries(signal, true);
        
        if(CopyBuffer(macdHandle, 0, 0, 2, macd) <= 0) return;
        if(CopyBuffer(macdHandle, 1, 0, 2, signal) <= 0) return;
        
        // Calcula viés baseado no MACD
        if(macd[0] > signal[0] && macd[1] <= signal[1]) {
            marketBias = 1.0; // Viés de alta
        }
        else if(macd[0] < signal[0] && macd[1] >= signal[1]) {
            marketBias = -1.0; // Viés de baixa
        }
        else {
            marketBias = 0.0; // Neutro
        }
    }
    
    double GetTrendStrength() {
        return trendStrength;
    }
    
    double GetMomentum() {
        return momentum;
    }
    
    double GetVolatility() {
        return volatility;
    }
    
    double GetMarketBias() {
        return marketBias;
    }
}; 