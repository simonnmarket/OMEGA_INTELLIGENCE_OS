//+------------------------------------------------------------------+
//|                                                 TradeExecutor.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include "..\Interfaces\IModule.mqh"

// Classe principal de execução de ordens
class CTradeExecutor : public IActionExecutor
{
private:
   CTrade m_trade;
   CPositionInfo m_position;
   double m_lot_size;
   int m_magic_number;
   double m_stop_loss;
   double m_take_profit;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CTradeExecutor()
   {
      m_lot_size = 0.01;
      m_magic_number = 0;
      m_stop_loss = 0.0;
      m_take_profit = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_lot_size = 0.01;
      m_magic_number = 0;
      m_stop_loss = 0.0;
      m_take_profit = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      m_trade.SetExpertMagicNumber(m_magic_number);
      m_trade.SetMarginMode();
      m_trade.SetTypeFillingBySymbol(_Symbol);
      m_trade.SetDeviationInPoints(10);
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_lot_size > 0.0 && m_magic_number > 0;
   }
   
   void Cleanup() override
   {
      m_lot_size = 0.01;
      m_magic_number = 0;
      m_stop_loss = 0.0;
      m_take_profit = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "TradeExecutor"; }
   
   // Implementação de IActionExecutor
   bool ExecuteAction(const ENUM_MARKET_SIGNAL signal) override
   {
      if(!m_is_initialized || signal == SIGNAL_NONE) return false;
      
      if(signal == SIGNAL_BUY)
         return ExecuteBuy();
      else if(signal == SIGNAL_SELL)
         return ExecuteSell();
         
      return false;
   }
   
   bool CanExecuteAction(const ENUM_MARKET_SIGNAL signal) override
   {
      if(!m_is_initialized || signal == SIGNAL_NONE) return false;
      
      // Verificar se já existe posição aberta
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(m_position.SelectByIndex(i))
         {
            if(m_position.Symbol() == _Symbol && m_position.Magic() == m_magic_number)
               return false;
         }
      }
      
      return true;
   }
   
   // Métodos específicos do TradeExecutor
   bool Init(double lot_size, int magic_number)
   {
      m_lot_size = lot_size;
      m_magic_number = magic_number;
      m_trade.SetExpertMagicNumber(magic_number);
      m_trade.SetMarginMode();
      m_trade.SetTypeFillingBySymbol(_Symbol);
      m_trade.SetDeviationInPoints(10);
      
      return true;
   }
   
   bool ExecuteTrade(ENUM_MARKET_SIGNAL signal, double stop_loss, double take_profit)
   {
      if(!m_is_initialized || signal == SIGNAL_NONE) return false;
      
      m_stop_loss = stop_loss;
      m_take_profit = take_profit;
      
      return ExecuteAction(signal);
   }
   
   bool CloseAllPositions()
   {
      if(!m_is_initialized) return false;
      
      bool result = true;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(m_position.SelectByIndex(i))
         {
            if(m_position.Symbol() == _Symbol && m_position.Magic() == m_magic_number)
            {
               if(!m_trade.PositionClose(m_position.Ticket()))
                  result = false;
            }
         }
      }
      
      return result;
   }
   
   // Getters
   double GetLotSize() const { return m_lot_size; }
   int GetMagicNumber() const { return m_magic_number; }
   
private:
   bool ExecuteBuy()
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl = (m_stop_loss > 0.0) ? ask - m_stop_loss * _Point : 0.0;
      double tp = (m_take_profit > 0.0) ? ask + m_take_profit * _Point : 0.0;
      
      return m_trade.Buy(m_lot_size, _Symbol, ask, sl, tp, "GALEX Buy");
   }
   
   bool ExecuteSell()
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl = (m_stop_loss > 0.0) ? bid + m_stop_loss * _Point : 0.0;
      double tp = (m_take_profit > 0.0) ? bid - m_take_profit * _Point : 0.0;
      
      return m_trade.Sell(m_lot_size, _Symbol, bid, sl, tp, "GALEX Sell");
   }
}; 