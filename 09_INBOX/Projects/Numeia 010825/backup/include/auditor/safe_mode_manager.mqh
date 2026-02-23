// ============================================================================
// ID: include/executionlogic
// Name: safe_mode_manager.mqh
// Projeto: QuantumOmegaGodMode
// Versão: v1.0
// Função: Gerenciar modo seguro com base em condições críticas de risco
// Criado em: 2025-07-13
// Classificação: TIER-0 | Segurança Operacional Institucional
// ============================================================================

#ifndef __SAFE_MODE_MANAGER_MQH__
#define __SAFE_MODE_MANAGER_MQH__

#include "../../utils/logger_institutional.mqh"

class safe_mode_manager
{
private:
   logger_institutional &m_logger;
   bool safe_mode;

public:
   safe_mode_manager(logger_institutional &logger)
      : m_logger(logger), safe_mode(false) {}

   void initialize()
   {
      m_logger.log_info("[safe_mode_manager] Inicializando monitoramento de segurança.");
   }

   void evaluate_conditions()
   {
      RefreshRates();

      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_warning("[safe_mode_manager] Desconectado do broker.");
         safe_mode = true;
         return;
      }

      double spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(spread > 50)
      {
         m_logger.log_warning("[safe_mode_manager] Spread crítico detectado: " + DoubleToString(spread));
         safe_mode = true;
         return;
      }

      // Placeholder para drawdown futuro
      // double drawdown = CalculateDrawdown();
      // if(drawdown > 5.0) { safe_mode = true; }

      safe_mode = false;
   }

   bool is_safe_mode_active()
   {
      return safe_mode;
   }

   string get_safe_status()
   {
      return safe_mode ? "ACTIVATED" : "NORMAL";
   }
};

#endif // __SAFE_MODE_MANAGER_MQH__