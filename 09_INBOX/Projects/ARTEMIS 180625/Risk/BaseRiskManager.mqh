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

//+------------------------------------------------------------------+
//| Base class for all risk management components                     |
//+------------------------------------------------------------------+
class CBaseRiskManager
{
protected:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    double m_risk_per_trade;
    double m_max_daily_risk;
    double m_max_drawdown;
    int m_atr_period;
    int m_atr_handle;
    bool m_is_initialized;
    
    // Common validation methods
    bool ValidateSymbol(string symbol) {
        return (symbol != NULL && symbol != "");
    }
    
    bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe) {
        return (timeframe > 0);
    }
    
    bool ValidateRisk(double risk) {
        return (risk > 0 && risk <= 1);
    }
    
    bool ValidatePeriod(int period) {
        return (period > 0);
    }
    
    // Common initialization method
    bool InitializeBase(string symbol, ENUM_TIMEFRAMES timeframe, double risk_per_trade = 0.02, 
                       double max_daily_risk = 0.05, double max_drawdown = 0.15, int atr_period = 14) {
        if(m_is_initialized) {
            Print("Componente já inicializado");
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
        
        if(!ValidateRisk(risk_per_trade)) {
            Print("Risco por trade inválido: ", risk_per_trade);
            return false;
        }
        
        if(!ValidateRisk(max_daily_risk)) {
            Print("Risco diário máximo inválido: ", max_daily_risk);
            return false;
        }
        
        if(!ValidateRisk(max_drawdown)) {
            Print("Drawdown máximo inválido: ", max_drawdown);
            return false;
        }
        
        if(!ValidatePeriod(atr_period)) {
            Print("Período ATR inválido: ", atr_period);
            return false;
        }
        
        m_symbol = symbol;
        m_timeframe = timeframe;
        m_risk_per_trade = risk_per_trade;
        m_max_daily_risk = max_daily_risk;
        m_max_drawdown = max_drawdown;
        m_atr_period = atr_period;
        
        // Initialize ATR
        m_atr_handle = iATR(m_symbol, m_timeframe, m_atr_period);
        if(m_atr_handle == INVALID_HANDLE) {
            Print("Erro ao inicializar ATR");
            return false;
        }
        
        m_is_initialized = true;
        return true;
    }
    
    // Common release method
    void ReleaseBase() {
        if(!m_is_initialized) return;
        
        if(m_atr_handle != INVALID_HANDLE) {
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
        }
        
        m_is_initialized = false;
    }
    
    // Common ATR getter
    double GetATR(int shift) {
        if(!m_is_initialized || m_atr_handle == INVALID_HANDLE) return 0;
        
        double buffer[];
        if(CopyBuffer(m_atr_handle, 0, shift, 1, buffer) <= 0) return 0;
        return buffer[0];
    }
    
public:
    CBaseRiskManager() {
        m_symbol = NULL;
        m_timeframe = PERIOD_CURRENT;
        m_risk_per_trade = 0.02;
        m_max_daily_risk = 0.05;
        m_max_drawdown = 0.15;
        m_atr_period = 14;
        m_atr_handle = INVALID_HANDLE;
        m_is_initialized = false;
    }
    
    virtual ~CBaseRiskManager() {
        ReleaseBase();
    }
    
    bool IsInitialized() const {
        return m_is_initialized;
    }
    
    // Getters
    string GetSymbol() const { return m_symbol; }
    ENUM_TIMEFRAMES GetTimeframe() const { return m_timeframe; }
    double GetRiskPerTrade() const { return m_risk_per_trade; }
    double GetMaxDailyRisk() const { return m_max_daily_risk; }
    double GetMaxDrawdown() const { return m_max_drawdown; }
    int GetATRPeriod() const { return m_atr_period; }
}; 