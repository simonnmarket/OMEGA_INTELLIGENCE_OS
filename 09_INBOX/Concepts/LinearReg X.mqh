//+------------------------------------------------------------------+
//| LinearReg.mqh - Regressão Linear e Correlação                    |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Linear Regression"
#property link      ""
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Regressão Linear Simples (OLS)                                   |
//+------------------------------------------------------------------+
double LinearRegression(double &y[], double &x[], double &residuals[])
{
   int n = ArraySize(y);
   if (n != ArraySize(x) || n < 2) return EMPTY_VALUE;

   ArrayResize(residuals, n);
   double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;

   for (int i = 0; i < n; i++)
   {
      sumX += x[i];
      sumY += y[i];
      sumXY += x[i] * y[i];
      sumXX += x[i] * x[i];
   }

   double beta = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
   double alpha = (sumY - beta * sumX) / n;

   for (int i = 0; i < n; i++)
      residuals[i] = y[i] - (alpha + beta * x[i]);

   PrintFormat("[LinearReg] Regressão: alpha=%.4f beta=%.4f", alpha, beta);
   return beta;
}

//+------------------------------------------------------------------+
//| Teste de Estacionariedade dos Resíduos (ADF simplificado)        |
//+------------------------------------------------------------------+
bool IsStationary(const double &residuals[], double threshold=0.02)
{
   int size = ArraySize(residuals);
   if (size < 10) return false;
   
   double sum = 0, sumSq = 0;
   for (int i = 0; i < size; i++)
   {
      sum += residuals[i];
      sumSq += residuals[i] * residuals[i];
   }
   
   double mean = sum / size;
   double var = (sumSq / size) - mean * mean;
   double stddev = MathSqrt(var);
   
   return stddev < threshold;
}

//+------------------------------------------------------------------+
//| Coeficiente de Correlação                                        |
//+------------------------------------------------------------------+
double CalculateCorrelation(const double &x[], const double &y[])
{
   int n = ArraySize(x);
   if (n != ArraySize(y) || n < 2) return EMPTY_VALUE;
   
   double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0, sumYY = 0;
   
   for (int i = 0; i < n; i++)
   {
      sumX += x[i];
      sumY += y[i];
      sumXY += x[i] * y[i];
      sumXX += x[i] * x[i];
      sumYY += y[i] * y[i];
   }
   
   double numerator = n * sumXY - sumX * sumY;
   double denominator = MathSqrt((n * sumXX - sumX * sumX) * (n * sumYY - sumY * sumY));
   
   if (denominator == 0) return 0.0;
   
   return numerator / denominator;
} 