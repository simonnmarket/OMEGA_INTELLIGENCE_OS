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
#include "FractalAnalysis.mqh"
#include "VolatilityAnalysis.mqh"

class TimeframeHierarchy {
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int m_ma_fast_handle;
    int m_ma_slow_handle;
    int m_ma_trend_handle;
    int m_rsi_handle;
    int m_adx_handle;
    bool m_is_initialized;
    
    // Validações
    bool ValidateSymbol(string symbol) {
        return (symbol != NULL && symbol != "");
    }
    
    bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe) {
        return (timeframe > 0);
    }
    
public:
    TimeframeHierarchy() {
        m_symbol = NULL;
        m_timeframe = PERIOD_CURRENT;
        m_ma_fast_handle = INVALID_HANDLE;
        m_ma_slow_handle = INVALID_HANDLE;
        m_ma_trend_handle = INVALID_HANDLE;
        m_rsi_handle = INVALID_HANDLE;
        m_adx_handle = INVALID_HANDLE;
        m_is_initialized = false;
    }
    
    ~TimeframeHierarchy() {
        Release();
    }
    
    bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe) {
        if(m_is_initialized) {
            Print("TimeframeHierarchy já inicializado");
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
        
        m_symbol = symbol;
        m_timeframe = timeframe;
        
        // Inicializar indicadores
        m_ma_fast_handle = iMA(m_symbol, m_timeframe, 8, 0, MODE_EMA, PRICE_CLOSE);
        if(m_ma_fast_handle == INVALID_HANDLE) {
            Print("Erro ao criar MA rápida: ", GetLastError());
            return false;
        }
        
        m_ma_slow_handle = iMA(m_symbol, m_timeframe, 20, 0, MODE_EMA, PRICE_CLOSE);
        if(m_ma_slow_handle == INVALID_HANDLE) {
            Print("Erro ao criar MA lenta: ", GetLastError());
            IndicatorRelease(m_ma_fast_handle);
            m_ma_fast_handle = INVALID_HANDLE;
            return false;
        }
        
        m_ma_trend_handle = iMA(m_symbol, m_timeframe, 50, 0, MODE_SMA, PRICE_CLOSE);
        if(m_ma_trend_handle == INVALID_HANDLE) {
            Print("Erro ao criar MA de tendência: ", GetLastError());
            IndicatorRelease(m_ma_fast_handle);
            IndicatorRelease(m_ma_slow_handle);
            m_ma_fast_handle = INVALID_HANDLE;
            m_ma_slow_handle = INVALID_HANDLE;
            return false;
        }
        
        m_rsi_handle = iRSI(m_symbol, m_timeframe, 14, PRICE_CLOSE);
        if(m_rsi_handle == INVALID_HANDLE) {
            Print("Erro ao criar RSI: ", GetLastError());
            IndicatorRelease(m_ma_fast_handle);
            IndicatorRelease(m_ma_slow_handle);
            IndicatorRelease(m_ma_trend_handle);
            m_ma_fast_handle = INVALID_HANDLE;
            m_ma_slow_handle = INVALID_HANDLE;
            m_ma_trend_handle = INVALID_HANDLE;
            return false;
        }
        
        m_adx_handle = iADX(m_symbol, m_timeframe, 14);
        if(m_adx_handle == INVALID_HANDLE) {
            Print("Erro ao criar ADX: ", GetLastError());
            IndicatorRelease(m_ma_fast_handle);
            IndicatorRelease(m_ma_slow_handle);
            IndicatorRelease(m_ma_trend_handle);
            IndicatorRelease(m_rsi_handle);
            m_ma_fast_handle = INVALID_HANDLE;
            m_ma_slow_handle = INVALID_HANDLE;
            m_ma_trend_handle = INVALID_HANDLE;
            m_rsi_handle = INVALID_HANDLE;
            return false;
        }
        
        m_is_initialized = true;
        return true;
    }
    
    void Release() {
        if(!m_is_initialized) return;
        
        if(m_ma_fast_handle != INVALID_HANDLE) {
            IndicatorRelease(m_ma_fast_handle);
            m_ma_fast_handle = INVALID_HANDLE;
        }
        
        if(m_ma_slow_handle != INVALID_HANDLE) {
            IndicatorRelease(m_ma_slow_handle);
            m_ma_slow_handle = INVALID_HANDLE;
        }
        
        if(m_ma_trend_handle != INVALID_HANDLE) {
            IndicatorRelease(m_ma_trend_handle);
            m_ma_trend_handle = INVALID_HANDLE;
        }
        
        if(m_rsi_handle != INVALID_HANDLE) {
            IndicatorRelease(m_rsi_handle);
            m_rsi_handle = INVALID_HANDLE;
        }
        
        if(m_adx_handle != INVALID_HANDLE) {
            IndicatorRelease(m_adx_handle);
            m_adx_handle = INVALID_HANDLE;
        }
        
        m_is_initialized = false;
    }
    
    bool IsInitialized() const {
        return m_is_initialized;
    }
    
    double GetMAFast(int shift) {
        if(!m_is_initialized || m_ma_fast_handle == INVALID_HANDLE) return 0;
        double buffer[];
        if(CopyBuffer(m_ma_fast_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
    double GetMASlow(int shift) {
        if(!m_is_initialized || m_ma_slow_handle == INVALID_HANDLE) return 0;
        double buffer[];
        if(CopyBuffer(m_ma_slow_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
    double GetMATrend(int shift) {
        if(!m_is_initialized || m_ma_trend_handle == INVALID_HANDLE) return 0;
        double buffer[];
        if(CopyBuffer(m_ma_trend_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
    double GetRSI(int shift) {
        if(!m_is_initialized || m_rsi_handle == INVALID_HANDLE) return 0;
        double buffer[];
        if(CopyBuffer(m_rsi_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
    double GetADX(int shift) {
        if(!m_is_initialized || m_adx_handle == INVALID_HANDLE) return 0;
        double buffer[];
        if(CopyBuffer(m_adx_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
}; 