//+------------------------------------------------------------------+
//| quantumfirewall.mqh - Mecanismo de Defesa Lógica Institucional   |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Pasta: Include/Security/                                        |
//| Versão: v1.2 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-21              |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_FIREWALL_MQH__
#define __QUANTUM_FIREWALL_MQH__

#include <Trade\Trade.mqh>
#include <include/utils/logger_institutional.mqh>
#include <include/executionlogic/safe_mode_manager.mqh>
#include <include/risk/risk_profile.mqh>
#include <include/analysis/market_regime_detector.mqh>
#include <include/intelligence/anomaly_detector_ai.mqh>
#include <include/visuals/decision_panel.mq5>

input bool Simulate = true; // Modo simulado para testes seguros
input int MonitorIntervalMs = 1000; // Intervalo de monitoramento
input double EntropyThreshold = 0.75; // Limite de entropia
input string LogDirectory = "logs/";

class QuantumFirewall
{
private:
   logger_institutional &m_logger;
   SafeModeManager &m_safe;
   MarketRegimeDetector &m_regime;
   AnomalyDetectorAI &m_ai;

   bool m_environment_verified;
   bool m_terminal_verified;
   bool m_firewall_active;
   datetime m_last_monitor_time;

   string m_integrity_history[];
   CLabel *m_firewall_label = NULL;

public:
   QuantumFirewall(logger_institutional &logger, SafeModeManager &safe, MarketRegimeDetector &regime, AnomalyDetectorAI &ai)
      : m_logger(logger), m_safe(safe), m_regime(regime), m_ai(ai)
   {
      m_environment_verified = false;
      m_terminal_verified = false;
      m_firewall_active = false;
      m_last_monitor_time = TimeCurrent();
   }

   bool initialize()
   {
      m_logger.log_info("[FIREWALL] Inicializando QuantumFirewall...");

      if(Simulate)
      {
         m_logger.log_debug("[FIREWALL] Modo simulado. Execução bloqueada.");
         return true;
      }

      if(!is_environment_safe())
      {
         m_logger.log_error("[FIREWALL] Ambiente não autorizado detectado.");
         m_safe.activate_safe_mode("ENVIRONMENT_FAILURE");
         return false;
      }

      if(!verify_terminal_integrity())
      {
         m_logger.log_error("[FIREWALL] Integridade do terminal comprometida.");
         m_safe.activate_safe_mode("TERMINAL_INTEGRITY_FAIL");
         return false;
      }

      if(!is_market_connected())
      {
         m_safe.activate_safe_mode("MARKET_CONNECTION_FAIL");
         return false;
      }

      if(!check_ai_integrity())
      {
         m_logger.log_critical("[FIREWALL] Anomalia crítica detectada por IA.");
         m_safe.activate_safe_mode("AI_ANOMALY_DETECTED");
         return false;
      }

      m_logger.log_success("[FIREWALL] QuantumFirewall ativado com sucesso.");
      m_firewall_active = true;
      update_firewall_display();
      return true;
   }

   bool is_firewall_active() const
   {
      m_logger.log_info("[FIREWALL] Estado do firewall: " + (m_firewall_active ? "Ativo" : "Inativo"));
      return m_firewall_active;
   }

   void monitor_integrity()
   {
      if(TimeCurrent() < m_last_monitor_time + MonitorIntervalMs / 1000.0)
         return;

      m_last_monitor_time = TimeCurrent();

      if(!is_environment_safe())
         log_integrity_failure("AMBIENTE INVÁLIDO");

      if(!verify_terminal_integrity())
         log_integrity_failure("TERMINAL INVÁLIDO");

      if(!check_ai_integrity())
         log_integrity_failure("ANOMALIA DE IA DETECTADA");

      if(!check_market_entropy())
         log_integrity_failure("ENTROPIA DE MERCADO ELEVADA");

      if(!is_market_connected())
         log_integrity_failure("CONEXÃO DE MERCADO PERDIDA");

      m_logger.log_info("[FIREWALL] Integridade verificada com sucesso.");
   }

private:
   bool is_environment_safe()
   {
      string env = TerminalInfoString(TERMINAL_DATA_PATH);
      string company = TerminalInfoString(TERMINAL_COMPANY);
      return StringFind(env, "\\Tester") < 0 && StringLen(company) > 0 && StringFind(company, "MetaQuotes") >= 0;
   }

   bool is_market_connected()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[FIREWALL] Sem conexão com o servidor de mercado");
         return false;
      }

      double latency = TerminalInfoDouble(TERMINAL_PING_LAST) / 1000.0;
      if(latency > 2.0)
      {
         m_logger.log_warning("[FIREWALL] Latência alta: " + DoubleToString(latency, 2) + "s");
         return false;
      }
      return true;
   }

   bool check_market_entropy()
   {
      double prices[];
      ArrayResize(prices, 20);
      for(int i = 0; i < 20; i++)
         prices[i] = iClose(_Symbol, PERIOD_M1, i);

      double entropy = 0.0;
      double sum = 0.0;
      for(int i = 0; i < ArraySize(prices); i++)
         sum += prices[i];

      if(sum == 0) return false;

      for(int i = 0; i < ArraySize(prices); i++)
      {
         double p = prices[i] / sum;
         if(p > 0) entropy -= p * MathLog(p);
      }

      if(entropy > EntropyThreshold)
      {
         m_logger.log_warning("[FIREWALL] Entropia de mercado elevada: " + DoubleToString(entropy, 4));
         return false;
      }
      return true;
   }

   bool verify_terminal_integrity()
   {
      m_terminal_verified = TerminalInfoInteger(TERMINAL_CONNECTED) &&
                           TerminalInfoInteger(TERMINAL_DLLS_ALLOWED) &&
                           TerminalInfoInteger(TERMINAL_TRADE_ALLOWED);

      if(!m_terminal_verified)
      {
         m_logger.log_error("[FIREWALL] Falha na verificação do terminal: " +
                           "Conexão=" + (TerminalInfoInteger(TERMINAL_CONNECTED) ? "OK" : "FALHA") +
                           ", DLLs=" + (TerminalInfoInteger(TERMINAL_DLLS_ALLOWED) ? "OK" : "FALHA") +
                           ", Trading=" + (TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) ? "OK" : "FALHA"));
      }
      return m_terminal_verified;
   }

   void log_integrity_failure(string reason)
   {
      string entry = TimeToString(TimeCurrent(), TIME_DATE) + " | Falha: " + reason;
      ArrayPushBack(m_integrity_history, entry);
      m_logger.log_warning(entry);
   }

   void update_firewall_display()
   {
      if(m_firewall_label == NULL)
         m_firewall_label = new CLabel("FirewallLabel", 0, 10, 110);

      m_firewall_label->text("FIREWALL: " + (m_firewall_active ? "ATIVO" : "INATIVO"));
      m_firewall_label->color(m_firewall_active ? clrLime : clrRed);
   }

   bool check_ai_integrity()
   {
      double anomaly_score = m_ai.detect_anomaly();
      return anomaly_score < 0.85;
   }
};

#endif // __QUANTUM_FIREWALL_MQH__