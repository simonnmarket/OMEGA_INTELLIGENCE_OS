//+------------------------------------------------------------------+
//| Include/Visuals/DefenseDashboard.mq5                             |
//| Interface visual institucional – Sato Defense Pro v3.1           |
//| Atualizado com interface externa para IA                         |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_buffers 6
#property indicator_plots   4

#ifndef __VISUALS_DEFENSE_DASHBOARD_MQ5__
#define __VISUALS_DEFENSE_DASHBOARD_MQ5__

#include <Modules/DefenseAgent.mqh>

//--- Buffers
double bufferDefense[], bufferBuyZone[], bufferSellZone[];
double bufferFootprint[], bufferSignal[], bufferVolatility[];

//--- Variáveis internas
int lastDefenseSignal = DEFENSE_NONE;

//--- Parâmetros visuais
input color colorDefenseLine = clrDodgerBlue;
input color colorBuyZone     = clrLime;
input color colorSellZone    = clrRed;
input color colorFootprint   = clrGold;
input int   VolatilityPeriod = 14;
input ENUM_TIMEFRAMES DashTimeframe = PERIOD_CURRENT;

//+------------------------------------------------------------------+
//| Função externa para IA consultar o último sinal                  |
//+------------------------------------------------------------------+
int GetLastDefenseSignal()
{
   return lastDefenseSignal;
}

//+------------------------------------------------------------------+
//| Inicialização                                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   SetIndexBuffer(0, bufferDefense);
   SetIndexStyle(0, DRAW_LINE, STYLE_SOLID, 2, colorDefenseLine);

   SetIndexBuffer(1, bufferBuyZone);
   SetIndexStyle(1, DRAW_ARROW, STYLE_SOLID, 1, colorBuyZone);
   SetIndexArrow(1, 233);

   SetIndexBuffer(2, bufferSellZone);
   SetIndexStyle(2, DRAW_ARROW, STYLE_SOLID, 1, colorSellZone);
   SetIndexArrow(2, 234);

   SetIndexBuffer(3, bufferFootprint);
   PlotIndexSetInteger(3, PLOT_DRAW_TYPE, DRAW_ARROW);
   PlotIndexSetInteger(3, PLOT_ARROW, 241);
   PlotIndexSetInteger(3, PLOT_LINE_COLOR, colorFootprint);

   SetIndexBuffer(4, bufferSignal);
   PlotIndexSetInteger(4, PLOT_DRAW_TYPE, DRAW_NONE);

   SetIndexBuffer(5, bufferVolatility);
   PlotIndexSetInteger(5, PLOT_DRAW_TYPE, DRAW_NONE);

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Cálculo principal                                                |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   int limit = rates_total - prev_calculated;
   if (limit > rates_total - 100) limit = rates_total - 100;

   for (int i = limit; i >= 0; i--)
   {
      DefenseStatus ds = GetDefenseStatus(i, close, high, low, volume);

      bufferDefense[i]    = ds.defenseLine;
      bufferBuyZone[i]    = ds.signal == DEFENSE_BUY_ZONE ? low[i] - 2 * _Point : EMPTY_VALUE;
      bufferSellZone[i]   = ds.signal == DEFENSE_SELL_ZONE ? high[i] + 2 * _Point : EMPTY_VALUE;
      bufferFootprint[i]  = ds.footprint != EMPTY_VALUE ? ds.footprint : EMPTY_VALUE;
      bufferSignal[i]     = (double)ds.signal;
      bufferVolatility[i] = iATR(NULL, 0, VolatilityPeriod, i);

      if (i == 0)
         lastDefenseSignal = ds.signal; // atualiza variável global
   }

   return rates_total;
}

#endif // __VISUALS_DEFENSE_DASHBOARD_MQ5__ 