//+------------------------------------------------------------------+
//|                     DecisionRouter.mqh                           |
//|    Roteia sinais e decisões vindas dos módulos analíticos        |
//+------------------------------------------------------------------+
#property strict

#include "..\Analysis\MarketAnalyzer.mqh"
#include "..\Analysis\SignalValidator.mqh"
#include "..\Analysis\VolumeDecisionEngine.mqh"
#include "..\Analysis\OrderFlowAnalyzer.mqh"

class DecisionRouter {
private:
   MarketAnalyzer         analyzer;
   SignalValidator        validator;
   VolumeDecisionEngine   volumeEngine;
   OrderFlowAnalyzer      orderFlow;

public:
   DecisionRouter() {}

   // Inicializa dependências
   void Init() {
      analyzer.Init();
      validator.Init();
      volumeEngine.Init();
      orderFlow.Init();
   }

   // Avalia condições para uma possível entrada
   bool ShouldEnterTrade(string symbol, ENUM_TIMEFRAMES tf) {
      double signalStrength = analyzer.GetSignalStrength(symbol, tf);
      double volumeScore    = volumeEngine.AnalyzeVolume(symbol, tf);
      double orderBias      = orderFlow.DetectBias(symbol, tf);

      bool validSignal = validator.IsSignalConfirmed(symbol, tf);

      PrintFormat("[DecisionRouter] %s | SignalStrength: %.2f | VolumeScore: %.2f | OrderBias: %.2f | Confirmed: %s",
                  symbol, signalStrength, volumeScore, orderBias, validSignal ? "YES" : "NO");

      if(signalStrength > 0.7 && volumeScore > 0.6 && orderBias > 0.5 && validSignal)
         return true;

      return false;
   }

   // Avalia condições para saída (pode ser expandido futuramente)
   bool ShouldExitTrade(string symbol, ENUM_TIMEFRAMES tf) {
      double signalStrength = analyzer.GetSignalStrength(symbol, tf);
      if(signalStrength < 0.3)
         return true;

      return false;
   }
}; 