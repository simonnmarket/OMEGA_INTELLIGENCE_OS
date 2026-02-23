// ============================================================================
// ID: core
// Name: core_brain_manager.mqh
// Projeto: QuantumOmegaGodMode
// Versão: v2.1
// Função: Núcleo central de controle com Safe Mode
// Atualizado em: 2025-07-13
// Classificação: TIER-0 | Blindado + SafeMode
// ============================================================================

#ifndef __CORE_BRAIN_MANAGER_MQH__
#define __CORE_BRAIN_MANAGER_MQH__

#include "../include/decisionengine/decision_router.mqh"
#include "../include/executionlogic/safe_mode_manager.mqh"
#include "../include/executionlogic/trade_executor.mqh"
#include "../types/trade_signal_enum.mqh"
#include "../utils/logger_institutional.mqh"

class core_brain_manager {
private:
   decision_router       &m_router;
   trade_executor        &m_executor;
   safe_mode_manager     &m_safety;
   logger_institutional  &m_logger;

public:
   core_brain_manager(
      decision_router &router,
      trade_executor &executor,
      safe_mode_manager &safety,
      logger_institutional &logger
   )
   : m_router(router), m_executor(executor), m_safety(safety), m_logger(logger) {}

   void initialize() {
      m_logger.log_info("[core_brain_manager] Inicializando módulos...");
      m_router.initialize();
      m_executor.initialize();
      m_safety.initialize();
   }

   void on_tick() {
      m_safety.evaluate_conditions();

      if(m_safety.is_safe_mode_active()) {
         m_logger.log_warning("[core_brain_manager] Safe Mode ATIVO - execução bloqueada.");
         return;
      }

      trade_signal signal = m_router.evaluate();
      if(signal == SIGNAL_BUY || signal == SIGNAL_SELL) {
         double volume = 1.0;
         if(volume > 0.0) {
            m_executor.execute_order(signal, volume);
         } else {
            m_logger.log_error("[core_brain_manager] Volume inválido.");
         }
      }
   }
};

#endif // __CORE_BRAIN_MANAGER_MQH__