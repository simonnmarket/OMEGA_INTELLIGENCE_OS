#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

class FractalAnalysis {
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int m_period;
    bool m_is_initialized;
    
    // Validações
    bool ValidateSymbol(string symbol) {
        return (symbol != NULL && symbol != "");
    }
    
    bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe) {
        return (timeframe > 0);
    }
    
    bool ValidatePeriod(int period) {
        return (period > 0);
    }
    
public:
    FractalAnalysis() {
        m_symbol = NULL;
        m_timeframe = PERIOD_CURRENT;
        m_period = 5;
        m_is_initialized = false;
    }
    
    ~FractalAnalysis() {
        Release();
    }
    
    bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int period = 5) {
        if(m_is_initialized) {
            Print("FractalAnalysis já inicializado");
            return false;
        }
        
        if(!ValidateSymbol(symbol)) {
            Print("Símbolo inválido: ", symbol);
            return false;
        }
        
        if(!ValidateTimeframe(timeframe)) {
            Print("Timeframe inválido: ", timeframe);
            return false;
        }
        
        if(!ValidatePeriod(period)) {
            Print("Período inválido: ", period);
            return false;
        }
        
        m_symbol = symbol;
        m_timeframe = timeframe;
        m_period = period;
        
        m_is_initialized = true;
        return true;
    }
    
    void Release() {
        if(!m_is_initialized) return;
        m_is_initialized = false;
    }
    
    bool IsInitialized() const {
        return m_is_initialized;
    }
    
    bool IsBullishFractal(int shift) {
        if(!m_is_initialized) return false;
        
        double high[];
        if(CopyHigh(m_symbol, m_timeframe, shift - m_period, m_period * 2 + 1, high) <= 0) return false;
        
        // Verifica se o ponto central é o mais alto
        for(int i = 0; i < m_period; i++) {
            if(high[m_period] <= high[i]) return false;
            if(high[m_period] <= high[m_period * 2 - i]) return false;
        }
        
        return true;
    }
    
    bool IsBearishFractal(int shift) {
        if(!m_is_initialized) return false;
        
        double low[];
        if(CopyLow(m_symbol, m_timeframe, shift - m_period, m_period * 2 + 1, low) <= 0) return false;
        
        // Verifica se o ponto central é o mais baixo
        for(int i = 0; i < m_period; i++) {
            if(low[m_period] >= low[i]) return false;
            if(low[m_period] >= low[m_period * 2 - i]) return false;
        }
        
        return true;
    }
    
    int FindLastBullishFractal(int start_shift = 0, int max_bars = 100) {
        if(!m_is_initialized) return -1;
        
        for(int i = start_shift; i < max_bars; i++) {
            if(IsBullishFractal(i)) return i;
        }
        
        return -1;
    }
    
    int FindLastBearishFractal(int start_shift = 0, int max_bars = 100) {
        if(!m_is_initialized) return -1;
        
        for(int i = start_shift; i < max_bars; i++) {
            if(IsBearishFractal(i)) return i;
        }
        
        return -1;
    }
    
    double GetFractalLevel(int shift, bool is_bullish) {
        if(!m_is_initialized) return 0;
        
        if(is_bullish) {
            double high[];
            if(CopyHigh(m_symbol, m_timeframe, shift, 1, high) <= 0) return 0;
            return high[0];
        } else {
            double low[];
            if(CopyLow(m_symbol, m_timeframe, shift, 1, low) <= 0) return 0;
            return low[0];
        }
    }
}; 