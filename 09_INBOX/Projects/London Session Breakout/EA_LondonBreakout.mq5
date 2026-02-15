//+------------------------------------------------------------------+
//|                                           EA_LondonBreakout.mq5    |
//+------------------------------------------------------------------+
#property copyright "London Breakout Strategy"
#property link      ""
#property version   "1.00"

#include <Trade\Trade.mqh>

// Estruturas e Classes Base
//+------------------------------------------------------------------+
class CRiskManager {
private:
    double m_riskPercent;
    
public:
    CRiskManager(double riskPercent = 1.0) {
        m_riskPercent = riskPercent;
    }
    
    double CalculatePositionSize(double stopLoss, string symbol) {
        double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        double riskAmount = accountBalance * (m_riskPercent / 100.0);
        
        double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        
        if(stopLoss <= 0 || tickSize <= 0 || tickValue <= 0) return 0.1;
        
        double positionSize = riskAmount / (stopLoss * (tickValue / tickSize));
        positionSize = NormalizeDouble(positionSize / lotStep, 0) * lotStep;
        
        double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        
        return MathMin(MathMax(positionSize, minLot), maxLot);
    }
};

//+------------------------------------------------------------------+
class CLondonBreakout {
private:
    CRiskManager* m_risk;
    
    // Parâmetros operacionais
    struct SParameters {
        datetime asianStart;      // 00:00 GMT
        datetime asianEnd;        // 07:50 GMT
        datetime londonStart;     // 07:50 GMT
        datetime londonEnd;       // 08:10 GMT
        double   stopLoss;        // 15 pips
        double   takeProfit;      // 25 pips
        double   riskPercent;     // 1%
        double   volumeMultiplier;// 200% do volume médio
        
        void Initialize() {
            stopLoss = 15;
            takeProfit = 25;
            riskPercent = 1.0;
            volumeMultiplier = 2.0;
            UpdateSessionTimes();
        }
        
        void UpdateSessionTimes() {
            MqlDateTime dt;
            TimeToStruct(TimeCurrent(), dt);
            
            asianStart = StringToTime(StringFormat("%d.%02d.%02d 00:00", 
                                    dt.year, dt.mon, dt.day));
            asianEnd = StringToTime(StringFormat("%d.%02d.%02d 07:50", 
                                    dt.year, dt.mon, dt.day));
            londonStart = asianEnd;
            londonEnd = StringToTime(StringFormat("%d.%02d.%02d 08:10", 
                                    dt.year, dt.mon, dt.day));
        }
    } m_params;
    
    // Análise da sessão asiática
    struct SAsianRange {
        double high;
        double low;
        double range;
        double avgRange;
        
        void Calculate() {
            int startBar = iBarShift(_Symbol, PERIOD_M15, m_params.asianStart);
            int endBar = iBarShift(_Symbol, PERIOD_M15, m_params.asianEnd);
            
            high = iHigh(_Symbol, PERIOD_M15, iHighest(_Symbol, PERIOD_M15, MODE_HIGH, startBar-endBar, endBar));
            low = iLow(_Symbol, PERIOD_M15, iLowest(_Symbol, PERIOD_M15, MODE_LOW, startBar-endBar, endBar));
            range = high - low;
            
            // Média dos últimos 5 dias
            avgRange = 0;
            for(int i = 1; i <= 5; i++) {
                avgRange += CalculateDayRange(i);
            }
            avgRange /= 5;
        }
        
        double CalculateDayRange(int daysAgo) {
            datetime pastDay = TimeCurrent() - (daysAgo * PeriodSeconds(PERIOD_D1));
            int startBar = iBarShift(_Symbol, PERIOD_M15, pastDay);
            double dayHigh = iHigh(_Symbol, PERIOD_M15, iHighest(_Symbol, PERIOD_M15, MODE_HIGH, 96, startBar));
            double dayLow = iLow(_Symbol, PERIOD_M15, iLowest(_Symbol, PERIOD_M15, MODE_LOW, 96, startBar));
            return dayHigh - dayLow;
        }
    } m_range;

public:
    CLondonBreakout(CRiskManager* risk = NULL) {
        m_risk = risk;
        m_params.Initialize();
    }
    
    void UpdateSessionTimes() {
        m_params.UpdateSessionTimes();
    }
    
    bool CheckLongEntry() {
        if(!IsValidTradingTime()) return false;
        if(!IsValidVolume()) return false;
        if(!CheckFilters()) return false;
        
        m_range.Calculate();
        return (SymbolInfoDouble(_Symbol, SYMBOL_ASK) > m_range.high && 
                m_range.range < m_range.avgRange * 1.5);
    }
    
    bool CheckShortEntry() {
        if(!IsValidTradingTime()) return false;
        if(!IsValidVolume()) return false;
        if(!CheckFilters()) return false;
        
        m_range.Calculate();
        return (SymbolInfoDouble(_Symbol, SYMBOL_BID) < m_range.low && 
                m_range.range < m_range.avgRange * 1.5);
    }
    
    double CalculatePositionSize() {
        if(!m_risk) return 0.1;
        return m_risk.CalculatePositionSize(m_params.stopLoss * _Point, _Symbol);
    }
    
    double GetStopLoss(bool isLong) {
        return isLong ? 
               SymbolInfoDouble(_Symbol, SYMBOL_ASK) - (m_params.stopLoss * _Point) :
               SymbolInfoDouble(_Symbol, SYMBOL_BID) + (m_params.stopLoss * _Point);
    }
    
    double GetTakeProfit(bool isLong) {
        return isLong ?
               SymbolInfoDouble(_Symbol, SYMBOL_ASK) + (m_params.takeProfit * _Point) :
               SymbolInfoDouble(_Symbol, SYMBOL_BID) - (m_params.takeProfit * _Point);
    }
    
private:
    bool IsValidTradingTime() {
        datetime current = TimeCurrent();
        return (current >= m_params.londonStart && 
                current <= m_params.londonEnd);
    }
    
