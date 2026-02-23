//+------------------------------------------------------------------+
//| Verificar se o trading é permitido                               |
//+------------------------------------------------------------------+
bool IsTradeAllowed()
{
   Print("=== IsTradeAllowed Debug ===");
   
   // Verificar se o trading está habilitado no terminal
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED))
   {
      Print("DEBUG: Trading automático não está habilitado no terminal");
      return false;
   }
   
   // Verificar se o trading está habilitado para o símbolo
   if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE))
   {
      Print("DEBUG: Trading não está habilitado para o símbolo ", _Symbol);
      return false;
   }
   
   // Verificar se o EA tem permissão para trading
   if(!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))
   {
      Print("DEBUG: Trading por EAs não está habilitado na conta");
      return false;
   }
   
   // Verificar se o mercado está aberto
   if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE))
   {
      Print("DEBUG: Mercado fechado para o símbolo ", _Symbol);
      return false;
   }
   
   Print("DEBUG: Todas as verificações de trading passaram");
   return true;
}
