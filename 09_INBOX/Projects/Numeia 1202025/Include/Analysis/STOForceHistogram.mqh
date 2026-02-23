//+------------------------------------------------------------------+
//| STOForceHistogram.mqh - Histograma de Força STO                  |
//| Projeto: EA Numeia - Analysis                                    |
//| Função: Analisa força e momentum através de histogramas STO      |
//+------------------------------------------------------------------+

#include <Utils/Log.mqh>
#include <Arrays/ArrayObj.mqh>

//--- Parâmetros configuráveis
input int    ticksPerSwing        = 15;
input int    minSwingCandles      = 3;
input int    maPeriod             = 20;
input double volumeFactor         = 1.3;
input int    swingBufferSize      = 50;
input double percentileCut        = 90.0;
input bool   useMAFilter          = true;
input bool   usePercentileFilter  = true;
input bool   useCandleCountFilter = true;
input bool   enableDebugPrint     = false;

//--- Estrutura interna para swings
struct Swing {
   int     startIdx;
   int     endIdx;
   double  volume;
   double  startPrice;
   double  endPrice;
   bool    isUp;
};

CArrayObj swingHistory;
int       swingDir = 0;
double    swingVolume = 0;
double    swingStartPrice = 0;
int       swingStartIdx = 0;
int       swingCandleCount = 0;

//+------------------------------------------------------------------+
//| Inicializa o histograma                                          |
//+------------------------------------------------------------------+
void InitStoForceHistogram() {
   swingHistory.Clear();
   swingDir = 0;
   swingVolume = 0;
   swingStartIdx = 0;
   swingStartPrice = 0;
   swingCandleCount = 0;
}

//+------------------------------------------------------------------+
//| Processamento dos swings                                         |
//+------------------------------------------------------------------+
void ProcessSwing(const int rates_total,
                  const datetime &time[],
                  const double &close[],
                  const long &tick_volume[],
                  double &histUp[],
                  double &histDown[]) {

   for (int i = 1; i < rates_total; i++) {
      double delta = close[i] - swingStartPrice;

      if (swingDir == 0) {
         swingStartIdx = i - 1;
         swingStartPrice = close[i - 1];
         swingDir = (delta >= 0 ? 1 : -1);
         swingVolume = tick_volume[i];
         swingCandleCount = 1;
      }
      else {
         swingVolume += tick_volume[i];
         swingCandleCount++;

         bool reverse = (swingDir == 1 && delta <= -ticksPerSwing * _Point) ||
                        (swingDir == -1 && delta >=  ticksPerSwing * _Point);

         if (reverse) {
            bool passCandleFilter = !useCandleCountFilter || (swingCandleCount >= minSwingCandles);
            double maVolume = CalcMASwingVolume();
            double percVolume = CalcPercentileSwingVolume();
            bool passMA = !useMAFilter || (swingVolume >= maVolume * volumeFactor);
            bool passPERC = !usePercentileFilter || (swingVolume >= percVolume);

            string msg = StringFormat("Swing %s | Vol=%.0f | MA=%.0f | Perc=%.0f | C=%d [%s-%s]",
                          (swingDir == 1 ? "UP" : "DOWN"),
                          swingVolume, maVolume, percVolume, swingCandleCount,
                          (passMA ? "MA_OK" : "MA_NO"), (passPERC ? "PERC_OK" : "PERC_NO"));

            if (enableDebugPrint)
               Print(msg);

            if (passCandleFilter && passMA && passPERC) {
               int idx = i;
               if (swingDir == 1) histUp[idx] = swingVolume;
               else               histDown[idx] = swingVolume;

               AuditLog("STOForceHistogram", Symbol(), "✅ Swing Aceito → " + msg);
               StoreSwing(swingStartIdx, i, swingVolume, swingStartPrice, close[i], swingDir == 1);
            } else {
               AuditLog("STOForceHistogram", Symbol(), "⛔ Swing Rejeitado → " + msg);
            }

            swingDir = -swingDir;
            swingStartIdx = i;
            swingStartPrice = close[i];
            swingVolume = tick_volume[i];
            swingCandleCount = 1;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Armazena swing no buffer                                         |
//+------------------------------------------------------------------+
void StoreSwing(int start, int end, double vol, double p1, double p2, bool isUp) {
   Swing *s = new Swing;
   s.startIdx = start;
   s.endIdx = end;
   s.volume = vol;
   s.startPrice = p1;
   s.endPrice = p2;
   s.isUp = isUp;
   swingHistory.Add(s);

   if (swingHistory.Total() > swingBufferSize)
      swingHistory.Delete(0);
}

//+------------------------------------------------------------------+
//| Cálculo da Média Móvel de volume                                 |
//+------------------------------------------------------------------+
double CalcMASwingVolume() {
   int total = MathMin(swingHistory.Total(), maPeriod);
   if (total == 0) return 0.0;
   double sum = 0;
   for (int i = swingHistory.Total() - total; i < swingHistory.Total(); i++) {
      Swing *s = (Swing *) swingHistory.At(i);
      sum += s.volume;
   }
   return sum / total;
}

//+------------------------------------------------------------------+
//| Cálculo do Percentil de volume swing                             |
//+------------------------------------------------------------------+
double CalcPercentileSwingVolume() {
   int total = swingHistory.Total();
   if (total == 0) return 0.0;
   double vols[];
   ArrayResize(vols, total);
   for (int i = 0; i < total; i++) {
      Swing *s = (Swing *) swingHistory.At(i);
      vols[i] = s.volume;
   }
   ArraySort(vols, WHOLE_ARRAY, 0, MODE_DESCEND);
   int idx = MathFloor((percentileCut / 100.0) * total);
   idx = MathMin(idx, total - 1);
   return vols[idx];
}

#endif // __ANALYSIS_STOFORCE_HISTOGRAM__ 