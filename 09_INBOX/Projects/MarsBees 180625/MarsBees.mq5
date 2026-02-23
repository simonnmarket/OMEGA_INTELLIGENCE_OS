//+------------------------------------------------------------------+
//| MarsBees.mq5 - Multiagent Exploration & Signal-Based Execution     |
//| Sistema Algorítmico Avançado                                     |
//| Versão 1.0 - Base funcional                                      |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>

#include "Core/QuantumState.mqh"
#include "Core/MarketField.mqh"
#include "Core/DecisionMatrix.mqh"

#include "Agents/AgentBase.mqh"
#include "Agents/MomentumAgent.mqh"
#include "Agents/MeanReversionAgent.mqh"
#include "Agents/VolumeSurgeAgent.mqh"

#include "Risk/DynamicRiskManager.mqh"
#include "Risk/PortfolioBalancer.mqh"

#include "Interface/HUDManager.mqh"

CTrade trade;

input string Symbols = "EURUSD,GBPUSD,USDJPY";
input double BaseRiskPercent = 1.5;
input int MaxOrdersPerSymbol = 3;
input int MagicNumber = 20250601;
input double TakeProfit = 100;
input double StopLoss = 100;
input bool UseTrailingStop = true;
input double TrailingStart = 50;
input double TrailingStep = 20;
input bool UseBreakeven = true;
input double BreakevenTrigger = 60;

string symbols[];
int total_symbols;

DynamicRiskManager* risk_manager = NULL;
HUDManager* hud = NULL;
MarketField* market_field = NULL;
PortfolioBalancer* portfolio_balancer = NULL;

AgentBase* agents[3];
DecisionMatrix* matrix = NULL;

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   EventSetTimer(10);

   // Inicializa símbolos
   total_symbols = StringSplit(Symbols, ',', symbols);
   Print("Símbolos carregados: ", total_symbols);

   // Inicializa módulos centrais
   risk_manager = new DynamicRiskManager(BaseRiskPercent, MaxOrdersPerSymbol, TakeProfit, StopLoss,
                                         UseTrailingStop, TrailingStart, TrailingStep,
                                         UseBreakeven, BreakevenTrigger);

   market_field = new MarketField();
   portfolio_balancer = new PortfolioBalancer(market_field, BaseRiskPercent * 3); // Exposição limitada a 3x risco base

   hud = new HUDManager();
   hud->Init();

   // Inicializa agentes autônomos
   for(int i=0; i<3; i++) {
      if(i == 0) agents[i] = new MomentumAgent();
      if(i == 1) agents[i] = new MeanReversionAgent();
      if(i == 2) agents[i] = new VolumeSurgeAgent();
   }

   matrix = new DecisionMatrix();

   // Atualiza campo vetorial inicial
   market_field->AnalyzeAll(symbols, total_symbols);

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   delete hud;
   delete risk_manager;
   delete market_field;
   delete portfolio_balancer;
   delete matrix;

   for(int i=0; i<3; i++)
      delete agents[i];

   EventKillTimer();
}

//+------------------------------------------------------------------+
//| OnTick                                                           |
//+------------------------------------------------------------------+
void OnTick()
{
   for(int i=0; i<total_symbols; i++)
   {
      string symbol = symbols[i];
      StringTrimLeft(symbol); StringTrimRight(symbol);
      if(!SymbolSelect(symbol, true)) continue;

      // Atualiza campo vetorial do mercado
      market_field->Update(symbol, i);

      // Cada agente analisa o mercado
      int signals[];
      ArrayInitialize(signals, 0);
      ArrayResize(signals, 3);

      for(int j=0; j<3; j++) {
         if(agents[j] == NULL) continue;

         signals[j] = agents[j]->Analyze(symbol);
         Print("Agente ", agents[j]->Name(), " | Sinal para ", symbol, ": ", SignalToString(signals[j]));
      }

      // Decisão coletiva via votação ponderada
      int final_signal = matrix->CollectiveDecision(agents, symbol);

      // Gerencia risco e executa ordem
      double lot_risk = risk_manager->CalcLot(symbol, StopLoss);
      if(final_signal != 0 && portfolio_balancer->CanOpenNewPosition(symbol, lot_risk))
      {
         LaunchOrder(symbol, final_signal, lot_risk);
      }

      // Atualiza interface gráfica
      string status = market_field->GetStatus(i);
      hud->Update(symbol, final_signal, status);

      // Atualiza trailing stop dinamicamente
      risk_manager->ManageTrailing(symbol, trade, MagicNumber);
   }
}

//+------------------------------------------------------------------+
//| Lança ordem com base no sinal                                   |
//+------------------------------------------------------------------+
void LaunchOrder(string symbol, int direction, double lot)
{
   double price = SymbolInfoDouble(symbol, (direction == ORDER_TYPE_BUY) ? SYMBOL_ASK : SYMBOL_BID);
   double sl = risk_manager->CalculateSL(symbol, price, direction, StopLoss);
   double tp = risk_manager->CalculateTP(symbol, price, direction, TakeProfit);

   trade.SetExpertMagicNumber(MagicNumber);
   if(direction == ORDER_TYPE_BUY)
      trade.Buy(lot, symbol, price, sl, tp, "MarsBees v1.0");
   else
      trade.Sell(lot, symbol, price, sl, tp, "MarsBees v1.0");
}

//+------------------------------------------------------------------+
//| Converte sinal para texto                                        |
//+------------------------------------------------------------------+
string SignalToString(int signal) {
   switch(signal) {
      case 1: return "🟢 Compra Forte";
      case -1: return "🔴 Venda Forte";
      default: return "🟠 Neutro";
   }
}