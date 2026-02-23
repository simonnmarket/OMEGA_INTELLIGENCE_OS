//+------------------------------------------------------------------+
//|                  Numeia Expert Advisor                          |
//|             Local: Numeia/Expert/NumeiaEA.mq5                   |
//+------------------------------------------------------------------+
#property copyright "Sky Lab Research"
#property version   "1.0"
#property strict

#include "..\\Core\\CoreBrainManager.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("Numeia EA inicializando...");
   CoreBrainManager::Init();
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("Numeia EA finalizando...");
   CoreBrainManager::Shutdown();
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   CoreBrainManager::Run();
}
