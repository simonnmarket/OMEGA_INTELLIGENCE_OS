//+------------------------------------------------------------------+
//| CVaRManager.mqh - CVaR com Janela Móvel e Log                    |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - CVaR Manager"
#property link      ""
#property version   "1.00"
#property strict
#include <Trade/Trade.mqh>

//+------------------------------------------------------------------+
//| CLASSE CVAR MANAGER                                              |
//+------------------------------------------------------------------+
class CVaRManager
{
private:
   double confidenceLevel;
   double historicalReturns[];
   double prevEquityVal;
   int maxWindowSize;

public:
   CVaRManager(double cl=0.95, int windowSize=252)
   {
      confidenceLevel = cl;
      maxWindowSize = windowSize;
      prevEquityVal = AccountInfoDouble(ACCOUNT_EQUITY);
   }
   
   void UpdateReturns(double newEquity)
   {
      double dailyReturn = (newEquity - prevEquityVal) / prevEquityVal;
      prevEquityVal = newEquity;
      
      int arrSize = ArraySize(historicalReturns);
      ArrayResize(historicalReturns, arrSize+1);
      historicalReturns[arrSize] = dailyReturn;

      // Reduz se ultrapassar janela
      if (ArraySize(historicalReturns) > maxWindowSize)
         ArrayRemove(historicalReturns, 0);
   }
   
   double CalculateCVaR()
   {
      int arrSize = ArraySize(historicalReturns);
      if(arrSize < 50) return EMPTY_VALUE;
      
      double sorted[];
      ArrayCopy(sorted, historicalReturns);
      ArraySort(sorted);
      
      int index = (int)(arrSize * (1-confidenceLevel));
      if(index <= 0) index = 1;
      
      double cvar = 0.0;
      for(int i=0; i<index; i++)
      {
         cvar += sorted[i];
      }
      double result = cvar / index;
      PrintFormat("[CVaRManager] CVaR Calculado: %.5f", result);
      return result;
   }
   
   void Reset()
   {
      ArrayResize(historicalReturns, 0);
      prevEquityVal = AccountInfoDouble(ACCOUNT_EQUITY);
   }
   
   int GetDataCount()
   {
      return ArraySize(historicalReturns);
   }
}; 