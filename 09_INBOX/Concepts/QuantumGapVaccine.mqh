IMPLEMENTAÇÃO CONSOLIDADA - VACINA GAP v1.0
Data: 28/02/2024 

//+------------------------------------------------------------------+
//|                                    QuantumGapVaccine.mqh          |
//+------------------------------------------------------------------+

#property copyright "Quantum"
#property version   "1.0"

enum ENUM_GAP_TYPE {
    GAP_BREAKAWAY,    
    GAP_EXHAUSTION,   
    GAP_CONTINUATION, 
    GAP_COMMON,       
    GAP_HIDDEN        
};

class CQuantumGapVaccine {
private:
    struct GapAnalysis {
        ENUM_GAP_TYPE type;
        double size;
        double priceBeforeGap;
        double priceAfterGap;
        double volumeRatio;
        bool isFilled;
        datetime gapTime;
        bool isValid;
        double probability;
        double riskRatio;
    };
    
    struct MarketContext {
        bool isUptrend;
        double trendStrength;
        double volatility;
        double averageVolume;
        double currentVolume;
        double preMarketVolume;
        bool isHighVolume;
        bool isLowVolume;
    };
    
    struct VSAMetrics {
        double volumeForce;
        double spreadSize;
        bool isClimax;
        bool isChurn;
        double effort;
        double result;
    };
    
    struct Statistics {
        int totalGaps;
        int successfulGaps;
        double winRate;
        double averageReturn;
        double maxDrawdown;
        int consecutiveWins;
        int consecutiveLosses;
    };
    
    GapAnalysis gap;
    MarketContext market;
    VSAMetrics vsa;
    Statistics stats;
    
    // Handles e buffers
    int bbHandle;
    int maHandle;
    double volumeBuffer[];
    double priceBuffer[];
    
public:
    CQuantumGapVaccine() {
        InitializeVaccine();
    }
    
    ~CQuantumGapVaccine() {
        CleanupHandles();
    }
    
    bool Initialize() {
        bbHandle = iBands(_Symbol, PERIOD_CURRENT, 20, 0, 2.0, PRICE_CLOSE);
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
        
        if(bbHandle == INVALID_HANDLE || maHandle == INVALID_HANDLE)
            return false;
            
        ArraySetAsSeries(volumeBuffer, true);
        ArraySetAsSeries(priceBuffer, true);
        
        return true;
    }
    
    bool AnalyzeGap() {
        if(!UpdateMarketContext()) return false;
        if(!IdentifyGap()) return false;
        
        ClassifyGap();
        CalculateVSAMetrics();
        UpdateStatistics();
        
        return ValidateGapOpportunity();
    }
    
    GapAnalysis* GetGapAnalysis() {
        return &gap;
    }
    
    bool ShouldTrade() {
        if(!gap.isValid) return false;
        if(gap.probability < 0.65) return false;
        if(gap.riskRatio < 1.5) return false;
        
        return ValidateTradeConditions();
    }

private:
    void InitializeVaccine() {
        ResetStatistics();
        ConfigureDefaultParameters();
    }
    
    bool UpdateMarketContext() {
        market.currentVolume = GetCurrentVolume();
        market.averageVolume = CalculateAverageVolume(20);
        market.volatility = CalculateVolatility(14);
        market.isUptrend = IdentifyTrend();
        market.trendStrength = CalculateTrendStrength();
        
        return true;
    }
    
    void ClassifyGap() {
        if(IsBreakawayGap())
            gap.type = GAP_BREAKAWAY;
        else if(IsExhaustionGap())
            gap.type = GAP_EXHAUSTION;
        else if(IsContinuationGap())
            gap.type = GAP_CONTINUATION;
        else if(IsHiddenGap())
            gap.type = GAP_HIDDEN;
        else
            gap.type = GAP_COMMON;
            
        gap.probability = CalculateGapProbability();
        gap.riskRatio = CalculateRiskRewardRatio();
    }
    
    void CalculateVSAMetrics() {
        vsa.volumeForce = market.currentVolume / market.averageVolume;
        vsa.spreadSize = CalculateSpreadSize();
        vsa.isClimax = IsClimaxVolume();
        vsa.isChurn = IsChurnVolume();
        vsa.effort = CalculateEffort();
        vsa.result = CalculateResult();
    }
    
    bool ValidateGapOpportunity() {
        if(!ValidateVolumeConditions()) return false;
        if(!ValidatePriceAction()) return false;
        if(!ValidateMarketContext()) return false;
        
        gap.isValid = true;
        return true;
    }
    
    bool ValidateTradeConditions() {
        switch(gap.type) {
            case GAP_BREAKAWAY:   return ValidateBreakawayTrade();
            case GAP_EXHAUSTION:  return ValidateExhaustionTrade();
            case GAP_CONTINUATION: return ValidateContinuationTrade();
            case GAP_HIDDEN:      return ValidateHiddenGapTrade();
            default:              return false;
        }
    }
    
    void UpdateStatistics() {
        stats.totalGaps++;
        if(IsSuccessfulGap()) {
            stats.successfulGaps++;
            stats.consecutiveWins++;
            stats.consecutiveLosses = 0;
        } else {
            stats.consecutiveLosses++;
            stats.consecutiveWins = 0;
        }
        
        stats.winRate = (double)stats.successfulGaps / stats.totalGaps;
        stats.averageReturn = CalculateAverageReturn();
        stats.maxDrawdown = CalculateMaxDrawdown();
    }
};
//+------------------------------------------------------------------+
//|                                    QuantumGapTradeManager.mqh      |
//+------------------------------------------------------------------+

