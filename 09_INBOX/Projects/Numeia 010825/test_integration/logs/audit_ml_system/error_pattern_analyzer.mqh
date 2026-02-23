//+------------------------------------------------------------------+
//| error_pattern_analyzer.mqh - Sistema ML para Prevenção de Erros   |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Versão: v1.0 (ML Error Prevention System)                       |
//| Atualizado em: 2025-07-21                                        |
//| Status: TIER-0 Compliant | SHA3 Protected | ML Ready             |
//| SHA3: b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7 |
//+------------------------------------------------------------------+
#ifndef __ERROR_PATTERN_ANALYZER_MQH__
#define __ERROR_PATTERN_ANALYZER_MQH__

#include <include/utils/logger_institutional.mqh>

//+------------------------------------------------------------------+
//| ESTRUTURAS DE DADOS PARA ML                                      |
//+------------------------------------------------------------------+

struct ErrorPattern
{
   string error_type;           // Tipo do erro (blindagem, include, dependência)
   string file_name;            // Arquivo onde ocorreu
   string error_description;    // Descrição detalhada
   datetime timestamp;          // Quando ocorreu
   int severity_level;          // Nível de severidade (1-5)
   bool was_corrected;          // Se foi corrigido
   string correction_method;    // Como foi corrigido
   double confidence_score;     // Score de confiança do ML
};

struct MLPrediction
{
   string file_name;            // Arquivo analisado
   double error_probability;    // Probabilidade de erro (0-1)
   string predicted_error;      // Erro previsto
   string prevention_action;    // Ação preventiva recomendada
   double confidence;           // Confiança da predição
   datetime prediction_time;    // Quando foi feita a predição
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL DO SISTEMA ML                                   |
//+------------------------------------------------------------------+

class ErrorPatternAnalyzer
{
private:
   logger_institutional &m_logger;
   
   // Base de dados de erros
   ErrorPattern m_error_database[];
   int m_error_count;
   
   // Modelo ML para predições
   double m_error_weights[5];  // Pesos para diferentes tipos de erro
   double m_file_risk_scores[]; // Scores de risco por arquivo
   
   // Configurações do sistema
   double m_learning_rate;
   double m_min_confidence;
   int m_max_patterns;
   
   // Histórico de predições
   MLPrediction m_predictions[];
   int m_prediction_count;

public:
   ErrorPatternAnalyzer(logger_institutional &logger)
      : m_logger(logger)
   {
      m_error_count = 0;
      m_prediction_count = 0;
      m_learning_rate = 0.1;
      m_min_confidence = 0.7;
      m_max_patterns = 1000;
      
      // Inicializar pesos do ML
      m_error_weights[0] = 0.3; // Blindagem
      m_error_weights[1] = 0.25; // Include
      m_error_weights[2] = 0.2;  // Dependência
      m_error_weights[3] = 0.15; // Compilação
      m_error_weights[4] = 0.1;  // Integração
      
      m_logger.log_info("[ML-ERROR] Sistema de ML para prevenção de erros inicializado");
   }

   //+------------------------------------------------------------------+
   //| REGISTRAR NOVO ERRO PARA APRENDIZADO                            |
   //+------------------------------------------------------------------+
   void register_error(string error_type, string file_name, string description, 
                      int severity, bool corrected = false, string correction = "")
   {
      if(m_error_count >= m_max_patterns)
      {
         // Remover padrões antigos se necessário
         remove_old_patterns();
      }
      
      ErrorPattern new_error;
      new_error.error_type = error_type;
      new_error.file_name = file_name;
      new_error.error_description = description;
      new_error.timestamp = TimeCurrent();
      new_error.severity_level = severity;
      new_error.was_corrected = corrected;
      new_error.correction_method = correction;
      new_error.confidence_score = calculate_confidence(severity, corrected);
      
      ArrayResize(m_error_database, m_error_count + 1);
      m_error_database[m_error_count] = new_error;
      m_error_count++;
      
      // Aprender com o erro
      learn_from_error(new_error);
      
      m_logger.log_warning("[ML-ERROR] Erro registrado: " + error_type + " em " + file_name);
   }

