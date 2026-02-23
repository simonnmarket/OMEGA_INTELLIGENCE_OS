//+------------------------------------------------------------------+
//| Atualizar indicadores visuais                                    |
//+------------------------------------------------------------------+
void UpdateIndicators()
{
   // Atualizar buffers do indicador
   for(int i = 0; i < 100; i++)
   {
      ExtGravZoneBuffer[i] = g_grav_model.channel_vector;
      ExtThermalEnergyBuffer[i] = g_grav_model.thermal_energy;
      ExtPOCBuffer[i] = g_grav_model.poc_level;
      ExtColorBuffer1[i] = g_grav_model.thermal_energy > 100.0 ? 0 : 1;
   }
   
   // Atualizar objetos gráficos
   string obj_name = "GALEX_FibLevels";
   ObjectsDeleteAll(0, obj_name);
   
   // Verificar se o array de níveis Fibonacci foi inicializado
   if(ArraySize(g_fib_analysis.fib_levels) > 0)
   {
      for(int i = 0; i < ArraySize(g_fib_analysis.fib_levels); i++)
      {
         string level_name = obj_name + "_" + IntegerToString(i);
         if(ObjectCreate(0, level_name, OBJ_HLINE, 0, 0, g_fib_analysis.fib_levels[i]))
         {
            ObjectSetInteger(0, level_name, OBJPROP_COLOR, clrGold);
            ObjectSetInteger(0, level_name, OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, level_name, OBJPROP_WIDTH, 1);
            ObjectSetInteger(0, level_name, OBJPROP_BACK, true);
            ObjectSetInteger(0, level_name, OBJPROP_SELECTABLE, false);
            ObjectSetInteger(0, level_name, OBJPROP_SELECTED, false);
            ObjectSetInteger(0, level_name, OBJPROP_HIDDEN, true);
            ObjectSetInteger(0, level_name, OBJPROP_ZORDER, 0);
         }
      }
   }
   
   // Forçar atualização do gráfico
   ChartRedraw(0);
   
   // Adicionar log para debug
   static datetime last_update = 0;
   datetime current_time = TimeCurrent();
   if(current_time - last_update >= 60) // Log a cada minuto
   {
      Print("Indicadores atualizados - Thermal Energy: ", g_grav_model.thermal_energy,
            " Volume Pulse: ", g_inst_radar.volume_pulse,
            " Neural Confidence: ", g_inst_radar.neural_confidence);
      last_update = current_time;
   }
} 