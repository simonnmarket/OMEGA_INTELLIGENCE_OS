//+------------------------------------------------------------------+
//| StealthExecutor.mqh - Execução Stealth e Iceberg Orders          |
//| Inspirado em: Renaissance Technologies, Two Sigma                 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>

class StealthExecutor
{
private:
   CTrade m_trade;
   int m_magic_number;
   double m_iceberg_size;
   double m_min_lot;
   double m_max_lot;
   double m_lot_step;
   string m_log_file;
   
   // Estrutura para ordens iceberg
   struct IcebergOrder {
      ulong ticket;
      double total_lot;
      double remaining_lot;
      ENUM_ORDER_TYPE direction;
      double price;
      double stop_loss;
      double take_profit;
   };
   
   IcebergOrder m_orders[];
   
   // Métodos privados
   bool ValidateLotSize(double lot)
   {
      return lot >= m_min_lot && lot <= m_max_lot;
   }
   
   double NormalizeLotSize(double lot)
   {
      return MathFloor(lot / m_lot_step) * m_lot_step;
   }
   
   string GetOrderSymbol(ulong ticket)
   {
      if(OrderSelect(ticket))
         return OrderGetString(ORDER_SYMBOL);
      return "";
   }
   
   void CleanupCompletedOrders()
   {
      for(int i = ArraySize(m_orders) - 1; i >= 0; i--)
      {
         if(!OrderSelect(m_orders[i].ticket))
         {
            ArrayRemove(m_orders, i, 1);
         }
      }
   }
   
   void Log(string message, string severity = "INFO") {
      int handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT|FILE_COMMON, ';');
      if(handle != INVALID_HANDLE) {
         string log_entry = StringFormat("[%s][%s] %s", 
            TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), 
            severity, 
            message);
         FileWrite(handle, log_entry);
         FileClose(handle);
      }
   }
   
   bool ValidateOrder(MqlTradeRequest request) {
      if(request.volume <= 0) {
         Log("Volume inválido", "ERROR");
         return false;
      }
      
      if(!SymbolInfoDouble(request.symbol, SYMBOL_TRADE_TICK_VALUE)) {
         Log("Símbolo inválido: " + request.symbol, "ERROR");
         return false;
      }
      
      return true;
   }
   
public:
   StealthExecutor(int magic_number, double iceberg_size)
   {
      m_magic_number = magic_number;
      m_iceberg_size = iceberg_size;
      m_trade.SetExpertMagicNumber(magic_number);
      
      // Configurar parâmetros de lotes
      m_min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
      m_max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
      m_lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
      
      m_log_file = "StealthExecutor_Log_" + IntegerToString(GetTickCount()) + ".txt";
   }
   
   bool ExecuteStealthOrder(string symbol, ENUM_ORDER_TYPE type, double lot_size, 
                          double take_profit, double stop_loss)
   {
      // Valida tamanho do lote
      if(!ValidateLotSize(lot_size))
         return false;
      
      // Calcula tamanho do iceberg
      int parts = (int)MathCeil(lot_size / m_iceberg_size);
      double iceberg_lot = NormalizeLotSize(lot_size / parts);
      
      // Cria ordem iceberg
      IcebergOrder order;
      order.ticket = 0;
      order.total_lot = lot_size;
      order.remaining_lot = lot_size - iceberg_lot;
      order.direction = type;
      order.price = type == ORDER_TYPE_BUY ? SymbolInfoDouble(symbol, SYMBOL_ASK) : 
                                             SymbolInfoDouble(symbol, SYMBOL_BID);
      order.stop_loss = stop_loss;
      order.take_profit = take_profit;
      
      // Executa primeira parte
      if(type == ORDER_TYPE_BUY)
      {
         if(!m_trade.Buy(iceberg_lot, symbol, 0, stop_loss, take_profit))
            return false;
      }
      else
      {
         if(!m_trade.Sell(iceberg_lot, symbol, 0, stop_loss, take_profit))
            return false;
      }
      
      // Salva ordem
      order.ticket = m_trade.ResultOrder();
      ArrayResize(m_orders, ArraySize(m_orders) + 1);
      m_orders[ArraySize(m_orders) - 1] = order;
      
      return true;
   }
   
   void UpdateIcebergOrders()
   {
      for(int i = 0; i < ArraySize(m_orders); i++)
      {
         if(m_orders[i].remaining_lot > 0)
         {
            ExecuteIcebergPart(i);
         }
      }
   }
   
   void ExecuteIcebergPart(int index)
   {
      if(index >= ArraySize(m_orders))
      {
         return;
      }
      
      IcebergOrder &order = m_orders[index];
      
      // Calcula próximo tamanho do lote
      double next_lot = MathMin(order.remaining_lot, m_iceberg_size);
      next_lot = NormalizeLotSize(next_lot);
      
      if(next_lot < m_min_lot)
      {
         return;
      }
      
      // Adiciona delay aleatório
      Sleep(MathRand() % 1000 + 500);
      
      // Executa ordem
      string symbol = GetOrderSymbol(order.ticket);
      if(symbol == "")
      {
         return;
      }
      
      if(order.direction == ORDER_TYPE_BUY)
      {
         if(m_trade.Buy(next_lot, symbol, 0, order.stop_loss, order.take_profit))
         {
            order.remaining_lot -= next_lot;
         }
      }
      else
      {
         if(m_trade.Sell(next_lot, symbol, 0, order.stop_loss, order.take_profit))
         {
            order.remaining_lot -= next_lot;
         }
      }
   }
   
   void SetIcebergSize(double size)
   {
      m_iceberg_size = size;
   }
   
   double GetIcebergSize()
   {
      return m_iceberg_size;
   }
   
   int GetActiveOrders()
   {
      return ArraySize(m_orders);
   }
   
   double GetRemainingLot(ulong ticket)
   {
      for(int i = 0; i < ArraySize(m_orders); i++)
      {
         if(m_orders[i].ticket == ticket)
         {
            return m_orders[i].remaining_lot;
         }
      }
      return 0;
   }
   
   bool ExecuteOrder(MqlTradeRequest request) {
      if(!ValidateOrder(request)) return false;
      
      CTrade trade;
      trade.SetExpertMagicNumber(m_magic_number);
      
      // Executa a ordem stealth
      if(!trade.OrderOpen(request.symbol, request.type, request.volume, 
                         request.price, request.sl, request.tp)) {
         Log("Erro ao abrir ordem stealth: " + IntegerToString(trade.ResultRetcode()), "ERROR");
         return false;
      }
      
      return true;
   }
}; 