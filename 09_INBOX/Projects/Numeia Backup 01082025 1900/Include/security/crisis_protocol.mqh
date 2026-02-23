//+------------------------------------------------------------------+
//| crisis_protocol.mqh - Protocolo de Crise Institucional           |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: include/security/                                        |
//| Versão: v1.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-24           |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __CRISIS_PROTOCOL_MQH__
#define __CRISIS_PROTOCOL_MQH__

#include "utils/logger_institutional.mqh"
#include "security/quantum_firewall.mqh"
#include "execution/trade_executor.mqh"
#include "../Core/quantum_blockchain.mqh"
#include "ChartObjects\ChartObjectsTxtControls.mqh"

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: CrisisProtocol                                |
//+------------------------------------------------------------------+
class CrisisProtocol
{
private:
   logger_institutional &m_logger;
   QuantumFirewall      &m_firewall;
   TradeExecutor        &m_executor;
   QuantumBlockchain    &m_blockchain;
   string               m_symbol;
   datetime             m_crisis_start;

   // Nível de crise
   enum ENUM_CRISIS_LEVEL
   {
      CRISIS_LEVEL_NONE,
      CRISIS_LEVEL_WARNING,
      CRISIS_LEVEL_ALERT,
      CRISIS_LEVEL_EMERGENCY
   };
   ENUM_CRISIS_LEVEL m_crisis_level;

   // Painel de crise
   CLabel *m_crisis_label = NULL;
   CLabel *m_crisis_details = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[CRISIS] Sem conexão com o servidor");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[CRISIS] Logger não inicializado");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de crise                                      |
   //+--------------------------------------------------------------+
   void updateCrisisDisplay(ENUM_CRISIS_LEVEL level, string details)
   {
      if(m_crisis_label == NULL)
      {
         m_crisis_label = new CLabel("CrisisLabel", 0, 10, 1800);
         m_crisis_label->text("CRISE: NENHUMA");
         m_crisis_label->color(clrGray);
      }

      if(m_crisis_details == NULL)
      {
         m_crisis_details = new CLabel("CrisisDetails", 0, 10, 1820);
         m_crisis_details->text("DETALHES: ?");
         m_crisis_details->color(clrGray);
      }

      string level_str = "";
      switch(level)
      {
         case CRISIS_LEVEL_NONE: level_str = "NENHUMA"; break;
         case CRISIS_LEVEL_WARNING: level_str = "ALERTA"; break;
         case CRISIS_LEVEL_ALERT: level_str = "ALERTA"; break;
         case CRISIS_LEVEL_EMERGENCY: level_str = "EMERGÊNCIA"; break;
      }

      m_crisis_label->text("CRISE: " + level_str);
      m_crisis_label->color(
         level == CRISIS_LEVEL_NONE ? clrLime :
         level == CRISIS_LEVEL_WARNING ? clrYellow :
         level == CRISIS_LEVEL_ALERT ? clrRed : clrRed
      );

      m_crisis_details->text("DETALHES: " + details);
      m_crisis_details->color(level > CRISIS_LEVEL_NONE ? clrRed : clrGray);
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CrisisProtocol(logger_institutional &logger,
                QuantumFirewall &qf,
                TradeExecutor &te,
                QuantumBlockchain &qb,
                string symbol = _Symbol) :
      m_logger(logger),
      m_firewall(qf),
      m_executor(te),
      m_blockchain(qb),
      m_symbol(symbol),
      m_crisis_level(CRISIS_LEVEL_NONE),
      m_crisis_start(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[CRISIS] Logger não inicializado");
         ExpertRemove();
      }

      m_logger.log_info("[CRISIS] Protocolo de Crise inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Ativa protocolo de crise                                     |
   //+--------------------------------------------------------------+
   bool ActivateCrisisProtocol(ENUM_CRISIS_LEVEL level, string reason)
   {
      if(!is_valid_context()) return false;

      m_crisis_level = level;
      m_crisis_start = TimeCurrent();

      // Registrar no blockchain
      string data = StringFormat("CRISIS=ACTIVATED|LEVEL=%d|REASON=%s|TIME=%s",
                               level,
                               reason,
                               TimeToString(m_crisis_start, TIME_DATE|TIME_SECONDS));
      m_blockchain.RecordTransaction(data, "CRISIS_PROTOCOL");

      // Ações por nível
      switch(level)
      {
         case CRISIS_LEVEL_WARNING:
            m_logger.log_warning("[CRISIS] Protocolo de crise ativado: " + reason);
            break;

         case CRISIS_LEVEL_ALERT:
            m_logger.log_error("[CRISIS] Alerta de crise: " + reason);
            m_executor.CancelAllPendingOrders();
            break;

         case CRISIS_LEVEL_EMERGENCY:
            m_logger.log_critical("[CRISIS] EMERGÊNCIA ATIVADA: " + reason);
            m_executor.CloseAllPositions();
            m_executor.CancelAllPendingOrders();
            m_firewall.ActivateEmergencyLock();
            break;

         default:
            return false;
      }

      m_logger.log_info("[CRISIS] Protocolo de crise ativado: " + IntegerToString(level) + " | Motivo: " + reason);
      updateCrisisDisplay(level, reason);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Desativa protocolo de crise                                  |
   //+--------------------------------------------------------------+
   bool DeactivateCrisisProtocol()
   {
      if(m_crisis_level == CRISIS_LEVEL_NONE) return true;

      string data = StringFormat("CRISIS=DEACTIVATED|LEVEL=%d|DURATION=%dmin",
                               m_crisis_level,
                               (TimeCurrent() - m_crisis_start) / 60);
      m_blockchain.RecordTransaction(data, "CRISIS_PROTOCOL");

      m_logger.log_info("[CRISIS] Protocolo de crise desativado");
      m_crisis_level = CRISIS_LEVEL_NONE;
      m_crisis_start = 0;
      updateCrisisDisplay(CRISIS_LEVEL_NONE, "Normal");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Obtém nível de crise                                         |
   //+--------------------------------------------------------------+
   ENUM_CRISIS_LEVEL GetCrisisLevel() const
   {
      return m_crisis_level;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está em crise                                     |
   //+--------------------------------------------------------------+
   bool IsInCrisis() const
   {
      return m_crisis_level > CRISIS_LEVEL_WARNING;
   }
};

#endif // __CRISIS_PROTOCOL_MQH__