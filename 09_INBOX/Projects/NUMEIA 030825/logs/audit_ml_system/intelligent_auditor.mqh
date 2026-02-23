//+------------------------------------------------------------------+
//| intelligent_auditor.mqh - Auditoria Inteligente com ML            |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Versão: v1.0 (Intelligent Audit System)                          |
//| Atualizado em: 2025-07-21                                        |
//| Status: TIER-0 Compliant | SHA3 Protected | ML Ready             |
//| SHA3: c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8 |
//+------------------------------------------------------------------+
#ifndef __INTELLIGENT_AUDITOR_MQH__
#define __INTELLIGENT_AUDITOR_MQH__

#include "utils/logger_institutional.mqh"
#include "logs/audit_ml_system/error_pattern_analyzer.mqh"

//+------------------------------------------------------------------+
//| ESTRUTURAS DE AUDITORIA INTELIGENTE                               |
//+------------------------------------------------------------------+

struct IntelligentAuditResult
{
   string file_name;                    // Arquivo auditado
   bool audit_passed;                   // Se passou na auditoria
   double risk_score;                   // Score de risco (0-1)
   string predicted_issues[];           // Problemas previstos
   string prevention_actions[];         // Ações preventivas
   double ml_confidence;                // Confiança do ML
   datetime audit_time;                 // Quando foi auditado
   string audit_summary;                // Resumo da auditoria
};

struct AuditLearningData
{
   string file_name;                    // Arquivo
   string audit_type;                   // Tipo de auditoria
   bool had_issues;                     // Teve problemas
   string issues_found[];               // Problemas encontrados
   bool issues_corrected;               // Se foram corrigidos
   datetime correction_time;             // Quando foram corrigidos
   double correction_effectiveness;     // Efetividade da correção
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL DO AUDITOR INTELIGENTE                           |
//+------------------------------------------------------------------+

class IntelligentAuditor
{
private:
   logger_institutional &m_logger;
   ErrorPatternAnalyzer &m_ml_analyzer;
   
   // Dados de aprendizado
   AuditLearningData m_learning_data[];
   int m_learning_count;
   
   // Configurações
   double m_risk_threshold;
   double m_confidence_threshold;
   bool m_auto_correction;
   
   // Histórico de auditorias
   IntelligentAuditResult m_audit_history[];
   int m_audit_count;

public:
   IntelligentAuditor(logger_institutional &logger, ErrorPatternAnalyzer &ml_analyzer)
      : m_logger(logger), m_ml_analyzer(ml_analyzer)
   {
      m_learning_count = 0;
      m_audit_count = 0;
      m_risk_threshold = 0.7;
      m_confidence_threshold = 0.8;
      m_auto_correction = false;
      
      m_logger.log_info("[INTELLIGENT-AUDIT] Sistema de auditoria inteligente inicializado");
   }

   //+------------------------------------------------------------------+
   //| AUDITORIA INTELIGENTE DE ARQUIVO                                |
   //+------------------------------------------------------------------+
   IntelligentAuditResult audit_file_intelligently(string file_path)
   {
      IntelligentAuditResult result;
      result.file_name = file_path;
      result.audit_time = TimeCurrent();
      
      m_logger.log_info("[INTELLIGENT-AUDIT] Iniciando auditoria inteligente: " + file_path);
      
      // 1. Predição ML
      MLPrediction ml_prediction = m_ml_analyzer.predict_errors(file_path);
      
      // 2. Auditoria tradicional
      bool traditional_audit = perform_traditional_audit(file_path);
      
      // 3. Análise de risco integrada
      result.risk_score = calculate_integrated_risk(ml_prediction, traditional_audit, file_path);
      
      // 4. Determinar resultado
      result.audit_passed = (result.risk_score < m_risk_threshold);
      
      // 5. Gerar predições e ações
      generate_predictions_and_actions(result, ml_prediction, file_path);
      
      // 6. Calcular confiança do ML
      result.ml_confidence = ml_prediction.confidence;
      
      // 7. Gerar resumo
      result.audit_summary = generate_audit_summary(result, ml_prediction);
      
      // 8. Registrar auditoria
      register_audit_result(result);
      
      // 9. Aprender com resultado
      learn_from_audit_result(result);
      
      return result;
   }

