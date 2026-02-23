// File: Include/INTELLIGENCE/SkyIntelManager.mqh
// Project: Quantum Omega God Mode
// Role: Agente Central de Inteligência Estratégica e Análise de Sinais Externos

#ifndef __SKY_INTEL_MANAGER_MQH__
#define __SKY_INTEL_MANAGER_MQH__

class SkyIntelManager {
private:
   double lastSentimentScore;

public:
   SkyIntelManager() {
      lastSentimentScore = 0.0;
   }

   void UpdateSentiment(double score) {
      lastSentimentScore = score;
      Print("[SKYINTEL] Atualizando sentimento: ", score);
   }

   double GetSentimentScore() {
      return lastSentimentScore;
   }

   bool DetectStrategicOpportunity() {
      return (lastSentimentScore > 0.75);
   }
};

#endif
