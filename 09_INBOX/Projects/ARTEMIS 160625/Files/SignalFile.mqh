class SignalFile
{
private:
   string m_filename;
   int m_file_handle;
   
   // Estrutura para armazenar sinais
   struct Signal
   {
      string symbol;
      string timeframe;
      int signal;
      double strength;
      double probability;
      datetime timestamp;
   };
   
public:
   SignalFile()
   {
      m_filename = "signals.csv";
      m_file_handle = INVALID_HANDLE;
   }
   
   // Abrir arquivo
   bool Open()
   {
      m_file_handle = FileOpen(m_filename, FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
      return m_file_handle != INVALID_HANDLE;
   }
   
   // Fechar arquivo
   void Close()
   {
      if(m_file_handle != INVALID_HANDLE)
      {
         FileClose(m_file_handle);
         m_file_handle = INVALID_HANDLE;
      }
   }
   
   // Ler cabeçalho
   bool ReadHeader()
   {
      if(m_file_handle == INVALID_HANDLE) return false;
      
      string header = FileReadString(m_file_handle);
      return header == "Symbol,Timeframe,Signal,Strength,Probability,Timestamp";
   }
   
   // Ler sinal
   bool ReadSignal(Signal &signal)
   {
      if(m_file_handle == INVALID_HANDLE) return false;
      
      signal.symbol = FileReadString(m_file_handle);
      signal.timeframe = FileReadString(m_file_handle);
      signal.signal = (int)FileReadNumber(m_file_handle);
      signal.strength = FileReadNumber(m_file_handle);
      signal.probability = FileReadNumber(m_file_handle);
      signal.timestamp = (datetime)FileReadNumber(m_file_handle);
      
      return !FileIsEnding(m_file_handle);
   }
   
   // Escrever sinal
   bool WriteSignal(const Signal &signal)
   {
      if(m_file_handle == INVALID_HANDLE) return false;
      
      FileWrite(m_file_handle,
                signal.symbol,
                signal.timeframe,
                signal.signal,
                signal.strength,
                signal.probability,
                signal.timestamp);
                
      return true;
   }
   
   // Validar sinal
   bool ValidateSignal(const Signal &signal)
   {
      if(signal.symbol == "" || signal.timeframe == "")
         return false;
         
      if(signal.signal < -1 || signal.signal > 1)
         return false;
         
      if(signal.strength < 0.0 || signal.strength > 1.0)
         return false;
         
      if(signal.probability < 0.0 || signal.probability > 1.0)
         return false;
         
      return true;
   }
   
   // Obter nome do arquivo
   string GetFilename() const
   {
      return m_filename;
   }
   
   // Definir nome do arquivo
   void SetFilename(const string filename)
   {
      m_filename = filename;
   }
}; 