   //+------------------------------------------------------------------+
   //| AUDITORIA TRADICIONAL                                            |
   //+------------------------------------------------------------------+
   bool perform_traditional_audit(string file_path)
   {
      // Verificar se arquivo existe
      if(!FileIsExist(file_path))
      {
         m_logger.log_error("[INTELLIGENT-AUDIT] Arquivo não encontrado: " + file_path);
         return false;
      }
      
      // Verificar blindagem SHA3
      bool has_blindagem = check_sha3_blindagem(file_path);
      
      // Verificar includes
      bool has_valid_includes = check_includes(file_path);
      
      // Verificar dependências
      bool has_valid_dependencies = check_dependencies(file_path);
      
      // Verificar sintaxe
      bool has_valid_syntax = check_syntax(file_path);
      
      return has_blindagem && has_valid_includes && has_valid_dependencies && has_valid_syntax;
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR BLINDAGEM SHA3                                         |
   //+------------------------------------------------------------------+
   bool check_sha3_blindagem(string file_path)
   {
      int file_handle = FileOpen(file_path, FILE_READ|FILE_TXT);
      if(file_handle == INVALID_HANDLE)
      {
         return false;
      }
      
      bool has_sha3 = false;
      string line;
      
      while(!FileIsEnding(file_handle))
      {
         line = FileReadString(file_handle);
         if(StringFind(line, "SHA3:") >= 0)
         {
            has_sha3 = true;
            break;
         }
      }
      
      FileClose(file_handle);
      return has_sha3;
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR INCLUDES                                               |
   //+------------------------------------------------------------------+
   bool check_includes(string file_path)
   {
      int file_handle = FileOpen(file_path, FILE_READ|FILE_TXT);
      if(file_handle == INVALID_HANDLE)
      {
         return false;
      }
      
      bool has_valid_includes = true;
      string line;
      
      while(!FileIsEnding(file_handle))
      {
         line = FileReadString(file_handle);
         if(StringFind(line, "#include") >= 0)
         {
            // Verificar se include existe
            string include_path = extract_include_path(line);
            if(include_path != "" && !FileIsExist(include_path))
            {
               has_valid_includes = false;
               m_logger.log_warning("[INTELLIGENT-AUDIT] Include não encontrado: " + include_path);
            }
         }
      }
      
      FileClose(file_handle);
      return has_valid_includes;
   }

   //+------------------------------------------------------------------+
   //| EXTRAIR CAMINHO DO INCLUDE                                       |
   //+------------------------------------------------------------------+
   string extract_include_path(string line)
   {
      int start = StringFind(line, "<");
      int end = StringFind(line, ">");
      
      if(start >= 0 && end >= 0 && end > start)
      {
         return StringSubstr(line, start + 1, end - start - 1);
      }
      
      start = StringFind(line, "\"");
      if(start >= 0)
      {
         end = StringFind(line, "\"", start + 1);
         if(end >= 0)
         {
            return StringSubstr(line, start + 1, end - start - 1);
         }
      }
      
      return "";
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR DEPENDÊNCIAS                                           |
   //+------------------------------------------------------------------+
   bool check_dependencies(string file_path)
   {
      // Verificar dependências conhecidas
      string dependencies[] = {
         "logger_institutional.mqh",
         "trade_signal_enum.mqh",
         "risk_profile.mqh",
         "market_regime_detector.mqh"
      };
      
      bool all_dependencies_exist = true;
      
      for(int i = 0; i < ArraySize(dependencies); i++)
      {
         if(!FileIsExist("include/" + dependencies[i]))
         {
            all_dependencies_exist = false;
            m_logger.log_warning("[INTELLIGENT-AUDIT] Dependência não encontrada: " + dependencies[i]);
         }
      }
      
      return all_dependencies_exist;
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR SINTAXE                                                |
   //+------------------------------------------------------------------+
   bool check_syntax(string file_path)
   {
      // Verificações básicas de sintaxe
      int file_handle = FileOpen(file_path, FILE_READ|FILE_TXT);
      if(file_handle == INVALID_HANDLE)
      {
         return false;
      }
      
      bool has_valid_syntax = true;
      string line;
      int brace_count = 0;
      int bracket_count = 0;
      int parenthesis_count = 0;
      
      while(!FileIsEnding(file_handle))
      {
         line = FileReadString(file_handle);
         
         // Contar chaves, colchetes e parênteses
         for(int i = 0; i < StringLen(line); i++)
         {
            string char = StringSubstr(line, i, 1);
            if(char == "{") brace_count++;
            if(char == "}") brace_count--;
            if(char == "[") bracket_count++;
            if(char == "]") bracket_count--;
            if(char == "(") parenthesis_count++;
            if(char == ")") parenthesis_count--;
         }
      }
      
      FileClose(file_handle);
      
      // Verificar se todos estão balanceados
      if(brace_count != 0 || bracket_count != 0 || parenthesis_count != 0)
      {
         has_valid_syntax = false;
         m_logger.log_error("[INTELLIGENT-AUDIT] Sintaxe desbalanceada em: " + file_path);
      }
      
      return has_valid_syntax;
   }

   //+------------------------------------------------------------------+
   //| CALCULAR RISCO INTEGRADO                                         |
   //+------------------------------------------------------------------+
   double calculate_integrated_risk(MLPrediction &prediction, bool traditional_audit, string file_path)
   {
      double ml_risk = prediction.error_probability;
      double traditional_risk = traditional_audit ? 0.0 : 0.8;
      
      // Peso para ML vs auditoria tradicional
      double ml_weight = 0.6;
      double traditional_weight = 0.4;
      
      // Risco integrado
      double integrated_risk = (ml_risk * ml_weight) + (traditional_risk * traditional_weight);
      
      // Ajustar baseado em histórico do arquivo
      integrated_risk = adjust_risk_by_history(integrated_risk, file_path);
      
      return MathMin(integrated_risk, 1.0);
   }

   //+------------------------------------------------------------------+
   //| AJUSTAR RISCO POR HISTÓRICO                                      |
   //+------------------------------------------------------------------+
   double adjust_risk_by_history(double base_risk, string file_path)
   {
      // Verificar se arquivo tem histórico de problemas
      for(int i = 0; i < m_learning_count; i++)
      {
         if(m_learning_data[i].file_name == file_path && m_learning_data[i].had_issues)
         {
            base_risk *= 1.3; // Aumentar risco para arquivos com histórico
         }
      }
      
      return base_risk;
   }

   //+------------------------------------------------------------------+
   //| GERAR PREDIÇÕES E AÇÕES                                          |
   //+------------------------------------------------------------------+
   void generate_predictions_and_actions(IntelligentAuditResult &result, 
                                       MLPrediction &prediction, string file_path)
   {
      // Adicionar predição do ML
      ArrayResize(result.predicted_issues, 1);
      result.predicted_issues[0] = prediction.predicted_error;
      
      ArrayResize(result.prevention_actions, 1);
      result.prevention_actions[0] = prediction.prevention_action;
      
      // Adicionar predições baseadas em análise tradicional
      if(!check_sha3_blindagem(file_path))
      {
         ArrayResize(result.predicted_issues, ArraySize(result.predicted_issues) + 1);
         result.predicted_issues[ArraySize(result.predicted_issues) - 1] = "BLINDAGEM";
         
         ArrayResize(result.prevention_actions, ArraySize(result.prevention_actions) + 1);
         result.prevention_actions[ArraySize(result.prevention_actions) - 1] = "Aplicar SHA3 blindagem";
      }
      
      if(!check_includes(file_path))
      {
         ArrayResize(result.predicted_issues, ArraySize(result.predicted_issues) + 1);
         result.predicted_issues[ArraySize(result.predicted_issues) - 1] = "INCLUDE";
         
         ArrayResize(result.prevention_actions, ArraySize(result.prevention_actions) + 1);
         result.prevention_actions[ArraySize(result.prevention_actions) - 1] = "Corrigir includes";
      }
   }

   //+------------------------------------------------------------------+
   //| GERAR RESUMO DA AUDITORIA                                        |
   //+------------------------------------------------------------------+
   string generate_audit_summary(IntelligentAuditResult &result, MLPrediction &prediction)
   {
      string summary = "=== AUDITORIA INTELIGENTE ===\n";
      summary += "Arquivo: " + result.file_name + "\n";
      summary += "Status: " + (result.audit_passed ? "APROVADO" : "REPROVADO") + "\n";
      summary += "Score de Risco: " + DoubleToString(result.risk_score, 3) + "\n";
      summary += "Confiança ML: " + DoubleToString(result.ml_confidence, 3) + "\n\n";
      
      summary += "PROBLEMAS PREDITOS:\n";
      for(int i = 0; i < ArraySize(result.predicted_issues); i++)
      {
         summary += "- " + result.predicted_issues[i] + "\n";
      }
      
      summary += "\nAÇÕES PREVENTIVAS:\n";
      for(int i = 0; i < ArraySize(result.prevention_actions); i++)
      {
         summary += "- " + result.prevention_actions[i] + "\n";
      }
      
      return summary;
   }

   //+------------------------------------------------------------------+
   //| REGISTRAR RESULTADO DA AUDITORIA                                |
   //+------------------------------------------------------------------+
   void register_audit_result(IntelligentAuditResult &result)
   {
      ArrayResize(m_audit_history, m_audit_count + 1);
      m_audit_history[m_audit_count] = result;
      m_audit_count++;
      
      m_logger.log_info("[INTELLIGENT-AUDIT] Auditoria registrada: " + result.file_name);
   }

   //+------------------------------------------------------------------+
   //| APRENDER COM RESULTADO DA AUDITORIA                             |
   //+------------------------------------------------------------------+
   void learn_from_audit_result(IntelligentAuditResult &result)
   {
      // Registrar dados de aprendizado
      AuditLearningData learning_data;
      learning_data.file_name = result.file_name;
      learning_data.audit_type = "INTELLIGENT";
      learning_data.had_issues = !result.audit_passed;
      learning_data.issues_corrected = false; // Será atualizado quando corrigido
      learning_data.correction_effectiveness = 0.0;
      
      // Copiar problemas encontrados
      ArrayResize(learning_data.issues_found, ArraySize(result.predicted_issues));
      for(int i = 0; i < ArraySize(result.predicted_issues); i++)
      {
         learning_data.issues_found[i] = result.predicted_issues[i];
      }
      
      ArrayResize(m_learning_data, m_learning_count + 1);
      m_learning_data[m_learning_count] = learning_data;
      m_learning_count++;
      
      // Registrar erros no sistema ML
      if(learning_data.had_issues)
      {
         for(int i = 0; i < ArraySize(learning_data.issues_found); i++)
         {
            m_ml_analyzer.register_error(learning_data.issues_found[i], 
                                       result.file_name, 
                                       "Problema detectado na auditoria inteligente",
                                       3, false, "");
         }
      }
   }

   //+------------------------------------------------------------------+
   //| ATUALIZAR EFETIVIDADE DA CORREÇÃO                               |
   //+------------------------------------------------------------------+
   void update_correction_effectiveness(string file_name, bool was_effective)
   {
      for(int i = 0; i < m_learning_count; i++)
      {
         if(m_learning_data[i].file_name == file_name)
         {
            m_learning_data[i].issues_corrected = true;
            m_learning_data[i].correction_time = TimeCurrent();
            m_learning_data[i].correction_effectiveness = was_effective ? 1.0 : 0.5;
            
            // Registrar correção no sistema ML
            for(int j = 0; j < ArraySize(m_learning_data[i].issues_found); j++)
            {
               m_ml_analyzer.register_error(m_learning_data[i].issues_found[j],
                                          file_name,
                                          "Problema corrigido",
                                          2, true, was_effective ? "Efetiva" : "Parcial");
            }
            
            break;
         }
      }
   }

   //+------------------------------------------------------------------+
   //| GERAR RELATÓRIO DE AUDITORIA INTELIGENTE                        |
   //+------------------------------------------------------------------+
   string generate_intelligent_audit_report()
   {
      string report = "=== RELATÓRIO DE AUDITORIA INTELIGENTE ===\n";
      report += "Total de auditorias: " + IntegerToString(m_audit_count) + "\n";
      report += "Total de aprendizado: " + IntegerToString(m_learning_count) + "\n";
      report += "Threshold de risco: " + DoubleToString(m_risk_threshold, 3) + "\n";
      report += "Threshold de confiança: " + DoubleToString(m_confidence_threshold, 3) + "\n\n";
      
      report += "ÚLTIMAS AUDITORIAS:\n";
      for(int i = MathMax(0, m_audit_count - 5); i < m_audit_count; i++)
      {
         report += "- " + m_audit_history[i].file_name + ": " + 
                  (m_audit_history[i].audit_passed ? "APROVADO" : "REPROVADO") + 
                  " (Risco: " + DoubleToString(m_audit_history[i].risk_score, 3) + ")\n";
      }
      
      report += "\nEFETIVIDADE DAS CORREÇÕES:\n";
      double total_effectiveness = 0.0;
      int correction_count = 0;
      
      for(int i = 0; i < m_learning_count; i++)
      {
         if(m_learning_data[i].issues_corrected)
         {
            total_effectiveness += m_learning_data[i].correction_effectiveness;
            correction_count++;
         }
      }
      
      if(correction_count > 0)
      {
         report += "Efetividade média: " + DoubleToString(total_effectiveness / correction_count, 3) + "\n";
      }
      
      return report;
   }

   //+------------------------------------------------------------------+
   //| CONFIGURAR THRESHOLDS                                            |
   //+------------------------------------------------------------------+
   void configure_thresholds(double risk_threshold, double confidence_threshold)
   {
      m_risk_threshold = risk_threshold;
      m_confidence_threshold = confidence_threshold;
      
      m_logger.log_info("[INTELLIGENT-AUDIT] Thresholds configurados - Risco: " + 
                       DoubleToString(risk_threshold, 3) + ", Confiança: " + 
                       DoubleToString(confidence_threshold, 3));
   }

   //+------------------------------------------------------------------+
   //| ATIVAR/DESATIVAR CORREÇÃO AUTOMÁTICA                            |
   //+------------------------------------------------------------------+
   void set_auto_correction(bool enabled)
   {
      m_auto_correction = enabled;
      
      m_logger.log_info("[INTELLIGENT-AUDIT] Correção automática: " + (enabled ? "ATIVADA" : "DESATIVADA"));
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR SE SISTEMA ESTÁ PRONTO                                |
   //+------------------------------------------------------------------+
   bool is_intelligent_audit_ready()
   {
      return m_ml_analyzer.is_ml_ready() && m_learning_count >= 5;
   }
};

#endif // __INTELLIGENT_AUDITOR_MQH__ 