//+------------------------------------------------------------------+
//|                                            TrajectoryAnalyzer.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CTrajectoryAnalyzer {
private:
    double gravForce;
    double poc;
    double monthlyHigh;
    double monthlyLow;
    double weeklyHigh;
    double weeklyLow;
    
public:
    CTrajectoryAnalyzer() {
        gravForce = 0.0;
        poc = 0.0;
        monthlyHigh = 0.0;
        monthlyLow = 0.0;
        weeklyHigh = 0.0;
        weeklyLow = 0.0;
    }
    
    void UpdateGravitationalForce(double force) {
        gravForce = force;
    }
    
    void UpdatePOC(double price) {
        poc = price;
    }
    
    void CalculateMonthlyChannel() {
        monthlyHigh = iHigh(_Symbol, PERIOD_MN1, 1);
        monthlyLow = iLow(_Symbol, PERIOD_MN1, 1);
    }
    
    void CalculateWeeklyChannel() {
        weeklyHigh = iHigh(_Symbol, PERIOD_W1, 1);
        weeklyLow = iLow(_Symbol, PERIOD_W1, 1);
    }
    
    double GetGravitationalForce() const { return gravForce; }
    double GetPOC() const { return poc; }
    double GetMonthlyHigh() const { return monthlyHigh; }
    double GetMonthlyLow() const { return monthlyLow; }
    double GetWeeklyHigh() const { return weeklyHigh; }
    double GetWeeklyLow() const { return weeklyLow; }
    
    void TraceReferenceLines() {
        double range = weeklyHigh - weeklyLow;
        string nameTop = "GravChannel_Top_" + DoubleToString(poc, 5);
        string nameBottom = "GravChannel_Bottom_" + DoubleToString(poc, 5);
        
        if(ObjectFind(0, nameTop) < 0) {
            ObjectCreate(0, nameTop, OBJ_HLINE, 0, 0, weeklyHigh);
            ObjectCreate(0, nameBottom, OBJ_HLINE, 0, 0, weeklyLow);
            ObjectSetInteger(0, nameTop, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, nameBottom, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, nameTop, OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, nameBottom, OBJPROP_STYLE, STYLE_DASH);
            
            string label = "POC_" + DoubleToString(poc, 5);
            ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), poc);
            ObjectSetString(0, label, OBJPROP_TEXT, "POC: " + DoubleToString(poc, 5));
            ObjectSetInteger(0, label, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
            Print("Canal Gravitacional: ", poc);
        }
    }
    
    void PlotGravitationalPulse() {
        if(gravForce > 500) {
            string name = "GravPulse_" + TimeToString(TimeCurrent());
            if(ObjectFind(0, name) < 0) {
                ObjectCreate(0, name, OBJ_VLINE, 0, TimeCurrent(), 0);
                ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
                string label = "Pulse_" + TimeToString(TimeCurrent());
                ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), iHigh(_Symbol, PERIOD_CURRENT, 0));
                ObjectSetString(0, label, OBJPROP_TEXT, "Força: " + DoubleToString(gravForce / 1000, 2) + "G");
                ObjectSetInteger(0, label, OBJPROP_COLOR, clrRed);
                ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
                Print("Pulso Gravitacional: ", gravForce);
            }
        }
    }
}; 