//+------------------------------------------------------------------+
//| Agent_Omega v3.0 - Supervisor TIER-0 com Correção Automatizada   |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//+------------------------------------------------------------------+
#ifndef __AGENT_OMEGA_V3_0_MQH__
#define __AGENT_OMEGA_V3_0_MQH__

#include "utils/logger_institutional.mqh"
#include "security/QuantumBlockchain.mqh"
#include "analysis/dependency_graph.mqh"

//+------------------------------------------------------------------+
//| Estrutura de Correção Avançada                                   |
//+------------------------------------------------------------------+
struct AutoFixResult
{
   string file;
   string issue;
   string fix_applied;
   bool success;
   datetime timestamp;
   double resolution_time;
   string error_details;
};

struct SystemMetrics
{
   int total_files;
   int total_dependencies;
   int errors_fixed;
   int warnings_resolved;
   double system_health;
   datetime last_scan;
};

class AgentOmega
{
private:
   logger_institutional &m_logger;
   QuantumBlockchain    &m_blockchain;
   CDependencyGraph     &m_dependency_graph;
   string               m_symbol;
   AutoFixResult        m_fix_history[];
   SystemMetrics        m_metrics;
   bool                 m_auto_correction_enabled;
   int                  m_correction_interval;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[OMEGA] Sem conexão com o servidor");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[OMEGA] Logger não inicializado");
         return false;
      }

      if(!m_blockchain.IsReady())
      {
         m_logger.log_warning("[OMEGA] Blockchain não está pronto");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Corrige caminho de include                                    |
   //+--------------------------------------------------------------+
   bool FixIncludePath(string &file_content, string target_include, string corrected_path)
   {
      string pattern = "#include "" + target_include + """;
      string replacement = "#include "" + corrected_path + """;
      
      int pos = StringFind(file_content, pattern);
      if(pos >= 0)
      {
         StringReplace(file_content, pattern, replacement);
         return true;
      }
      
      pattern = "#include \"" + target_include + "\"";
      replacement = "#include \"" + corrected_path + "\"";
      pos = StringFind(file_content, pattern);
      if(pos >= 0)
      {
         StringReplace(file_content, pattern, replacement);
         return true;
      }
      
      return false;
   }

   //+--------------------------------------------------------------+
   //| Registra correção no histórico                                |
   //+--------------------------------------------------------------+
   void LogFix(string file, string issue, string fix, bool success, double resolution_time = 0.0, string error_details = "")
   {
      AutoFixResult result;
      result.file = file;
      result.issue = issue;
      result.fix_applied = fix;
      result.success = success;
      result.timestamp = TimeCurrent();
      result.resolution_time = resolution_time;
      result.error_details = error_details;
      
      ArrayPushBack(m_fix_history, result);
      
      // Atualizar métricas
      if(success)
      {
         m_metrics.errors_fixed++;
         m_logger.log_info("[OMEGA] Correção aplicada: " + fix);
      }
      else
      {
         m_logger.log_error("[OMEGA] Falha na correção: " + fix);
      }
      
      // Registrar no blockchain
      string data = StringFormat("FIX=%s|FILE=%s|ISSUE=%s|SUCCESS=%s|TIME=%s|RESOLUTION_TIME=%.2f",
                               fix,
                               file,
                               issue,
                               success ? "YES" : "NO",
                               TimeToString(result.timestamp, TIME_DATE|TIME_SECONDS),
                               resolution_time);
      m_blockchain.RecordTransaction(data, "AUTO_FIX");
   }

   //+--------------------------------------------------------------+
   //| Calcula métricas do sistema                                   |
   //+--------------------------------------------------------------+
   void CalculateSystemMetrics()
   {
      m_metrics.total_files = ArraySize(m_fix_history);
      m_metrics.total_dependencies = 0; // Será calculado pelo dependency_graph
      m_metrics.last_scan = TimeCurrent();
      
      // Calcular saúde do sistema
      int successful_fixes = 0;
      for(int i = 0; i < ArraySize(m_fix_history); i++)
      {
         if(m_fix_history[i].success)
            successful_fixes++;
      }
      
      m_metrics.system_health = ArraySize(m_fix_history) > 0 ? 
                               (double)successful_fixes / ArraySize(m_fix_history) * 100.0 : 100.0;
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   AgentOmega(logger_institutional &logger,
             QuantumBlockchain &qb,
             CDependencyGraph &dg,
             string symbol = _Symbol,
             bool auto_correction = true,
             int correction_interval = 5) :
      m_logger(logger),
      m_blockchain(qb),
      m_dependency_graph(dg),
      m_symbol(symbol),
      m_auto_correction_enabled(auto_correction),
      m_correction_interval(correction_interval)
   {
      ArrayInitialize(m_fix_history, 0);
      m_metrics.total_files = 0;
      m_metrics.total_dependencies = 0;
      m_metrics.errors_fixed = 0;
      m_metrics.warnings_resolved = 0;
      m_metrics.system_health = 100.0;
      m_metrics.last_scan = TimeCurrent();
      
      m_logger.log_info("[OMEGA] Supervisor TIER-0 v3.0 ativado");
   }

   //+--------------------------------------------------------------+
   //| Executa correção automática                                  |
   //+--------------------------------------------------------------+
   bool RunAutoFix()
   {
      if(!is_valid_context()) return false;

      datetime start_time = TimeCurrent();
      m_logger.log_info("[OMEGA] Iniciando correção automática...");
      
      // 1. Escaneia dependências
      m_dependency_graph.ScanProjectStructure();
      
      // 2. Detecta includes faltantes
      string missing_includes[];
      if(m_dependency_graph.FindMissingIncludes(missing_includes))
      {
         for(int i = 0; i < ArraySize(missing_includes); i++)
         {
            string include = missing_includes[i];
            string corrected = CorrectIncludePath(include);
            
            if(corrected != include)
            {
               // Tenta corrigir no arquivo
               string file_path = m_dependency_graph.GetFileContainingInclude(include);
               if(StringLen(file_path) > 0)
               {
                  string content;
                  if(FileReadToString(file_path, content))
                  {
                     datetime fix_start = TimeCurrent();
                     if(FixIncludePath(content, include, corrected))
                     {
                        // Salva arquivo corrigido
                        if(FileWriteFromString(file_path, content))
                        {
                           double resolution_time = (TimeCurrent() - fix_start) / 1000.0;
                           LogFix(file_path, "INCLUDE_NOT_FOUND", "CORRECTED_PATH=" + corrected, true, resolution_time);
                           m_logger.log_success("[OMEGA] Include corrigido: " + include + " → " + corrected);
                        }
                        else
                        {
                           double resolution_time = (TimeCurrent() - fix_start) / 1000.0;
                           LogFix(file_path, "INCLUDE_NOT_FOUND", "CORRECTED_PATH=" + corrected, false, resolution_time, "Falha ao salvar arquivo");
                        }
                     }
                  }
               }
            }
         }
      }
      
      // 3. Valida segurança
      if(!m_dependency_graph.ValidateSecurityCompliance())
      {
         m_logger.log_error("[OMEGA] Falha na auditoria de segurança");
         return false;
      }
      
      // 4. Calcula métricas
      CalculateSystemMetrics();
      
      double total_time = (TimeCurrent() - start_time) / 1000.0;
      m_logger.log_success(StringFormat("[OMEGA] Correção automática concluída em %.2f segundos", total_time));
      return true;
   }

   //+--------------------------------------------------------------+
   //| Corrige caminho de include                                    |
   //+--------------------------------------------------------------+
   string CorrectIncludePath(string include_path)
   {
      // Regras de correção avançadas
      if(StringFind(include_path, "utils/") >= 0 && StringFind(include_path, "include/") == -1)
         return "include/" + include_path;
         
      if(StringFind(include_path, "security/") >= 0 && StringFind(include_path, "include/") == -1)
         return "include/" + include_path;
         
      if(StringFind(include_path, "intelligence/") >= 0 && StringFind(include_path, "include/") == -1)
         return "include/" + include_path;
         
      if(StringFind(include_path, "CORE/") >= 0)
         return "CORE/" + StringSubstr(include_path, StringFind(include_path, "CORE/") + 5);
         
      if(StringFind(include_path, "AUDITOR/") >= 0)
         return "AUDITOR/" + StringSubstr(include_path, StringFind(include_path, "AUDITOR/") + 8);
         
      if(StringFind(include_path, "EXPERT/") >= 0)
         return "EXPERT/" + StringSubstr(include_path, StringFind(include_path, "EXPERT/") + 7);
         
      return include_path;
   }

   //+--------------------------------------------------------------+
   //| Gera relatório quântico                                      |
   //+--------------------------------------------------------------+
   void GenerateQuantumReport()
   {
      string report = "=== RELATÓRIO QUÂNTICO DE CORREÇÃO v3.0 ===\n";
      report += "Data: " + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\n";
      report += "Status: " + (ArraySize(m_fix_history) > 0 ? "CORREÇÕES APLICADAS" : "SEM CORREÇÕES") + "\n";
      report += "Correções: " + IntegerToString(ArraySize(m_fix_history)) + "\n";
      report += "Saúde do Sistema: " + DoubleToString(m_metrics.system_health, 2) + "%\n";
      report += "Erros Corrigidos: " + IntegerToString(m_metrics.errors_fixed) + "\n";
      report += "Avisos Resolvidos: " + IntegerToString(m_metrics.warnings_resolved) + "\n";
      
      for(int i = 0; i < ArraySize(m_fix_history); i++)
      {
         report += StringFormat("Arquivo: %s | Problema: %s | Correção: %s | Sucesso: %s | Tempo: %.2fs\n",
                              m_fix_history[i].file,
                              m_fix_history[i].issue,
                              m_fix_history[i].fix_applied,
                              m_fix_history[i].success ? "SIM" : "NÃO",
                              m_fix_history[i].resolution_time);
      }
      
      int handle = FileOpen("MQL5/LOGS/quantum_fix_report_" + TimeToString(TimeCurrent(), "yyyymmdd") + ".txt", FILE_WRITE|FILE_TXT);
      if(handle != INVALID_HANDLE)
      {
         FileWrite(handle, report);
         FileClose(handle);
         m_logger.log_info("[OMEGA] Relatório quântico de correção gerado");
      }
   }

   //+--------------------------------------------------------------+
   //| Retorna histórico de correções                                |
   //+--------------------------------------------------------------+
   AutoFixResult[] GetFixHistory() const
   {
      return m_fix_history;
   }

   //+--------------------------------------------------------------+
   //| Retorna métricas do sistema                                   |
   //+--------------------------------------------------------------+
   SystemMetrics GetSystemMetrics() const
   {
      return m_metrics;
   }

   //+--------------------------------------------------------------+
   //| Ativa/desativa correção automática                            |
   //+--------------------------------------------------------------+
   void SetAutoCorrection(bool enabled)
   {
      m_auto_correction_enabled = enabled;
      m_logger.log_info(StringFormat("[OMEGA] Correção automática %s", enabled ? "ativada" : "desativada"));
   }

   //+--------------------------------------------------------------+
   //| Define intervalo de correção                                  |
   //+--------------------------------------------------------------+
   void SetCorrectionInterval(int interval)
   {
      m_correction_interval = interval;
      m_logger.log_info(StringFormat("[OMEGA] Intervalo de correção definido para %d segundos", interval));
   }
};

#endif // __AGENT_OMEGA_V3_0_MQH__ 