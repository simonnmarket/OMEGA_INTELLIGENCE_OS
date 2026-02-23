//+------------------------------------------------------------------+
//|                      AuditInterface.mqh                          |
//|     Interface de Comunicação com o Módulo de Auditoria           |
//+------------------------------------------------------------------+
#pragma once

// Estrutura para mensagens de auditoria
struct AuditMessage {
   string module_name;      // Nome do módulo que gerou a mensagem
   string action_type;      // Tipo de ação auditada (ex: "Order", "RiskCheck", "PatternDetected")
   string description;      // Descrição detalhada da ação
   datetime timestamp;      // Momento em que ocorreu
};

// Interface base de auditoria
class IAuditInterface {
public:
   // Envia uma mensagem de auditoria ao AuditManager
   virtual void SendAudit(const AuditMessage &msg) = 0;
};

// Implementação padrão (exemplo inicial)
class AuditInterface : public IAuditInterface {
public:
   // Implementação do envio para o AuditManager (pode ser log ou comunicação direta)
   void SendAudit(const AuditMessage &msg) override {
      PrintFormat("[AUDIT] %s | [%s] %s @ %s",
                  msg.module_name,
                  msg.action_type,
                  msg.description,
                  TimeToString(msg.timestamp, TIME_DATE | TIME_MINUTES));
   }
};
