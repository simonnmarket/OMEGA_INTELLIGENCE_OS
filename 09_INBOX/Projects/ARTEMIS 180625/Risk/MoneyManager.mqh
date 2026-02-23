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
#include "TimeframeHierarchy.mqh"
#include "Statistics.mqh"
#include "VolatilityAnalysis.mqh"
#include "PortfolioBalancer.mqh"
#include "DynamicLotManager.mqh"
#include "AdaptiveRiskSystem.mqh"
#include "RiskManager.mqh"

class MoneyManager {
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    double m_risk_per_trade;
    double m_max_daily_risk;
    double m_max_drawdown;
    int m_atr_period;
    int m_atr_handle;
    TimeframeHierarchy* m_timeframe_hierarchy;
    Statistics* m_statistics;
    VolatilityAnalysis* m_volatility;
    PortfolioBalancer* m_portfolio;
    DynamicLotManager* m_lot_manager;
    AdaptiveRiskSystem* m_risk_system;
    RiskManager* m_risk_manager;
    bool m_is_initialized;
    
    // Validações
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
    
public:
    MoneyManager() {
        m_symbol = NULL;
        m_timeframe = PERIOD_CURRENT;
        m_risk_per_trade = 0.02;
        m_max_daily_risk = 0.05;
        m_max_drawdown = 0.15;
        m_atr_period = 14;
        m_atr_handle = INVALID_HANDLE;
        m_timeframe_hierarchy = NULL;
        m_statistics = NULL;
        m_volatility = NULL;
        m_portfolio = NULL;
        m_lot_manager = NULL;
        m_risk_system = NULL;
        m_risk_manager = NULL;
        m_is_initialized = false;
    }
    
    ~MoneyManager() {
        Release();
    }
    
    bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe, double risk_per_trade = 0.02, double max_daily_risk = 0.05, double max_drawdown = 0.15, int atr_period = 14) {
        if(m_is_initialized) {
            Print("MoneyManager já inicializado");
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
        
        // Inicializar ATR
        m_atr_handle = iATR(m_symbol, m_timeframe, m_atr_period);
        if(m_atr_handle == INVALID_HANDLE) {
            Print("Erro ao criar ATR: ", GetLastError());
            return false;
        }
        
        // Inicializar componentes
        m_timeframe_hierarchy = new TimeframeHierarchy();
        if(!m_timeframe_hierarchy.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar TimeframeHierarchy");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            return false;
        }
        
        m_statistics = new Statistics();
        if(!m_statistics.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar Statistics");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            delete m_statistics;
            m_statistics = NULL;
            return false;
        }
        
        m_volatility = new VolatilityAnalysis();
        if(!m_volatility.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar VolatilityAnalysis");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
            delete m_volatility;
            m_volatility = NULL;
            return false;
        }
        
        m_portfolio = new PortfolioBalancer();
        if(!m_portfolio.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar PortfolioBalancer");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
            delete m_portfolio;
            m_portfolio = NULL;
            return false;
        }
        
        m_lot_manager = new DynamicLotManager();
        if(!m_lot_manager.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar DynamicLotManager");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
            m_portfolio.Release();
            delete m_portfolio;
            m_portfolio = NULL;
            delete m_lot_manager;
            m_lot_manager = NULL;
            return false;
        }
        
        m_risk_system = new AdaptiveRiskSystem();
        if(!m_risk_system.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar AdaptiveRiskSystem");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
            m_portfolio.Release();
            delete m_portfolio;
            m_portfolio = NULL;
            m_lot_manager.Release();
            delete m_lot_manager;
            m_lot_manager = NULL;
            delete m_risk_system;
            m_risk_system = NULL;
            return false;
        }
        
        m_risk_manager = new RiskManager();
        if(!m_risk_manager.Initialize(symbol, timeframe)) {
            Print("Erro ao inicializar RiskManager");
            IndicatorRelease(m_atr_handle);
            m_atr_handle = INVALID_HANDLE;
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
            m_portfolio.Release();
            delete m_portfolio;
            m_portfolio = NULL;
            m_lot_manager.Release();
            delete m_lot_manager;
            m_lot_manager = NULL;
            m_risk_system.Release();
            delete m_risk_system;
            m_risk_system = NULL;
            delete m_risk_manager;
            m_risk_manager = NULL;
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
        
        if(m_timeframe_hierarchy != NULL) {
            m_timeframe_hierarchy.Release();
            delete m_timeframe_hierarchy;
            m_timeframe_hierarchy = NULL;
        }
        
        if(m_statistics != NULL) {
            m_statistics.Release();
            delete m_statistics;
            m_statistics = NULL;
        }
        
        if(m_volatility != NULL) {
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
        }
        
        if(m_portfolio != NULL) {
            m_portfolio.Release();
            delete m_portfolio;
            m_portfolio = NULL;
        }
        
        if(m_lot_manager != NULL) {
            m_lot_manager.Release();
            delete m_lot_manager;
            m_lot_manager = NULL;
        }
        
        if(m_risk_system != NULL) {
            m_risk_system.Release();
            delete m_risk_system;
            m_risk_system = NULL;
        }
        
        if(m_risk_manager != NULL) {
            m_risk_manager.Release();
            delete m_risk_manager;
            m_risk_manager = NULL;
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
    
    bool CheckDailyRisk() {
        if(!m_is_initialized) return false;
        
        double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double account_equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double daily_profit = account_equity - account_balance;
        
        double max_daily_loss = account_balance * m_max_daily_risk;
        
        return (daily_profit >= -max_daily_loss);
    }
    
    bool CheckDrawdown() {
        if(!m_is_initialized) return false;
        
        double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double account_equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double drawdown = (account_balance - account_equity) / account_balance;
        
        return (drawdown <= m_max_drawdown);
    }
    
    double CalculatePositionSize(double stop_loss_points) {
        if(!m_is_initialized) return 0;
        
        double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double risk_amount = account_balance * m_risk_per_trade;
        
        double tick_size = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_SIZE);
        double tick_value = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE);
        double point_value = tick_value / tick_size;
        
        double position_size = risk_amount / (stop_loss_points * point_value);
        
        // Normalizar para o lote mínimo
        double min_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double max_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
        double lot_step = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        
        position_size = MathFloor(position_size / lot_step) * lot_step;
        position_size = MathMax(min_lot, MathMin(max_lot, position_size));
        
        return position_size;
    }
    
    double CalculateSortinoRatio() {
        if(!m_is_initialized || m_statistics == NULL) return 0;
        return m_statistics.CalculateSortinoRatio();
    }
    
    double CalculateCalmarRatio() {
        if(!m_is_initialized || m_statistics == NULL) return 0;
        return m_statistics.CalculateCalmarRatio();
    }
    
    bool IsVolatile() {
        if(!m_is_initialized || m_volatility == NULL) return false;
        return m_volatility.IsVolatile();
    }
    
    double GetVolatility() {
        if(!m_is_initialized || m_volatility == NULL) return 0;
        return m_volatility.GetVolatility();
    }
    
    bool IsTrending() {
        if(!m_is_initialized || m_timeframe_hierarchy == NULL) return false;
        return m_timeframe_hierarchy.IsTrending();
    }
    
    bool IsUptrend() {
        if(!m_is_initialized || m_timeframe_hierarchy == NULL) return false;
        return m_timeframe_hierarchy.IsUptrend();
    }
    
    bool IsDowntrend() {
        if(!m_is_initialized || m_timeframe_hierarchy == NULL) return false;
        return m_timeframe_hierarchy.IsDowntrend();
    }
    
    double GetTrendStrength() {
        if(!m_is_initialized || m_timeframe_hierarchy == NULL) return 0;
        return m_timeframe_hierarchy.GetTrendStrength();
    }
}; 