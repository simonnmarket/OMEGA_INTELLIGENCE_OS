//+------------------------------------------------------------------+
//| QuantumState.mqh - Estado quântico do mercado                     |
//| Usa funções vetoriais para detectar reversões e impulsos           |
//+------------------------------------------------------------------+

#include "..\Math\QuantumMath.mqh"

class QuantumState {
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_index;

   double m_price;
   double m_volatility;
   double m_momentum;
   double m_wave_function;
   double m_probability;

public:
   // Construtor padrão
   QuantumState() : m_price(0), m_volatility(0), m_momentum(0),
                    m_wave_function(0), m_probability(0) {}

   // Atualiza o estado quântico do ativo
   void Observe(string symbol, ENUM_TIMEFRAMES timeframe = PERIOD_M1, int index = 0) {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_index = index;

      m_price = iClose(symbol, timeframe, index);
      m_volatility = iATR(symbol, timeframe, 14, index);
      m_momentum = iMA(symbol, timeframe, 14, 0, MODE_SMA, PRICE_CLOSE, index);

      // Função de onda financeira
      m_wave_function = MathExp(-MathPow(m_momentum / (m_volatility + 1e-8), 2));
      m_probability = MathPow(m_wave_function, 2);
   }

   double Probability() const { return m_probability; }
   double Momentum() const { return m_momentum; }
   double Volatility() const { return m_volatility; }
   double Price() const { return m_price; }

   // Detecta colapso do campo vetorial
   bool FieldCollapse() const {
      double delta = iClose(m_symbol, m_timeframe, m_index) - iClose(m_symbol, m_timeframe, m_index + 1);
      double avg_delta = iMA(m_symbol, m_timeframe, 14, 0, MODE_SMA, PRICE_CLOSE, m_index);
      return MathAbs(delta) > MathAbs(avg_delta) * 1.5;
   }

   // Calcula divergência do campo vetorial
   double Divergence() const {
      double delta = iClose(m_symbol, m_timeframe, m_index) - iClose(m_symbol, m_timeframe, m_index + 1);
      double ma = iMA(m_symbol, m_timeframe, 14, 0, MODE_SMA, PRICE_CLOSE, m_index);
      return (delta - ma) / (iATR(m_symbol, m_timeframe, 14, m_index) + 1e-8);
   }
};