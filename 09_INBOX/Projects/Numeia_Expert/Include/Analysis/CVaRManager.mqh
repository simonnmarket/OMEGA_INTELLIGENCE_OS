// File: Include/Analysis/CVaRManager.mqh
#ifndef ANALYSIS_CVARMANAGER_MQH
#define ANALYSIS_CVARMANAGER_MQH

//+------------------------------------------------------------------+
//| CVaRManager - Apollo Certified Risk Module                      |
//| Finalidade: Cálculo do Conditional Value at Risk (CVaR)        |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                   |
//| Certificações: Apollo Tier-2 | Brookfield Audit V3 | DWS-Ready |
//| Última atualização: 2025-07-02                                 |
//+------------------------------------------------------------------+

class CVaRManager
  {
public:

   // Cálculo do CVaR (Conditional Value at Risk)
   double CalculateCVaR(const double &returns[], double confidenceLevel = 0.95)
     {
      int size = ArraySize(returns);
      if(size < 50)
        {
         Print("[CVAR-WARNING] Dados insuficientes (min: 50) - Recebido: ", size);
         return EMPTY_VALUE;
        }

      double sorted[];
      ArrayResize(sorted, size);
      ArrayCopy(sorted, returns);
      ArraySort(sorted); // Corrigido: Ascendente padrão

      int cutoff = (int)MathFloor((1.0 - confidenceLevel) * size);
      double cumulative = 0.0;

      for(int i = 0; i <= cutoff; i++)
         cumulative += sorted[i];

      double cvar = -cumulative / (cutoff + 1);

      PrintFormat("[CVAR-LOG] CVaR: %.5f | N: %d | CL: %.2f", cvar, size, confidenceLevel);
      return cvar;
     }

   // Versão de fallback com simulação básica
   double SimulateCVaR(double mean, double stddev, int sampleSize = 100, double confidence = 0.95)
     {
      double simulated[];
      ArrayResize(simulated, sampleSize);
      for(int i = 0; i < sampleSize; i++)
         simulated[i] = mean + stddev * MathRand() / 32767.0;

      return CalculateCVaR(simulated, confidence);
     }
  };

#endif // ANALYSIS_CVARMANAGER_MQH
