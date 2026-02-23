//+------------------------------------------------------------------+
//| GARCH.mqh - Modelo GARCH(1,1) Robusto                            |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - GARCH Model"
#property link      ""
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Modelo GARCH(1,1) para cálculo de volatilidade dinâmica          |
//+------------------------------------------------------------------+
double GARCH11(double &returnsArray[])
{
   const double omega = 0.0001;   // Constante de volatilidade de longo prazo
   const double alpha = 0.12;     // Parâmetro de choque (ARCH)
   const double beta = 0.85;      // Parâmetro de persistência (GARCH)
   
   int n = ArraySize(returnsArray);
   if (n < 2) return EMPTY_VALUE;

   double var = 0.0;
   for (int i = 0; i < n; i++)
      var += returnsArray[i] * returnsArray[i];
   var /= n;

   for (int i = 1; i < n; i++)
      var = omega + alpha * MathPow(returnsArray[i - 1], 2) + beta * var;

   double result = MathSqrt(var);
   PrintFormat("[GARCH] Volatilidade GARCH(1,1): %.6f", result);
   return result;
}

//+------------------------------------------------------------------+
//| Função auxiliar para calcular retornos logarítmicos              |
//+------------------------------------------------------------------+
void CalculateLogReturns(const double &prices[], double &returns[])
{
   int size = ArraySize(prices);
   if(size < 2) return;
   
   ArrayResize(returns, size-1);
   
   for(int i=0; i<size-1; i++)
   {
      if(prices[i+1] > 0)
         returns[i] = MathLog(prices[i+1] / prices[i]);
      else
         returns[i] = 0.0;
   }
}

//+------------------------------------------------------------------+
//| Função para calcular volatilidade histórica                      |
//+------------------------------------------------------------------+
double CalculateHistoricalVolatility(const double &returns[], int period=20)
{
   if(ArraySize(returns) < period) return 0.01;
   
   double sum = 0.0;
   double sumSq = 0.0;
   
   for(int i=0; i<period; i++)
   {
      sum += returns[i];
      sumSq += MathPow(returns[i], 2);
   }
   
   double mean = sum / period;
   double variance = (sumSq / period) - MathPow(mean, 2);
   
   return MathSqrt(variance);
} 