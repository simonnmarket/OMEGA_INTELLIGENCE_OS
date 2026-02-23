#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh> // For statistical functions

//--- Input parameters
input int EMA_Fast_Period = 12;
input int EMA_Slow_Period = 26;
input int RSI_Period = 14;
input int ATR_Period = 14;
input int ROC_Period = 10;       // Period for Rate of Change calculation
input int MaxTradesPerDay = 5;
input double MaxDailyRisk = 2.0; // Percentage of account balance
input double MaxLotSize = 1.0;
input double RiskPerTrade = 0.5; // Percentage of account balance
input bool EnableTimeFilter = true;
input int StartHour = 9;
input int EndHour = 18;
input int MagicNumber = 20240529;
input bool DebugMode = true;
input double Slippage = 3.0;    // Slippage in points

//--- Stop Loss and Take Profit parameters (as multiples of ATR)
input double StopLossMultiplier = 2.0;
input double TakeProfitMultiplier = 3.0;

//--- Trailing Stop parameters
input bool UseTrailingStop = true;
input double TrailingStopATRMultiplier = 1.0; // Trailing stop distance as a multiple of ATR

//--- Money Management parameters
input bool UseFixedLotSize = false;
input double FixedLotSize = 0.01;

//--- Volatility Filter parameters
input bool UseVolatilityFilter = true;
input double MinATRValue = 0.001;  // Minimum acceptable ATR value (e.g., 0.001 for 10 pips on a currency pair)

//--- Trend Filter parameters
input bool UseTrendFilter = true;
input int TrendFilterPeriod = 200;  // Period for the trend-defining moving average

//--- RSI Overbought/Oversold levels
input int RSI_Overbought = 70;
input int RSI_Oversold = 30;

//--- Global variables
int tradesToday = 0;
double dailyRisk = 0;
datetime lastTradeDay = 0;
int handle_ema_fast, handle_ema_slow, handle_rsi, handle_atr, handle_trend_ma;
CTrade trade;
double last_price; // Store the last price to avoid redundant calls when possible.

