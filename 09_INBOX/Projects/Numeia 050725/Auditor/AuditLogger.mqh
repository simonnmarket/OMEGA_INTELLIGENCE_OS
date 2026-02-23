//+------------------------------------------------------------------+
//|                                            AuditLogger.mqh       |
//|            Sistema de log interno para o módulo de auditoria    |
//+------------------------------------------------------------------+
#ifndef __AUDIT_LOGGER_MQH__
#define __AUDIT_LOGGER_MQH__

#include "../Utils/Log.mqh"

class AuditLogger {
private:
   string prefix;

public:
   void Init(string module_name = "AUDIT") {
      prefix = "[" + module_name + "]";
   }

   // Log simples
   void Log(string message) {
      Print(prefix + " " + message);
   }

   // Log com formatação (versão simples sem variádico)
   void LogFormat(string format, string param1, string param2 = "", double param3 = 0.0, int param4 = 0) {
      string formatted = StringFormat(format, param1, param2, param3, param4);
      Log(formatted);
   }

   // Overloads para diferentes tipos
   void LogFormat(string format, string param1, double param2) {
      string formatted = StringFormat(format, param1, param2);
      Log(formatted);
   }

   void LogFormat(string format, string param1, string param2, double param3) {
      string formatted = StringFormat(format, param1, param2, param3);
      Log(formatted);
   }

   void LogFormat(string format, string param1, string param2, double param3, int param4) {
      string formatted = StringFormat(format, param1, param2, param3, param4);
      Log(formatted);
   }

   void LogWarning(string message) {
      Print(prefix + " ⚠️ " + message);
   }

   void LogError(string message) {
      Print(prefix + " ❌ ERRO: " + message);
   }

   void LogSuccess(string message) {
      Print(prefix + " ✅ " + message);
   }
};

#endif // __AUDIT_LOGGER_MQH__
