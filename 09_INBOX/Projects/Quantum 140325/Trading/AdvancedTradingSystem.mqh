#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include <Trade/Trade.mqh>
#include <Indicators/Trend.mqh>
#include <Indicators/Oscillators.mqh>
#include "../Core/QuantumCore.mqh"
#include "../Indicators/WeisWaves.mqh"
#include "../Indicators/VSA.mqh"

//+------------------------------------------------------------------+
//| Classe AdvancedTradingSystem                                       |
//+------------------------------------------------------------------+
class CAdvancedTradingSystem {
private:
    // Objetos de trading e indicadores
    CTrade*          m_trade;
    CiMA*            m_ema;
    CiRSI*           m_rsi;
    CWeisWaves*      m_weisWaves;
    CVSA*            m_vsa;
    
    // Parâmetros dos indicadores
    input int        m_emaPeriod = 20;        // Período EMA
    input int        m_rsiPeriod = 14;        // Período RSI
    input double     m_rsiOverbought = 70;    // Nível sobrecomprado RSI
    input double     m_rsiOversold = 30;      // Nível sobrevendido RSI
    
    // Estado da conexão
    bool             m_isConnected;
    string          m_lastError;
    
    // Métodos privados
    bool            ValidateConnection();
    bool            InitializeIndicators();
    void            CleanupIndicators();
    
public:
    // Construtor e destrutor
                    CAdvancedTradingSystem();
                   ~CAdvancedTradingSystem();
    
    // Métodos principais
    bool            InitializeConnection();
    bool            IsConnected() const { return m_isConnected; }
    string          GetLastError() const { return m_lastError; }
    
    // Métodos de análise
    double          GetEMAValue(int shift = 0);
    double          GetRSIValue(int shift = 0);
    double          GetWeisWaveValue(int shift = 0);
    VSASignal       GetVSASignal(int shift = 0);
    
    // Métodos de trading
    bool            ExecuteOrder(ENUM_ORDER_TYPE type, double volume, double price = 0.0);
    void            CloseAllPositions();
    
    // Métodos de gestão de risco
    double          CalculatePositionSize(double riskPercentage);
    bool            ValidateRiskParameters(double volume, double stopLoss);
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CAdvancedTradingSystem::CAdvancedTradingSystem() {
    m_trade = new CTrade();
    m_ema = new CiMA();
    m_rsi = new CiRSI();
    m_weisWaves = new CWeisWaves();
    m_vsa = new CVSA();
    m_isConnected = false;
    m_lastError = "";
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CAdvancedTradingSystem::~CAdvancedTradingSystem() {
    CleanupIndicators();
    delete m_trade;
}

//+------------------------------------------------------------------+
//| Inicializa conexão com MT5                                         |
//+------------------------------------------------------------------+
bool CAdvancedTradingSystem::InitializeConnection() {
    if(!ValidateConnection()) {
        m_lastError = "Failed to validate MT5 connection";
        return false;
    }
    
    if(!InitializeIndicators()) {
        m_lastError = "Failed to initialize indicators";
        return false;
    }
    
    m_isConnected = true;
    return true;
}

//+------------------------------------------------------------------+
//| Valida conexão com MT5                                            |
//+------------------------------------------------------------------+
bool CAdvancedTradingSystem::ValidateConnection() {
    if(!TerminalInfoInteger(TERMINAL_CONNECTED)) {
        m_lastError = "Terminal not connected to server";
        return false;
    }
    
    if(!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)) {
        m_lastError = "Trading not allowed for this account";
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicializa indicadores                                            |
//+------------------------------------------------------------------+
bool CAdvancedTradingSystem::InitializeIndicators() {
    // Inicializa EMA
    if(!m_ema.Create(_Symbol, PERIOD_CURRENT, m_emaPeriod, 0, MODE_EMA, PRICE_CLOSE)) {
        m_lastError = "Failed to create EMA indicator";
        return false;
    }
    
    // Inicializa RSI
    if(!m_rsi.Create(_Symbol, PERIOD_CURRENT, m_rsiPeriod, PRICE_CLOSE)) {
        m_lastError = "Failed to create RSI indicator";
        return false;
    }
    
    // Inicializa Weis Waves
    if(!m_weisWaves.Initialize(_Symbol, PERIOD_CURRENT)) {
        m_lastError = "Failed to initialize Weis Waves";
        return false;
    }
    
    // Inicializa VSA
    if(!m_vsa.Initialize(_Symbol, PERIOD_CURRENT)) {
        m_lastError = "Failed to initialize VSA";
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Limpa indicadores                                                  |
//+------------------------------------------------------------------+
void CAdvancedTradingSystem::CleanupIndicators() {
    delete m_ema;
    delete m_rsi;
    delete m_weisWaves;
    delete m_vsa;
}

//+------------------------------------------------------------------+
//| Obtém valor da EMA                                                |
//+------------------------------------------------------------------+
double CAdvancedTradingSystem::GetEMAValue(int shift = 0) {
    return m_ema.Main(shift);
}

//+------------------------------------------------------------------+
//| Obtém valor do RSI                                                |
//+------------------------------------------------------------------+
double CAdvancedTradingSystem::GetRSIValue(int shift = 0) {
    return m_rsi.Main(shift);
}

//+------------------------------------------------------------------+
//| Obtém valor das Weis Waves                                        |
//+------------------------------------------------------------------+
double CAdvancedTradingSystem::GetWeisWaveValue(int shift = 0) {
    return m_weisWaves.GetWaveValue(shift);
}

//+------------------------------------------------------------------+
//| Obtém sinal do VSA                                                |
//+------------------------------------------------------------------+
VSASignal CAdvancedTradingSystem::GetVSASignal(int shift = 0) {
    return m_vsa.GetSignal(shift);
}

//+------------------------------------------------------------------+
//| Executa ordem                                                      |
//+------------------------------------------------------------------+
bool CAdvancedTradingSystem::ExecuteOrder(ENUM_ORDER_TYPE type, double volume, double price = 0.0) {
    if(!m_isConnected) {
        m_lastError = "System not connected";
        return false;
    }
    
    if(!ValidateRiskParameters(volume, 0.0)) {
        return false;
    }
    
    switch(type) {
        case ORDER_TYPE_BUY:
            return m_trade.Buy(volume, _Symbol, price);
        case ORDER_TYPE_SELL:
            return m_trade.Sell(volume, _Symbol, price);
        default:
            m_lastError = "Invalid order type";
            return false;
    }
}

//+------------------------------------------------------------------+
//| Fecha todas as posições                                           |
//+------------------------------------------------------------------+
void CAdvancedTradingSystem::CloseAllPositions() {
    m_trade.PositionClose(_Symbol);
}

//+------------------------------------------------------------------+
//| Calcula tamanho da posição                                        |
//+------------------------------------------------------------------+
double CAdvancedTradingSystem::CalculatePositionSize(double riskPercentage) {
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = balance * (riskPercentage / 100.0);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    
    if(tickValue == 0) return 0;
    
    return NormalizeDouble(riskAmount / tickValue, 2);
}

//+------------------------------------------------------------------+
//| Valida parâmetros de risco                                        |
//+------------------------------------------------------------------+
bool CAdvancedTradingSystem::ValidateRiskParameters(double volume, double stopLoss) {
    if(volume <= 0) {
        m_lastError = "Invalid volume";
        return false;
    }
    
    double maxVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    if(volume > maxVolume) {
        m_lastError = "Volume exceeds maximum allowed";
        return false;
    }
    
    return true;
} 