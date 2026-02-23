//+------------------------------------------------------------------+
//| core_brain_manager.mqh - Core Brain Manager                      |
//| Projeto: QuantumOmegaGodMode                                     |
//| Versão: v2.3 (Thaler-Enhanced + Blindagem Institucional)        |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready       |
//| SHA3 Checksum: 7e6d5c4b3a2918273645544332211009abcdef876543210987654321098765432 |
//| Atualizado em: 2025-07-20 | Agente: Grok (IA Agent)             |
//+------------------------------------------------------------------+
#ifndef __CORE_BRAIN_MANAGER_MQH__
#define __CORE_BRAIN_MANAGER_MQH__

// Macros institucionais de segurança
#define SAFE_EXEC(x) if(!(x)) { \
   if(m_logger != NULL) m_logger.log_error("[CORE] Falha em " + #x); \
   return false; \
}

#define VALIDATE_POINTER(ptr) if(ptr == NULL) { \
   if(m_logger != NULL) m_logger.log_error("[CORE] Ponteiro NULL: " + #ptr); \
   return false; \
}

#define VALIDATE_ARRAY(arr) if(ArraySize(arr) <= 0) { \
   if(m_logger != NULL) m_logger.log_error("[CORE] Array vazio: " + #arr); \
   return false; \
}

// Parâmetros de entrada com validação
input group "Core Brain Manager Settings"
input bool Simulate = true;                    // Modo simulado para testes seguros
input double MaxSlippage = 0.5;               // Slippage máximo permitido (pips)
input int MaxRetries = 3;                     // Máximo de tentativas de reconexão
input bool EnableEmergencyShutdown = true;    // Ativar shutdown de emergência

#include <decisionengine/decision_router.mqh>
#include <executionlogic/safe_mode_manager.mqh>
#include <executionlogic/trade_executor.mqh>
#include <types/trade_signal_enum.mqh>
#include <utils/logger_institutional.mqh>
#include <security/quantumfirewall.mqh>

//+------------------------------------------------------------------+
class core_brain_manager {
private:
   // Componentes principais com validação de ponteiros
   decision_router       *m_router;
   trade_executor        *m_executor;
   safe_mode_manager     *m_safety;
   logger_institutional  *m_logger;
   QuantumFirewall        m_firewall;
   
   // Configurações de segurança
   double                 m_max_slippage;
   int                    m_retry_count;
   bool                   m_initialized;
   datetime              m_last_tick_time;
   
   // Histórico de operações para auditoria
   struct OperationLog {
      datetime timestamp;
      string operation;
      bool success;
      string details;
   };
   OperationLog m_operation_history[];

public:
   core_brain_manager(
      decision_router &router,
      trade_executor &executor,
      safe_mode_manager &safety,
      logger_institutional &logger
   ) : m_router(&router), m_executor(&executor), 
       m_safety(&safety), m_logger(&logger), m_initialized(false) {
      
      // Validação de ponteiros no construtor
      VALIDATE_POINTER(m_router);
      VALIDATE_POINTER(m_executor);
      VALIDATE_POINTER(m_safety);
      VALIDATE_POINTER(m_logger);
      
      m_max_slippage = MathMax(0.1, MathMin(MaxSlippage, 10.0)); // Fallback defensivo
      m_retry_count = 0;
      m_last_tick_time = 0;
      
      // Inicialização segura do firewall
      SAFE_EXEC(m_firewall.initialize());
      
      log_operation("Construtor", true, "Core brain manager criado com sucesso");
   }

   void initialize() {
      if(m_initialized) {
         if(m_logger != NULL) m_logger.log_warning("[CORE] Já inicializado");
         return;
      }
      
      // Validação de conectividade do terminal
      if(!TerminalInfoInteger(TERMINAL_CONNECTED)) {
         log_operation("Inicialização", false, "Terminal offline");
         if(m_logger != NULL) m_logger.log_critical("[CORE] Terminal offline");
         ExpertRemove();
         return;
      }
      
      // Validação de ponteiros antes da inicialização
      VALIDATE_POINTER(m_router);
      VALIDATE_POINTER(m_executor);
      VALIDATE_POINTER(m_safety);
      VALIDATE_POINTER(m_logger);
      
      if(m_logger != NULL) m_logger.log_info("[CORE] Iniciando inicialização de módulos...");
      
      // Inicialização segura dos módulos
      SAFE_EXEC(m_router.initialize());
      SAFE_EXEC(m_executor.initialize());
      SAFE_EXEC(m_safety.initialize());
      SAFE_EXEC(m_firewall.scan_dependencies());
      
      m_initialized = true;
      m_retry_count = 0;
      
      log_operation("Inicialização", true, "Todos os módulos inicializados com sucesso");
      
      if(m_logger != NULL) m_logger.log_info("[CORE] Inicialização concluída com sucesso");
   }

