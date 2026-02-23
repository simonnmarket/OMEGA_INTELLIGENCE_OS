//+------------------------------------------------------------------+
//| OrderLauncher.mqh - Trade Execution Manager                      |
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

class OrderLauncher
{
private:
   CTrade m_trade;
   int m_magic_number;
   double m_take_profit;
   double m_stop_loss;
   string m_symbol;
   double m_volume;
   double m_sl;
   double m_tp;
   ENUM_ORDER_TYPE m_type;
   string m_log_file;
   
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
   
   bool ValidateOrder() {
      if(m_volume <= 0) {
         Log("Volume inválido", "ERROR");
         return false;
      }
      
      if(!SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE)) {
         Log("Símbolo inválido: " + m_symbol, "ERROR");
         return false;
      }
      
      return true;
   }
   
public:
   OrderLauncher(string symbol, double volume, double sl, double tp, 
                ENUM_ORDER_TYPE type, long magic_number = 123456) 
      : m_symbol(symbol), m_volume(volume), m_sl(sl), m_tp(tp),
        m_type(type), m_magic_number(magic_number) {
      m_log_file = "OrderLauncher_Log_" + IntegerToString(GetTickCount()) + ".txt";
      
      m_trade.SetExpertMagicNumber(m_magic_number);
      m_trade.SetMarginMode();
      m_trade.SetTypeFillingBySymbol(_Symbol);
      m_trade.SetDeviationInPoints(10);
   }
   
   bool ExecuteOrder()
   {
      if(!ValidateOrder()) return false;
      
      double price = m_type == ORDER_TYPE_BUY ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) 
                                             : SymbolInfoDouble(m_symbol, SYMBOL_BID);
      
      if(!m_trade.OrderOpen(m_symbol, m_type, m_volume, price, m_sl, m_tp)) {
         Log("Erro ao abrir ordem: " + IntegerToString((int)m_trade.ResultRetcode()), "ERROR");
         return false;
      }
      
      return true;
   }
   
   void SetTakeProfit(double tp)
   {
      m_take_profit = tp;
   }
   
   void SetStopLoss(double sl)
   {
      m_stop_loss = sl;
   }
   
   bool ModifyOrder()
   {
      if(!ValidateOrder()) return false;
      
      for(int i = OrdersTotal() - 1; i >= 0; i--) {
         if(OrderSelect(i, SELECT_BY_POS)) {
            ulong ticket = OrderGetTicket(i);
            if(OrderGetString(ORDER_SYMBOL) == m_symbol && 
               OrderGetInteger(ORDER_MAGIC) == m_magic_number) {
               
               if(!m_trade.OrderModify(ticket, OrderGetDouble(ORDER_PRICE_OPEN), 
                                   m_sl, m_tp)) {
                  Log("Erro ao modificar ordem: " + IntegerToString((int)m_trade.ResultRetcode()), "ERROR");
                  return false;
               }
            }
         }
      }
      
      return true;
   }
   
   bool ClosePosition(ulong ticket)
   {
      if(!m_trade.PositionClose(ticket)) {
         Print("Erro ao fechar posição: ", m_trade.ResultRetcodeDescription());
         return false;
      }
      return true;
   }
   
   double GetLastOrderPrice()
   {
      return m_trade.ResultPrice();
   }
   
   int GetLastOrderError()
   {
      return m_trade.ResultRetcode();
   }
   
   string GetLastOrderErrorDescription()
   {
      return m_trade.ResultRetcodeDescription();
   }
}; 