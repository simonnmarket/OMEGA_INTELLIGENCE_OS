//+------------------------------------------------------------------+
//| GALEX.mq5 - Sistema principal                                    |
//+------------------------------------------------------------------+
#include "Core/QuantumState.mqh"
#include "Core/MarketField.mqh"
#include "Agents/MomentumAgent.mqh"
#include "Agents/MeanReversionAgent.mqh"
#include "Agents/VolumeSurgeAgent.mqh"
#include "Risk/DynamicRiskManager.mqh"
#include "Trade/OrderLauncher.mqh"

input string Symbols = "EURUSD,GBPUSD,USDJPY";
input double RiskPercent = 1.0;
input int MagicNumber = 20250601;

string symbols[];
int total_symbols;
DynamicRiskManager risk_manager(RiskPercent);
OrderLauncher order_launcher(MagicNumber);
MomentumAgent momentum_agent;
MeanReversionAgent meanrev_agent;
VolumeSurgeAgent volume_agent;

int OnInit() {
   total_symbols = StringSplit(Symbols, ',', symbols);
   EventSetTimer(10);
   return INIT_SUCCEEDED;
}

void OnTick() {
   for(int i=0; i<total_symbols; i++) {
      string symbol = symbols[i];
      if(!SymbolSelect(symbol, true)) continue;
      
      int signal = momentum_agent.Analyze(symbol);
      double lot = risk_manager.CalcLot(symbol, 100);
      
      if(signal != 0 && risk_manager.CanOpenNewPosition(symbol, MagicNumber)) {
         order_launcher.SendOrder(symbol, signal, lot);
      }
   }
}

void OnDeinit(const int reason) {
   EventKillTimer();
}