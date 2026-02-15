//+------------------------------------------------------------------+
//|                                    BigPlayersAnalysis.mq5         |
//|                                     Version 1.0                   |
//|                                     Título: Identificação de Big Players |
//+------------------------------------------------------------------+

#property copyright "Samsung Global Market"
#property version   "1.0"
#property strict

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Enums e Definições                                                |
//+------------------------------------------------------------------+
enum ENUM_TRADE_SIGNAL {
    SIGNAL_NONE,
    SIGNAL_BUY,
    SIGNAL_SELL
};

enum ENUM_MARKET_CONDITION {
    CONDITION_TRENDING,
    CONDITION_RANGING,
    CONDITION_VOLATILE,
    CONDITION_UNDEFINED
};

enum ENUM_ORDER_STATUS {
    ORDER_PENDING,
    ORDER_EXECUTED,
    ORDER_REJECTED,
    ORDER_CANCELED
};

enum ENUM_PLAYER_TYPE {
    PLAYER_INSTITUTIONAL,
    PLAYER_INDIVIDUAL,
    PLAYER_HFUND,
    PLAYER_UNDEFINED
};

//+------------------------------------------------------------------+
//| Estruturas Principais                                             |
//+------------------------------------------------------------------+
struct MarketData {
    double open;
    double high;
    double low;
    double close;

    double volume;
    double volumeMA;
    double volumeDelta;

    double trend;
    double momentum;
    double volatility;

    double valueAreaHigh;
    double valueAreaLow;
    double poc; // Point of Control

    ENUM_MARKET_CONDITION condition;
    bool isValid;
    datetime lastUpdate;
};

struct PlayerData {
    ENUM_PLAYER_TYPE type;
    double influence;
    double activityLevel;
    string name;
    bool isValid;
};

struct TradeSetup {
    ENUM_TRADE_SIGNAL signal;
    double entry;
    double stopLoss;
    double takeProfit;
    double volume;
    double risk;
    double reward;
    double confidence;
    string reason;
    bool isValid;
};

struct PerformanceMetrics {
    int totalTrades;
    int winTrades;
    int lossTrades;
    double profitFactor;
    double winRate;
    double maxDrawdown;
    double sharpeRatio;
    datetime lastUpdate;
};

struct RiskMetrics {
    double currentRisk;
    double maxRisk;
    double exposure;
    double heatLevel;
    bool isValid;
};

//+------------------------------------------------------------------+
//| Variáveis Globais                                                 |
//+------------------------------------------------------------------+
CTrade trade;
MarketData marketData;
PlayerData playerData;
TradeSetup setup;
PerformanceMetrics performance;
RiskMetrics risk;

double maBuffer[];
double volumeBuffer[];
double atrBuffer[];

int maHandle = INVALID_HANDLE;
int volumeHandle = INVALID_HANDLE;
int atrHandle = INVALID_HANDLE;

string logFile = "big_players_logs.txt";
int dailyTrades = 0;
int consecutiveLosses = 0;
double currentDrawdown = 0;

input int TimeframeMin = 5; // Timeframe (minutos)
input double RiskPercent = 1.0; // Risco por operação (%)
input int MaxDailyTrades = 3; // Máximo trades diários
input bool UseBreakEven = true; // Usar Break Even
input int BreakEvenPoints = 300; // Pontos para Break Even

input double VolumeThreshold = 1.5; // Multiplicador de volume
input int VolumePeriod = 20; // Período da média móvel de volume

input int StopLoss = 400; // Stop Loss (pontos)
input int TakeProfit = 800; // Take Profit (pontos)

input double MinimumMomentum = 0.5; // Momentum mínimo
input double MaxDrawdown = 1000; // Drawdown máximo permitido
input int TrailingStopPoints = 200; // Pontos para trailing stop

//+------------------------------------------------------------------+
//| Funções Auxiliares                                                |
//+------------------------------------------------------------------+
void Log(string message) {
    Print(message);
    int handle = FileOpen(logFile, FILE_WRITE | FILE_TXT);
    if(handle != INVALID_HANDLE) {
        FileWriteString(handle, TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES) + " - " + message + "\n");
        FileClose(handle);
    }
}

