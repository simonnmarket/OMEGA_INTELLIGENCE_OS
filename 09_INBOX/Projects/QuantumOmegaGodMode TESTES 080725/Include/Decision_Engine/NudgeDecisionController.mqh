// File: Include/DECISION_ENGINE/NudgeDecisionController.mqh
// Project: Quantum Omega God Mode
// Role: Controlador de Decisão baseado na Teoria do Nudge (Richard H. Thaler)

#ifndef __NUDGE_DECISION_CONTROLLER_MQH__
#define __NUDGE_DECISION_CONTROLLER_MQH__

class NudgeDecisionController {
private:
   double biasFactor;

public:
   NudgeDecisionController() {
      biasFactor = 1.0;
   }

   void SetBias(double factor) {
      biasFactor = factor;
   }

   int Decide(double signal) {
      double adjusted = signal * biasFactor;

      if(adjusted > 0.7)
         return 1; // BUY
      else if(adjusted < -0.7)
         return -1; // SELL
      else
         return 0; // HOLD
   }
};

#endif
