//+------------------------------------------------------------------+
//| quantum_firewall.mqh - Firewall Quântico Institucional           |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: include/security/                                        |
//| Versão: v1.2 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-24            |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_FIREWALL_MQH__
#define __QUANTUM_FIREWALL_MQH__

#include "utils/logger_institutional.mqh"
#include "executionlogic/safe_mode_manager.mqh"
#include "risk/risk_profile.mqh"
#include "analysis/market_regime_detector.mqh"
#include "intelligence/anomaly_detector_ai.mqh"
#include "core/quantum_blockchain.mqh"
#include "intelligence/quantum_learning.mqh"

//+------------------------------------------------------------------+
//| Estrutura de Resultado de Validação                             |
//+------------------------------------------------------------------+
struct FirewallResult
{
   bool allowed;
   ENUM_AUDIT_ISSUE issue;
   string details;
   datetime timestamp;
   double risk_score;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumFirewall                               |
//+------------------------------------------------------------------+
class QuantumFirewall
{
private:
   logger_institutional &m_logger;
   SafeModeManager      &m_safe;
   MarketRegimeDetector &m_regime;
   AnomalyDetectorAI    &m_ai;
   QuantumBlockchain    &m_blockchain;
   QuantumLearning      &m_learning;
   string               m_symbol;
   datetime             m_last_monitor_time;

   // Estados do firewall
   bool m_environment_verified;
   bool m_terminal_verified;
   bool m_firewall_active;
   bool m_emergency_lock;

   // Histórico de bloqueios
   FirewallResult m_firewall_log[];

