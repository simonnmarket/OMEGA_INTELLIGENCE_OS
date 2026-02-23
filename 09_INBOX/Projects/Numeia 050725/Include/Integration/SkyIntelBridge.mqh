#pragma once
//+------------------------------------------------------------------+
//| SkyIntelBridge.mqh - Ponte entre SKYINTEL e EA Numeia           |
//| Projeto: Numeia EA - Integração com Módulo Estratégico          |
//| Função: Consultar o núcleo SkyIntel, validar o sinal e          |
//| repassar ao CoreBrainManager ou DecisionEngine                  |
//+------------------------------------------------------------------+

#include <Intelligence/SkyIntelCore.mqh>
#include <Intelligence/ComplianceGuardian.mqh>
#include <Logs/AuditManager.mqh>

namespace SkyIntelBridge
{
    input bool EnableSkyIntel = true; // ✅ Input externo para ativar ou não

    // Função principal para avaliação de sinal estratégico
    ENUM_SIGNAL_TYPE EvaluateSkyIntelSignal(string symbol)
    {
        if (!EnableSkyIntel)
        {
            AuditLog("SkyIntelBridge", symbol, "❎ SkyIntel desativado pelo operador.");
            return SIGNAL_NONE;
        }

        ENUM_SIGNAL_TYPE signal = SkyIntel::CheckScenarioFor(symbol);

        if (ComplianceGuardian::IsSignalExecutable(signal))
        {
            string label = SkyIntel::StatusReport();
            AuditLog("SkyIntelBridge", symbol,
                     StringFormat("✅ Sinal estratégico aceito: %s | [%s]",
                                  EnumToString(signal), label));
        }
        else
        {
            AuditLog("SkyIntelBridge", symbol,
                     StringFormat("⚠️ Sinal ignorado ou bloqueado: %s",
                                  EnumToString(signal)));
        }

        return signal;
    }

    // Função auxiliar para nome do sinal
    string DescribeSignal(ENUM_SIGNAL_TYPE signal)
    {
        switch (signal)
        {
            case SIGNAL_SPIKE_LONG:  return "Oportunidade Estratégica: Long";
            case SIGNAL_SPIKE_SHORT: return "Oportunidade Estratégica: Short";
            case SIGNAL_UNCERTAIN:   return "Sinal Estratégico Incerto";
            default:                 return "Nenhum Sinal Estratégico";
        }
    }
}