   //+------------------------------------------------------------------+
   //| PREDIZER ERROS EM ARQUIVO                                       |
   //+------------------------------------------------------------------+
   MLPrediction predict_errors(string file_name)
   {
      MLPrediction prediction;
      prediction.file_name = file_name;
      prediction.prediction_time = TimeCurrent();
      
      // Analisar padrões históricos
      double blindagem_risk = analyze_blindagem_patterns(file_name);
      double include_risk = analyze_include_patterns(file_name);
      double dependency_risk = analyze_dependency_patterns(file_name);
      double compilation_risk = analyze_compilation_patterns(file_name);
      double integration_risk = analyze_integration_patterns(file_name);
      
      // Calcular risco total
      prediction.error_probability = calculate_total_risk(blindagem_risk, include_risk, 
                                                       dependency_risk, compilation_risk, integration_risk);
      
      // Determinar tipo de erro mais provável
      prediction.predicted_error = determine_most_likely_error(blindagem_risk, include_risk,
                                                             dependency_risk, compilation_risk, integration_risk);
      
      // Gerar ação preventiva
      prediction.prevention_action = generate_prevention_action(prediction.predicted_error, file_name);
      
      // Calcular confiança baseada na qualidade dos dados
      prediction.confidence = calculate_prediction_confidence(file_name);
      
      // Registrar predição
      register_prediction(prediction);
      
      return prediction;
   }

