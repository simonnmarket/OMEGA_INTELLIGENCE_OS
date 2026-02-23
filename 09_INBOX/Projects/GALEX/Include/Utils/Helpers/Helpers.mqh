//+------------------------------------------------------------------+
//|                                                   Helpers.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de arquivos necessários
#include <Trade\Trade.mqh>
#include <Arrays\ArrayDouble.mqh>
#include <Arrays\ArrayInt.mqh>
#include <Arrays\ArrayString.mqh>
#include <Math\Stat\Math.mqh>
#include <Math\Stat\Statistics.mqh>
#include <Math\Stat\Normal.mqh>
#include <Math\Stat\Uniform.mqh>
#include <Math\Stat\Gamma.mqh>
#include <Math\Stat\Beta.mqh>
#include <Math\Stat\ChiSquare.mqh>
#include <Math\Stat\F.mqh>
#include <Math\Stat\T.mqh>
#include <Math\Stat\Weibull.mqh>
#include <Math\Stat\Exponential.mqh>
#include <Math\Stat\Logistic.mqh>
#include <Math\Stat\Cauchy.mqh>
#include <Math\Stat\Hypergeometric.mqh>
#include <Math\Stat\Poisson.mqh>
#include <Math\Stat\Binomial.mqh>
#include <Math\Stat\Geometric.mqh>
#include <Math\Stat\NegativeBinomial.mqh>
#include <Math\Stat\Pareto.mqh>
#include <Math\Stat\Rayleigh.mqh>
#include <Math\Stat\Maxwell.mqh>
#include <Math\Stat\Gumbel.mqh>
#include <Math\Stat\Frechet.mqh>
#include <Math\Stat\LogNormal.mqh>
#include <Math\Stat\Logistic.mqh>
#include <Math\Stat\Cauchy.mqh>
#include <Math\Stat\Hypergeometric.mqh>
#include <Math\Stat\Poisson.mqh>
#include <Math\Stat\Binomial.mqh>
#include <Math\Stat\Geometric.mqh>
#include <Math\Stat\NegativeBinomial.mqh>
#include <Math\Stat\Pareto.mqh>
#include <Math\Stat\Rayleigh.mqh>
#include <Math\Stat\Maxwell.mqh>
#include <Math\Stat\Gumbel.mqh>
#include <Math\Stat\Frechet.mqh>
#include <Math\Stat\LogNormal.mqh>

//+------------------------------------------------------------------+
//| Funções de manipulação de arrays                                 |
//+------------------------------------------------------------------+
double ArraySum(const double &array[])
{
   double sum = 0.0;
   for(int i = 0; i < ArraySize(array); i++)
      sum += array[i];
   return sum;
}

double ArrayMean(const double &array[])
{
   return ArraySum(array) / ArraySize(array);
}

double ArrayStdDev(const double &array[])
{
   double mean = ArrayMean(array);
   double sum = 0.0;
   for(int i = 0; i < ArraySize(array); i++)
      sum += MathPow(array[i] - mean, 2);
   return MathSqrt(sum / ArraySize(array));
}

double ArrayMax(const double &array[])
{
   double max = array[0];
   for(int i = 1; i < ArraySize(array); i++)
      if(array[i] > max)
         max = array[i];
   return max;
}

double ArrayMin(const double &array[])
{
   double min = array[0];
   for(int i = 1; i < ArraySize(array); i++)
      if(array[i] < min)
         min = array[i];
   return min;
}

int ArrayMaxIndex(const double &array[])
{
   int max_index = 0;
   double max = array[0];
   for(int i = 1; i < ArraySize(array); i++)
      if(array[i] > max)
      {
         max = array[i];
         max_index = i;
      }
   return max_index;
}

int ArrayMinIndex(const double &array[])
{
   int min_index = 0;
   double min = array[0];
   for(int i = 1; i < ArraySize(array); i++)
      if(array[i] < min)
      {
         min = array[i];
         min_index = i;
      }
   return min_index;
}

