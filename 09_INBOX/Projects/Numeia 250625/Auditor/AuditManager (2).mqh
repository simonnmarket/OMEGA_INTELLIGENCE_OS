//+------------------------------------------------------------------+
//|                                             AuditManager.mqh     |
//|               Parte do sistema de auditoria interna da Numeia   |
//+------------------------------------------------------------------+
#ifndef __AUDIT_MANAGER_MQH__
#define __AUDIT_MANAGER_MQH__

#include "../Core/types.mqh"
#include "../Utils/Log.mqh"

class AuditManager {
private:
   bool auditActive;

public:
   AuditManager() {
      auditActive = true;
   }

   // Inicializa o sistema de auditoria
   bool Init() {
      AuditLog("[AuditManager] Inicializando sistema de auditoria...");
      return true;
   }

   // Encerra o sistema de auditoria
   void OnDeinit() {
      AuditLog("[AuditManager] Encerrando sistema de auditoria...");
   }

   // Valida execução de ordens conforme regras internas
   bool ValidateTradeRequest(string agent, string symbol, ENUM_ORDER_TYPE type, double volume, double price) {
      if(volume <= 0.0 || volume > 100.0) {
         AuditLog("[AuditManager] Volume inválido detectado pelo agente [" + agent + "] no ativo [" + symbol + "]: " + DoubleToString(volume, 2), LOG_LEVEL_ERROR);
         return false;
      }

      if(type != ORDER_TYPE_BUY && type != ORDER_TYPE_SELL) {
         string typeStr = IntegerToString(type);
         AuditLog("[AuditManager] Tipo de ordem inválido detectado pelo agente [" + agent + "]: " + typeStr, LOG_LEVEL_ERROR);
         return false;
      }

      // Log de validação com compliance
      AuditLog("[AuditManager] Ordem validada pelo agente [" + agent + "] para [" + symbol + "] com volume [" + DoubleToString(volume, 2) + "]");
      return true;
   }

   // Valida alinhamento com múltiplos timeframes antes de abrir uma ordem
   bool ValidateMultiTFAlignment(string symbol, bool aligned) {
      if(!aligned) {
         AuditLog("[AuditManager] Desalinhamento entre timeframes detectado para [" + symbol + "]", LOG_LEVEL_WARN);
         return false;
      }

      AuditLog("[AuditManager] Alinhamento entre timeframes confirmado para [" + symbol + "]");
      return true;
   }

   // Valida se a estratégia respeita o limite de risco configurado
   bool ValidateRiskThreshold(double currentRisk, double maxRisk) {
      if(currentRisk > maxRisk) {
         string currentRiskStr = DoubleToString(currentRisk, 2);
         string maxRiskStr = DoubleToString(maxRisk, 2);
         AuditLog("[AuditManager] Risco excedido: atual [" + currentRiskStr + "], máximo permitido [" + maxRiskStr + "]", LOG_LEVEL_ERROR);
         return false;
      }

      AuditLog("[AuditManager] Risco dentro dos limites aceitáveis");
      return true;
   }

   // Notifica auditoria manual ou falha crítica
   void Flag(string message) {
      AuditLog("[AuditManager] 🚨 Alerta de Auditoria: " + message, LOG_LEVEL_ERROR);
   }

   // Auditoria de compliance institucional
   void AuditCompliance(string checkName, bool passed, string details = "") {
      if(passed) {
         AuditLog("[AuditManager] Compliance [" + checkName + "] APROVADO: " + details);
      } else {
         AuditLog("[AuditManager] Compliance [" + checkName + "] REPROVADO: " + details, LOG_LEVEL_ERROR);
      }
   }

   // Auditoria de performance
   void AuditPerformance(string operation, datetime startTime) {
      datetime endTime = TimeCurrent();
      int duration = (int)(endTime - startTime);
      AuditLog("[AuditManager] Performance [" + operation + "]: " + IntegerToString(duration) + " segundos");
   }
};

#endif // __AUDIT_MANAGER_MQH__ 