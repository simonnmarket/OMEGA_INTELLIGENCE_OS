//+------------------------------------------------------------------+
//| DecisionPanel.mq5 - Visualizador Estratégico da NumeiaEA        |
//| Certificação Tripartite: Apollo / Brookfield / DWS              |
//| Posição: Scripts/DecisionPanel.mq5                              |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include <Analysis/CVaRManager.mqh>
#include <Analysis/GARCH.mqh>
#include <Analysis/LinearReg.mqh>

//+------------------------------------------------------------------+
//| Referências Globais Externas (declaradas na EA principal)       |
//+------------------------------------------------------------------+
extern GARCHModel         *g_garch;
extern LinearRegression   *g_lr;

//+------------------------------------------------------------------+
//| Enum para decisão estratégica                                   |
//+------------------------------------------------------------------+
enum STRATEGIC_DECISION
  {
   STRATEGIC_HOLD,
   STRATEGIC_BUY,
   STRATEGIC_SELL
  };

//+------------------------------------------------------------------+
//| Lógica Simplificada de Decisão Estratégica                      |
//+------------------------------------------------------------------+
STRATEGIC_DECISION QuantumDecision(string symbol)
  {
   double volume = iVolume(symbol, PERIOD_H1, 0);
   double avgVolume = iMA(symbol, PERIOD_H1, 20, 0, MODE_SMA, VOLUME_TICK, 0);
   if(avgVolume == 0.0)
      return STRATEGIC_HOLD;

   double ratio = volume / avgVolume;
   if(ratio > 3.0)
     {
      if(iClose(symbol, PERIOD_H1, 0) > iOpen(symbol, PERIOD_H1, 0))
         return STRATEGIC_BUY;
      else
         return STRATEGIC_SELL;
     }

   return STRATEGIC_HOLD;
  }

//+------------------------------------------------------------------+
//| Painel Estratégico (ao clicar no gráfico)                       |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_CLICK)
     {
      double cvar = (g_garch != NULL) ? g_garch.Forecast() : EMPTY_VALUE;
      double residual = (g_lr != NULL) ? g_lr.GetLastResidual() : EMPTY_VALUE;

      string signal = "HOLD";
      STRATEGIC_DECISION decision = QuantumDecision(_Symbol);
      if(decision == STRATEGIC_BUY)
         signal = "BUY";
      else if(decision == STRATEGIC_SELL)
         signal = "SELL";

      Comment("\n=== PAINEL ESTRATÉGICO NumeiaEA ===\n",
              "Símbolo: ", _Symbol, "\n",
              "Decisão Atual: ", signal, "\n",
              "Volatilidade (GARCH): ", DoubleToString(cvar, 5), "\n",
              "Resíduo (LR): ", DoubleToString(residual, 5), "\n",
              "Data: ", TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES));
     }
  }
//+------------------------------------------------------------------+
