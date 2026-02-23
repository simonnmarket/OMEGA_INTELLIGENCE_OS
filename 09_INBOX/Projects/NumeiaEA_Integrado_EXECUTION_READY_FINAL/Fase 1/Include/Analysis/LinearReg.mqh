// File: Include/Analysis/LinearReg.mqh
#ifndef ANALYSIS_LINEARREG_MQH
#define ANALYSIS_LINEARREG_MQH

//+------------------------------------------------------------------+
//| Linear Regression Model - Apollo Certified                      |
//| Certificações: Apollo / Brookfield / DWS                        |
//| Finalidade: Estimar resíduos e tendência linear                 |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                    |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+

class LinearRegression
  {
private:
   double slope;
   double intercept;
   double lastResidual;

public:
   bool Calculate(const double &x[], const double &y[])
     {
      int n = ArraySize(x);
      if(n != ArraySize(y) || n < 2)
         return false;

      double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
      for(int i = 0; i < n; i++)
        {
         sumX  += x[i];
         sumY  += y[i];
         sumXY += x[i] * y[i];
         sumXX += x[i] * x[i];
        }

      double denominator = n * sumXX - sumX * sumX;
      if(denominator == 0.0)
         return false;

      slope     = (n * sumXY - sumX * sumY) / denominator;
      intercept = (sumY - slope * sumX) / n;

      lastResidual = y[n - 1] - (slope * x[n - 1] + intercept);
      return true;
     }

   double GetSlope() const { return slope; }
   double GetIntercept() const { return intercept; }
   double GetLastResidual() const { return lastResidual; }
  };

#endif // ANALYSIS_LINEARREG_MQH
