//+------------------------------------------------------------------+
//| Robô Multiativos - Interface Moderna                             |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>
#include "includes/SignalProcessor.mqh"
#include "includes/RiskManager.mqh"
#include "includes/GuiManager.mqh"

CTrade trade;
GuiManager* gui;
SignalProcessor* signal_processor;
RiskManager* risk_manager;

input string Symbols = "EURUSD,GBPUSD,USDJPY";
input double RiskPercent = 2.0;
input int MaxOrders = 3;
input int MagicNumber = 20250601;
input double TakeProfit = 100;
input double StopLoss = 100;
input bool UseTrailing = true;
input double TrailingStart = 50;
input double TrailingStep = 20;
input bool UseBreakeven = true;
input double BreakevenTrigger = 60;
input bool UseVolume = true;
input int VolumePeriod = 20;
input bool UseExternalSignal = false;

string symbols[];
int total_symbols;

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   EventSetTimer(10);
   int count = StringSplit(Symbols, ',', symbols);
   total_symbols = count;
   
   // Inicializa os módulos
   gui = new GuiManager();
   signal_processor = new SignalProcessor(UseVolume, VolumePeriod, UseExternalSignal);
   risk_manager = new RiskManager(RiskPercent, MaxOrders, TakeProfit, StopLoss,
                                UseTrailing, TrailingStart, TrailingStep,
                                UseBreakeven, BreakevenTrigger);
   gui.Init();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   gui.Destroy();
   delete gui;
   delete signal_processor;
   delete risk_manager;
}

//+------------------------------------------------------------------+
//| OnTick                                                           |
//+------------------------------------------------------------------+
void OnTick()
{
   for(int i = 0; i < total_symbols; i++)
   {
      string symbol = symbols[i];
      StringTrimLeft(symbol); StringTrimRight(symbol);
      if(!SymbolSelect(symbol, true)) continue;
      
      if(risk_manager.CanOpenNewPosition(symbol, MagicNumber))
      {
         int signal = signal_processor.GetSignal(symbol);
         string status = (signal == 1) ? "Forte" : (signal == -1) ? "Médio" : "Neutro";
         gui.Update(symbol, signal, status);
         
         if(signal != 0)
         {
            double lot = risk_manager.CalcLot(symbol, StopLoss);
            OpenOrder(symbol, signal, lot);
         }
      }
      
      risk_manager.ManageTrailingStop(symbol, MagicNumber);
   }
}

//+------------------------------------------------------------------+
//| Execução de ordens                                               |
//+------------------------------------------------------------------+
void OpenOrder(string symbol, int direction, double lot)
{
   double price = (direction > 0) ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
   double sl = (direction > 0) ? price - StopLoss * _Point : price + StopLoss * _Point;
   double tp = (direction > 0) ? price + TakeProfit * _Point : price - TakeProfit * _Point;
   
   trade.SetExpertMagicNumber(MagicNumber);
   if(direction > 0)
      trade.Buy(lot, symbol, price, sl, tp);
   else
      trade.Sell(lot, symbol, price, sl, tp);
} 