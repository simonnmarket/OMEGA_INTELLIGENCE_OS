//+------------------------------------------------------------------+
//|                                              SkylerBotV3.0.mq5   |
//|                        Copyright 2023, Skyler Trading Systems    |
//|                                    https://www.skylertrading.com |
//+------------------------------------------------------------------+
#property copyright "Skyler Trading Systems"
#property version   "3.00"
#property strict

// Enums
enum ENUM_SIGNAL {
   SIGNAL_NONE = 0,
   SIGNAL_BUY = 1,
   SIGNAL_SELL = -1
};

enum ENUM_CONFIDENCE {
   CONFIDENCE_LOW = 0,
   CONFIDENCE_MEDIUM = 1,
   CONFIDENCE_HIGH = 2
};

enum ENUM_NEWS_IMPACT {
   NEWS_IGNORE = 0,
   NEWS_FILTER_MEDIUM = 1,
   NEWS_FILTER_HIGH = 2
};

// Input Parameters
input group "Strategy Settings"
input ENUM_TIMEFRAMES Timeframe = PERIOD_H1;           // Timeframe for analysis
input string SymbolToTrade = "EURUSD";                 // Symbol to trade
input int MovingAveragePeriod = 20;                    // MA period
input int RSI_Period = 14;                            // RSI period
input int RSI_UpperLevel = 70;                         // RSI overbought level
input int RSI_LowerLevel = 30;                         // RSI oversold level
input int MACD_Fast = 12;                              // MACD fast EMA
input int MACD_Slow = 26;                              // MACD slow EMA
input int MACD_Signal = 9;                             // MACD signal line

input group "Risk Management"
input double LotSize = 0.1;                            // Base lot size
input double RiskPercent = 2.0;                        // Risk per trade (%)
input int StopLoss = 200;                              // Default SL (points)
input int TakeProfit = 400;                            // Default TP (points)
input bool UseDynamicRisk = true;                      // Use dynamic risk
input double MaxRiskPercent = 5.0;                     // Max risk per trade (%)

input group "Trade Execution"
input int Slippage = 5;                                // Max allowed slippage
input bool UseTrailingStop = true;                     // Enable trailing stop
input int TrailingStop = 100;                          // Trailing stop distance
input int TrailingStep = 10;                           // Trailing step size
input bool UseBreakEven = true;                        // Enable break even
input int BreakEvenPoints = 50;                        // BE activation level
input int MinTradeGap = 3600;                          // Minimum time between trades (seconds)

input group "Filters"
input bool UseTimeFilter = true;                       // Enable time filter
input string StartTime = "08:00";                      // Trading start time
input string EndTime = "20:00";                        // Trading end time
input ENUM_NEWS_IMPACT NewsFilter = NEWS_FILTER_HIGH;  // News filtering level
input int NewsMinutesBefore = 60;                      // Minutes before news
input int NewsMinutesAfter = 30;                       // Minutes after news
input double MaxSpread = 3.0;                          // Max allowed spread (points)
input double MinATR = 0.0005;                          // Minimum ATR for trading
input double MaxATR = 0.0050;                          // Maximum ATR for trading

// Handles
int ma_handle, rsi_handle, macd_handle, atr_handle;

