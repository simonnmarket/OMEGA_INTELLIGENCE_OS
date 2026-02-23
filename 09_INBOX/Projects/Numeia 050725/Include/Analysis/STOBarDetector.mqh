//+------------------------------------------------------------------+
//| Include/Analysis/STOBarDetector.mqh                              |
//| Módulo Institucional: Detecção de Big Players por Z-Score + Delta|
//| Integrado com AuditManager e exportação direta para IA           |
//+------------------------------------------------------------------+
#ifndef __ANALYSIS_STOBAR_DETECTOR__
#define __ANALYSIS_STOBAR_DETECTOR__

#include <Logs/AuditManager.mqh>

//--- Enumeração institucional
enum PlayerStrength { None = 0, Light, Moderate, Strong, Institutional };

//--- Parâmetros globais (podem ser reconfigurados no EA)
input int    DefaultVolumePeriod  = 20;
input double DefaultAlertZScore   = 2.0;
input bool   DefaultUseDelta      = true;
input int    DefaultDeltaThreshold = 1000;
input bool   EnableDetectionLog   = true;

//+------------------------------------------------------------------+
//| Função principal de detecção de Big Players                      |
//+------------------------------------------------------------------+
PlayerStrength DetectBigPlayer(const int index,
                               const long &volume[],
                               const long &tick_volume[],
                               const double &open[],
                               const double &close[],
                               int volumePeriod       = DefaultVolumePeriod,
                               double alertZScore     = DefaultAlertZScore,
                               bool useDeltaFilter    = DefaultUseDelta,
                               int deltaThreshold     = DefaultDeltaThreshold)
{
   if (index < volumePeriod)
      return None;

   //--- Estatísticas de volume
   double sumVol = 0, sumSq = 0;
   for (int j = 1; j <= volumePeriod; j++) {
      double v = volume[index - j];
      sumVol += v;
      sumSq += v * v;
   }

   double avgVol = sumVol / volumePeriod;
   double stdVol = MathSqrt(MathMax(sumSq / volumePeriod - avgVol * avgVol, 1e-6));
   double zscore = (volume[index] - avgVol) / stdVol;

   //--- Cálculo do delta
   double delta = 0;
   if (useDeltaFilter) {
      if (close[index] > open[index])
         delta = tick_volume[index];
      else if (close[index] < open[index])
         delta = -tick_volume[index];
   }

   //--- Classificação
   PlayerStrength strength = None;
   if (zscore < 0.5)
      strength = None;
   else if (zscore < 1.0)
      strength = Light;
   else if (zscore < 1.5)
      strength = Moderate;
   else if (zscore < alertZScore)
      strength = Strong;
   else if (!useDeltaFilter || MathAbs(delta) >= deltaThreshold)
      strength = Institutional;
   else
      strength = Strong;

   //--- Log institucional
   if (EnableDetectionLog && strength != None) {
      string msg = StringFormat("STOBarDetector i=%d | Z=%.2f | Δ=%.0f | Strength=%d",
                                index, zscore, delta, strength);
      AuditLog("STOBarDetector", Symbol(), msg);
   }

   return strength;
}

#endif // __ANALYSIS_STOBAR_DETECTOR__
