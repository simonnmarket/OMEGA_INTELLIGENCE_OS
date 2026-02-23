//+------------------------------------------------------------------+
//| SignalProcessor.mqh - Processador de Sinais                      |
//+------------------------------------------------------------------+
class SignalProcessor
{
private:
   bool use_volume;
   int volume_period;
   bool use_external_signal;
   
public:
   SignalProcessor(bool use_vol = true, int vol_period = 20, bool use_ext = false)
   {
      use_volume = use_vol;
      volume_period = vol_period;
      use_external_signal = use_ext;
   }
   
   int GetSignal(string symbol)
   {
      if(use_external_signal)
      {
         int signal = GetSignalFromCSV(symbol);
         if(signal != 0) return signal;
      }
      
      return AnalyzePriceAction(symbol);
   }
   
private:
   int AnalyzePriceAction(string symbol)
   {
      double price = SymbolInfoDouble(symbol, SYMBOL_BID);
      double volume = iVolume(symbol, PERIOD_M5, 0);
      
      // Análise de Volume
      if(use_volume)
      {
         int ma_handle = iMA(symbol, PERIOD_M5, volume_period, 0, MODE_SMA, PRICE_CLOSE);
         double volMA[];
         CopyBuffer(ma_handle, 0, 0, 1, volMA);
         
         if(volume > volMA[0])
         {
            double highPrev = iHigh(symbol, PERIOD_M5, 1);
            double lowPrev = iLow(symbol, PERIOD_M5, 1);
            
            if(price > highPrev) return 1;  // Sinal de compra
            if(price < lowPrev) return -1;  // Sinal de venda
         }
      }
      
      // Análise de Price Action
      double open = iOpen(symbol, PERIOD_M5, 1);
      double close = iClose(symbol, PERIOD_M5, 1);
      double highPrev = iHigh(symbol, PERIOD_M5, 1);
      double lowPrev = iLow(symbol, PERIOD_M5, 1);
      
      if(close > open && price > highPrev) return 1;   // Sinal de compra
      if(close < open && price < lowPrev) return -1;   // Sinal de venda
      
      return 0;  // Sem sinal
   }
   
   int GetSignalFromCSV(string symbol)
   {
      string filename = "Files/signals.csv";
      int handle = FileOpen(filename, FILE_READ|FILE_CSV|FILE_ANSI);
      
      if(handle == INVALID_HANDLE)
      {
         Print("Erro ao abrir arquivo de sinais: ", GetLastError());
         return 0;
      }
      
      while(!FileIsEnding(handle))
      {
         string line = FileReadString(handle);
         string parts[];
         StringSplit(line, ',', parts);
         
         if(ArraySize(parts) >= 2 && parts[0] == symbol)
         {
            FileClose(handle);
            return (int)StringToInteger(parts[1]);
         }
      }
      
      FileClose(handle);
      return 0;
   }
}; 