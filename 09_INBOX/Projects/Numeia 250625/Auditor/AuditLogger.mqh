//+------------------------------------------------------------------+
//|                                            AuditLogger.mqh       |
//|            Sistema de log interno para o módulo de auditoria    |
//|                    NÍVEL INSTITUCIONAL - FUNDOS DE INVESTIMENTO |
//+------------------------------------------------------------------+
#ifndef __AUDIT_LOGGER_MQH__
#define __AUDIT_LOGGER_MQH__

#include "../Utils/Log.mqh"

class AuditLogger {
private:
   string prefix;
   bool audit_mode_enabled;
   datetime last_audit_time;
   int audit_level;

public:
   void Init(string module_name = "AUDIT") {
      prefix = "[" + module_name + "]";
      audit_mode_enabled = true;
      last_audit_time = TimeCurrent();
      audit_level = 3; // Nível máximo de auditoria
   }

   // Log simples
   void Log(string message) {
      Print(prefix + " " + message);
   }

   // Log com formatação avançada (versões específicas sem ambiguidade)
   void LogWithCode(string format, string param1, string param2, double param3, int param4) {
      string formatted = StringFormat(format, param1, param2, param3, param4);
      Log(formatted);
   }

   void LogSimple(string format, string param1, double param2) {
      string formatted = StringFormat(format, param1, param2);
      Log(formatted);
   }

   void LogDetailed(string format, string param1, string param2, double param3) {
      string formatted = StringFormat(format, param1, param2, param3);
      Log(formatted);
   }

   // Logs especializados para auditoria institucional
   void LogWarning(string message) {
      Print(prefix + " ⚠️ " + message);
   }

   void LogError(string message) {
      Print(prefix + " ❌ ERRO: " + message);
   }

   void LogSuccess(string message) {
      Print(prefix + " ✅ " + message);
   }

   void LogCritical(string message) {
      Print(prefix + " 🚨 CRÍTICO: " + message);
   }

   void LogCompliance(string message) {
      Print(prefix + " 📋 COMPLIANCE: " + message);
   }

   void LogRisk(string message) {
      Print(prefix + " ⚡ RISCO: " + message);
   }

   void LogPerformance(string message) {
      Print(prefix + " 📊 PERFORMANCE: " + message);
   }

   // Auditoria de tempo e performance
   void LogExecutionTime(string operation, datetime start_time) {
      datetime end_time = TimeCurrent();
      double execution_time = (double)(end_time - start_time);
      LogPerformance(StringFormat("Operação '%s' executada em %.3f segundos", operation, execution_time));
   }

   // Auditoria de compliance institucional
   void LogComplianceCheck(string check_name, bool passed, string details = "") {
      if (passed) {
         LogCompliance(StringFormat("CHECK '%s': APROVADO - %s", check_name, details));
      } else {
         LogCritical(StringFormat("CHECK '%s': REPROVADO - %s", check_name, details));
      }
   }
};

#endif // __AUDIT_LOGGER_MQH__ 