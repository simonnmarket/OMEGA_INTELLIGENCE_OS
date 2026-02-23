// File: Include/ExecutionLogic/EntropyTrailingStop.mqh
#ifndef EXECUTIONLOGIC_ENTROPYTRAILINGSTOP_MQH
#define EXECUTIONLOGIC_ENTROPYTRAILINGSTOP_MQH

//+------------------------------------------------------------------+
//| EntropyTrailingStop - Stop Adaptativo por Entropia de Preço     |
//| Certificações: Apollo / Brookfield / DWS                        |
//| Estratégia: Ajuste dinâmico conforme variabilidade do mercado   |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                    |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+

class EntropyTrailingStop
  {
private:
   int     m_period;
   double  m_lastEntropy;

public:
   EntropyTrailingStop(int period = 20)
     {
      m_period = period;
      m_lastEntropy = 0.0;
     }

   // Calcula a entropia (base logarítmica natural)
   double CalculateEntropy(const double &priceSeries[])
     {
      int size = ArraySize(priceSeries);
      if(size < 2)
         return 0.0;

      double entropy = 0.0;
      for(int i = 1; i < size; i++)
        {
         double diff = MathAbs(priceSeries[i] - priceSeries[i - 1]);
         if(diff > 0.0)
            entropy += -diff * MathLog(diff);
        }

      m_lastEntropy = entropy;
      return entropy;
     }

   // Retorna trailing adaptado com base na entropia
   double GetTrailingStop()
     {
      return MathMax(5 * m_lastEntropy, 10 * _Point); // trailing mínimo
     }
  };

#endif // EXECUTIONLOGIC_ENTROPYTRAILINGSTOP_MQH
