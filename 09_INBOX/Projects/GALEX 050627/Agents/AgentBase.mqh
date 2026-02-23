//+------------------------------------------------------------------+
//| AgentBase.mqh - Classe base abstrata para agentes                |
//+------------------------------------------------------------------+
#include "QuantumState.mqh"

class AgentBase {
protected:
   string m_name;
   double m_confidence;
   
public:
   AgentBase(string name) : m_name(name), m_confidence(0) {}
   
   virtual int Analyze(string symbol, ENUM_TIMEFRAMES timeframe=PERIOD_M1) = 0;
   
   string Name() const { return m_name; }
   double Confidence() const { return m_confidence; }
   
   bool IsPriceAboveMA(string symbol, int period=20, ENUM_TIMEFRAMES timeframe=PERIOD_M1) {
      return iClose(symbol, timeframe, 0) > iMA(symbol, timeframe, period, 0, MODE_SMA, PRICE_CLOSE, 0);
   }
};