//+------------------------------------------------------------------+
//| QuantumState.mqh - Estado quântico do mercado                     |
//| Detecta reversões e impulsos com base em função de onda             |
//+------------------------------------------------------------------+

class QuantumState {
private:
   string m_symbol;
   ENUM_TIMEFRAMES m_timeframe;
   int m_index;

   double m_price;
   double m_volatility;
   double m_momentum;

public:
   // Construtor padrão
   QuantumState() : m_price(0), m_volatility(0), m_momentum(0) {}

   // Atualiza o estado quântico do ativo
   void Observe(string symbol, ENUM_TIMEFRAMES timeframe = PERIOD_M1, int index = 0) {
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_index = index;

      m_price = iClose(symbol, timeframe, index);
      m_volatility = iATR(symbol, timeframe, 14, index);
      m_momentum = iMA(symbol, timeframe, 14, 0, MODE_SMA, PRICE_CLOSE, index);
   }

   double Volatility() const { return m_volatility; }
   double Momentum() const { return m_momentum; }
   double Price() const { return m_price; }
};