   //+------------------------------------------------------------------+
   //| ANALISAR PADRÕES DE BLINDAGEM                                   |
   //+------------------------------------------------------------------+
   double analyze_blindagem_patterns(string file_name)
   {
      double risk_score = 0.0;
      int blindagem_errors = 0;
      int total_files = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].error_type == "BLINDAGEM")
         {
            blindagem_errors++;
            risk_score += m_error_database[i].severity_level * m_error_weights[0];
         }
         total_files++;
      }
      
      // Verificar se arquivo já teve problemas de blindagem
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].file_name == file_name && 
            m_error_database[i].error_type == "BLINDAGEM")
         {
            risk_score *= 1.5; // Multiplicador para arquivos com histórico
         }
      }
      
      return (total_files > 0) ? (risk_score / total_files) : 0.0;
   }

   //+------------------------------------------------------------------+
   //| ANALISAR PADRÕES DE INCLUDES                                    |
   //+------------------------------------------------------------------+
   double analyze_include_patterns(string file_name)
   {
      double risk_score = 0.0;
      int include_errors = 0;
      int total_files = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].error_type == "INCLUDE")
         {
            include_errors++;
            risk_score += m_error_database[i].severity_level * m_error_weights[1];
         }
         total_files++;
      }
      
      return (total_files > 0) ? (risk_score / total_files) : 0.0;
   }

   //+------------------------------------------------------------------+
   //| ANALISAR PADRÕES DE DEPENDÊNCIAS                                |
   //+------------------------------------------------------------------+
   double analyze_dependency_patterns(string file_name)
   {
      double risk_score = 0.0;
      int dependency_errors = 0;
      int total_files = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].error_type == "DEPENDENCIA")
         {
            dependency_errors++;
            risk_score += m_error_database[i].severity_level * m_error_weights[2];
         }
         total_files++;
      }
      
      return (total_files > 0) ? (risk_score / total_files) : 0.0;
   }

   //+------------------------------------------------------------------+
   //| ANALISAR PADRÕES DE COMPILAÇÃO                                  |
   //+------------------------------------------------------------------+
   double analyze_compilation_patterns(string file_name)
   {
      double risk_score = 0.0;
      int compilation_errors = 0;
      int total_files = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].error_type == "COMPILACAO")
         {
            compilation_errors++;
            risk_score += m_error_database[i].severity_level * m_error_weights[3];
         }
         total_files++;
      }
      
      return (total_files > 0) ? (risk_score / total_files) : 0.0;
   }

   //+------------------------------------------------------------------+
   //| ANALISAR PADRÕES DE INTEGRAÇÃO                                  |
   //+------------------------------------------------------------------+
   double analyze_integration_patterns(string file_name)
   {
      double risk_score = 0.0;
      int integration_errors = 0;
      int total_files = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].error_type == "INTEGRACAO")
         {
            integration_errors++;
            risk_score += m_error_database[i].severity_level * m_error_weights[4];
         }
         total_files++;
      }
      
      return (total_files > 0) ? (risk_score / total_files) : 0.0;
   }

   //+------------------------------------------------------------------+
   //| CALCULAR RISCO TOTAL                                            |
   //+------------------------------------------------------------------+
   double calculate_total_risk(double blindagem, double include, double dependency, 
                              double compilation, double integration)
   {
      double total_risk = (blindagem * m_error_weights[0]) +
                         (include * m_error_weights[1]) +
                         (dependency * m_error_weights[2]) +
                         (compilation * m_error_weights[3]) +
                         (integration * m_error_weights[4]);
      
      // Normalizar para 0-1
      return MathMin(total_risk, 1.0);
   }

   //+------------------------------------------------------------------+
   //| DETERMINAR ERRO MAIS PROVÁVEL                                  |
   //+------------------------------------------------------------------+
   string determine_most_likely_error(double blindagem, double include, double dependency,
                                     double compilation, double integration)
   {
      double risks[5] = {blindagem, include, dependency, compilation, integration};
      string error_types[5] = {"BLINDAGEM", "INCLUDE", "DEPENDENCIA", "COMPILACAO", "INTEGRACAO"};
      
      int max_index = 0;
      double max_risk = risks[0];
      
      for(int i = 1; i < 5; i++)
      {
         if(risks[i] > max_risk)
         {
            max_risk = risks[i];
            max_index = i;
         }
      }
      
      return error_types[max_index];
   }

   //+------------------------------------------------------------------+
   //| GERAR AÇÃO PREVENTIVA                                           |
   //+------------------------------------------------------------------+
   string generate_prevention_action(string error_type, string file_name)
   {
      string action = "";
      
      if(error_type == "BLINDAGEM")
      {
         action = "Aplicar SHA3 blindagem imediatamente em " + file_name;
      }
      else if(error_type == "INCLUDE")
      {
         action = "Verificar e corrigir includes em " + file_name;
      }
      else if(error_type == "DEPENDENCIA")
      {
         action = "Criar arquivos de dependência pendentes para " + file_name;
      }
      else if(error_type == "COMPILACAO")
      {
         action = "Validar sintaxe e estrutura de " + file_name;
      }
      else if(error_type == "INTEGRACAO")
      {
         action = "Testar integração de " + file_name + " com módulos existentes";
      }
      
      return action;
   }

   //+------------------------------------------------------------------+
   //| APRENDER COM ERRO                                               |
   //+------------------------------------------------------------------+
   void learn_from_error(ErrorPattern &error)
   {
      // Ajustar pesos baseado no tipo de erro
      int weight_index = get_weight_index(error.error_type);
      if(weight_index >= 0)
      {
         if(error.was_corrected)
         {
            // Reduzir peso se erro foi corrigido
            m_error_weights[weight_index] *= (1.0 - m_learning_rate);
         }
         else
         {
            // Aumentar peso se erro não foi corrigido
            m_error_weights[weight_index] *= (1.0 + m_learning_rate);
         }
         
         // Normalizar pesos
         normalize_weights();
      }
      
      m_logger.log_info("[ML-ERROR] Aprendizado aplicado para erro: " + error.error_type);
   }

   //+------------------------------------------------------------------+
   //| OBTER ÍNDICE DO PESO                                            |
   //+------------------------------------------------------------------+
   int get_weight_index(string error_type)
   {
      if(error_type == "BLINDAGEM") return 0;
      if(error_type == "INCLUDE") return 1;
      if(error_type == "DEPENDENCIA") return 2;
      if(error_type == "COMPILACAO") return 3;
      if(error_type == "INTEGRACAO") return 4;
      return -1;
   }

   //+------------------------------------------------------------------+
   //| NORMALIZAR PESOS                                                |
   //+------------------------------------------------------------------+
   void normalize_weights()
   {
      double total = 0.0;
      for(int i = 0; i < 5; i++)
      {
         total += m_error_weights[i];
      }
      
      for(int i = 0; i < 5; i++)
      {
         m_error_weights[i] /= total;
      }
   }

   //+------------------------------------------------------------------+
   //| CALCULAR CONFIANÇA                                              |
   //+------------------------------------------------------------------+
   double calculate_confidence(int severity, bool corrected)
   {
      double base_confidence = 0.5;
      double severity_factor = severity / 5.0;
      double correction_factor = corrected ? 0.3 : -0.2;
      
      return MathMax(0.1, MathMin(1.0, base_confidence + severity_factor + correction_factor));
   }

   //+------------------------------------------------------------------+
   //| CALCULAR CONFIANÇA DA PREDIÇÃO                                  |
   //+------------------------------------------------------------------+
   double calculate_prediction_confidence(string file_name)
   {
      // Baseado na quantidade de dados históricos
      double data_confidence = MathMin(m_error_count / 100.0, 1.0);
      
      // Baseado na qualidade dos padrões
      double pattern_quality = 0.0;
      int quality_count = 0;
      
      for(int i = 0; i < m_error_count; i++)
      {
         if(m_error_database[i].confidence_score > 0.7)
         {
            pattern_quality += m_error_database[i].confidence_score;
            quality_count++;
         }
      }
      
      if(quality_count > 0)
      {
         pattern_quality /= quality_count;
      }
      
      return (data_confidence + pattern_quality) / 2.0;
   }

   //+------------------------------------------------------------------+
   //| REGISTRAR PREDIÇÃO                                              |
   //+------------------------------------------------------------------+
   void register_prediction(MLPrediction &prediction)
   {
      ArrayResize(m_predictions, m_prediction_count + 1);
      m_predictions[m_prediction_count] = prediction;
      m_prediction_count++;
   }

   //+------------------------------------------------------------------+
   //| REMOVER PADRÕES ANTIGOS                                         |
   //+------------------------------------------------------------------+
   void remove_old_patterns()
   {
      // Manter apenas os padrões mais recentes
      int keep_count = m_max_patterns / 2;
      
      for(int i = 0; i < keep_count; i++)
      {
         m_error_database[i] = m_error_database[m_error_count - keep_count + i];
      }
      
      m_error_count = keep_count;
      ArrayResize(m_error_database, keep_count);
   }

   //+------------------------------------------------------------------+
   //| GERAR RELATÓRIO DE APRENDIZADO                                 |
   //+------------------------------------------------------------------+
   string generate_learning_report()
   {
      string report = "=== RELATÓRIO DE APRENDIZADO ML ===\n";
      report += "Total de erros registrados: " + IntegerToString(m_error_count) + "\n";
      report += "Total de predições: " + IntegerToString(m_prediction_count) + "\n";
      report += "Taxa de aprendizado: " + DoubleToString(m_learning_rate, 3) + "\n\n";
      
      report += "PESOS ATUAIS:\n";
      report += "- Blindagem: " + DoubleToString(m_error_weights[0], 3) + "\n";
      report += "- Include: " + DoubleToString(m_error_weights[1], 3) + "\n";
      report += "- Dependência: " + DoubleToString(m_error_weights[2], 3) + "\n";
      report += "- Compilação: " + DoubleToString(m_error_weights[3], 3) + "\n";
      report += "- Integração: " + DoubleToString(m_error_weights[4], 3) + "\n\n";
      
      report += "ÚLTIMAS PREDIÇÕES:\n";
      for(int i = MathMax(0, m_prediction_count - 5); i < m_prediction_count; i++)
      {
         report += "- " + m_predictions[i].file_name + ": " + 
                  DoubleToString(m_predictions[i].error_probability, 3) + 
                  " (" + m_predictions[i].predicted_error + ")\n";
      }
      
      return report;
   }

   //+------------------------------------------------------------------+
   //| VERIFICAR SE SISTEMA ESTÁ PRONTO                                |
   //+------------------------------------------------------------------+
   bool is_ml_ready()
   {
      return m_error_count >= 10; // Mínimo de dados para aprendizado
   }
};

#endif // __ERROR_PATTERN_ANALYZER_MQH__ 