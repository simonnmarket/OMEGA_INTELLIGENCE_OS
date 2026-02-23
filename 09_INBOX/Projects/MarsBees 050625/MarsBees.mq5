//+------------------------------------------------------------------+
//| GALEX.mq5 - Sistema de Trading Quântico                          |
//+------------------------------------------------------------------+
#include "Core/QuantumMath.mqh"
#include "Agents/AgentBase.mqh"
#include "Agents/MomentumAgent.mqh"
#include "Risk/DynamicRiskManager.mqh"

input string   Symbols = "EURUSD,GBPUSD,USDJPY";
input double   RiskPercent = 1.0;
input int      MaxOrdersPerSymbol = 3;
input int      MagicNumber = 20250601;
input int      StopLossPips = 100;
input int      TakeProfitPips = 150;

string symbolArray[];
int    symbolCount;

DynamicRiskManager riskManager(RiskPercent, MaxOrdersPerSymbol);
MomentumAgent momentumAgent(14, 1.5);  // Passando período e fator de volatilidade
CTrade trade;

int OnInit() {
   // Inicialização dos símbolos
   symbolCount = StringSplit(Symbols, ',', symbolArray);
   if(symbolCount == 0) {
      Print("Nenhum símbolo configurado!");
      return INIT_FAILED;
   }
   
   trade.SetExpertMagicNumber(MagicNumber);
   EventSetTimer(10);
   
   return INIT_SUCCEEDED;
}

void OnTick() {
   for(int i=0; i<symbolCount; i++) {
      string symbol = symbolArray[i];
      SymbolSelect(symbol, true);
      
      // Obter sinal do agente
      int signal = momentumAgent.Analyze(symbol);
      
      // Gerenciamento de risco
      if(signal != 0 && riskManager.CanOpenNewPosition(symbol, MagicNumber)) {
         double lot = riskManager.CalculateLotSize(symbol, StopLossPips);
         double price = (signal == 1) ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
         double sl = (signal == 1) ? price - StopLossPips * _Point : price + StopLossPips * _Point;
         double tp = (signal == 1) ? price + TakeProfitPips * _Point : price - TakeProfitPips * _Point;
         
         if(signal == 1) {
            trade.Buy(lot, symbol, price, sl, tp, "GALEX Buy Signal");
         } else {
            trade.Sell(lot, symbol, price, sl, tp, "GALEX Sell Signal");
         }
      }
   }
}

void OnDeinit(const int reason) {
   EventKillTimer();
}

void OnTimer() {
   // Atualizações periódicas podem ser adicionadas aqui
}