//--- Function prototypes
double CalculateLotSize();
double GetTrendDirection();
double CalculateStopLoss(ENUM_ORDER_TYPE orderType);
double CalculateTakeProfit(ENUM_ORDER_TYPE orderType);
double NormalizeDoubleSafe(double value, int digits);

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Create handles for indicators
   handle_ema_fast = iMA(_Symbol, PERIOD_CURRENT, EMA_Fast_Period, 0, MODE_EMA, PRICE_CLOSE);
   handle_ema_slow = iMA(_Symbol, PERIOD_CURRENT, EMA_Slow_Period, 0, MODE_EMA, PRICE_CLOSE);
   handle_rsi = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
   handle_atr = iATR(_Symbol, PERIOD_CURRENT, ATR_Period);
   handle_trend_ma = iMA(_Symbol, PERIOD_CURRENT, TrendFilterPeriod, 0, MODE_SMA, PRICE_CLOSE);

   //--- Check for invalid handles
   if (handle_ema_fast == INVALID_HANDLE || handle_ema_slow == INVALID_HANDLE ||
       handle_rsi == INVALID_HANDLE || handle_atr == INVALID_HANDLE || handle_trend_ma == INVALID_HANDLE)
   {
      Print("Error creating indicator handles: ", GetLastError());
      return INIT_FAILED;
   }

   //--- Initialize the trade object
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetDeviationInPoints(Slippage);

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   //--- Release indicator handles
   IndicatorRelease(handle_ema_fast);
   IndicatorRelease(handle_ema_slow);
   IndicatorRelease(handle_rsi);
   IndicatorRelease(handle_atr);
   IndicatorRelease(handle_trend_ma);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   //--- Time filter
   datetime current_time = TimeCurrent();
   MqlDateTime str;
   TimeToStruct(current_time, str);
   int current_hour = str.hour;
   int current_day = str.day;

   if (EnableTimeFilter && (current_hour < StartHour || current_hour >= EndHour))
      return;

   //--- Daily trade limit reset
   MqlDateTime last;
   TimeToStruct(lastTradeDay, last);

   if (last.day != current_day)
   {
      tradesToday = 0;
      dailyRisk = 0;
      lastTradeDay = current_time;
   }

   //--- Trade limits check
   if (tradesToday >= MaxTradesPerDay || dailyRisk >= MaxDailyRisk)
      return;

   //--- Indicator buffers
   double ema_fast[], ema_slow[], rsi[], atr[], trend_ma[];

   //--- Copy indicator data
   if (!CopyBuffer(handle_ema_fast, 0, 0, 3, ema_fast)) return;
   if (!CopyBuffer(handle_ema_slow, 0, 0, 3, ema_slow)) return;
   if (!CopyBuffer(handle_rsi, 0, 0, 3, rsi)) return;
   if (!CopyBuffer(handle_atr, 0, 0, 3, atr)) return;
   if (!CopyBuffer(handle_trend_ma, 0, 0, 3, trend_ma)) return;

   //--- Volatility filter
   if (UseVolatilityFilter && atr[1] < MinATRValue)
   {
      if (DebugMode) Print("Volatility too low, skipping trade.");
      return;
   }

   //--- Trend filter
   double trendDirection = GetTrendDirection();
   if (UseTrendFilter)
   {
      if (trendDirection == 1 && (ema_fast[1] < ema_slow[1]))
      {
         if (DebugMode) Print("Not trading against uptrend.");
         return;
      }
      if (trendDirection == -1 && (ema_fast[1] > ema_slow[1]))
      {
         if (DebugMode) Print("Not trading against downtrend.");
         return;
      }
   }

   //--- Trading logic
   double lotSize = CalculateLotSize();

   //--- Buy condition
   if (ema_fast[1] > ema_slow[1] && ema_fast[2] <= ema_slow[2] && rsi[1] > 50 && rsi[1] < RSI_Overbought)
   {
      double stopLoss = CalculateStopLoss(ORDER_TYPE_BUY);
      double takeProfit = CalculateTakeProfit(ORDER_TYPE_BUY);

      if (trade.Buy(lotSize, _Symbol, 0, stopLoss, takeProfit))
      {
         tradesToday++;
         dailyRisk += RiskPerTrade;
         if (DebugMode)
         {
            Print("Buy order executed: ", lotSize, " SL: ", stopLoss, " TP: ", takeProfit);
         }
      }
      else
      {
         Print("Error opening buy order: ", trade.ResultRetcodeDescription());
      }
   }
   //--- Sell condition
   else if (ema_fast[1] < ema_slow[1] && ema_fast[2] >= ema_slow[2] && rsi[1] < 50 && rsi[1] > RSI_Oversold)
   {
      double stopLoss = CalculateStopLoss(ORDER_TYPE_SELL);
      double takeProfit = CalculateTakeProfit(ORDER_TYPE_SELL);

      if (trade.Sell(lotSize, _Symbol, 0, stopLoss, takeProfit))
      {
         tradesToday++;
         dailyRisk += RiskPerTrade;
         if (DebugMode)
         {
            Print("Sell order executed: ", lotSize, " SL: ", stopLoss, " TP: ", takeProfit);
         }
      }
      else
      {
         Print("Error opening sell order: ", trade.ResultRetcodeDescription());
      }
   }

   //--- Trailing Stop implementation (call this on every tick)
   if (UseTrailingStop)
   {
      ManageTrailingStops();
   }
}

//+------------------------------------------------------------------+
//| Calculate Lot Size                                               |
//+------------------------------------------------------------------+
double CalculateLotSize()
{
   if (UseFixedLotSize)
   {
      return FixedLotSize;
   }
   else
   {
      double lot = NormalizeDoubleSafe(MathMin(MaxLotSize, AccountInfoDouble(ACCOUNT_FREEMARGIN) * RiskPerTrade / 100.0 / 1000.0), 2);
      return lot;
   }
}

