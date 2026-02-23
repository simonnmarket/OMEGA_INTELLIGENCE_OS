//+------------------------------------------------------------------+
//|                      TradingAgent.mqh                            |
//|       Agente responsável por executar ordens de trading          |
//+------------------------------------------------------------------+
#pragma once
#include "..\Core\types.mqh"
#include "..\Utils\Log.mqh"
#include "..\Config\GlobalConfig.mqh"

class TradingAgent {
private:
   string symbol;
   double lot_size;

public:
   // Construtor
   void Init(string _symbol, double _lot) {
      symbol   = _symbol;
      lot_size = _lot;
   }

   // Execução de ordem de compra
   TaskResult Buy(double sl=0.0, double tp=0.0, string comment="Numeia Buy") {
      TaskResult result;
      result.timestamp = TimeCurrent();

      double price = SymbolInfoDouble(symbol, SYMBOL_ASK);
      if (price == 0) {
         result.success = false;
         result.message = "Erro ao obter preço ASK";
         Log::Error(result.message);
         return result;
      }

      MqlTradeRequest request = {};
      MqlTradeResult  trade_result = {};
      request.action   = TRADE_ACTION_DEAL;
      request.symbol   = symbol;
      request.volume   = lot_size;
      request.type     = ORDER_TYPE_BUY;
      request.price    = price;
      request.sl       = sl;
      request.tp       = tp;
      request.deviation= 10;
      request.magic    = GlobalConfig::MAGIC_NUMBER;
      request.comment  = comment;

      if (!OrderSend(request, trade_result)) {
         result.success = false;
         result.message = "Erro na execução da ordem de compra: " + trade_result.comment;
         Log::Error(result.message);
      } else {
         result.success = true;
         result.message = "Ordem de compra executada com sucesso. Ticket: " + IntegerToString(trade_result.order);
         Log::Info(result.message);
      }

      return result;
   }

   // Execução de ordem de venda
   TaskResult Sell(double sl=0.0, double tp=0.0, string comment="Numeia Sell") {
      TaskResult result;
      result.timestamp = TimeCurrent();

      double price = SymbolInfoDouble(symbol, SYMBOL_BID);
      if (price == 0) {
         result.success = false;
         result.message = "Erro ao obter preço BID";
         Log::Error(result.message);
         return result;
      }

      MqlTradeRequest request = {};
      MqlTradeResult  trade_result = {};
      request.action   = TRADE_ACTION_DEAL;
      request.symbol   = symbol;
      request.volume   = lot_size;
      request.type     = ORDER_TYPE_SELL;
      request.price    = price;
      request.sl       = sl;
      request.tp       = tp;
      request.deviation= 10;
      request.magic    = GlobalConfig::MAGIC_NUMBER;
      request.comment  = comment;

      if (!OrderSend(request, trade_result)) {
         result.success = false;
         result.message = "Erro na execução da ordem de venda: " + trade_result.comment;
         Log::Error(result.message);
      } else {
         result.success = true;
         result.message = "Ordem de venda executada com sucesso. Ticket: " + IntegerToString(trade_result.order);
         Log::Info(result.message);
      }

      return result;
   }
};
