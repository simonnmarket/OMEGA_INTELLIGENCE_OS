//+------------------------------------------------------------------+
//| QuantumState.mqh - Estado quântico do mercado                    |
//+------------------------------------------------------------------+
#include "QuantumMath.mqh"

class QuantumState {
private:
   Complex m_wave_function;
   double m_probability;
   
public:
   void Observe(string symbol, ENUM_TIMEFRAMES timeframe, int index) {
      double price = iClose(symbol, timeframe, index);
      double prev_price = iClose(symbol, timeframe, index+1);
      double momentum = (price - prev_price)/prev_price;
      double volatility = iATR(symbol, timeframe, 14, index)/price;
      
      m_wave_function = Complex(QuantumMath::NormalizedWave(momentum, volatility), 0);
      m_probability = m_wave_function.Norm();
   }
   
   double Probability() const { return m_probability; }
   Complex GetWaveFunction() const { return m_wave_function; }
};