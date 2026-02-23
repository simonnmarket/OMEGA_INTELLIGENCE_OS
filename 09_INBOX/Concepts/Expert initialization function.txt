//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Configuração do indicador
   SetIndexBuffer(0, ExtGravZoneBuffer, INDICATOR_DATA);
   SetIndexBuffer(1, ExtThermalEnergyBuffer, INDICATOR_DATA);
   SetIndexBuffer(2, ExtPOCBuffer, INDICATOR_DATA);
   SetIndexBuffer(3, ExtColorBuffer1, INDICATOR_COLOR_INDEX);
   
   // Configurar propriedades dos plots
   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_COLOR_HISTOGRAM);
   PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_HISTOGRAM);
   PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_ARROW);
   
   // Configurar cores
   PlotIndexSetInteger(0, PLOT_LINE_COLOR, clrGreen);
   PlotIndexSetInteger(1, PLOT_LINE_COLOR, clrDodgerBlue);
   PlotIndexSetInteger(2, PLOT_LINE_COLOR, clrGold);
   
   // Configurar larguras
   PlotIndexSetInteger(0, PLOT_LINE_WIDTH, 5);
   PlotIndexSetInteger(1, PLOT_LINE_WIDTH, 2);
   PlotIndexSetInteger(2, PLOT_LINE_WIDTH, 1);
   
   // Configuração do trade
   g_trade.SetExpertMagicNumber(MagicNumber);
   g_trade.SetMarginMode();
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetDeviationInPoints(10);
   
   // Inicializar arrays
   ArrayResize(ExtGravZoneBuffer, 100);
   ArrayResize(ExtThermalEnergyBuffer, 100);
   ArrayResize(ExtPOCBuffer, 100);
   ArrayResize(ExtColorBuffer1, 100);
   
   // Inicializar arrays como séries temporais
   ArraySetAsSeries(ExtGravZoneBuffer, true);
   ArraySetAsSeries(ExtThermalEnergyBuffer, true);
   ArraySetAsSeries(ExtPOCBuffer, true);
   ArraySetAsSeries(ExtColorBuffer1, true);
   
   Print("EA inicializado com sucesso!");
   return(INIT_SUCCEEDED);
}

