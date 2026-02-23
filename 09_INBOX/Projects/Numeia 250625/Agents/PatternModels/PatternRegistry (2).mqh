//+------------------------------------------------------------------+
//| PatternRegistry.mqh - Registro de Padrões                       |
//| Projeto: EA Numeia - PatternModels                              |
//| Função: Gerencia e registra todos os padrões disponíveis        |
//+------------------------------------------------------------------+
#ifndef __PATTERN_REGISTRY_MQH__
#define __PATTERN_REGISTRY_MQH__

#include "PatternBase.mqh"
#include "EngulfingPattern.mqh"

class PatternRegistry {
private:
    IPatternModel *patterns[];

public:
    PatternRegistry() {
        // Registra padrões disponíveis
        ArrayResize(patterns, 1);
        patterns[0] = new EngulfingPattern();
        // Ex: patterns[1] = new PinBarPattern(); etc.
    }

    void RegisterPattern(IPatternModel *pattern) {
        int size = ArraySize(patterns);
        ArrayResize(patterns, size + 1);
        patterns[size] = pattern;
    }

    IPatternModel *GetPattern(int index) {
        if (index >= 0 && index < ArraySize(patterns))
            return patterns[index];
        return NULL;
    }

    int GetPatternCount() {
        return ArraySize(patterns);
    }
};

#endif // __PATTERN_REGISTRY_MQH__ 