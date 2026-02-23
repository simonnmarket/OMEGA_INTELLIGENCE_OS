//+------------------------------------------------------------------+
//| HUDManager.mqh - Interface tipo cockpit                           |
//| Mostra sinais, vetores, status e decisão coletiva                 |
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

   // Inicializa interface gráfica
   void Init() {
      VectorDisplay title("title", 50, 30);
      title.Create(0, 0, 50, 30);
      title.Update("🌌 MARSBEES v1.0 - Multiagent Exploration System");
   }

   // Atualiza interface com base no símbolo e sinal
   void Update(string symbol, int signal, string status) {
      int index = SymbolToIndex(symbol);
      if(index >= 0 && index < 3) {
         string signal_str = SignalToString(signal);
         m_displays[index]->Update(symbol + "     " + signal_str + "     " + status + "     " + DoubleToString(SignalToWeight(signal), 2));
      }
   }

   // Mapeia o símbolo para índice (ex: EURUSD → 0)
   int SymbolToIndex(string symbol) {
      if(symbol == "EURUSD") return 0;
      if(symbol == "GBPUSD") return 1;
      if(symbol == "USDJPY") return 2;
      return -1;
   }

   // Converte sinal para texto visual
   string SignalToString(int signal) {
      return (signal == 1) ? "🔺 Compra" :
             (signal == -1) ? "🔻 Venda" : "⬤ Neutro";
   }

   // Calcula peso visual do sinal
   double SignalToWeight(int signal) {
      return (signal != 0) ? MathAbs(signal * 0.8) : 0.0;
   }
};