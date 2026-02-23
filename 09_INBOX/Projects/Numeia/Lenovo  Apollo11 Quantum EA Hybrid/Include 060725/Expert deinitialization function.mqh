//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Limpeza de objetos gráficos
   ObjectsDeleteAll(0, "GALEX_");
}
