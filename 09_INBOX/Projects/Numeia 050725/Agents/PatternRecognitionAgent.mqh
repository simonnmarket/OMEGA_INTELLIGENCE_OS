//+------------------------------------------------------------------+
//| PatternRecognitionAgent.mqh                                      |
//| Responsável por detectar padrões gráficos recorrentes            |
//| em múltiplos timeframes e sinalizar o CoreBrainManager           |
//+------------------------------------------------------------------+
#pragma once

#include "..\Utils\Log.mqh"
#include "..\Core\types.mqh"
#include "..\Auditor\AuditLogger.mqh"
#include "PatternModels\PatternRegistry.mqh"

class PatternRecognitionAgent {
private:
    string symbol;
    ENUM_TIMEFRAMES tf;

public:
    PatternRecognitionAgent(string _symbol, ENUM_TIMEFRAMES _tf) {
        symbol = _symbol;
        tf = _tf;
    }

    // Função chamada a cada novo tick
    void OnTick() {
        Log("PatternRecognitionAgent", "Verificando padrões no ativo " + symbol);

        PatternRegistry::Init(symbol, tf);  // Inicializa os padrões registrados

        for (int i = 0; i < PatternRegistry::GetTotal(); i++) {
            IPatternModel *pattern = PatternRegistry::GetPattern(i);
            if (pattern != NULL && pattern.CheckPattern()) {
                string name = pattern.GetName();
                Log("PatternDetection", name + " detectado em " + EnumToString(tf));
                AuditLogger::LogEvent("Padrão detectado: " + name, symbol, tf);
                // Aqui podemos acionar visualização ou tomada de decisão futura
            }
        }
    }

    void SetTimeframe(ENUM_TIMEFRAMES new_tf) {
        tf = new_tf;
    }
};
