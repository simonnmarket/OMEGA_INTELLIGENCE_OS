//+------------------------------------------------------------------+
//| Verificar sinais de trading                                      |
//+------------------------------------------------------------------+
ENUM_APOLLO11_SIGNAL CheckForSignal()
{
   Print("=== CheckForSignal Debug ===");
   Print("Thermal Energy: ", g_grav_model.thermal_energy);
   Print("Volume Pulse: ", g_inst_radar.volume_pulse);
   Print("Neural Confidence: ", g_inst_radar.neural_confidence);
   
   // Ajustar os níveis para serem mais realistas
   if(g_grav_model.thermal_energy > 1.2 && 
      g_inst_radar.volume_pulse > 0.3 && 
      g_inst_radar.neural_confidence > 15.0)
   {
      Print("DEBUG: Condições de COMPRA atendidas:");
      Print("DEBUG: - Thermal Energy > 1.2: ", g_grav_model.thermal_energy);
      Print("DEBUG: - Volume Pulse > 0.3: ", g_inst_radar.volume_pulse);
      Print("DEBUG: - Neural Confidence > 15.0: ", g_inst_radar.neural_confidence);
      return SIGNAL_BUY;
   }
   
   if(g_grav_model.thermal_energy < 0.8 && 
      g_inst_radar.volume_pulse < 0.2 && 
      g_inst_radar.neural_confidence > 15.0)
   {
      Print("DEBUG: Condições de VENDA atendidas:");
      Print("DEBUG: - Thermal Energy < 0.8: ", g_grav_model.thermal_energy);
      Print("DEBUG: - Volume Pulse < 0.2: ", g_inst_radar.volume_pulse);
      Print("DEBUG: - Neural Confidence > 15.0: ", g_inst_radar.neural_confidence);
      return SIGNAL_SELL;
   }
   
   Print("DEBUG: Nenhuma condição de entrada atendida");
   return SIGNAL_NONE;
}
