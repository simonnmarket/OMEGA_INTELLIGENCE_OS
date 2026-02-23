#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Object.mqh>
#include <StdLibErr.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>

class VolatilityAnalysis {
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int m_atr_period;
    int m_atr_handle;
    double m_volatility_threshold;
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
    
    bool ValidateThreshold(double threshold) {
        return (threshold > 0);
    }
    
public:
    VolatilityAnalysis() {
        m_symbol = NULL;
        m_timeframe = PERIOD_CURRENT;
        m_atr_period = 14;
        m_atr_handle = INVALID_HANDLE;
        m_volatility_threshold = 0.002;
        m_is_initialized = false;
    }
    
    ~VolatilityAnalysis() {
        Release();
    }
    
    bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int atr_period = 14, double volatility_threshold = 0.002) {
        if(m_is_initialized) {
            Print("VolatilityAnalysis já inicializado");
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
        
        if(!ValidatePeriod(atr_period)) {
            Print("Período ATR inválido: ", atr_period);
            return false;
        }
        
        if(!ValidateThreshold(volatility_threshold)) {
            Print("Limite de volatilidade inválido: ", volatility_threshold);
            return false;
        }
        
        m_symbol = symbol;
        m_timeframe = timeframe;
        m_atr_period = atr_period;
        m_volatility_threshold = volatility_threshold;
        
        // Inicializar ATR
        m_atr_handle = iATR(m_symbol, m_timeframe, m_atr_period);
        if(m_atr_handle == INVALID_HANDLE) {
            Print("Erro ao criar ATR: ", GetLastError());
            return false;
        }
        
        m_is_initialized = true;
        return true;
    }
    
    void Release() {
        if(!m_is_initialized) return;
        
        if(m_atr_handle != INVALID_HANDLE) {
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
        }
        
        m_is_initialized = false;
    }
    
    bool IsInitialized() const {
        return m_is_initialized;
    }
    
    double GetATR(int shift) {
        if(!m_is_initialized || m_atr_handle == INVALID_HANDLE) return 0;
        
        double buffer[];
        if(CopyBuffer(m_atr_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
    bool IsVolatile() {
        if(!m_is_initialized) return false;
        
        double atr = GetATR(0);
        double close = iClose(m_symbol, m_timeframe, 0);
        
        if(close == 0) return false;
        
        double volatility = atr / close;
        return (volatility > m_volatility_threshold);
    }
    
    double GetVolatility() {
        if(!m_is_initialized) return 0;
        
        double atr = GetATR(0);
        double close = iClose(m_symbol, m_timeframe, 0);
        
        if(close == 0) return 0;
        
        return atr / close;
    }
    
    double GetVolatilityRatio() {
        if(!m_is_initialized) return 0;
        
        double atr1 = GetATR(0);
        double atr2 = GetATR(1);
        
        if(atr2 == 0) return 0;
        
        return atr1 / atr2;
    }
    
    bool IsVolatilityIncreasing() {
        if(!m_is_initialized) return false;
        
        double ratio = GetVolatilityRatio();
        return (ratio > 1.0);
    }
    
    bool IsVolatilityDecreasing() {
        if(!m_is_initialized) return false;
        
        double ratio = GetVolatilityRatio();
        return (ratio < 1.0);
    }
}; 