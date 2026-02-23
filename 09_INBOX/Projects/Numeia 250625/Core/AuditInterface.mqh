//+------------------------------------------------------------------+
//| AuditInterface.mqh - Interface de Auditoria                     |
//| Projeto: EA Numeia - Core                                       |
//| Função: Interface padronizada para auditoria e compliance       |
//+------------------------------------------------------------------+
#ifndef __AUDIT_INTERFACE_MQH__
#define __AUDIT_INTERFACE_MQH__

#include "../Utils/Log.mqh"

// Estrutura para mensagens de auditoria
struct AuditMessage
{
   string module;
   string action;
   string details;
   datetime timestamp;
   bool success;
};

// Interface de auditoria
class AuditInterface {
private:
   string moduleName;

public:
   AuditInterface(string name = "SYSTEM") {
      moduleName = name;
   }

   void LogAction(string action, string details, bool success = true) {
      AuditMessage msg;
      msg.module = moduleName;
      msg.action = action;
      msg.details = details;
      msg.timestamp = TimeCurrent();
      msg.success = success;

      AuditLog(moduleName, "SYSTEM", StringFormat("%s: %s", action, details));
   }

   void LogError(string action, string error) {
      LogAction(action, error, false);
   }
};

#endif // __AUDIT_INTERFACE_MQH__ 