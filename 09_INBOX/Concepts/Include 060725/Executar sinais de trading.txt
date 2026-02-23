//+------------------------------------------------------------------+
//| Executar sinais de trading                                       |
//+------------------------------------------------------------------+
bool ExecuteSignal(ENUM_APOLLO11_SIGNAL signal)
{
   Print("=== ExecuteSignal Debug ===");
   
   // Verificar se o trading está permitido
   if(!IsTradeAllowed())
   {
      Print("DEBUG: Trading não permitido na função ExecuteSignal");
      return false;
   }
   
   // Verificar se já existe posição aberta
   if(PositionSelect(_Symbol))
   {
      Print("DEBUG: Já existe posição aberta para ", _Symbol);
      return false;
   }
   
   // Obter preços atuais
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   Print("DEBUG: Preços atuais - Ask: ", ask, " Bid: ", bid, " Point: ", point);
   
   // Calcular tamanho do lote
   double lots = CalculateLots();
   Print("DEBUG: Tamanho do lote calculado: ", lots);
   
   if(lots <= 0)
   {
      Print("DEBUG: Erro: Cálculo de lotes resultou em valor inválido: ", lots);
      return false;
   }
   
   // Preparar ordem
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = lots;
   request.magic = MagicNumber;
   request.deviation = 10;
   
   if(signal == SIGNAL_BUY)
   {
      request.type = ORDER_TYPE_BUY;
      request.price = ask;
      request.sl = ask - StopLossPoints * point;
      request.tp = ask + TakeProfitPoints * point;
      Print("DEBUG: Ordem de COMPRA - Preço: ", request.price, " SL: ", request.sl, " TP: ", request.tp);
   }
   else if(signal == SIGNAL_SELL)
   {
      request.type = ORDER_TYPE_SELL;
      request.price = bid;
      request.sl = bid + StopLossPoints * point;
      request.tp = bid - TakeProfitPoints * point;
      Print("DEBUG: Ordem de VENDA - Preço: ", request.price, " SL: ", request.sl, " TP: ", request.tp);
   }
   
   // Enviar ordem
   bool success = OrderSend(request, result);
   Print("DEBUG: Resultado do envio da ordem: ", success ? "Sucesso" : "Falha");
   
   if(!success)
   {
      int error = GetLastError();
      Print("DEBUG: Erro ao enviar ordem - Código: ", error);
      Print("DEBUG: Descrição do erro: ", GetLastError());
      return false;
   }
   
   Print("DEBUG: Ordem executada com sucesso - Ticket: ", result.order);
   return true;
}
