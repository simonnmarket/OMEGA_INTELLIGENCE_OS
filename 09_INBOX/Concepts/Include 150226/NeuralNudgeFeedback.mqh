
//+------------------------------------------------------------------+
//| NeuralNudgeFeedback.mqh                                          |
//| Feedback neural baseado em resposta comportamental contínua     |
//+------------------------------------------------------------------+
#pragma once

class NeuralNudgeFeedback {
private:
    double m_lastFeedback;
public:
    void UpdateWithBehavioralSignal(double signalStrength);
    double GetAdaptiveWeight();
    bool IsLearningStable();
};