void ArrayReverse(double &array[])
{
   int size = ArraySize(array);
   for(int i = 0; i < size / 2; i++)
   {
      double temp = array[i];
      array[i] = array[size - 1 - i];
      array[size - 1 - i] = temp;
   }
}

void ArrayShift(double &array[], int shift)
{
   int size = ArraySize(array);
   if(shift > 0)
   {
      for(int i = size - 1; i >= shift; i--)
         array[i] = array[i - shift];
      for(int i = 0; i < shift; i++)
         array[i] = 0.0;
   }
   else if(shift < 0)
   {
      shift = -shift;
      for(int i = 0; i < size - shift; i++)
         array[i] = array[i + shift];
      for(int i = size - shift; i < size; i++)
         array[i] = 0.0;
   }
}

//+------------------------------------------------------------------+
//| Funções de manipulação de strings                                |
//+------------------------------------------------------------------+
string StringFormat(const string format, ...)
{
   string result = "";
   va_list args;
   va_start(args, format);
   result = StringFormatV(format, args);
   va_end(args);
   return result;
}

string StringFormatV(const string format, va_list args)
{
   string result = "";
   int len = StringLen(format);
   for(int i = 0; i < len; i++)
   {
      if(format[i] == '%')
      {
         i++;
         if(i < len)
         {
            switch(format[i])
            {
               case 'd':
                  result += IntegerToString(va_arg(args, int));
                  break;
               case 'f':
                  result += DoubleToString(va_arg(args, double), 8);
                  break;
               case 's':
                  result += va_arg(args, string);
                  break;
               case '%':
                  result += "%";
                  break;
               default:
                  result += "%" + StringSubstr(format, i, 1);
                  break;
            }
         }
      }
      else
         result += StringSubstr(format, i, 1);
   }
   return result;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de tempo                                  |
//+------------------------------------------------------------------+
datetime TimeAdd(const datetime time, const int seconds)
{
   return time + seconds;
}

datetime TimeSubtract(const datetime time, const int seconds)
{
   return time - seconds;
}

int TimeDiff(const datetime time1, const datetime time2)
{
   return (int)(time1 - time2);
}

bool IsTimeInRange(const datetime time, const datetime start, const datetime end)
{
   return time >= start && time <= end;
}

bool IsTimeInRangeEx(const datetime time, const datetime start, const datetime end, const bool include_start = true, const bool include_end = true)
{
   if(include_start && include_end)
      return time >= start && time <= end;
   else if(include_start)
      return time >= start && time < end;
   else if(include_end)
      return time > start && time <= end;
   else
      return time > start && time < end;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de preços                                 |
//+------------------------------------------------------------------+
double NormalizePrice(const double price, const int digits)
{
   return NormalizeDouble(price, digits);
}

double NormalizeLots(const double lots)
{
   double min_lot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN);
   double max_lot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX);
   double lot_step = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_STEP);
   
   lots = MathMax(min_lot, MathMin(max_lot, lots));
   lots = MathFloor(lots / lot_step) * lot_step;
   
   return NormalizeDouble(lots, 2);
}

double CalculatePips(const double price1, const double price2)
{
   int digits = (int)SymbolInfoInteger(Symbol(), SYMBOL_DIGITS);
   return MathAbs(price1 - price2) * MathPow(10, digits);
}

