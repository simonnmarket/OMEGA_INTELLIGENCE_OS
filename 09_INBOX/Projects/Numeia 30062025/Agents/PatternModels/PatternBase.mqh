//+------------------------------------------------------------------+
//| PatternBase.mqh - Classe Base para Padrões                      |
//| Projeto: EA Numeia - PatternModels                              |
//| Função: Interface base para todos os padrões de trading         |
//+------------------------------------------------------------------+
#ifndef __PATTERN_BASE_MQH__
#define __PATTERN_BASE_MQH__

#include "../../Utils/Log.mqh"

// Interface base para padrões
class IPatternModel {
public:
   virtual bool Detect(string symbol, ENUM_TIMEFRAMES tf) = 0;
   virtual string GetName() = 0;
   virtual double GetConfidence() = 0;
};

#endif // __PATTERN_BASE_MQH__ 