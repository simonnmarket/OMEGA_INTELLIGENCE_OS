//+------------------------------------------------------------------+
//|                            Log.mqh                               |
//|        Utilitário genérico de logging para a EA Numeia          |
//+------------------------------------------------------------------+
#ifndef __LOG_MQH__
#define __LOG_MQH__

// Tipos de log
enum LogLevel {
   LOG_INFO,
   LOG_WARNING,
   LOG_ERROR,
   LOG_SUCCESS
};

// Log principal formatado
void LogPrint(string message, LogLevel level = LOG_INFO, string source = "SYSTEM") {
   string prefix;

   switch(level) {
      case LOG_INFO:    prefix = "ℹ️ [INFO]";    break;
      case LOG_WARNING: prefix = "⚠️ [WARN]";    break;
      case LOG_ERROR:   prefix = "❌ [ERROR]";   break;
      case LOG_SUCCESS: prefix = "✅ [OK]";      break;
      default:          prefix = "[LOG]";
   }

   string full_message = StringFormat("%s [%s] %s", prefix, source, message);
   Print(full_message);
}

// Versões simplificadas
void LogInfo(string msg, string src = "SYSTEM")    { LogPrint(msg, LOG_INFO, src); }
void LogWarn(string msg, string src = "SYSTEM")    { LogPrint(msg, LOG_WARNING, src); }
void LogErr(string msg, string src = "SYSTEM")     { LogPrint(msg, LOG_ERROR, src); }
void LogOK(string msg, string src = "SYSTEM")      { LogPrint(msg, LOG_SUCCESS, src); }

// Versão auditável para módulos institucionais
void AuditLog(const string origin, const string symbol, const string message)
{
   string full_message = StringFormat("[AUDIT] [%s] %s >> %s", origin, symbol, message);
   Print(full_message);
}

#endif // __LOG_MQH__
