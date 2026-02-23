
//+------------------------------------------------------------------+
//| BehavioralEconomyKernel.mqh                                      |
//| Modelagem de economia comportamental aplicada ao trading        |
//+------------------------------------------------------------------+
#pragma once

class BehavioralEconomyKernel {
public:
    double AdjustRiskByLossAversion(double baseRisk, double drawdown);
    double ModifyEntryByRecencyEffect(double history[]);
    double ConvertHeuristicToWeight(string heuristicType);
};
