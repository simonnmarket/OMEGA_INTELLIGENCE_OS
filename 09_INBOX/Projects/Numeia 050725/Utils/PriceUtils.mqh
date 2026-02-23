//+------------------------------------------------------------------+
//|                       PriceUtils.mqh                             |
//|     Funções auxiliares para manipulação e análise de preços      |
//+------------------------------------------------------------------+
#ifndef __PRICE_UTILS_MQH__
#define __PRICE_UTILS_MQH__

#include <Trade\SymbolInfo.mqh>

// Retorna o preço Ask atual do símbolo
double GetCurrentAsk(string symbol = NULL) {
   if (symbol == NULL) symbol = _Symbol;
   return SymbolInfoDouble(symbol, SYMBOL_ASK);
}

// Retorna o preço Bid atual do símbolo
double GetCurrentBid(string symbol = NULL) {
   if (symbol == NULL) symbol = _Symbol;
   return SymbolInfoDouble(symbol, SYMBOL_BID);
}

// Retorna o spread atual do símbolo
double GetSpreadPoints(string symbol = NULL) {
   if (symbol == NULL) symbol = _Symbol;
   double ask = GetCurrentAsk(symbol);
   double bid = GetCurrentBid(symbol);
   return (ask - bid) / SymbolInfoDouble(symbol, SYMBOL_POINT);
}

// Retorna o tamanho mínimo de lote permitido para o símbolo
double GetMinLotSize(string symbol = NULL) {
   if (symbol == NULL) symbol = _Symbol;
   return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
}

// Arredonda um preço de acordo com os dígitos do ativo
double NormalizePrice(double price, string symbol = NULL) {
   if (symbol == NULL) symbol = _Symbol;
   int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   return NormalizeDouble(price, digits);
}

#endif // __PRICE_UTILS_MQH__
