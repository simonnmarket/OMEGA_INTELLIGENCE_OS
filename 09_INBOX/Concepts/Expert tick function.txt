//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Verificar se o trading é permitido
   if(!IsTradeAllowed())
   {
      Print("DEBUG: Trading não permitido. Verifique as configurações do terminal.");
      return;
   }
   
   // Obter dados de preço e volume
   double high[], low[], close[], volume[];
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(volume, true);
   
   int copied = CopyHigh(_Symbol, PERIOD_CURRENT, 0, 100, high);
   if(copied != 100) 
   {
      Print("DEBUG: Falha ao copiar dados de High: ", GetLastError());
      return;
   }
   
   copied = CopyLow(_Symbol, PERIOD_CURRENT, 0, 100, low);
   if(copied != 100) 
   {
      Print("DEBUG: Falha ao copiar dados de Low: ", GetLastError());
      return;
   }
   
   copied = CopyClose(_Symbol, PERIOD_CURRENT, 0, 100, close);
   if(copied != 100) 
   {
      Print("DEBUG: Falha ao copiar dados de Close: ", GetLastError());
      return;
   }
   
   // Corrigindo o uso do CopyTickVolume
   long volume_array[];
   ArraySetAsSeries(volume_array, true);
   copied = CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, 100, volume_array);
   if(copied != 100) 
   {
      Print("DEBUG: Falha ao copiar dados de Volume: ", GetLastError());
      return;
   }
   
   // Convertendo long para double
   ArrayResize(volume, copied);
   for(int i = 0; i < copied; i++)
   {
      volume[i] = (double)volume_array[i];
   }
   
   // Atualizar modelos
   g_grav_model.UpdateThermalEnergy(volume, 20);
   g_grav_model.CalculateMagneticField(high, low, 20);
   g_grav_model.MapChannelVector(close, volume, 20);
   g_grav_model.IdentifyPOCs(close, volume, 20);
   
   g_inst_radar.ScanInstitutionalPulse(volume, 20);
   g_inst_radar.MapEnergyFlow(close, volume, 20);
   
   datetime time[];
   ArraySetAsSeries(time, true);
   copied = CopyTime(_Symbol, PERIOD_CURRENT, 0, 100, time);
   if(copied != 100) 
   {
      Print("DEBUG: Falha ao copiar dados de Time: ", GetLastError());
      return;
   }
   
   g_inst_radar.TuneCosmicFrequency(time, volume, 20);
   
   g_fib_analysis.IdentifySwingPoints(high, low, 20);
   g_fib_analysis.CalculateFibonacciLevels();
   
   // Verificar sinais de trading
   ENUM_APOLLO11_SIGNAL signal = CheckForSignal();
   Print("DEBUG: Sinal gerado: ", SignalToString(signal));
   
   // Gerenciar posições existentes
   ManagePositions();
   
   // Executar sinais de trading
   if(signal != SIGNAL_NONE)
   {
      Print("DEBUG: Tentando executar sinal: ", SignalToString(signal));
      if(ExecuteSignal(signal))
      {
         Print("DEBUG: Sinal executado com sucesso!");
      }
      else
      {
         Print("DEBUG: Falha ao executar sinal!");
      }
   }
   
   // Atualizar indicadores visuais
   UpdateIndicators();
}