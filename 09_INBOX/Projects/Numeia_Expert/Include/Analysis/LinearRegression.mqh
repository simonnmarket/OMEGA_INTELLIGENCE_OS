//+------------------------------------------------------------------+
//| Project: NumeiaEA - Quantitative Infrastructure                  |
//| Module: LinearRegression.mqh                                     |
//| Location: Include/Analysis/                                      |
//| Certification: Apollo Capital / Brookfield Risk Labs            |
//| Description: Regressão Linear com cálculo de coeficientes       |
//| Version: 1.0-HYBRID                                              |
//| Last Update: 2025-07-02                                          |
//| Authors: Apollo Research Division / Brookfield Quant Group      |
//+------------------------------------------------------------------+
#ifndef ANALYSIS_LINEARREGRESSION_MQH
#define ANALYSIS_LINEARREGRESSION_MQH

//+------------------------------------------------------------------+
//| Classe: LinearRegression                                         |
//| Descrição: Estima relação entre duas séries de dados            |
//| Uso: Para modelagem de tendência, resíduos, cointegração, etc.  |
//+------------------------------------------------------------------+
class LinearRegression
  {
public:
   double slope;
   double intercept;
   double r_squared;

   LinearRegression()
     {
      slope = 0.0;
      intercept = 0.0;
      r_squared = 0.0;
     }

   bool Fit(const double &x[], const double &y[])
     {
      int n = MathMin(ArraySize(x), ArraySize(y));
      if(n < 2)
         return false;

      double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0, sumYY = 0;
      for(int i = 0; i < n; i++)
        {
         sumX += x[i];
         sumY += y[i];
         sumXY += x[i] * y[i];
         sumXX += x[i] * x[i];
         sumYY += y[i] * y[i];
        }

      double meanX = sumX / n;
      double meanY = sumY / n;
      double denom = sumXX - n * meanX * meanX;
      if(denom == 0.0)
         return false;

      slope = (sumXY - n * meanX * meanY) / denom;
      intercept = meanY - slope * meanX;

      // R² (coeficiente de determinação)
      double ss_total = 0.0, ss_res = 0.0;
      for(int i = 0; i < n; i++)
        {
         double y_pred = Predict(x[i]);
         ss_total += MathPow(y[i] - meanY, 2);
         ss_res += MathPow(y[i] - y_pred, 2);
        }
      r_squared = 1.0 - (ss_res / ss_total);

      return true;
     }

   // Predição de valor Y para um dado X
   double Predict(double xVal)
     {
      return intercept + slope * xVal;
     }
  };

#endif // ANALYSIS_LINEARREGRESSION_MQH
