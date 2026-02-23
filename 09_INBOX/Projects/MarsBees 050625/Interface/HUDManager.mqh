//+------------------------------------------------------------------+
//| HUDManager.mqh - Interface tipo cockpit                           |
//| Mostra sinais, vetores, status e decisão coletiva                |
//+------------------------------------------------------------------+

#include "VectorDisplay.mqh"

class HUDManager {
private:
   VectorDisplay* m_displays[3]; // Para até 3 ativos simultâneos

public:
   HUDManager() {
      for(int i=0; i<3; i++) {
         m_displays[i] = new VectorDisplay("signal_"+IntegerToString(i), 50, 70 + i*20);
         m_displays[i]->Create(0, 0, 50, 70 + i*20);
      }
   }

   ~HUDManager() {
      for(int i=0; i<3; i++)
         delete m_displays[i];
   }

   void Init() {
      ObjectCreate(0, "title", OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, "title", OBJPROP_XDISTANCE, 50);
      ObjectSetInteger(0, "title", OBJPROP_YDISTANCE, 30);
      ObjectSetText(0, "title", "🌌 MARSBEES v2.0 - Multiagent Exploration System", 12, "Arial", clrWhite);
   }

   void Update(string symbol, int signal, string status) {
      int index = SymbolToIndex(symbol);
      if(index >= 0 && index < 3) {
         string signal_str = SignalToString(signal);
         ObjectSetText(0, "signal_"+IntegerToString(index),
                       symbol + "     " + signal_str + "     " + status + "     " + DoubleToString(SignalToWeight(signal), 2),
                       12, "Arial", GetColorFromSignal(signal));
      }
   }

   int SymbolToIndex(string symbol) {
      if(symbol == "EURUSD") return 0;
      if(symbol == "GBPUSD") return 1;
      if(symbol == "USDJPY") return 2;
      return -1;
   }

   string SignalToString(int signal) {
      return (signal == 1) ? "🔺 Compra" : (signal == -1) ? "🔻 Venda" : "⬤ Neutro";
   }

   double SignalToWeight(int signal) {
      return (signal != 0) ? MathAbs(signal * 0.8) : 0.0;
   }

   color GetColorFromSignal(int signal) {
      return (signal == 1) ? clrGreen : (signal == -1) ? clrRed : clrWhite;
   }
};