class CQuantumGapTradeManager {
private:
    struct TradeParameters {
        double entryPrice;
        double stopLoss;
        double takeProfit;
        double lotSize;
        datetime expiry;
        ENUM_GAP_TYPE gapType;
        bool isLong;
    };
    
    struct RiskParameters {
        double maxRiskPercent;
        double maxDrawdown;
        double minRiskReward;
        int maxDailyTrades;
        double maxPositionSize;
    };
    
    TradeParameters trade;
    RiskParameters risk;
    
public:
    bool PrepareGapTrade(const GapAnalysis* gap) {
        if(!ValidateGapTrade(gap)) return false;
        
        CalculateTradeParameters(gap);
        if(!ValidateRiskParameters()) return false;
        
        return true;
    }
    
    bool ExecuteGapTrade() {
        if(!IsValidTradingTime()) return false;
        if(!CheckMarketConditions()) return false;
        
        return OpenGapPosition();
    }
    
    void UpdateTradeStatus() {
        if(!PositionSelect(_Symbol)) return;
        
        ManageOpenPosition();
        UpdateStopLoss();
        CheckExpiryTime();
    }

private:
    bool ValidateGapTrade(const GapAnalysis* gap) {
        if(gap.probability < 0.65) return false;
        if(gap.riskRatio < risk.minRiskReward) return false;
        if(!CheckDailyTradeLimit()) return false;
        
        return true;
    }
    
    void CalculateTradeParameters(const GapAnalysis* gap) {
        trade.gapType = gap.type;
        trade.isLong = DetermineDirection(gap);
        
        CalculateEntryPrice(gap);
        CalculateStopLoss(gap);
        CalculateTakeProfit(gap);
        CalculateLotSize();
        SetExpiryTime(gap);
    }
    
    bool OpenGapPosition() {
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.symbol = _Symbol;
        request.volume = trade.lotSize;
        request.type = trade.isLong ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        request.price = trade.entryPrice;
        request.sl = trade.stopLoss;
        request.tp = trade.takeProfit;
        request.deviation = 5;
        request.magic = EXPERT_MAGIC;
        request.comment = "Gap Trade " + EnumToString(trade.gapType);
        
        return OrderSend(request, result);
    }
    
    void ManageOpenPosition() {
        if(ShouldModifyPosition()) {
            ModifyPosition();
        }
        
        if(ShouldClosePosition()) {
            ClosePosition();
        }
    }
    
    void UpdateStopLoss() {
        double newStopLoss = CalculateTrailingStop();
        if(newStopLoss != trade.stopLoss) {
            ModifyStopLoss(newStopLoss);
        }
    }
    
    bool CheckDailyTradeLimit() {
        int dailyTrades = CountDailyTrades();
        return dailyTrades < risk.maxDailyTrades;
    }
    
    double CalculateLotSize() {
        double accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        double riskAmount = accountEquity * risk.maxRiskPercent;
        double pipValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        double stopLossPoints = MathAbs(trade.entryPrice - trade.stopLoss) / _Point;
        
        return NormalizeDouble(riskAmount / (stopLossPoints * pipValue), 2);
    }
};

//+------------------------------------------------------------------+
//|                                    QuantumGapIndicator.mqh         |
//+------------------------------------------------------------------+

class CQuantumGapIndicator {
private:
    struct IndicatorBuffers {
        double gapBuffer[];
        double strengthBuffer[];
        double probabilityBuffer[];
        int colorBuffer[];
    };
    
    IndicatorBuffers buffers;
    int indicatorHandle;
    
public:
    bool Initialize() {
        ArraySetAsSeries(buffers.gapBuffer, true);
        ArraySetAsSeries(buffers.strengthBuffer, true);
        ArraySetAsSeries(buffers.probabilityBuffer, true);
        ArraySetAsSeries(buffers.colorBuffer, true);
        
        return true;
    }
    
    void UpdateIndicator(const GapAnalysis* gap) {
        if(!gap.isValid) return;
        
        UpdateBuffers(gap);
        DrawGapVisuals(gap);
        ShowGapInfo(gap);
    }
    
private:
    void UpdateBuffers(const GapAnalysis* gap) {
        buffers.gapBuffer[0] = gap.size;
        buffers.strengthBuffer[0] = gap.probability;
        buffers.probabilityBuffer[0] = gap.riskRatio;
        buffers.colorBuffer[0] = GetGapColor(gap);
    }
    
    void DrawGapVisuals(const GapAnalysis* gap) {
        string objName = "Gap_" + TimeToString(gap.gapTime);
        
        ObjectCreate(0, objName, OBJ_RECTANGLE, 0,
                    gap.gapTime, gap.priceBeforeGap,
                    TimeCurrent(), gap.priceAfterGap);
                    
        ObjectSetInteger(0, objName, OBJPROP_COLOR, GetGapColor(gap));
        ObjectSetInteger(0, objName, OBJPROP_STYLE, STYLE_SOLID);
        ObjectSetInteger(0, objName, OBJPROP_WIDTH, 1);
    }
    
    void ShowGapInfo(const GapAnalysis* gap) {
        string info = StringFormat("Gap Type: %s\nProbability: %.2f%%\nRisk Ratio: %.2f",
                                 EnumToString(gap.type),
                                 gap.probability * 100,
                                 gap.riskRatio);
                                 
        Comment(info);
    }
    
    color GetGapColor(const GapAnalysis* gap) {
        switch(gap.type) {
            case GAP_BREAKAWAY:   return clrBlue;
            case GAP_EXHAUSTION:  return clrRed;
            case GAP_CONTINUATION: return clrGreen;
            case GAP_HIDDEN:      return clrPurple;
            default:              return clrGray;
        }
    }
};