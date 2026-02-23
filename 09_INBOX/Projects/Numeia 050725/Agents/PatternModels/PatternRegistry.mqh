//+--------------------------------------------------------------+
//| Registro Central de Padrões Ativos                           |
//+--------------------------------------------------------------+
#pragma once
#include "EngulfingPattern.mqh"

class PatternRegistry {
private:
    static IPatternModel *patterns[];

public:
    static void Init() {
        ArrayResize(patterns, 1);
        patterns[0] = new EngulfingPattern();
        // Ex: patterns[1] = new PinBarPattern(); etc.
    }

    static int GetTotal() {
        return ArraySize(patterns);
    }

    static IPatternModel *GetPattern(int index) {
        if (index < 0 || index >= ArraySize(patterns))
            return NULL;
        return patterns[index];
    }
};

IPatternModel *PatternRegistry::patterns[];