double CalculatePositionSize(double accountBalance, double riskPercent, double stopDistance) {
    double riskAmount = accountBalance * (riskPercent / 100);
    double lotSize = NormalizeDouble(riskAmount / (stopDistance * SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE)), 2);
    return MathMin(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), MathMax(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), lotSize));
}

bool IsMarketOpen() {
    datetime time = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(time, dt);

    if(dt.day_of_week == 0 || dt.day_of_week == 6) return false; // Não opera em finais de semana.
    if(dt.hour < 9 || dt.hour >= 18) return false; // Horário comercial: 9h-18h.

    return true;
}

bool IsHighSpread() {
    double currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point;
    double maxSpread = 5 * _Point; // Spread máximo permitido.
    return (currentSpread > maxSpread);
}

bool HasSufficientVolume() {
    double relativeVolume = marketData.volume / marketData.volumeMA;
    return (relativeVolume > VolumeThreshold);
}

bool CheckDailyLimits() {
    if(dailyTrades >= MaxDailyTrades) return false;
    if(currentDrawdown > MaxDrawdown) return false;

    return true;
}

//+------------------------------------------------------------------+
//| Classe Principal do Sistema                                       |
//+------------------------------------------------------------------+
class CBigPlayersManager {
private:
    struct AnalysisResult {
        bool trendValid;
        bool volumeValid;
        bool priceValid;
        bool flowValid;
        double confidence;
        string analysis;
    };

public:
    CBigPlayersManager() {
        InitializeMetrics();
    }

    ~CBigPlayersManager() {
        Cleanup();
    }

    bool Initialize() {
        if(!InitializeIndicators()) {
            Print("Erro ao inicializar indicadores!");
            return false;
        }
        ConfigureTrade();
        InitializeMetrics();
        return true;
    }

    void ProcessTick() {
        if(!ValidateMarket()) return;

        UpdateMarketData();

        if(AnalyzeMarket()) {
            if(IdentifyBigPlayers()) {
                GenerateSignals();
                ExecuteTrades();
            }
        }

        ManagePositions();
        UpdateMetrics();
    }

private:
    bool InitializeIndicators() {
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_EMA, PRICE_CLOSE); // Média Móvel Exponencial.
        if(maHandle == INVALID_HANDLE) return false;

        volumeHandle = iVolume(_Symbol, PERIOD_CURRENT, VOLUME_TICK); // Volume Tick.
        if(volumeHandle == INVALID_HANDLE) return false;

        atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14); // Average True Range.
        if(atrHandle == INVALID_HANDLE) return false;

        ArraySetAsSeries(maBuffer, true);
        ArraySetAsSeries(volumeBuffer, true);
        ArraySetAsSeries(atrBuffer, true);

        CopyBuffer(maHandle, 0, 0, 100, maBuffer);
        CopyBuffer(volumeHandle, 0, 0, 100, volumeBuffer);
        CopyBuffer(atrHandle, 0, 0, 100, atrBuffer);

        return true;
    }

    void ConfigureTrade() {
        trade.SetDeviationInPoints(10);
        trade.SetTypeFilling(ORDER_FILLING_FOK);
        trade.LogLevel(LOG_LEVEL_ERRORS);
    }

    void InitializeMetrics() {
        dailyTrades = 0;
        consecutiveLosses = 0;
        currentDrawdown = 0;

        performance.totalTrades = 0;
        performance.winTrades = 0;
        performance.lossTrades = 0;
        performance.profitFactor = 0;
        performance.maxDrawdown = 0;
        performance.sharpeRatio = 0;
        performance.lastUpdate = TimeCurrent();

        risk.maxRisk = RiskPercent;
        risk.currentRisk = 0;
        risk.exposure = 0;
        risk.isValid = true;
    }

    bool ValidateMarket() {
        if(!IsMarketOpen()) return false;
        if(IsHighSpread()) return false;
        if(!HasSufficientVolume()) return false;
        if(!CheckDailyLimits()) return false;

        return true;
    }

    void UpdateMarketData() {
        marketData.open = iOpen(_Symbol, PERIOD_CURRENT, 0);
        marketData.high = iHigh(_Symbol, PERIOD_CURRENT, 0);
        marketData.low = iLow(_Symbol, PERIOD_CURRENT, 0);
        marketData.close = iClose(_Symbol, PERIOD_CURRENT, 0);

        CopyBuffer(maHandle, 0, 0, 3, maBuffer);
        CopyBuffer(volumeHandle, 0, 0, 3, volumeBuffer);
        CopyBuffer(atrHandle, 0, 0, 3, atrBuffer);

        marketData.volume = iVolume(_Symbol, PERIOD_CURRENT, 0);
        marketData.volumeMA = CalculateVolumeMA();
        marketData.volumeDelta = CalculateVolumeDelta();

        marketData.trend = CalculateTrend();
        marketData.momentum = CalculateMomentum();
        marketData.volatility = atrBuffer[0];

        marketData.valueAreaHigh = CalculateValueAreaHigh();
        marketData.valueAreaLow = CalculateValueAreaLow();
        marketData.poc = CalculatePOC();

        marketData.condition = DetermineMarketCondition();

        marketData.isValid = true;
        marketData.lastUpdate = TimeCurrent();
    }

    bool AnalyzeMarket() {
        if(!marketData.isValid) return false;

        AnalysisResult analysis;
        analysis.trendValid = AnalyzeTrend();
        analysis.volumeValid = AnalyzeVolume();
        analysis.priceValid = AnalyzePrice();
        analysis.flowValid = AnalyzeFlow();

        analysis.confidence = 0;
        analysis.confidence += analysis.trendValid ? 0.25 : 0;
        analysis.confidence += analysis.volumeValid ? 0.25 : 0;
        analysis.confidence += analysis.priceValid ? 0.25 : 0;
        analysis.confidence += analysis.flowValid ? 0.25 : 0;

        return (analysis.confidence >= 0.75);
    }

    bool IdentifyBigPlayers() {
        playerData.type = DeterminePlayerType();
        playerData.influence = CalculatePlayerInfluence();
        playerData.activityLevel = CalculateActivityLevel();

        if(playerData.influence > 0.8 && playerData.activityLevel > 0.7) {
            playerData.isValid = true;
            return true;
        }

        return false;
    }

    void GenerateSignals() {
        switch(marketData.condition) {
            case CONDITION_TRENDING:
                setup.signal = (marketData.volumeDelta > 0 ? SIGNAL_BUY : SIGNAL_SELL);
                setup.entry = marketData.close;
                setup.stopLoss = (setup.signal == SIGNAL_BUY ? marketData.low - StopLoss * _Point : marketData.high + StopLoss * _Point);
                setup.takeProfit = (setup.signal == SIGNAL_BUY ? marketData.close + TakeProfit * _Point : marketData.close - TakeProfit * _Point);
                setup.isValid = true;
                break;

            case CONDITION_RANGING:
                setup.signal = SIGNAL_NONE;
                setup.isValid = false;
                break;

            case CONDITION_VOLATILE:
                setup.signal = SIGNAL_NONE;
                setup.isValid = false;
                break;

            default:
                setup.signal = SIGNAL_NONE;
                setup.isValid = false;
                break;
        }
    }

    void ExecuteTrades() {
        if(!setup.isValid) return;

        setup.volume = CalculatePositionSize(AccountInfoDouble(ACCOUNT_BALANCE), RiskPercent, MathAbs(setup.entry - setup.stopLoss));

        switch(setup.signal) {
            case SIGNAL_BUY:
                ExecuteBuy();
                break;

            case SIGNAL_SELL:
                ExecuteSell();
                break;
        }
    }

    void ManagePositions() {
        if(!PositionSelect(_Symbol)) return;

        if(UseBreakEven) {
            CheckBreakEven();
        }

        UpdateStops();
        CheckExit();
    }

    void UpdateMetrics() {
        if(dailyTrades >= MaxDailyTrades) {
            Log("Limite diário de trades atingido.");
        }

        if(currentDrawdown > MaxDrawdown) {
            Log("Drawdown máximo excedido.");
        }
    }

    void Cleanup() {
        IndicatorRelease(maHandle);
        IndicatorRelease(volumeHandle);
        IndicatorRelease(atrHandle);

        if(PositionSelect(_Symbol)) {
            trade.PositionClose(_Symbol);
        }
    }

    //+------------------------------------------------------------------+
    //| Funções de Cálculo                                                |
    //+------------------------------------------------------------------+
    double CalculateVolumeMA() {
        double sum = 0;
        for(int i = 0; i < VolumePeriod; i++) {
            sum += volumeBuffer[i];
        }
        return sum / VolumePeriod;
    }

    double CalculateVolumeDelta() {
        if(marketData.close > marketData.open) {
            return marketData.volume;
        } else if(marketData.close < marketData.open) {
            return -marketData.volume;
        }
        return 0;
    }

    double CalculatePlayerInfluence() {
        double relativeVolume = marketData.volume / marketData.volumeMA;
        return NormalizeDouble(relativeVolume, 2);
    }

    double CalculateActivityLevel() {
        double volatility = MathAbs(marketData.high - marketData.low) / marketData.open * 100;
        return NormalizeDouble(volatility, 2);
    }

    double CalculatePOC() {
        double sumVolume = 0;
        double sumPrice = 0;

        for(int i = 0; i < VolumePeriod; i++) {
            sumVolume += volumeBuffer[i];
            sumPrice += iClose(_Symbol, PERIOD_CURRENT, i) * volumeBuffer[i];
        }

        return sumVolume != 0 ? sumPrice / sumVolume : 0;
    }

    double CalculateValueAreaHigh() {
        double stdDev = CalculateVolatilityAroundPOC();
        return marketData.poc + stdDev;
    }

    double CalculateValueAreaLow() {
        double stdDev = CalculateVolatilityAroundPOC();
        return marketData.poc - stdDev;
    }

    double CalculateVolatilityAroundPOC() {
        double mean = marketData.poc;
        double sumSquaredDiff = 0;

        for(int i = 0; i < VolumePeriod; i++) {
            double price = iClose(_Symbol, PERIOD_CURRENT, i);
            sumSquaredDiff += MathPow(price - mean, 2) * volumeBuffer[i];
        }

        double variance = sumSquaredDiff / CalculateTotalVolume();
        return MathSqrt(variance);
    }

    double CalculateTotalVolume() {
        double sum = 0;
        for(int i = 0; i < VolumePeriod; i++) {
            sum += volumeBuffer[i];
        }
        return sum;
    }

    double CalculateTrend() {
        return (maBuffer[0] - maBuffer[2]) / maBuffer[2] * 100;
    }

    double CalculateMomentum() {
        return (marketData.close - marketData.open) / marketData.open * 100;
    }

    //+------------------------------------------------------------------+
    //| Funções de Análise                                                |
    //+------------------------------------------------------------------+
    bool AnalyzeTrend() {
        bool trendUp = (maBuffer[0] > maBuffer[1] && maBuffer[1] > maBuffer[2]);
        bool trendDown = (maBuffer[0] < maBuffer[1] && maBuffer[1] < maBuffer[2]);

        return trendUp || trendDown;
    }

    bool AnalyzeVolume() {
        double relativeVolume = marketData.volume / marketData.volumeMA;
        return (relativeVolume > VolumeThreshold);
    }

    bool AnalyzePrice() {
        return (MathAbs(marketData.momentum) > MinimumMomentum);
    }

    bool AnalyzeFlow() {
        bool buyingPressure = (marketData.volumeDelta > 0);
        bool sellingPressure = (marketData.volumeDelta < 0);

        return buyingPressure || sellingPressure;
    }

    ENUM_MARKET_CONDITION DetermineMarketCondition() {
        if(MathAbs(marketData.trend) > 0.5) {
            return CONDITION_TRENDING;
        } else if(MathAbs(marketData.momentum) < 0.1) {
            return CONDITION_RANGING;
        } else if(marketData.volatility > 0.01) {
            return CONDITION_VOLATILE;
        }

        return CONDITION_UNDEFINED;
    }

    ENUM_PLAYER_TYPE DeterminePlayerType() {
        if(CalculatePlayerInfluence() > 0.9 && CalculateActivityLevel() > 0.8) {
            return PLAYER_INSTITUTIONAL;
        } else if(CalculatePlayerInfluence() > 0.7 && CalculateActivityLevel() > 0.6) {
            return PLAYER_HFUND;
        }

        return PLAYER_INDIVIDUAL;
    }

    //+------------------------------------------------------------------+
    //| Funções de Trading                                               |
    //+------------------------------------------------------------------+
    void ExecuteBuy() {
        if(!trade.Buy(
            setup.volume,
            _Symbol,
            setup.entry,
            setup.stopLoss,
            setup.takeProfit,
            "Big Players Analysis - Buy"
        )) {
            Log("Erro na execução da compra: " + IntegerToString(GetLastError()));
            return;
        }

        Log("Compra executada com sucesso.");
    }

    void ExecuteSell() {
        if(!trade.Sell(
            setup.volume,
            _Symbol,
            setup.entry,
            setup.stopLoss,
            setup.takeProfit,
            "Big Players Analysis - Sell"
        )) {
            Log("Erro na execução da venda: " + IntegerToString(GetLastError()));
            return;
        }

        Log("Venda executada com sucesso.");
    }

    void CheckBreakEven() {
        if(!UseBreakEven || !PositionSelect(_Symbol)) return;

        double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);

        if(setup.signal == SIGNAL_BUY && currentPrice - openPrice > BreakEvenPoints * _Point) {
            if(trade.PositionModify(_Symbol, openPrice, PositionGetDouble(POSITION_TP))) {
                Log("Break even ativado para compra.");
            }
        } else if(setup.signal == SIGNAL_SELL && openPrice - currentPrice > BreakEvenPoints * _Point) {
            if(trade.PositionModify(_Symbol, openPrice, PositionGetDouble(POSITION_TP))) {
                Log("Break even ativado para venda.");
            }
        }
    }

    void UpdateStops() {
        if(!PositionSelect(_Symbol)) return;

        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double trailingDistance = TrailingStopPoints * _Point;

        if(setup.signal == SIGNAL_BUY && currentPrice - PositionGetDouble(POSITION_PRICE_OPEN) > trailingDistance) {
            double newStopLoss = currentPrice - trailingDistance;
            trade.PositionModify(_Symbol, newStopLoss, PositionGetDouble(POSITION_TP));
        } else if(setup.signal == SIGNAL_SELL && PositionGetDouble(POSITION_PRICE_OPEN) - currentPrice > trailingDistance) {
            double newStopLoss = currentPrice + trailingDistance;
            trade.PositionModify(_Symbol, newStopLoss, PositionGetDouble(POSITION_TP));
        }
    }

    void CheckExit() {
        if(!PositionSelect(_Symbol)) return;

        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double stopLoss = PositionGetDouble(POSITION_SL);
        double takeProfit = PositionGetDouble(POSITION_TP);

        if(setup.signal == SIGNAL_BUY && (currentPrice <= stopLoss || currentPrice >= takeProfit)) {
            ClosePosition();
        } else if(setup.signal == SIGNAL_SELL && (currentPrice >= stopLoss || currentPrice <= takeProfit)) {
            ClosePosition();
        }
    }

    void ClosePosition() {
        if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
            trade.Sell(PositionGetInteger(POSITION_TICKET), "", 0, 0, 0, "Big Players Analysis - Close Buy");
        } else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL) {
            trade.Buy(PositionGetInteger(POSITION_TICKET), "", 0, 0, 0, "Big Players Analysis - Close Sell");
        }

        Log("Posição fechada com sucesso.");
    }
};