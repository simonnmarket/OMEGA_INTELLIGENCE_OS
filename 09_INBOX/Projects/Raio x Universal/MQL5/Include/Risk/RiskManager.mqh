//+------------------------------------------------------------------+
//|                                               RiskManager.mqh |
//|                                    Sistema Universal de Análise |
//|                                           RaioX Trading System |
//+------------------------------------------------------------------+
#property copyright "RaioX Trading System"
#property link      ""
#property version   "1.0"

#include <Trade\Trade.mqh>
#include "..\Core\MarketCore.mqh"

// Estrutura para informações da posição
struct PositionInfo {
    ulong  ticket;           // Ticket da posição
    double entryPrice;       // Preço de entrada
    double currentPrice;     // Preço atual
    double stopLoss;        // Stop Loss
    double takeProfit;      // Take Profit
    double lots;            // Volume
    double riskMoney;       // Risco em dinheiro
    double riskPercent;     // Risco em percentual
    
    void Init() {
        ticket = 0;
        entryPrice = 0;
        currentPrice = 0;
        stopLoss = 0;
        takeProfit = 0;
        lots = 0;
        riskMoney = 0;
        riskPercent = 0;
    }
};

// Estrutura para plano de escalonamento
struct ScalingPlan {
    double initialLots;     // Lote inicial
    double maxLots;         // Lote máximo
    int    maxScales;       // Número máximo de escalas
    int    currentScale;    // Escala atual
    
    void Init(double initLots, double maxLot, int maxScal) {
        initialLots = initLots;
        maxLots = maxLot;
        maxScales = maxScal;
        currentScale = 0;
    }
    
    bool CanScale() {
        return currentScale < maxScales;
    }
    
    double GetNextLot() {
        double nextLot = initialLots * (1.0 + currentScale * 0.5);
        return MathMin(nextLot, maxLots);
    }
};

// Classe principal de gerenciamento de risco
class CRiskManager {
private:
    double         m_initialLots;    // Lote inicial
    double         m_maxLots;        // Lote máximo
    int            m_maxScales;      // Máximo de escalas
    double         m_maxRiskPercent; // Risco máximo por operação
    int            m_atrPeriod;      // Período do ATR
    double         m_atrMultiplier;  // Multiplicador do ATR
    ScalingPlan    m_scalingPlan;    // Plano de escalonamento
    CTrade         m_trade;          // Objeto de trading
    int            m_atrHandle;      // Handle do ATR
    
public:
    void CRiskManager() {
        m_initialLots = 0.1;
        m_maxLots = 1.0;
        m_maxScales = 3;
        m_maxRiskPercent = 2.0;
        m_atrPeriod = 14;
        m_atrMultiplier = 1.5;
        m_atrHandle = INVALID_HANDLE;
    }
    
    ~CRiskManager() {
        if(m_atrHandle != INVALID_HANDLE)
            IndicatorRelease(m_atrHandle);
    }
    
    bool Initialize(double initialLots, double maxLots, int maxScales, 
                   double maxRiskPercent = 2.0, int atrPeriod = 14, double atrMultiplier = 1.5) {
        m_initialLots = initialLots;
        m_maxLots = maxLots;
        m_maxScales = maxScales;
        m_maxRiskPercent = maxRiskPercent;
        m_atrPeriod = atrPeriod;
        m_atrMultiplier = atrMultiplier;
        
        m_scalingPlan.Init(initialLots, maxLots, maxScales);
        
        // Inicializa o ATR
        m_atrHandle = iATR(_Symbol, PERIOD_CURRENT, m_atrPeriod);
        return m_atrHandle != INVALID_HANDLE;
    }
    
    bool ValidateNewPosition(const double entryPrice, const double stopLoss, const double lots) {
        if(lots <= 0 || lots > m_maxLots)
            return false;
            
        double riskMoney = CalculateRiskMoney(entryPrice, stopLoss, lots);
        double accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        double riskPercent = (riskMoney / accountEquity) * 100;
        
        return riskPercent <= m_maxRiskPercent;
    }
    
    double CalculatePositionSize(const double stopDistance) {
        if(stopDistance <= 0)
            return 0;
            
        double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        double accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        
        double riskMoney = accountEquity * (m_maxRiskPercent / 100);
        double moneyPerPip = riskMoney / (stopDistance / tickSize);
        double lots = moneyPerPip / tickValue;
        
        return NormalizeLots(lots);
    }
    
    bool CanScalePosition() {
        return m_scalingPlan.CanScale();
    }
    
    double GetScalingLots() {
        return m_scalingPlan.GetNextLot();
    }
    
    double GetATRValue() {
        double atrBuffer[];
        ArraySetAsSeries(atrBuffer, true);
        
        if(CopyBuffer(m_atrHandle, 0, 0, 1, atrBuffer) <= 0)
            return 0;
            
        return atrBuffer[0];
    }
    
    double CalculateATRStop(const bool isBuy) {
        double atr = GetATRValue();
        if(atr == 0) return 0;
        
        double currentPrice = isBuy ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                                    SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                                    
        return isBuy ? currentPrice - (atr * m_atrMultiplier) : 
                      currentPrice + (atr * m_atrMultiplier);
    }
    
    void UpdateDynamicStops(const ulong ticket) {
        if(!PositionSelectByTicket(ticket))
            return;
            
        double currentStop = PositionGetDouble(POSITION_SL);
        double atr = GetATRValue();
        if(atr == 0) return;
        
        bool isBuy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
        double newStop = isBuy ? currentStop + (atr * 0.5) : currentStop - (atr * 0.5);
        newStop = NormalizePrice(newStop);
        
        if(MathAbs(currentStop - newStop) > _Point)
            m_trade.PositionModify(ticket, newStop, PositionGetDouble(POSITION_TP));
    }
    
private:
    double CalculateRiskMoney(const double entryPrice, const double stopLoss, const double lots) {
        double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        double stopDistance = MathAbs(entryPrice - stopLoss);
        
        return (stopDistance / tickSize) * tickValue * lots;
    }
    
    double NormalizeLots(const double lots) {
        double minLots = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
        double maxLots = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
        double stepLots = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
        
        double normalizedLots = MathRound(lots / stepLots) * stepLots;
        normalizedLots = MathMax(minLots, MathMin(normalizedLots, m_maxLots));
        
        return normalizedLots;
    }
    
    double NormalizePrice(const double price) {
        double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        return MathRound(price / tickSize) * tickSize;
    }
};