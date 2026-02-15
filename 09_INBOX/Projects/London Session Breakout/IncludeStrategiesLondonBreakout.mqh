//+------------------------------------------------------------------+
//|                                              LondonBreakout.mqh    |
//+------------------------------------------------------------------+
#include "../ProjectStructure.mqh"
#include "../RiskManager.mqh"

class CLondonBreakout {
private:
    CProjectStructure* m_project;
    CRiskManager*     m_risk;
    SDocumentation    m_doc;
    
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
    // Construtor
    CLondonBreakout(CRiskManager* risk = NULL) {
        m_project = new CProjectStructure();
        m_risk = risk;
        m_params.Initialize();
        InitializeDocumentation();
    }
    
    // Destrutor
    ~CLondonBreakout() {
        delete m_project;
    }
    
    // Verificar sinais
    bool CheckLongEntry() {
        if(!IsValidTradingTime()) return false;
        if(!IsValidVolume()) return false;
        if(!CheckFilters()) return false;
        
        m_range.Calculate();
        return (Ask > m_range.high && m_range.range < m_range.avgRange * 1.5);
    }
    
    bool CheckShortEntry() {
        if(!IsValidTradingTime()) return false;
        if(!IsValidVolume()) return false;
        if(!CheckFilters()) return false;
        
        m_range.Calculate();
        return (Bid < m_range.low && m_range.range < m_range.avgRange * 1.5);
    }
    
    // Cálculos operacionais
    double CalculatePositionSize() {
        if(!m_risk) return 0.1;  // Tamanho padrão se não tiver RiskManager
        return m_risk.CalculatePositionSize(m_params.stopLoss * _Point, _Symbol);
    }
    
    double GetStopLoss(bool isLong) {
        return isLong ? 
               Ask - (m_params.stopLoss * _Point) :
               Bid + (m_params.stopLoss * _Point);
    }
    
    double GetTakeProfit(bool isLong) {
        return isLong ?
               Ask + (m_params.takeProfit * _Point) :
               Bid - (m_params.takeProfit * _Point);
    }
    
private:
    // Verificações
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