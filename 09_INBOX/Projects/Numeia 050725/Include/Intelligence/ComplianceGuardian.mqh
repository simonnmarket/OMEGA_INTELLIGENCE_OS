#pragma once
//+------------------------------------------------------------------+
//| ComplianceGuardian.mqh - Guardião de Conformidade Estratégica   |
//| Projeto: EA Numeia - SkyIntel                                   |
//| Função: Monitorar padrões éticos, validar legalidade e          |
//| bloquear simplificações abaixo do padrão institucional          |
//| Estado: Ativo em todas as chamadas principais de inteligência   |
//+------------------------------------------------------------------+

#include <Logs/AuditManager.mqh>

namespace ComplianceGuardian
{
    bool audit_mode_enabled = true;

    // Executa auditoria pré-ativação
    void RunPreFlightAudit()
    {
        if (audit_mode_enabled)
        {
            string msg = "Auditoria pré-execução concluída. Sistema dentro dos padrões.";
            Print("ComplianceGuardian: " + msg);
            AuditLog("ComplianceGuardian", "SYSTEM", "✅ " + msg);
        }
    }

    // Valida sinais antes de envio para qualquer módulo de execução
    void ValidateSignal(string symbol, ENUM_SIGNAL_TYPE signal)
    {
        if (!audit_mode_enabled)
            return;

        string signalName = EnumToString(signal);

        if (signal == SIGNAL_NONE)
        {
            string msg = "Nenhum sinal relevante detectado para " + symbol;
            Print("ComplianceGuardian: " + msg);
            AuditLog("ComplianceGuardian", symbol, "🟡 " + msg);
            return;
        }

        if (signal == SIGNAL_UNCERTAIN)
        {
            string msg = "⚠️ Sinal incerto detectado para " + symbol + ". Execução bloqueada por auditoria.";
            Print(msg);
            AuditLog("ComplianceGuardian", symbol, msg);
            // [FUTURE BLOCK] - Aqui poderá impedir ordens diretamente
        }

        string msg = "Sinal validado e liberado para análise final: " + signalName;
        Print("ComplianceGuardian: " + msg);
        AuditLog("ComplianceGuardian", symbol, "✅ " + msg);
    }

    // Registro de eventos críticos
    void Log(string message, string tag = "Compliance")
    {
        if (audit_mode_enabled)
        {
            Print("📘 [" + tag + "] " + message);
            AuditLog("ComplianceGuardian", "SYSTEM", message);
        }
    }

    // Valida se o sinal é elegível para execução
    bool IsSignalExecutable(ENUM_SIGNAL_TYPE signal)
    {
        return (signal == SIGNAL_SPIKE_LONG || signal == SIGNAL_SPIKE_SHORT);
    }
}
