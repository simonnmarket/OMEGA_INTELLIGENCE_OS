// ============================================================================
// ID: include/decisionengine
// Name: decision_router.mqh
// Projeto: QuantumOmegaGodMode
// Versão: v2.2 Integrado com IA (strategy_quantum_neural)
// Função: Roteamento de decisão com fallback neural adaptativo
// Atualizado em: 2025-07-13
// Classificação: TIER-0 | Inteligência Modular + Logger + Neural Strategy
// ============================================================================

#ifndef __DECISION_ROUTER_MQH__
#define __DECISION_ROUTER_MQH__

#include "../../types/trade_signal_enum.mqh"
#include "../../utils/logger_institutional.mqh"
#include "signal_validator.mqh"
#include "strategy_quantum_neural.mqh"

class decision_router {
private:
   logger_institutional   &m_logger;
   signal_validator       m_validator;
   strategy_quantum_neural m_strategy;

public:
   decision_router(logger_institutional &logger)
      : m_logger(logger), m_strategy(logger) {}

   void initialize() {
      m_logger.log_info("[decision_router] Inicializado com estratégia neural.");
      m_strategy.initialize();
   }

   trade_signal evaluate() {
      if(!m_validator.validate_signal()) {
         m_logger.log_warning("[decision_router] Sinal invalidado pelos filtros.");
         return SIGNAL_NONE;
      }

      trade_signal signal = m_strategy.evaluate();
      return signal;
   }
};

#endif // __DECISION_ROUTER_MQH__