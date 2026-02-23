#pragma once
//+------------------------------------------------------------------+
//| SkyIntelCore.mqh - Núcleo Central de Inteligência Estratégica   |
//| Projeto: EA Numeia - Módulo SkyIntel                            |
//| Função: Interface de alto nível para ativação, leitura e        |
//|          comunicação entre os submódulos de inteligência         |
//| Estratégia: Modular, expansível e auditável                     |
//+------------------------------------------------------------------+

#include "SkyCrawlerNet.mqh"
#include "DeepPersonaLens.mqh"
#include "ScenarioIntelCore.mqh"
#include "ComplianceGuardian.mqh"
#include <Logs/AuditManager.mqh>  // Log institucional

namespace SkyIntel
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

    // Status simples do sistema
    string StatusReport()
    {
        return StringFormat("SkyIntel Initialized: %s", SkyIntel_Initialized ? "YES" : "NO");
    }

    // [EXTENSIBLE MODULE] - Ponto de expansão para integração com novos módulos
}
