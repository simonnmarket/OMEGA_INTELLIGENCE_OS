
//+------------------------------------------------------------------+
//| NudgeDecisionController.mqh                                      |
//| Aplica a Teoria do Nudge para influenciar decisões algorítmicas |
//+------------------------------------------------------------------+
#pragma once

class NudgeDecisionController {
public:
    int GetDefaultStrategy();
    void ApplySmartDefaults(int context);
    void ReinforceOptimalPath(string decisionType);
};