    bool IsValidVolume() {
        double currentVolume = iVolume(_Symbol, PERIOD_M15, 0);
        double avgVolume = 0;
        
        for(int i = 1; i <= 20; i++) {
            avgVolume += iVolume(_Symbol, PERIOD_M15, i);
        }
        avgVolume /= 20;
        
        return (currentVolume > avgVolume * m_params.volumeMultiplier);
    }
    
    bool CheckFilters() {
        return CheckCalendar() && CheckSpread();
    }
    
    bool CheckCalendar() {
        MqlCalendarValue values[];
        datetime start = TimeCurrent();
        datetime end = start + PeriodSeconds(PERIOD_H4);
        
        if(CalendarValueHistory(values, start, end)) {
            for(int i = 0; i < ArraySize(values); i++) {
                if(values[i].impact_type == CALENDAR_IMPACT_HIGH) {
                    if(values[i].currency == "GBP" || values[i].currency == "USD") {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    
    bool CheckSpread() {
        double currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point;
        return (currentSpread <= 1.5 * _Point);
    }
};

// Variáveis globais
CLondonBreakout* strategy = NULL;
CRiskManager*    riskManager = NULL;
CTrade          trade;
int             magicNumber = 20250304;  // AAAAMMDD

// Inputs para configuração
input group "Configurações Gerais"
input bool   InpEnableTrading = true;     // Habilitar Trading
input double InpRiskPercent = 1.0;        // Risco por Operação (%)
input double InpMaxSpread = 1.5;          // Spread Máximo (pips)

input group "Horários de Operação"
input string InpAsianStart = "00:00";     // Início Sessão Asiática
input string InpAsianEnd = "07:50";       // Fim Sessão Asiática
input string InpLondonStart = "07:50";    // Início Sessão Londres
input string InpLondonEnd = "08:10";      // Fim Sessão Londres

input group "Filtros"
input bool   InpUseNewsFilter = true;     // Filtro de Notícias
input bool   InpUseVolumeFilter = true;   // Filtro de Volume
input double InpVolumeMultiplier = 2.0;   // Multiplicador Volume (200%)

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit() {
    // Verificar período
    if(Period() != PERIOD_M15) {
        Print("EA deve ser usado em M15!");
        return INIT_PARAMETERS_INCORRECT;
    }
    
    // Inicializar gerenciadores
    riskManager = new CRiskManager(InpRiskPercent);
    if(!riskManager) {
        Print("Erro ao criar RiskManager!");
        return INIT_FAILED;
    }
    
    strategy = new CLondonBreakout(riskManager);
    if(!strategy) {
        Print("Erro ao criar Strategy!");
        return INIT_FAILED;
    }
    
    // Configurar trade
    trade.SetExpertMagicNumber(magicNumber);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(_Symbol);
    trade.SetDeviationInPoints(10);
    
    // Logging inicial
    PrintFormat("EA London Breakout iniciado - %s", TimeToString(TimeCurrent()));
    PrintFormat("Risco por operação: %.1f%%", InpRiskPercent);
    PrintFormat("Spread máximo: %.1f pips", InpMaxSpread);
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    delete strategy;
    delete riskManager;
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick() {
    if(!InpEnableTrading) return;
    
    // Verificar horário de trading
    datetime current = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(current, dt);
    
    // Se for fim de semana, não operar
    if(dt.day_of_week == 0 || dt.day_of_week == 6) return;
    
    // Verificar posições abertas
    if(PositionsTotal() > 0) {
        for(int i = PositionsTotal() - 1; i >= 0; i--) {
            if(PositionGetTicket(i) > 0) {
                if(PositionGetInteger(POSITION_MAGIC) == magicNumber) {
                    return; // Já tem posição aberta
                }
            }
        }
    }
    
    // Verificar spread atual
    double currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point;
    if(currentSpread > InpMaxSpread * _Point) {
        Print("Spread muito alto: ", DoubleToString(currentSpread/_Point, 1), " pips");
        return;
    }
    
    // Verificar entradas
    if(strategy.CheckLongEntry()) {
        double volume = strategy.CalculatePositionSize();
        double sl = strategy.GetStopLoss(true);
        double tp = strategy.GetTakeProfit(true);
        
        trade.Buy(volume, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 
                 sl, tp, "London Breakout Long");
    }
    
    if(strategy.CheckShortEntry()) {
        double volume = strategy.CalculatePositionSize();
        double sl = strategy.GetStopLoss(false);
        double tp = strategy.GetTakeProfit(false);
        
        trade.Sell(volume, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 
                  sl, tp, "London Breakout Short");
    }
}

//+------------------------------------------------------------------+
//| Custom functions                                                  |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                       const MqlTradeRequest& request,
                       const MqlTradeResult& result) {
    // Logging de operações
    if(trans.type == TRADE_TRANSACTION_DEAL_ADD) {
        if(HistoryDealSelect(trans.deal)) {
            long dealType = HistoryDealGetInteger(trans.deal, DEAL_TYPE);
            double dealProfit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT);
            
            if(dealType == DEAL_TYPE_BUY || dealType == DEAL_TYPE_SELL) {
                string direction = (dealType == DEAL_TYPE_BUY) ? "LONG" : "SHORT";
                Print("London Breakout: Nova operação ", direction, 
                      " Lucro: ", DoubleToString(dealProfit, 2));
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Timer function                                                     |
//+------------------------------------------------------------------+
void OnTimer() {
    if(strategy) strategy.UpdateSessionTimes();
} 