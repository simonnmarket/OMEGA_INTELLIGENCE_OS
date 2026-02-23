//+------------------------------------------------------------------+
//| Script: DecisionPanel.mq5 - Painel Estratégico Visual           |
//| Projeto: NumeiaEA (Apollo/Brookfield/DWS)                       |
//| Local: Scripts/DecisionPanel.mq5                                |
//| Finalidade: Exibir decisão atual, CVaR e resíduo da regressão   |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs

#include <Analysis/CVaRManager.mqh>
#include <Analysis/GARCH.mqh>
#include <Analysis/LinearReg.mqh>

// Instâncias externas (verifique se estão inicializadas)
extern GARCHModel          *g_garch;
extern LinearRegression    *g_lr;

//+------------------------------------------------------------------+
//| Evento ao clicar no gráfico                                     |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_CLICK)
     {
      double cvar     = (g_garch != NULL) ? g_garch.Forecast() : EMPTY_VALUE;
      double residual = (g_lr != NULL) ? g_lr.GetLastResidual() : EMPTY_VALUE;

      string signal = "HOLD";
      STRATEGIC_DECISION dec = QuantumDecision(_Symbol);
      if(dec == STRATEGIC_BUY)
         signal = "BUY";
      else if(dec == STRATEGIC_SELL)
         signal = "SELL";

      Comment("\n=== NumeiaEA - Decision Panel ===\n",
              "Símbolo: ", _Symbol, "\n",
              "Decisão Atual: ", signal, "\n",
              "Volatilidade (GARCH): ", DoubleToString(cvar, 5), "\n",
              "Resíduo (LinearReg): ", DoubleToString(residual, 5), "\n",
              "Hora: ", TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES));
     }
  }

//+------------------------------------------------------------------+
//| Estratégia base para visualização                               |
//+------------------------------------------------------------------+
enum STRATEGIC_DECISION
  {
   STRATEGIC_HOLD,
   STRATEGIC_BUY,
   STRATEGIC_SELL
  };

STRATEGIC_DECISION QuantumDecision(string symbol)
  {
   double volume     = iVolume(symbol, PERIOD_H1, 0);
   double avgVolume  = iMA(symbol, PERIOD_H1, 20, 0, MODE_SMA, VOLUME_TICK, 0);
   if(avgVolume == 0.0) return STRATEGIC_HOLD;

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
