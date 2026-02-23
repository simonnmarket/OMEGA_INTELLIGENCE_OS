#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include "..\Math\Statistics.mqh"
#include "..\Math\FractalAnalysis.mqh"

class TimeframeHierarchy {
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframes[6];
    double m_trend_strength[];
    double m_trend_alignment[];
    int m_ma_period;
    int m_rsi_period;
    int m_adx_period;
    
    // Métodos privados
    double CalculateTrendStrength(ENUM_TIMEFRAMES timeframe) {
        double ma_fast = iMA(m_symbol, timeframe, 8, 0, MODE_EMA, PRICE_CLOSE, 0);
        double ma_slow = iMA(m_symbol, timeframe, 21, 0, MODE_EMA, PRICE_CLOSE, 0);
        double ma_very_slow = iMA(m_symbol, timeframe, 55, 0, MODE_EMA, PRICE_CLOSE, 0);
        
        double rsi = iRSI(m_symbol, timeframe, 14, PRICE_CLOSE, 0);
        double adx = iADX(m_symbol, timeframe, 14, PRICE_CLOSE, MODE_MAIN, 0);
        
        // Calcula força da tendência
        double trend_strength = 0;
        
        // Direção da tendência
        if(ma_fast > ma_slow && ma_slow > ma_very_slow) {
            trend_strength += 40; // Tendência de alta forte
        } else if(ma_fast < ma_slow && ma_slow < ma_very_slow) {
            trend_strength += 40; // Tendência de baixa forte
        } else if(ma_fast > ma_slow || ma_slow > ma_very_slow) {
            trend_strength += 20; // Tendência de alta fraca
        } else if(ma_fast < ma_slow || ma_slow < ma_very_slow) {
            trend_strength += 20; // Tendência de baixa fraca
        }
        
        // Força da tendência (ADX)
        trend_strength += adx * 0.6; // ADX contribui com até 60 pontos
        
        // Momentum (RSI)
        if(rsi > 70 || rsi < 30) {
            trend_strength += 20; // RSI extremo indica tendência forte
        } else if(rsi > 60 || rsi < 40) {
            trend_strength += 10; // RSI moderado indica tendência moderada
        }
        
        return MathMin(100, trend_strength);
    }
    
    double CalculateTrendAlignment(ENUM_TIMEFRAMES tf1, ENUM_TIMEFRAMES tf2) {
        double ma1 = iMA(m_symbol, tf1, 21, 0, MODE_EMA, PRICE_CLOSE, 0);
        double ma2 = iMA(m_symbol, tf2, 21, 0, MODE_EMA, PRICE_CLOSE, 0);
        
        double close1 = iClose(m_symbol, tf1, 0);
        double close2 = iClose(m_symbol, tf2, 0);
        
        // Calcula alinhamento
        double alignment = 0;
        
        // Alinhamento de médias
        if((ma1 > close1 && ma2 > close2) || (ma1 < close1 && ma2 < close2)) {
            alignment += 50; // Alinhamento forte
        } else if((ma1 > close1 || ma2 > close2) && (ma1 < close1 || ma2 < close2)) {
            alignment += 25; // Alinhamento parcial
        }
        
        // Alinhamento de preços
        double price_diff1 = (close1 - ma1) / ma1;
        double price_diff2 = (close2 - ma2) / ma2;
        
        if(MathAbs(price_diff1 - price_diff2) < 0.001) {
            alignment += 50; // Alinhamento forte
        } else if(MathAbs(price_diff1 - price_diff2) < 0.002) {
            alignment += 25; // Alinhamento parcial
        }
        
        return alignment / 100.0; // Normaliza para [-1, 1]
    }
    
public:
    TimeframeHierarchy() {
        m_symbol = Symbol();
        
        // Inicializa timeframes
        m_timeframes[0] = PERIOD_M1;
        m_timeframes[1] = PERIOD_M5;
        m_timeframes[2] = PERIOD_M15;
        m_timeframes[3] = PERIOD_H1;
        m_timeframes[4] = PERIOD_H4;
        m_timeframes[5] = PERIOD_D1;
        
        // Inicializa arrays
        ArrayResize(m_trend_strength, ArraySize(m_timeframes));
        ArrayResize(m_trend_alignment, ArraySize(m_timeframes) - 1);
        
        // Inicializa valores
        ArrayInitialize(m_trend_strength, 0);
        ArrayInitialize(m_trend_alignment, 0);
        
        m_ma_period = 20;
        m_rsi_period = 14;
        m_adx_period = 14;
    }
    
