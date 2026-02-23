//+------------------------------------------------------------------+
//| SignalProcessor.mqh - Processador de Sinais                      |
//+------------------------------------------------------------------+

class SignalProcessor
{
private:
   // Estrutura para armazenar sinais
   struct Signal
   {
      string symbol;
      ENUM_TIMEFRAMES timeframe;
      int type;
      double strength;
      double probability;
      datetime time;
   };
   
   // Array de sinais
   Signal m_signals[];
   int m_signal_count;
   
   // Parâmetros de processamento
   double m_min_strength;
   double m_min_probability;
   int m_max_signals;
   
public:
   SignalProcessor()
   {
      m_signal_count = 0;
      ArrayResize(m_signals, 0);
      
      m_min_strength = 0.7;
      m_min_probability = 0.8;
      m_max_signals = 100;
   }
   
   // Adicionar sinal
   bool AddSignal(const string symbol, const ENUM_TIMEFRAMES timeframe, const int type,
                 const double strength, const double probability)
   {
      // Validar parâmetros
      if(symbol == "" || strength < 0.0 || strength > 1.0 || probability < 0.0 || probability > 1.0)
         return false;
         
      // Verificar limites
      if(m_signal_count >= m_max_signals)
         return false;
         
      // Verificar força e probabilidade mínimas
      if(strength < m_min_strength || probability < m_min_probability)
         return false;
         
      // Adicionar sinal
      int new_size = m_signal_count + 1;
      ArrayResize(m_signals, new_size);
      
      m_signals[m_signal_count].symbol = symbol;
      m_signals[m_signal_count].timeframe = timeframe;
      m_signals[m_signal_count].type = type;
      m_signals[m_signal_count].strength = strength;
      m_signals[m_signal_count].probability = probability;
      m_signals[m_signal_count].time = TimeCurrent();
      
      m_signal_count++;
      return true;
   }
   
   // Obter sinal
   bool GetSignal(const int index, string &symbol, ENUM_TIMEFRAMES &timeframe, int &type,
                 double &strength, double &probability, datetime &time)
   {
      if(index < 0 || index >= m_signal_count)
         return false;
         
      symbol = m_signals[index].symbol;
      timeframe = m_signals[index].timeframe;
      type = m_signals[index].type;
      strength = m_signals[index].strength;
      probability = m_signals[index].probability;
      time = m_signals[index].time;
      
      return true;
   }
   
   // Processar sinal
   bool ProcessSignal(const int index)
   {
      if(index < 0 || index >= m_signal_count)
         return false;
         
      // Validar sinal
      if(!ValidateSignal(m_signals[index]))
         return false;
         
      // Processar sinal
      double signal_value = (double)m_signals[index].type * m_signals[index].strength * m_signals[index].probability;
      
      // Verificar resultado
      if(MathAbs(signal_value) < 0.1)
         return false;
         
      return true;
   }
   
   // Validar sinal
   bool ValidateSignal(const Signal &signal)
   {
      if(signal.symbol == "")
         return false;
         
      if(signal.type < -1 || signal.type > 1)
         return false;
         
      if(signal.strength < 0.0 || signal.strength > 1.0)
         return false;
         
      if(signal.probability < 0.0 || signal.probability > 1.0)
         return false;
         
      return true;
   }
   
   // Limpar sinais
   void Clear()
   {
      m_signal_count = 0;
      ArrayResize(m_signals, 0);
   }
   
   // Obter contagem de sinais
   int GetSignalCount() const
   {
      return m_signal_count;
   }
   
   // Configurar parâmetros
   void SetParameters(const double min_strength, const double min_probability, const int max_signals)
   {
      m_min_strength = min_strength;
      m_min_probability = min_probability;
      m_max_signals = max_signals;
   }
}; 