double CalculatePoints(const double price1, const double price2)
{
   double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   return MathAbs(price1 - price2) / point;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de ordens                                 |
//+------------------------------------------------------------------+
bool IsOrderTypeBuy(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_BUY || type == ORDER_TYPE_BUY_LIMIT || type == ORDER_TYPE_BUY_STOP;
}

bool IsOrderTypeSell(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_SELL || type == ORDER_TYPE_SELL_LIMIT || type == ORDER_TYPE_SELL_STOP;
}

bool IsOrderTypeMarket(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_BUY || type == ORDER_TYPE_SELL;
}

bool IsOrderTypePending(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_BUY_LIMIT || type == ORDER_TYPE_BUY_STOP || type == ORDER_TYPE_SELL_LIMIT || type == ORDER_TYPE_SELL_STOP;
}

bool IsOrderTypeStop(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_BUY_STOP || type == ORDER_TYPE_SELL_STOP;
}

bool IsOrderTypeLimit(const ENUM_ORDER_TYPE type)
{
   return type == ORDER_TYPE_BUY_LIMIT || type == ORDER_TYPE_SELL_LIMIT;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de posições                               |
//+------------------------------------------------------------------+
bool IsPositionTypeBuy(const ENUM_POSITION_TYPE type)
{
   return type == POSITION_TYPE_BUY;
}

bool IsPositionTypeSell(const ENUM_POSITION_TYPE type)
{
   return type == POSITION_TYPE_SELL;
}

bool IsPositionTypeLong(const ENUM_POSITION_TYPE type)
{
   return type == POSITION_TYPE_BUY;
}

bool IsPositionTypeShort(const ENUM_POSITION_TYPE type)
{
   return type == POSITION_TYPE_SELL;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de indicadores                            |
//+------------------------------------------------------------------+
double CalculateATR(const int period)
{
   double atr[];
   ArraySetAsSeries(atr, true);
   int atr_handle = iATR(Symbol(), PERIOD_CURRENT, period);
   if(atr_handle == INVALID_HANDLE)
      return 0.0;
   
   if(CopyBuffer(atr_handle, 0, 0, 1, atr) <= 0)
      return 0.0;
   
   IndicatorRelease(atr_handle);
   return atr[0];
}

double CalculateRSI(const int period)
{
   double rsi[];
   ArraySetAsSeries(rsi, true);
   int rsi_handle = iRSI(Symbol(), PERIOD_CURRENT, period, PRICE_CLOSE);
   if(rsi_handle == INVALID_HANDLE)
      return 0.0;
   
   if(CopyBuffer(rsi_handle, 0, 0, 1, rsi) <= 0)
      return 0.0;
   
   IndicatorRelease(rsi_handle);
   return rsi[0];
}

double CalculateMACD(const int fast_ema, const int slow_ema, const int signal)
{
   double macd[];
   ArraySetAsSeries(macd, true);
   int macd_handle = iMACD(Symbol(), PERIOD_CURRENT, fast_ema, slow_ema, signal, PRICE_CLOSE);
   if(macd_handle == INVALID_HANDLE)
      return 0.0;
   
   if(CopyBuffer(macd_handle, 0, 0, 1, macd) <= 0)
      return 0.0;
   
   IndicatorRelease(macd_handle);
   return macd[0];
}

double CalculateBB(const int period, const double deviation)
{
   double bb[];
   ArraySetAsSeries(bb, true);
   int bb_handle = iBands(Symbol(), PERIOD_CURRENT, period, 0, deviation, PRICE_CLOSE);
   if(bb_handle == INVALID_HANDLE)
      return 0.0;
   
   if(CopyBuffer(bb_handle, 0, 0, 1, bb) <= 0)
      return 0.0;
   
   IndicatorRelease(bb_handle);
   return bb[0];
}

double CalculateMA(const int period, const int shift, const ENUM_MA_METHOD method)
{
   double ma[];
   ArraySetAsSeries(ma, true);
   int ma_handle = iMA(Symbol(), PERIOD_CURRENT, period, shift, method, PRICE_CLOSE);
   if(ma_handle == INVALID_HANDLE)
      return 0.0;
   
   if(CopyBuffer(ma_handle, 0, 0, 1, ma) <= 0)
      return 0.0;
   
   IndicatorRelease(ma_handle);
   return ma[0];
}

//+------------------------------------------------------------------+
//| Funções de manipulação de física                                 |
//+------------------------------------------------------------------+
double CalculateGravitationalForce(const double mass1, const double mass2, const double distance)
{
   return GRAVITATIONAL_CONSTANT * mass1 * mass2 / MathPow(distance, 2);
}

double CalculatePotentialEnergy(const double mass, const double height)
{
   return mass * GRAVITATIONAL_CONSTANT * height;
}

double CalculateKineticEnergy(const double mass, const double velocity)
{
   return 0.5 * mass * MathPow(velocity, 2);
}

double CalculateDragForce(const double velocity, const double area, const double drag_coefficient, const double air_density)
{
   return 0.5 * air_density * MathPow(velocity, 2) * area * drag_coefficient;
}

double CalculateThrust(const double mass_flow_rate, const double exhaust_velocity)
{
   return mass_flow_rate * exhaust_velocity;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de trajetória                             |
//+------------------------------------------------------------------+
double CalculateTrajectoryAngle(const double velocity, const double distance)
{
   return MathArcsin(distance * GRAVITATIONAL_CONSTANT / MathPow(velocity, 2)) / 2.0;
}

double CalculateTrajectoryDistance(const double velocity, const double angle)
{
   return MathPow(velocity, 2) * MathSin(2.0 * angle) / GRAVITATIONAL_CONSTANT;
}

double CalculateTrajectoryHeight(const double velocity, const double angle)
{
   return MathPow(velocity, 2) * MathPow(MathSin(angle), 2) / (2.0 * GRAVITATIONAL_CONSTANT);
}

double CalculateTrajectoryTime(const double velocity, const double angle)
{
   return 2.0 * velocity * MathSin(angle) / GRAVITATIONAL_CONSTANT;
}

double CalculateTrajectoryRange(const double velocity, const double angle)
{
   return MathPow(velocity, 2) * MathSin(2.0 * angle) / GRAVITATIONAL_CONSTANT;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de análise de mercado                     |
//+------------------------------------------------------------------+
double CalculateTrendStrength(const double &price_array[], const int period)
{
   double ma1 = CalculateMA(period, 0, MODE_SMA);
   double ma2 = CalculateMA(period * 2, 0, MODE_SMA);
   return (ma1 - ma2) / ma2 * 100.0;
}

double CalculateMomentum(const double &price_array[], const int period)
{
   return (price_array[0] - price_array[period]) / price_array[period] * 100.0;
}

double CalculateVolatility(const double &price_array[], const int period)
{
   return ArrayStdDev(price_array) / ArrayMean(price_array) * 100.0;
}

double CalculateVolumeFlow(const double &volume_array[], const int period)
{
   return ArraySum(volume_array) / period;
}

double CalculatePriceAction(const double &price_array[], const int period)
{
   return (price_array[0] - price_array[period]) / price_array[period] * 100.0;
}

//+------------------------------------------------------------------+
//| Funções de manipulação de atividade institucional                |
//+------------------------------------------------------------------+
double CalculateVolumePulse(const double &volume_array[], const int period)
{
   return ArrayMean(volume_array) / ArrayStdDev(volume_array);
}

double CalculateEnergyFlow(const double &price_array[], const double &volume_array[], const int period)
{
   return ArraySum(price_array) * ArraySum(volume_array) / period;
}

double CalculateCosmicFrequency(const double &price_array[], const int period)
{
   return 1.0 / (ArrayStdDev(price_array) / ArrayMean(price_array));
}

double CalculateNeuralConfidence(const double &price_array[], const double &volume_array[], const int period)
{
   return ArrayMean(price_array) * ArrayMean(volume_array) / (ArrayStdDev(price_array) * ArrayStdDev(volume_array));
}

bool DetectInstitutionalActivity(const double &price_array[], const double &volume_array[], const int period, const double volume_threshold, const double price_threshold)
{
   double volume_pulse = CalculateVolumePulse(volume_array, period);
   double energy_flow = CalculateEnergyFlow(price_array, volume_array, period);
   double cosmic_frequency = CalculateCosmicFrequency(price_array, period);
   double neural_confidence = CalculateNeuralConfidence(price_array, volume_array, period);
   
   return volume_pulse > volume_threshold && energy_flow > price_threshold && cosmic_frequency > 0.0 && neural_confidence > 0.0;
} 