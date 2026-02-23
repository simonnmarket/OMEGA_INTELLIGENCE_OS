//+------------------------------------------------------------------+
//|                                             AuditManager.mqh     |
//|               Parte do sistema de auditoria interna da Numeia   |
//+------------------------------------------------------------------+
#ifndef __AUDIT_MANAGER_MQH__
#define __AUDIT_MANAGER_MQH__

#include "../Core/types.mqh"
#include "AuditLogger.mqh"

class AuditManager {
private:
   AuditLogger logger;

public:
   // Inicializa o sistema de auditoria
   void Init() {
      logger.Init();
      logger.Log("AuditManager iniciado.");
   }

   // Valida execução de ordens conforme regras internas
   bool ValidateTradeRequest(string agent, string symbol, ENUM_ORDER_TYPE type, double volume, double price) {
      if(volume <= 0.0 || volume > 100.0) {
         logger.LogFormat("Volume inválido detectado pelo agente [%s] no ativo [%s]: %.2f", agent, symbol, volume);
         return false;
      }

      if(type != ORDER_TYPE_BUY && type != ORDER_TYPE_SELL) {
         logger.LogFormat("Tipo de ordem inválido detectado pelo agente [%s]: %d", agent, type);
         return false;
      }

      // Log de validação
      logger.LogFormat("Ordem validada pelo agente [%s] para [%s] com volume [%.2f] e tipo [%d]",
                       agent, symbol, volume, type);

      return true;
   }

   // Valida alinhamento com múltiplos timeframes antes de abrir uma ordem
   bool ValidateMultiTFAlignment(string symbol, bool aligned) {
      if(!aligned) {
         logger.LogFormat("Desalinhamento entre timeframes detectado para [%s]", symbol);
         return false;
      }

      logger.LogFormat("Alinhamento entre timeframes confirmado para [%s]", symbol);
      return true;
   }

   // Valida se a estratégia respeita o limite de risco configurado
   bool ValidateRiskThreshold(double currentRisk, double maxRisk) {
      if(currentRisk > maxRisk) {
         logger.LogFormat("Risco excedido: atual [%.2f], máximo permitido [%.2f]", currentRisk, maxRisk);
         return false;
      }

      return true;
   }

   // Notifica auditoria manual ou falha crítica
   void Flag(string message) {
      logger.Log("⚠️ Alerta de Auditoria: " + message);
   }
};

#endif // __AUDIT_MANAGER_MQH__
