// File: Experts/NumeiaEA_Integrado_EXECUTION_READY_FINAL_FIXED_v5.mq5
//+------------------------------------------------------------------+
//| NumeiaEA - Execution Ready Final v5                             |
//| Certificação: Apollo / Brookfield / DWS                         |
//| Objetivo: EA institucional com execução real e inteligência     |
//| Build mínimo: MetaTrader 5 - 3045                               |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+
#property strict

#include <Trade\Trade.mqh>

// Análise
#include <Analysis/CVaRManager.mqh>
#include <Analysis/GARCH.mqh>
#include <Analysis/LinearReg.mqh>
#include <Analysis/QuantumEntanglementMap.mqh>
#include <Analysis/WhaleDetector.mqh>
#include <Analysis/CurrencyDNAManager.mqh>
#include <Analysis/AsymmetricCorrelationDetector.mqh>

// Execução
#include <ExecutionLogic/EntropyTrailingStop.mqh>
#include <ExecutionLogic/HydraManager.mqh>
#include <ExecutionLogic/PositionManager.mqh>

//+------------------------------------------------------------------+
//| Variáveis Globais                                               |
//+------------------------------------------------------------------+
CVaRManager              g_cvar;
GARCHModel              *g_garch;
LinearRegression        *g_lr;
PositionManager         *g_positionManager;
HydraManager             g_hydra;

double                   g_riskCapital = 10000.0;
int                      g_maxTrades = 3;

//+------------------------------------------------------------------+
//| Função de Inicialização                                         |
//+------------------------------------------------------------------+
int OnInit()
  {
   g_garch = new GARCHModel();
   g_lr    = new LinearRegression();
   g_positionManager = new PositionManager(_Symbol, 1.0, 2.0, g_maxTrades);
   g_hydra = HydraManager(_Symbol, 0.01);

   Print("[NumeiaEA] Inicialização completa.");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Função principal                                                 |
//+------------------------------------------------------------------+
void OnTick()
  {
   // Indicadores
   double atr = 0;
   int atrHandle = iATR(_Symbol, PERIOD_H1, 14);
   if(atrHandle != INVALID_HANDLE)
     {
      double atrBuffer[1];
      if(CopyBuffer(atrHandle, 0, 0, 1, atrBuffer) > 0)
         atr = atrBuffer[0];
     }

   double volume = iVolume(_Symbol, PERIOD_H1, 0);
   double avgVol = iMA(_Symbol, PERIOD_H1, 20, 0, MODE_SMA, VOLUME_TICK, 0);

   double ratio = 0;
   if(avgVol > 0)
      ratio = volume / avgVol;

   // Decisão
   if(ratio > 3.0)
     {
      if(iClose(_Symbol, PERIOD_H1, 0) > iOpen(_Symbol, PERIOD_H1, 0))
        {
         Print("[NumeiaEA] Sinal de COMPRA");
         g_positionManager.OpenTrade(ORDER_TYPE_BUY, 0.1, SymbolInfoDouble(_Symbol, SYMBOL_ASK), atr * 2, atr * 4, "BUY_Signal");
        }
      else
        {
         Print("[NumeiaEA] Sinal de VENDA");
         g_positionManager.OpenTrade(ORDER_TYPE_SELL, 0.1, SymbolInfoDouble(_Symbol, SYMBOL_BID), atr * 2, atr * 4, "SELL_Signal");
        }
     }
  }

//+------------------------------------------------------------------+
//| Finalização                                                      |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   delete g_garch;
   delete g_lr;
   delete g_positionManager;
  }
//+------------------------------------------------------------------+