    void Update() {
        // Atualiza força da tendência
        for(int i=0; i<ArraySize(m_timeframes); i++) {
            m_trend_strength[i] = CalculateTrendStrength(m_timeframes[i]);
        }
        
        // Atualiza alinhamento
        for(int i=0; i<ArraySize(m_timeframes)-1; i++) {
            m_trend_alignment[i] = CalculateTrendAlignment(m_timeframes[i], m_timeframes[i+1]);
        }
    }
    
    double GetTrendStrength(ENUM_TIMEFRAMES timeframe) {
        for(int i=0; i<ArraySize(m_timeframes); i++) {
            if(m_timeframes[i] == timeframe) {
                return m_trend_strength[i];
            }
        }
        return 0;
    }
    
    double GetTrendAlignment(ENUM_TIMEFRAMES tf1, ENUM_TIMEFRAMES tf2) {
        for(int i=0; i<ArraySize(m_timeframes)-1; i++) {
            if(m_timeframes[i] == tf1 && m_timeframes[i+1] == tf2) {
                return m_trend_alignment[i];
            }
        }
        return 0;
    }
    
    bool IsAligned(ENUM_TIMEFRAMES tf1, ENUM_TIMEFRAMES tf2) {
        return MathAbs(GetTrendAlignment(tf1, tf2)) > 0.7;
    }
    
    bool IsStrongTrend(ENUM_TIMEFRAMES timeframe) {
        return GetTrendStrength(timeframe) > 70;
    }
    
    ENUM_TIMEFRAMES GetDominantTimeframe() {
        double max_strength = 0;
        ENUM_TIMEFRAMES dominant = PERIOD_CURRENT;
        
        for(int i=0; i<ArraySize(m_timeframes); i++) {
            if(m_trend_strength[i] > max_strength) {
                max_strength = m_trend_strength[i];
                dominant = m_timeframes[i];
            }
        }
        
        return dominant;
    }
    
    // Obter tendência
    int GetTrend(const ENUM_TIMEFRAMES timeframe)
    {
        double ma[];
        ArraySetAsSeries(ma, true);
        ArrayResize(ma, 2);
        
        int handle = iMA(m_symbol, timeframe, m_ma_period, 0, MODE_SMA, PRICE_CLOSE);
        if(handle == INVALID_HANDLE) return 0;
        
        if(CopyBuffer(handle, 0, 0, 2, ma) > 0)
        {
            IndicatorRelease(handle);
            return ma[0] > ma[1] ? 1 : -1;
        }
        
        IndicatorRelease(handle);
        return 0;
    }
    
    // Obter sobrecompra/sobrevenda
    double GetRSI(const ENUM_TIMEFRAMES timeframe)
    {
        double rsi[];
        ArraySetAsSeries(rsi, true);
        ArrayResize(rsi, 1);
        
        int handle = iRSI(m_symbol, timeframe, m_rsi_period, PRICE_CLOSE);
        if(handle == INVALID_HANDLE) return 50.0;
        
        if(CopyBuffer(handle, 0, 0, 1, rsi) > 0)
        {
            IndicatorRelease(handle);
            return rsi[0];
        }
        
        IndicatorRelease(handle);
        return 50.0;
    }
    
    // Configurar parâmetros
    void SetParameters(const string symbol, const int ma_period, const int rsi_period, const int adx_period)
    {
        m_symbol = symbol;
        m_ma_period = ma_period;
        m_rsi_period = rsi_period;
        m_adx_period = adx_period;
    }
}; 