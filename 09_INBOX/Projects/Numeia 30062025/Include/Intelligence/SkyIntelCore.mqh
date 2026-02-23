//+------------------------------------------------------------------+
//| SkyIntelCore.mqh - Núcleo de Inteligência Estratégica           |
//| Projeto: EA Numeia - Sistema de IA Avançada                     |
//+------------------------------------------------------------------+
#ifndef __SKYINTEL_CORE_MQH__
#define __SKYINTEL_CORE_MQH__

#include "SkyCrawlerNet.mqh"
#include "DeepPersonaLens.mqh"
#include "ScenarioIntelCore.mqh"
#include "ComplianceGuardian.mqh"
#include "../../Utils/Log.mqh"  // Log institucional

namespace SkyIntelCore
{
    // Estado geral do sistema
    bool SkyIntel_Initialized = false;

    // Inicialização completa do sistema SkyIntel
    void Initialize()
    {
        if (SkyIntel_Initialized)
            return;

        ComplianceGuardian::RunPreFlightAudit();
        SkyCrawlerNet::Initialize();
        DeepPersonaLens::Initialize();
        ScenarioIntelCore::Initialize();

        SkyIntel_Initialized = true;

        ComplianceGuardian::Log("SkyIntelCore: Inicialização completa.");
        AuditLog("SkyIntelCore", "SYSTEM", "✅ Sistema SkyIntel iniciado com sucesso.");
    }

    // Verifica cenários de inteligência para um ativo
    ENUM_SIGNAL_TYPE CheckScenarioFor(string symbol)
    {
        if (!SkyIntel_Initialized)
            Initialize();

        PersonaProfile persona = DeepPersonaLens::AnalyzePersonas(symbol);
        ENUM_SIGNAL_TYPE signal = ScenarioIntelCore::EvaluateScenario(symbol, persona);

        ComplianceGuardian::ValidateSignal(symbol, signal);
        return signal;
    }

    // Interface principal para obter sinal estratégico (usado pelo script de teste)
    ENUM_SIGNAL_TYPE GetStrategicSignal(string symbol)
    {
        return CheckScenarioFor(symbol);
    }

    // Status simples do sistema
    string StatusReport()
    {
        return StringFormat("SkyIntel Initialized: %s", SkyIntel_Initialized ? "YES" : "NO");
    }

    // [EXTENSIBLE MODULE] - Ponto de expansão para integração com novos módulos
}

#endif // __SKYINTEL_CORE_MQH__ 