//+------------------------------------------------------------------+
//| Get Trend Direction                                              |
//+------------------------------------------------------------------+
double GetTrendDirection()
{
   double trend_ma[];
   if (!CopyBuffer(handle_trend_ma, 0, 0, 2, trend_ma))
   {
      Print("Error copying trend MA buffer: ", GetLastError());
      return 0; // Indicate error
   }

   if (trend_ma[0] > trend_ma[1])
   {
      return 1;  // Uptrend
   }
   else if (trend_ma[0] < trend_ma[1])
   {
      return -1; // Downtrend
   }
   else
   {
      return 0;  // Sideways
   }
}

//+------------------------------------------------------------------+
//| Calculate Stop Loss                                              |
//+------------------------------------------------------------------+
double CalculateStopLoss(ENUM_ORDER_TYPE orderType)
{
   double atr[];
   if (!CopyBuffer(handle_atr, 0, 0, 1, atr))
   {
      Print("Error copying ATR buffer: ", GetLastError());
      return 0;
   }

   double stopLoss;
   if (orderType == ORDER_TYPE_BUY)
   {
      stopLoss = Ask - atr[0] * StopLossMultiplier * _Point;
   }
   else
   {
      stopLoss = Bid + atr[0] * StopLossMultiplier * _Point;
   }

   return NormalizeDoubleSafe(stopLoss, _Digits);
}

//+------------------------------------------------------------------+
//| Calculate Take Profit                                            |
//+------------------------------------------------------------------+
double CalculateTakeProfit(ENUM_ORDER_TYPE orderType)
{
   double atr[];
   if (!CopyBuffer(handle_atr, 0, 0, 1, atr))
   {
      Print("Error copying ATR buffer: ", GetLastError());
      return 0;
   }

   double takeProfit;
   if (orderType == ORDER_TYPE_BUY)
   {
      takeProfit = Ask + atr[0] * TakeProfitMultiplier * _Point;
   }
   else
   {
      takeProfit = Bid - atr[0] * TakeProfitMultiplier * _Point;
   }

   return NormalizeDoubleSafe(takeProfit, _Digits);
}

//+------------------------------------------------------------------+
//| Normalize Double Safe                                            |
//+------------------------------------------------------------------+
double NormalizeDoubleSafe(double value, int digits)
{
   if (digits < 0 || digits > 8)
   {
      Print("Invalid digits value. Using _Digits.");
      digits = _Digits;
   }
   return NormalizeDouble(value, digits);
}

//+------------------------------------------------------------------+
//| Manage Trailing Stops                                            |
//+------------------------------------------------------------------+
void ManageTrailingStops()
{
   double atr[];
   if (!CopyBuffer(handle_atr, 0, 0, 1, atr))
   {
      Print("Error copying ATR buffer for trailing stop: ", GetLastError());
      return;
   }

   double trailingStopDistance = atr[0] * TrailingStopATRMultiplier * _Point;

   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if (OrderSelect(i, SELECT_BY_POS) && OrderMagicNumber() == MagicNumber && OrderSymbol() == _Symbol)
      {
         if (OrderType() == ORDER_TYPE_BUY)
         {
            double newStopLoss = Bid - trailingStopDistance;
            if (newStopLoss > OrderStopLoss() && newStopLoss < OrderOpenPrice()) //Ensure SL is not greater than open price.
            {
               newStopLoss = NormalizeDoubleSafe(newStopLoss, _Digits);
               if (!trade.OrderModify(OrderTicket(), OrderOpenPrice(), newStopLoss, OrderTakeProfit()))
               {
                  Print("Error modifying buy order trailing stop: ", trade.ResultRetcodeDescription());
               }
            }
         }
         else if (OrderType() == ORDER_TYPE_SELL)
         {
            double newStopLoss = Ask + trailingStopDistance;
            if (newStopLoss < OrderStopLoss() && newStopLoss > OrderOpenPrice())  //Ensure SL is not less than open price.
            {
               newStopLoss = NormalizeDoubleSafe(newStopLoss, _Digits);
               if (!trade.OrderModify(OrderTicket(), OrderOpenPrice(), newStopLoss, OrderTakeProfit()))
               {
                  Print("Error modifying sell order trailing stop: ", trade.ResultRetcodeDescription());
               }
            }
         }
      }
   }
}