// Global variables
datetime last_bar_time;
int magic_number = 2025;
double point;
ENUM_SIGNAL last_signal;
ENUM_CONFIDENCE last_confidence;
double last_score;
datetime last_trade_time;
int total_trades;
int winning_trades;
double total_profit;
double equity_high;
double equity_low;
MqlDateTime start_time_struct, end_time_struct;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Validate symbol
   if(Symbol() != SymbolToTrade)
   {
      Alert("Error: EA should be attached to ", SymbolToTrade, " chart");
      return INIT_FAILED;
   }

   // Get point value
   point = SymbolInfoDouble(SymbolToTrade, SYMBOL_POINT);
   if(point == 0)
   {
      Alert("Error: Failed to get point value");
      return INIT_FAILED;
   }

   // Parse trading times
   if(!TimeToStruct(StringToTime(StartTime), start_time_struct) || 
      !TimeToStruct(StringToTime(EndTime), end_time_struct))
   {
      Alert("Error: Invalid time format. Use HH:MM");
      return INIT_FAILED;
   }

   // Initialize indicators
   ma_handle = iMA(SymbolToTrade, Timeframe, MovingAveragePeriod, 0, MODE_SMA, PRICE_CLOSE);
   rsi_handle = iRSI(SymbolToTrade, Timeframe, RSI_Period, PRICE_CLOSE);
   macd_handle = iMACD(SymbolToTrade, Timeframe, MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE);
   atr_handle = iATR(SymbolToTrade, Timeframe, 14);

   if(ma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE || 
      macd_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE)
   {
      Alert("Error: Failed to create indicator handles");
      return INIT_FAILED;
   }

   // Reset statistics
   total_trades = 0;
   winning_trades = 0;
   total_profit = 0.0;
   last_trade_time = 0;
   last_signal = SIGNAL_NONE;
   last_confidence = CONFIDENCE_LOW;
   last_score = 0.0;
   equity_high = AccountInfoDouble(ACCOUNT_EQUITY);
   equity_low = equity_high;

   // Set magic number based on symbol and timeframe
   magic_number = StringHash(SymbolToTrade + EnumToString(Timeframe)) % 100000;

   Print("SkylerBotV3.0 initialized successfully on ", SymbolToTrade, " ", EnumToString(Timeframe));
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Release indicators
   IndicatorRelease(ma_handle);
   IndicatorRelease(rsi_handle);
   IndicatorRelease(macd_handle);
   IndicatorRelease(atr_handle);
   
   // Save performance report
   SavePerformanceReport();
   
   Print("SkylerBotV3.0 deinitialized. Reason: ", GetUninitReasonText(reason));
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check for new bar
   if(!IsNewBar()) return;
   
   // Check trading conditions
   if(!CheckTradingConditions()) return;
   
   // Manage open positions
   ManagePositions();
   
   // Check for new trading opportunities
   if(!HasOpenPosition() && TimeCurrent() - last_trade_time >= MinTradeGap)
   {
      ENUM_SIGNAL signal = GetTradingSignal();
      if(signal != SIGNAL_NONE)
      {
         ExecuteTrade(signal);
      }
   }
   
   // Update equity tracking
   UpdateEquityTracking();
}

//+------------------------------------------------------------------+
//| Check if new bar has formed                                      |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime current_time = iTime(SymbolToTrade, Timeframe, 0);
   if(current_time == last_bar_time) return false;
   last_bar_time = current_time;
   return true;
}

