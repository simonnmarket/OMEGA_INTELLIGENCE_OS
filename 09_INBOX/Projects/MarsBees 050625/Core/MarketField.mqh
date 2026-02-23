//+------------------------------------------------------------------+
//| MarketField.mqh - Campo Vetorial do Mercado                       |
//| Usa operadores quânticos para calcular forças financeiras           |
//+------------------------------------------------------------------+

#include "QuantumState.mqh"

class MarketVector {
private:
   string m_status;

public:
   MarketVector() : m_status("→ Neutro") {}

   void Update(double delta, double vol) {
      double magnitude = MathAbs(delta / (vol + 1e-8));
      double direction = (delta > 0) ? 1 : (delta < 0) ? -1 : 0;

      if(direction > 0) {
         if(magnitude > 1.5) m_status = "↑↑ Forte Impulso";
         else if(magnitude > 0.8) m_status = "↑ Impulso";
         else m_status = "→ Leve Alta";
      } else if(direction < 0) {
         if(magnitude > 1.5) m_status = "↓↓ Queda Acentuada";
         else if(magnitude > 0.8) m_status = "↓ Queda";
         else m_status = "→ Leve Queda";
      } else {
         m_status = "→ Estável";
      }
   }

   string Status() const { return m_status; }
};

class MarketField {
private:
   MarketVector m_vectors[3]; // Para até 3 ativos simultâneos
   QuantumState m_states[3];

public:
   MarketField() {}

   void AnalyzeAll(string &symbols[], int count, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      for(int i=0; i<count && i<3; i++) {
         m_states[i].Observe(symbols[i], timeframe, 0);
         m_vectors[i].Update(m_states[i].Momentum(), m_states[i].Volatility());
      }
   }

   void Update(string symbol, int index, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      if(index >= 0 && index < 3) {
         m_states[index].Observe(symbol, timeframe, 0);
         m_vectors[index].Update(m_states[index].Momentum(), m_states[index].Volatility());
      }
   }

   string GetStatus(int index) {
      if(index >= 0 && index < 3)
         return m_vectors[index].Status();
      return "→ Desconhecido";
   }
};