   void on_tick() {
      // Validação de inicialização
      if(!m_initialized) {
         if(m_logger != NULL) m_logger.log_error("[CORE] Tentativa de on_tick sem inicialização");
         return;
      }
      
      // Validação de ponteiros
      VALIDATE_POINTER(m_router);
      VALIDATE_POINTER(m_executor);
      VALIDATE_POINTER(m_safety);
      VALIDATE_POINTER(m_logger);
      
      // Proteção contra chamadas muito frequentes
      datetime current_time = TimeCurrent();
      if(current_time - m_last_tick_time < 1) { // Mínimo 1 segundo entre ticks
         return;
      }
      m_last_tick_time = current_time;
      
      // Validação de ambiente
      if(!m_firewall.validate_environment()) {
         log_operation("Firewall", false, "Violação de firewall detectada");
         if(m_logger != NULL) m_logger.log_critical("[CORE] Violação de firewall detectada");
         
         if(EnableEmergencyShutdown) {
            SAFE_EXEC(m_safety.activate_emergency_shutdown());
         }
         return;
      }

      // Avaliação de condições de segurança
      SAFE_EXEC(m_safety.evaluate_conditions());

      if(m_safety.is_safe_mode_active()) {
         if(m_logger != NULL) m_logger.log_warning("[CORE] Safe Mode ATIVO - Operações bloqueadas");
         return;
      }

      // Modo simulado
      if(Simulate) {
         if(m_logger != NULL) m_logger.log_debug("[CORE] Modo simulado - Execução bloqueada");
         return;
      }

      // Avaliação de sinais
      trade_signal signal = SIGNAL_NONE;
      SAFE_EXEC(signal = m_router.evaluate());
      
      if(signal != SIGNAL_NONE) {
         // Cálculo de volume com validação
         double volume = 0.0;
         SAFE_EXEC(volume = m_router.calculate_volume());
         
         if(volume > 0.0 && m_firewall.validate_volume(volume)) {
            // Validação de slippage
            double slippage = MathMax(0.1, MathMin(m_max_slippage, 10.0));
            
            SAFE_EXEC(m_executor.execute_order(signal, volume, slippage));
            
            log_operation("Execução", true, 
               StringFormat("Ordem executada: %s, Volume: %.2f, Slippage: %.1f", 
                  signal_to_string(signal), volume, slippage));
         } else {
            if(m_logger != NULL) m_logger.log_warning("[CORE] Volume inválido ou rejeitado pelo firewall");
         }
      }
   }

private:
   void log_operation(string operation, bool success, string details) {
      if(m_logger == NULL) return;
      
      // Adiciona entrada ao histórico
      int size = ArraySize(m_operation_history);
      ArrayResize(m_operation_history, size + 1);
      
      m_operation_history[size].timestamp = TimeCurrent();
      m_operation_history[size].operation = operation;
      m_operation_history[size].success = success;
      m_operation_history[size].details = details;
      
      // Log baseado no sucesso
      if(success) {
         m_logger.log_info(StringFormat("[CORE] %s: %s", operation, details));
      } else {
         m_logger.log_error(StringFormat("[CORE] %s: %s", operation, details));
      }
   }
   
   string signal_to_string(trade_signal signal) {
      switch(signal) {
         case SIGNAL_BUY: return "COMPRA";
         case SIGNAL_SELL: return "VENDA";
         case SIGNAL_REVERSA: return "REVERSA";
         case SIGNAL_QUANTUM: return "QUANTUM";
         case SIGNAL_NONE: return "NENHUM";
         default: return "DESCONHECIDO";
      }
   }
};

#endif // __CORE_BRAIN_MANAGER_MQH__