//+------------------------------------------------------------------+
//| Check all trading conditions                                     |
//+------------------------------------------------------------------+
bool CheckTradingConditions()
{
   // Check time filter
   if(UseTimeFilter && !IsTradingTime()) return false;
   
   // Check news filter
   if(NewsFilter != NEWS_IGNORE && IsNewsTime()) return false;
   
   // Check spread
   double spread = SymbolInfoInteger(SymbolToTrade, SYMBOL_SPREAD) * point;
   if(spread > MaxSpread * point)
   {
      Print("Spread too high: ", spread / point, " points");
      return false;
   }
   
   // Check volatility
   double atr[];
   if(CopyBuffer(atr_handle, 0, 0, 1, atr) <= 0) return false;
   if(atr[0] < MinATR || atr[0] > MaxATR)
   {
      Print("ATR out of range: ", atr[0]);
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check if current time is within trading hours                    |
//+------------------------------------------------------------------+
bool IsTradingTime()
{
   MqlDateTime current_time;
   TimeToStruct(TimeCurrent(), current_time);
   
   // Check if current time is within the trading window
   if(current_time.hour > start_time_struct.hour && current_time.hour < end_time_struct.hour)
      return true;
      
   if(current_time.hour == start_time_struct.hour && current_time.min >= start_time_struct.min)
      return true;
      
   if(current_time.hour == end_time_struct.hour && current_time.min <= end_time_struct.min)
      return true;
      
   return false;
}

//+------------------------------------------------------------------+
//| Check if news time                                               |
//+------------------------------------------------------------------+
bool IsNewsTime()
{
   // This is a placeholder for actual news checking logic
   // In a real EA, you would integrate with a news API or calendar
   return false;
}

//+------------------------------------------------------------------+
//| Generate trading signal                                          |
//+------------------------------------------------------------------+
ENUM_SIGNAL GetTradingSignal()
{
   // Get indicator values
   double ma[2], rsi[2], macd_main[2], macd_signal[2];
   if(CopyBuffer(ma_handle, 0, 0, 2, ma) <= 0 ||
      CopyBuffer(rsi_handle, 0, 0, 2, rsi) <= 0 ||
      CopyBuffer(macd_handle, 0, 0, 2, macd_main) <= 0 ||
      CopyBuffer(macd_handle, 1, 0, 2, macd_signal) <= 0)
   {
      Print("Error getting indicator values");
      return SIGNAL_NONE;
   }
   
   // Get current price
   double bid = SymbolInfoDouble(SymbolToTrade, SYMBOL_BID);
   double ask = SymbolInfoDouble(SymbolToTrade, SYMBOL_ASK);
   if(bid == 0 || ask == 0) return SIGNAL_NONE;
   
   // Calculate signals
   bool buy_signal = bid > ma[0] && 
                    rsi[0] < RSI_UpperLevel && 
                    macd_main[0] > macd_signal[0] &&
                    macd_main[0] < 0; // Only buy when MACD is below zero
                    
   bool sell_signal = ask < ma[0] && 
                     rsi[0] > RSI_LowerLevel && 
                     macd_main[0] < macd_signal[0] &&
                     macd_main[0] > 0; // Only sell when MACD is above zero
   
   // Calculate confidence level
   ENUM_CONFIDENCE confidence = CalculateConfidence(bid, ma, rsi, macd_main, macd_signal);
   
   // Only trade with medium or high confidence
   if(confidence < CONFIDENCE_MEDIUM) return SIGNAL_NONE;
   
   // Update signal tracking
   ENUM_SIGNAL new_signal = SIGNAL_NONE;
   if(buy_signal) new_signal = SIGNAL_BUY;
   if(sell_signal) new_signal = SIGNAL_SELL;
   
   if(new_signal != last_signal)
   {
      Print("Signal changed: ", SignalToString(last_signal), " -> ", SignalToString(new_signal),
            " Confidence: ", ConfidenceToString(confidence));
   }
   
   last_signal = new_signal;
   last_confidence = confidence;
   
   return new_signal;
}

//+------------------------------------------------------------------+
//| Calculate signal confidence                                      |
//+------------------------------------------------------------------+
ENUM_CONFIDENCE CalculateConfidence(double price, const double &ma[], const double &rsi[], 
                                   const double &macd_main[], const double &macd_signal[])
{
   double score = 0.0;
   
   // Trend strength (price and MA alignment)
   if((price > ma[0] && ma[0] > ma[1]) || (price < ma[0] && ma[0] < ma[1]))
      score += 0.3;
   
   // RSI confirmation
   if((rsi[0] > 60 && last_signal == SIGNAL_BUY) || (rsi[0] < 40 && last_signal == SIGNAL_SELL))
      score += 0.3;
   
   // MACD confirmation
   if((macd_main[0] > macd_signal[0] && last_signal == SIGNAL_BUY) || 
      (macd_main[0] < macd_signal[0] && last_signal == SIGNAL_SELL))
      score += 0.4;
   
   // Determine confidence level
   if(score >= 0.8) return CONFIDENCE_HIGH;
   if(score >= 0.6) return CONFIDENCE_MEDIUM;
   return CONFIDENCE_LOW;
}

//+------------------------------------------------------------------+
//| Check for open positions                                         |
//+------------------------------------------------------------------+
bool HasOpenPosition()
{
   return PositionsTotal() > 0;
}

//+------------------------------------------------------------------+
//| Manage open positions                                            |
//+------------------------------------------------------------------+
void ManagePositions()
{
   for(int i = PositionsTotal()-1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      
      if(PositionGetString(POSITION_SYMBOL) != SymbolToTrade || 
         PositionGetInteger(POSITION_MAGIC) != magic_number)
         continue;
      
      // Apply trailing stop
      if(UseTrailingStop)
         ApplyTrailingStop(ticket);
      
      // Apply break even
      if(UseBreakEven)
         ApplyBreakEven(ticket);
   }
}

//+------------------------------------------------------------------+
//| Apply trailing stop                                              |
//+------------------------------------------------------------------+
void ApplyTrailingStop(ulong ticket)
{
   if(!PositionSelectByTicket(ticket)) return;
   
   double current_sl = PositionGetDouble(POSITION_SL);
   double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
   double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
   ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
   
   if(pos_type == POSITION_TYPE_BUY)
   {
      if(current_price - open_price > TrailingStop * point)
      {
         double new_sl = current_price - TrailingStop * point;
         if(new_sl > current_sl + TrailingStep * point)
         {
            ModifyPosition(ticket, new_sl, PositionGetDouble(POSITION_TP));
         }
      }
   }
   else if(pos_type == POSITION_TYPE_SELL)
   {
      if(open_price - current_price > TrailingStop * point)
      {
         double new_sl = current_price + TrailingStop * point;
         if(new_sl < current_sl - TrailingStep * point)
         {
            ModifyPosition(ticket, new_sl, PositionGetDouble(POSITION_TP));
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Apply break even                                                 |
//+------------------------------------------------------------------+
void ApplyBreakEven(ulong ticket)
{
   if(!PositionSelectByTicket(ticket)) return;
   
   double current_sl = PositionGetDouble(POSITION_SL);
   double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
   double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
   ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
   
   if(pos_type == POSITION_TYPE_BUY)
   {
      if(current_price - open_price > BreakEvenPoints * point && current_sl < open_price)
      {
         ModifyPosition(ticket, open_price, PositionGetDouble(POSITION_TP));
      }
   }
   else if(pos_type == POSITION_TYPE_SELL)
   {
      if(open_price - current_price > BreakEvenPoints * point && current_sl > open_price)
      {
         ModifyPosition(ticket, open_price, PositionGetDouble(POSITION_TP));
      }
   }
}

//+------------------------------------------------------------------+
//| Modify position                                                  |
//+------------------------------------------------------------------+
bool ModifyPosition(ulong ticket, double sl, double tp)
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_SLTP;
   request.position = ticket;
   request.symbol = SymbolToTrade;
   request.sl = NormalizeDouble(sl, (int)SymbolInfoInteger(SymbolToTrade, SYMBOL_DIGITS));
   request.tp = NormalizeDouble(tp, (int)SymbolInfoInteger(SymbolToTrade, SYMBOL_DIGITS));
   
   if(!OrderSend(request, result))
   {
      Print("Failed to modify position ", ticket, " Error: ", GetTradeErrorText(result.retcode));
      return false;
   }
   
   Print("Position ", ticket, " modified. New SL: ", sl, " TP: ", tp);
   return true;
}

//+------------------------------------------------------------------+
//| Execute trade                                                    |
//+------------------------------------------------------------------+
void ExecuteTrade(ENUM_SIGNAL signal)
{
   // Calculate lot size
   double lot_size = CalculateLotSize();
   
   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   request.action = TRADE_ACTION_DEAL;
   request.symbol = SymbolToTrade;
   request.volume = lot_size;
   request.deviation = Slippage;
   request.magic = magic_number;
   
   // Set price, SL, TP based on signal
   if(signal == SIGNAL_BUY)
   {
      request.type = ORDER_TYPE_BUY;
      request.price = SymbolInfoDouble(SymbolToTrade, SYMBOL_ASK);
      request.sl = NormalizeDouble(request.price - StopLoss * point, _Digits);
      request.tp = NormalizeDouble(request.price + TakeProfit * point, _Digits);
   }
   else
   {
      request.type = ORDER_TYPE_SELL;
      request.price = SymbolInfoDouble(SymbolToTrade, SYMBOL_BID);
      request.sl = NormalizeDouble(request.price + StopLoss * point, _Digits);
      request.tp = NormalizeDouble(request.price - TakeProfit * point, _Digits);
   }
   
   // Send trade request
   if(!OrderSend(request, result))
   {
      Print("Trade failed. Error: ", GetTradeErrorText(result.retcode));
      return;
   }
   
   // Update trade statistics
   last_trade_time = TimeCurrent();
   total_trades++;
   
   Print("Trade executed: ", SignalToString(signal), 
         " Lot: ", lot_size, 
         " Price: ", request.price, 
         " SL: ", request.sl, 
         " TP: ", request.tp);
}

//+------------------------------------------------------------------+
//| Calculate lot size                                               |
//+------------------------------------------------------------------+
double CalculateLotSize()
{
   double lot_size = LotSize;
   
   // Dynamic risk calculation
   if(UseDynamicRisk)
   {
      double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double risk_amount = account_balance * RiskPercent / 100.0;
      double tick_value = SymbolInfoDouble(SymbolToTrade, SYMBOL_TRADE_TICK_VALUE);
      double tick_size = SymbolInfoDouble(SymbolToTrade, SYMBOL_TRADE_TICK_SIZE);
      
      // Calculate lot size based on risk
      if(tick_value > 0 && tick_size > 0)
      {
         double risk_lot = risk_amount / (StopLoss * point / tick_size * tick_value);
         lot_size = MathMin(lot_size, risk_lot);
      }
      
      // Apply max risk limit
      double max_risk_lot = account_balance * MaxRiskPercent / 100.0 / (StopLoss * point * SymbolInfoDouble(SymbolToTrade, SYMBOL_TRADE_CONTRACT_SIZE));
      lot_size = MathMin(lot_size, max_risk_lot);
   }
   
   // Normalize lot size
   double min_lot = SymbolInfoDouble(SymbolToTrade, SYMBOL_VOLUME_MIN);
   double max_lot = SymbolInfoDouble(SymbolToTrade, SYMBOL_VOLUME_MAX);
   double lot_step = SymbolInfoDouble(SymbolToTrade, SYMBOL_VOLUME_STEP);
   
   lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
   lot_size = NormalizeDouble(lot_size / lot_step, 0) * lot_step;
   
   return lot_size;
}

//+------------------------------------------------------------------+
//| Update equity tracking                                           |
//+------------------------------------------------------------------+
void UpdateEquityTracking()
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   equity_high = MathMax(equity_high, equity);
   equity_low = MathMin(equity_low, equity);
}

//+------------------------------------------------------------------+
//| Save performance report                                          |
//+------------------------------------------------------------------+
void SavePerformanceReport()
{
   string report = "\n=== SkylerBotV3.0 Performance Report ===\n";
   report += "Symbol: " + SymbolToTrade + "\n";
   report += "Timeframe: " + EnumToString(Timeframe) + "\n";
   report += "Period: " + TimeToString(TimeCurrent(), TIME_DATE) + "\n";
   report += "Total Trades: " + IntegerToString(total_trades) + "\n";
   
   if(total_trades > 0)
   {
      double win_rate = winning_trades * 100.0 / total_trades;
      report += "Winning Trades: " + IntegerToString(winning_trades) + " (" + DoubleToString(win_rate, 2) + "%)\n";
      report += "Total Profit: " + DoubleToString(total_profit, 2) + "\n";
      report += "Equity High: " + DoubleToString(equity_high, 2) + "\n";
      report += "Equity Low: " + DoubleToString(equity_low, 2) + "\n";
      report += "Max Drawdown: " + DoubleToString((equity_high-equity_low)/equity_high*100, 2) + "%\n";
   }
   
   // Save to file
   string filename = "SkylerBot_Report_" + SymbolToTrade + "_" + EnumToString(Timeframe) + ".txt";
   int handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, report);
      FileClose(handle);
   }
   
   Print(report);
}

//+------------------------------------------------------------------+
//| Helper functions                                                 |
//+------------------------------------------------------------------+
string SignalToString(ENUM_SIGNAL signal)
{
   switch(signal)
   {
      case SIGNAL_BUY:  return "BUY";
      case SIGNAL_SELL: return "SELL";
      default:          return "NONE";
   }
}

string ConfidenceToString(ENUM_CONFIDENCE confidence)
{
   switch(confidence)
   {
      case CONFIDENCE_HIGH:   return "HIGH";
      case CONFIDENCE_MEDIUM: return "MEDIUM";
      default:                return "LOW";
   }
}

string GetTradeErrorText(int error_code)
{
   switch(error_code)
   {
      case 10004: return "Requote";
      case 10006: return "Request rejected";
      case 10007: return "Request canceled by trader";
      case 10008: return "Order placed";
      case 10009: return "Request completed";
      case 10010: return "Only part of the request was completed";
      case 10011: return "Request processing error";
      case 10012: return "Request canceled by timeout";
      case 10013: return "Invalid request";
      case 10014: return "Invalid volume in the request";
      case 10015: return "Invalid price in the request";
      case 10016: return "Invalid stops in the request";
      case 10017: return "Trade is disabled";
      case 10018: return "Market is closed";
      case 10019: return "Not enough money";
      case 10020: return "Prices changed";
      case 10021: return "There are no quotes to process the request";
      case 10022: return "Invalid order expiration date in the request";
      case 10023: return "Order state changed";
      case 10024: return "Too frequent requests";
      case 10025: return "No changes in request";
      case 10026: return "Autotrading disabled by server";
      case 10027: return "Autotrading disabled by client terminal";
      case 10028: return "Request locked for processing";
      case 10029: return "Order or position frozen";
      default:    return "Unknown error (" + IntegerToString(error_code) + ")";
   }
}

string GetUninitReasonText(int reason_code)
{
   switch(reason_code)
   {
      case REASON_ACCOUNT:    return "Account changed";
      case REASON_CHARTCHANGE:return "Symbol or timeframe changed";
      case REASON_CHARTCLOSE: return "Chart closed";
      case REASON_CLOSE:      return "Terminal closed";
      case REASON_INITFAILED: return "Initialization failed";
      case REASON_PARAMETERS: return "Input parameters changed";
      case REASON_RECOMPILE:  return "Program recompiled";
      case REASON_REMOVE:     return "Program removed from chart";
      case REASON_TEMPLATE:   return "Template changed";
      default:                return "Unknown reason";
   }
}

int StringHash(string str)
{
   int hash = 0;
   for(int i = 0; i < StringLen(str); i++)
      hash = hash * 31 + StringGetCharacter(str, i);
   return MathAbs(hash);
}