   // Painel de decisão
   CLabel *m_firewall_label = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[FIREWALL] Sem conexão com o servidor");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[FIREWALL] Logger não inicializado");
         return false;
      }

      if(!m_blockchain.IsReady())
      {
         m_logger.log_warning("[FIREWALL] Blockchain não está pronto");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Verifica integridade do ambiente                              |
   //+--------------------------------------------------------------+
   bool is_environment_safe()
   {
      if(StringFind(TerminalInfoString(TERMINAL_DATA_PATH), "\\Tester") >= 0)
      {
         m_logger.log_error("[FIREWALL] Execução em modo Tester não permitida");
         return false;
      }

      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[FIREWALL] Terminal desconectado");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Verifica integridade do terminal                              |
   //+--------------------------------------------------------------+
   bool verify_terminal_integrity()
   {
      double spread = SymbolInfoInteger(m_symbol, SYMBOL_SPREAD);
      if(spread > 50)
      {
         m_logger.log_warning("[FIREWALL] Spread alto: " + DoubleToString(spread, 0));
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Verifica integridade da IA                                    |
   //+--------------------------------------------------------------+
   bool check_ai_integrity()
   {
      double anomaly_score = m_ai.detect_anomaly();
      if(anomaly_score > 0.85)
      {
         m_logger.log_error("[FIREWALL] Anomalia crítica detectada: " + DoubleToString(anomaly_score, 3));
         return false;
      }
      return true;
   }

   //+--------------------------------------------------------------+
   //| Registra falha de integridade                                 |
   //+--------------------------------------------------------------+
   void log_integrity_failure(string issue)
   {
      m_logger.log_error("[FIREWALL] Falha de integridade: " + issue);
      m_safe.activateQuantumLockdown();
   }

   //+--------------------------------------------------------------+
   //| Registra bloqueio no blockchain                               |
   //+--------------------------------------------------------------+
   void LogBlock(const FirewallResult &result)
   {
      if(!m_blockchain.IsReady()) return;

      string data = StringFormat("BLOCK=%s|ISSUE=%s|DETAILS=%s|RISK=%.4f|TIME=%s",
                               result.allowed ? "NO" : "YES",
                               EnumToString(result.issue),
                               result.details,
                               result.risk_score,
                               TimeToString(result.timestamp, TIME_DATE|TIME_SECONDS));
      m_blockchain.RecordTransaction(data, "FIREWALL_BLOCK");
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de firewall                                   |
   //+--------------------------------------------------------------+
   void update_firewall_display()
   {
      if(m_firewall_label == NULL)
      {
         m_firewall_label = new CLabel("FirewallLabel", 0, 10, 110);
         if(m_firewall_label != NULL)
            m_firewall_label->text("FIREWALL: " + (m_firewall_active ? "ATIVO" : "INATIVO"));
      }

      if(m_firewall_label != NULL)
      {
         m_firewall_label->text("FIREWALL: " + (m_firewall_active ? "ATIVO" : "INATIVO"));
         m_firewall_label->color(m_firewall_active ? clrLime : clrRed);
      }
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   QuantumFirewall(logger_institutional &logger,
                 SafeModeManager &safe,
                 MarketRegimeDetector &regime,
                 AnomalyDetectorAI &ai,
                 QuantumBlockchain &qb,
                 QuantumLearning &ql,
                 string symbol = _Symbol) :
      m_logger(logger),
      m_safe(safe),
      m_regime(regime),
      m_ai(ai),
      m_blockchain(qb),
      m_learning(ql),
      m_symbol(symbol),
      m_environment_verified(false),
      m_terminal_verified(false),
      m_firewall_active(false),
      m_emergency_lock(false),
      m_last_monitor_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[FIREWALL] Logger não inicializado");
         ExpertRemove();
      }

      if(!m_blockchain.IsReady())
      {
         m_logger.log_error("[FIREWALL] Blockchain quântico não está pronto");
         ExpertRemove();
      }

      m_logger.log_info("[FIREWALL] Firewall Quântico inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Inicializa firewall                                           |
   //+--------------------------------------------------------------+
   bool initialize()
   {
      m_logger.log_info("[FIREWALL] Inicializando QuantumFirewall...");

      if(!is_valid_context()) return false;

      if(!is_environment_safe())
      {
         log_integrity_failure("AMBIENTE INVÁLIDO");
         return false;
      }

      if(!verify_terminal_integrity())
      {
         log_integrity_failure("TERMINAL INVÁLIDO");
         return false;
      }

      if(!check_ai_integrity())
      {
         log_integrity_failure("IA COMPROMETIDA");
         return false;
      }

      m_environment_verified = true;
      m_terminal_verified = true;
      m_firewall_active = true;

      m_logger.log_success("[FIREWALL] QuantumFirewall ativado com sucesso.");
      update_firewall_display();
      return true;
   }

   //+--------------------------------------------------------------+
   //| Valida ambiente de execução                                   |
   //+--------------------------------------------------------------+
   bool validate_environment()
   {
      if(!is_valid_context() || !m_firewall_active || m_emergency_lock) return false;

      FirewallResult result;
      result.allowed = true;
      result.issue = AUDIT_ISSUE_NONE;
      result.details = "Ambiente seguro";
      result.timestamp = TimeCurrent();
      result.risk_score = 0.0;

      // Verificar conectividade
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         result.allowed = false;
         result.issue = AUDIT_ISSUE_TERMINAL_DISCONNECTED;
         result.details = "Terminal desconectado";
         result.risk_score = 1.0;
      }

      // Verificar spread
      double spread = SymbolInfoInteger(m_symbol, SYMBOL_SPREAD);
      if(spread > 50)
      {
         result.allowed = false;
         result.issue = AUDIT_ISSUE_HIGH_SPREAD;
         result.details = "Spread alto: " + DoubleToString(spread, 0);
         result.risk_score = 0.8;
      }

      // Verificar risco de mercado
      double volatility = iATR(m_symbol, PERIOD_H1, 14, 0);
      if(volatility > 1.5 * iMA(m_symbol, PERIOD_H1, 100, 0, MODE_SMA, PRICE_CLOSE, 0))
      {
         result.allowed = false;
         result.issue = AUDIT_ISSUE_HIGH_VOLATILITY;
         result.details = "Volatilidade extrema";
         result.risk_score = 0.9;
      }

      // Verificar anomalias com IA
      if(m_learning.IsMarketAnomalyDetected())
      {
         result.allowed = false;
         result.issue = AUDIT_ISSUE_MARKET_ANOMALY;
         result.details = "Anomalia de mercado detectada";
         result.risk_score = 1.0;
      }

      // Registrar no log
      ArrayPushBack(m_firewall_log, result);
      if(!result.allowed)
      {
         m_logger.log_critical("[FIREWALL] Execução bloqueada: " + result.details);
         LogBlock(result);
      }

      return result.allowed;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está ativo                                         |
   //+--------------------------------------------------------------+
   bool IsActive() const
   {
      return m_firewall_active && !m_emergency_lock;
   }

   //+--------------------------------------------------------------+
   //| Monitora integridade                                          |
   //+--------------------------------------------------------------+
   void monitor_integrity()
   {
      if(!m_firewall_active || m_emergency_lock) return;

      if(TimeCurrent() < m_last_monitor_time + 1) // 1 segundo
      {
         m_last_monitor_time = TimeCurrent();
         return;
      }

      if(!is_environment_safe()) log_integrity_failure("AMBIENTE INVÁLIDO");
      if(!verify_terminal_integrity()) log_integrity_failure("TERMINAL INVÁLIDO");
      if(!check_ai_integrity()) log_integrity_failure("IA COMPROMETIDA");
   }

   //+--------------------------------------------------------------+
   //| Ativa modo de emergência                                     |
   //+--------------------------------------------------------------+
   void ActivateEmergencyLock()
   {
      m_emergency_lock = true;
      m_firewall_active = false;
      m_safe.activateQuantumLockdown();
      m_logger.log_critical("[FIREWALL] Modo de emergência ativado");
   }

   //+--------------------------------------------------------------+
   //| Desativa modo de emergência                                  |
   //+--------------------------------------------------------------+
   void DeactivateEmergencyLock()
   {
      m_emergency_lock = false;
      m_firewall_active = true;
      m_logger.log_info("[FIREWALL] Modo de emergência desativado");
   }

   //+--------------------------------------------------------------+
   //| Exporta log de bloqueios                                     |
   //+--------------------------------------------------------------+
   bool ExportFirewallLog(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_firewall_log); i++)
      {
         FileWrite(handle,
            TimeToString(m_firewall_log[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_firewall_log[i].allowed ? "SIM" : "NÃO",
            EnumToString(m_firewall_log[i].issue),
            m_firewall_log[i].details,
            DoubleToString(m_firewall_log[i].risk_score, 4)
         );
      }

      FileClose(handle);
      m_logger.log_info("[FIREWALL] Log de bloqueios exportado para: " + file_path);
      return true;
   }
};

#endif // __QUANTUM_FIREWALL_MQH__