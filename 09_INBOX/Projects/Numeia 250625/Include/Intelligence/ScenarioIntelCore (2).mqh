//+------------------------------------------------------------------+
//| ScenarioIntelCore.mqh - Construção de Cenários Estratégicos     |
//| Projeto: EA Numeia - SkyIntel                                   |
//| Função: Cruzar sinais coletados e analisados para construir     |
//| projeções de movimentos do mercado com base em padrões sociais  |
//+------------------------------------------------------------------+

#include "DeepPersonaLens.mqh"
#include "../../Utils/Log.mqh"
#include "../../Core/types.mqh"

namespace ScenarioIntelCore
{
    bool scenario_initialized = false;

    void Initialize()
    {
        scenario_initialized = true;
        Print("ScenarioIntelCore: Núcleo de cenários iniciado.");
        AuditLog("ScenarioIntelCore", "SYSTEM", "✅ Núcleo de construção de cenários ativado.");
    }

    // Avalia o cenário atual com base no perfil comportamental recebido
    ENUM_SIGNAL_TYPE EvaluateScenario(string symbol, PersonaProfile &persona)
    {
        ENUM_SIGNAL_TYPE signal = SIGNAL_NONE;

        if (persona.highRiskBehavior && persona.displayLuxury && persona.influenceScore > 0.85)
        {
            for (int i = 0; i < ArraySize(persona.recentSignals); i++)
            {
                string content = StringToLower(persona.recentSignals[i]);
                
                // Log para debug
                AuditLog("ScenarioIntelCore", symbol, 
                         StringFormat("Analisando sinal %d: '%s'", i+1, persona.recentSignals[i]));

                if (StringFind(content, "long") != -1 || StringFind(content, "rocket") != -1 || 
                    StringFind(content, "🚀") != -1 || StringFind(content, "buy") != -1)
                {
                    signal = SIGNAL_SPIKE_LONG;
                    AuditLog("ScenarioIntelCore", symbol, "🚀 Sinal LONG detectado!");
                    break;
                }
                else if (StringFind(content, "short") != -1 || StringFind(content, "collapse") != -1 || 
                         StringFind(content, "💥") != -1 || StringFind(content, "sell") != -1)
                {
                    signal = SIGNAL_SPIKE_SHORT;
                    AuditLog("ScenarioIntelCore", symbol, "💥 Sinal SHORT detectado!");
                    break;
                }
            }

            if (signal == SIGNAL_NONE)
            {
                signal = SIGNAL_UNCERTAIN;
                AuditLog("ScenarioIntelCore", symbol, "❓ Nenhum sinal claro detectado - UNCERTAIN");
            }
        }
        else
        {
            string riskStatus = (persona.highRiskBehavior) ? "true" : "false";
            string luxuryStatus = (persona.displayLuxury) ? "true" : "false";
            
            AuditLog("ScenarioIntelCore", symbol, 
                     StringFormat("Perfil não atende critérios: Risk=%s, Luxury=%s, Score=%.2f", 
                                  riskStatus, luxuryStatus, persona.influenceScore));
        }

        AuditLog("ScenarioIntelCore", symbol,
                 StringFormat("Cenário avaliado: %s | Sinal Estratégico: %s",
                              persona.name, GetSignalName(signal)));

        return signal;
    }

    // Função auxiliar de conversão
    string GetSignalName(ENUM_SIGNAL_TYPE s)
    {
        switch (s)
        {
            case SIGNAL_SPIKE_LONG:  return "Spike Long";
            case SIGNAL_SPIKE_SHORT: return "Spike Short";
            case SIGNAL_UNCERTAIN:   return "Incerteza";
            default:                 return "Nenhum";
        }
    }
} 