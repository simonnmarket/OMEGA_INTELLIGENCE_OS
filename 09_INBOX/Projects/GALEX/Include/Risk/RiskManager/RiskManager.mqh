//+------------------------------------------------------------------+
//|                                                  RiskManager.mqh |
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
#include <Arrays\ArrayDouble.mqh>

// Classe principal de gestão de risco
class CRiskManager
{
private:
   double m_initial_lots;
   double m_max_lots;
   double m_risk_percent;
   int m_stop_loss_points;
   int m_take_profit_points;
   bool m_use_atr_stop_loss;
   double m_atr_stop_loss_multiplier;
   bool m_use_atr_take_profit;
   double m_atr_take_profit_multiplier;
   bool m_use_trailing_stop;
   int m_trailing_stop;
   int m_trailing_step;
   bool m_use_break_even;
   int m_break_even_points;
   int m_break_even_profit;
   
public:
   // Construtor
   CRiskManager()
   {
      m_initial_lots = 0.01;
      m_max_lots = 1.0;
      m_risk_percent = 1.0;
      m_stop_loss_points = 150;
      m_take_profit_points = 300;
      m_use_atr_stop_loss = true;
      m_atr_stop_loss_multiplier = 2.0;
      m_use_atr_take_profit = true;
      m_atr_take_profit_multiplier = 3.0;
      m_use_trailing_stop = true;
      m_trailing_stop = 50;
      m_trailing_step = 10;
      m_use_break_even = true;
      m_break_even_points = 30;
      m_break_even_profit = 10;
   }
   
   // Inicialização
   bool Init(double initial_lots, double max_lots, double risk_percent,
             int stop_loss_points, int take_profit_points,
             bool use_atr_stop_loss, double atr_stop_loss_multiplier,
             bool use_atr_take_profit, double atr_take_profit_multiplier,
             bool use_trailing_stop, int trailing_stop, int trailing_step,
             bool use_break_even, int break_even_points, int break_even_profit)
   {
      m_initial_lots = initial_lots;
      m_max_lots = max_lots;
      m_risk_percent = risk_percent;
      m_stop_loss_points = stop_loss_points;
      m_take_profit_points = take_profit_points;
      m_use_atr_stop_loss = use_atr_stop_loss;
      m_atr_stop_loss_multiplier = atr_stop_loss_multiplier;
      m_use_atr_take_profit = use_atr_take_profit;
      m_atr_take_profit_multiplier = atr_take_profit_multiplier;
      m_use_trailing_stop = use_trailing_stop;
      m_trailing_stop = trailing_stop;
      m_trailing_step = trailing_step;
      m_use_break_even = use_break_even;
      m_break_even_points = break_even_points;
      m_break_even_profit = break_even_profit;
      
      return true;
   }
   
   // Atualizar gestão de risco
   void Update()
   {
      if(m_use_trailing_stop)
         UpdateTrailingStop();
         
      if(m_use_break_even)
         UpdateBreakEven();
   }
   
   // Obter tamanho do lote
   double GetPositionSize(double stop_loss_points)
   {
      double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double risk_amount = account_balance * m_risk_percent / 100.0;
      double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
      
      double lots = NormalizeDouble(risk_amount / (stop_loss_points * tick_value), 2);
      lots = MathFloor(lots / lot_step) * lot_step;
      
      return MathMin(MathMax(lots, m_initial_lots), m_max_lots);
   }
   
   // Obter Stop Loss
   double GetStopLoss(ENUM_MARKET_SIGNAL signal)
   {
      if(m_use_atr_stop_loss)
      {
         double atr = iATR(_Symbol, PERIOD_CURRENT, 14, 0);
         return atr * m_atr_stop_loss_multiplier;
      }
      
      return m_stop_loss_points;
   }
   
   // Obter Take Profit
   double GetTakeProfit(ENUM_MARKET_SIGNAL signal)
   {
      if(m_use_atr_take_profit)
      {
         double atr = iATR(_Symbol, PERIOD_CURRENT, 14, 0);
         return atr * m_atr_take_profit_multiplier;
      }
      
      return m_take_profit_points;
   }
   
private:
   // Atualizar Trailing Stop
   void UpdateTrailingStop()
   {
      CPositionInfo position;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == _Symbol)
            {
               double current_sl = position.StopLoss();
               double current_tp = position.TakeProfit();
               double current_price = position.PriceOpen();
               double current_profit = position.Profit();
               
               if(current_profit > 0)
               {
                  double new_sl = 0.0;
                  
                  if(position.PositionType() == POSITION_TYPE_BUY)
                  {
                     new_sl = SymbolInfoDouble(_Symbol, SYMBOL_BID) - m_trailing_stop * _Point;
                     if(new_sl > current_sl + m_trailing_step * _Point)
                     {
                        CTrade trade;
                        trade.PositionModify(position.Ticket(), new_sl, current_tp);
                     }
                  }
                  else if(position.PositionType() == POSITION_TYPE_SELL)
                  {
                     new_sl = SymbolInfoDouble(_Symbol, SYMBOL_ASK) + m_trailing_stop * _Point;
                     if(new_sl < current_sl - m_trailing_step * _Point || current_sl == 0)
                     {
                        CTrade trade;
                        trade.PositionModify(position.Ticket(), new_sl, current_tp);
                     }
                  }
               }
            }
         }
      }
   }
   
   // Atualizar Break Even
   void UpdateBreakEven()
   {
      CPositionInfo position;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(position.SelectByIndex(i))
         {
            if(position.Symbol() == _Symbol)
            {
               double current_sl = position.StopLoss();
               double current_tp = position.TakeProfit();
               double current_price = position.PriceOpen();
               double current_profit = position.Profit();
               
               if(current_profit > m_break_even_points * _Point)
               {
                  if(position.PositionType() == POSITION_TYPE_BUY)
                  {
                     if(current_sl < current_price)
                     {
                        CTrade trade;
                        trade.PositionModify(position.Ticket(), current_price + m_break_even_profit * _Point, current_tp);
                     }
                  }
                  else if(position.PositionType() == POSITION_TYPE_SELL)
                  {
                     if(current_sl > current_price || current_sl == 0)
                     {
                        CTrade trade;
                        trade.PositionModify(position.Ticket(), current_price - m_break_even_profit * _Point, current_tp);
                     }
                  }
               }
            }
         }
      }
   }
}; 