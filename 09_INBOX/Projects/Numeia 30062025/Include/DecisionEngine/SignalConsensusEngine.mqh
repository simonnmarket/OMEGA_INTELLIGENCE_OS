//+------------------------------------------------------------------+
//| SignalConsensusEngine.mqh - Núcleo de Energia Decisional         |
//| Projeto Numeia - Sky Lab                                         |
//| Função: Gerar Sinal Final com Base em Múltiplos Agentes          |
//+------------------------------------------------------------------+
#ifndef __SIGNAL_CONSENSUS_ENGINE_MQH__
#define __SIGNAL_CONSENSUS_ENGINE_MQH__

#include <Intelligence/SkyIntelBridge.mqh>
#include <Include/Analysis/PatternRecognitionAgent.mqh>
#include <Include/Analysis/VolumeAnalysisAgent.mqh>
#include <Include/Agents/BigPlayerDetector.mqh>
#include <Include/Risk/RiskAgent.mqh>

// Enum para convicção final
enum SignalConvictionLevel
{
   NO_SIGNAL = 0,
   AVOID = 1,
   NEUTRAL = 2,
   WEAK_BUY = 3,
   STRONG_BUY = 4,
   WEAK_SELL = 5,
   STRONG_SELL = 6
};

class SignalConsensusEngine
{
private:
   string symbol;
   ENUM_TIMEFRAMES timeframe;

public:
   SignalConsensusEngine(const string _symbol, ENUM_TIMEFRAMES _tf)
   {
      symbol = _symbol;
      timeframe = _tf;
   }

   SignalConvictionLevel GetConsensus()
   {
      double score = 0.0;
      int votes = 0;

      // SkyIntel Signal
      StrategicSignal s_signal = SkyIntelBridge::GetStrategicSignal(symbol);
      if(s_signal == STRATEGIC_BUY)   { score += 1.5; votes++; }
      if(s_signal == STRATEGIC_SELL)  { score -= 1.5; votes++; }

      // Pattern Recognition
      PatternSignal p_signal = PatternRecognitionAgent::GetSignal(symbol, timeframe);
      if(p_signal == PATTERN_BUY)     { score += 1.0; votes++; }
      if(p_signal == PATTERN_SELL)    { score -= 1.0; votes++; }

      // Volume Analysis
      double volume_energy = VolumeAnalysisAgent::GetEnergyScore(symbol, timeframe);
      if(volume_energy > 0.7) { score += 1.0; votes++; }
      else if(volume_energy < 0.3) { score -= 1.0; votes++; }

      // Big Player Detection
      int bp_bias = BigPlayerDetector::GetBias(symbol);
      if(bp_bias > 0) { score += 1.0; votes++; }
      else if(bp_bias < 0) { score -= 1.0; votes++; }

      // Risk Check
      if(!RiskAgent::IsRiskAcceptable(symbol))
      {
         Print("⚠️ Risco elevado. Sinal anulado.");
         return AVOID;
      }

      // Final Decision
      if(votes == 0) return NO_SIGNAL;
      double avg_score = score / votes;

      if(avg_score >= 1.0) return STRONG_BUY;
      if(avg_score >= 0.5) return WEAK_BUY;
      if(avg_score <= -1.0) return STRONG_SELL;
      if(avg_score <= -0.5) return WEAK_SELL;

      return NEUTRAL;
   }
};

#endif // __SIGNAL_CONSENSUS_ENGINE_MQH__ 