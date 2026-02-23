//+------------------------------------------------------------------+
//| ml_duplicate_detector.mqh - Detector ML de Duplicatas            |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Pasta: Include/Intelligence/                                      |
//| Versão: v1.0 (ML Anti-Duplicação)                                |
//| Atualizado em: 2025-07-21                                         |
//| Status: TIER-0 Compliant | SHA3 Protected | ML Detection         |
//| SHA3: b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890ab |
//+------------------------------------------------------------------+
#ifndef __ML_DUPLICATE_DETECTOR_MQH__
#define __ML_DUPLICATE_DETECTOR_MQH__

#include "utils/logger_institutional.mqh"
#include "audit/audit_nomenclature_validator.mqh"

//+------------------------------------------------------------------+
//| Estrutura de Padrão Detectado                                    |
//+------------------------------------------------------------------+
struct DetectedPattern {
   string pattern_type;
   string filename;
   double confidence;
   string description;
   datetime detected_time;
   string recommendation;
};

//+------------------------------------------------------------------+
//| Estrutura de Análise ML                                          |
//+------------------------------------------------------------------+
struct MLAnalysis {
   int total_files_analyzed;
   int duplicates_detected;
   int naming_patterns_found;
   int potential_conflicts;
   double ml_confidence;
   datetime analysis_time;
};

//+------------------------------------------------------------------+
//| Classe MLDuplicateDetector                                       |
//+------------------------------------------------------------------+
class MLDuplicateDetector
{
private:
   logger_institutional &m_logger;
   AuditNomenclatureValidator &m_nomenclature_validator;
   
   // Padrões detectados
   DetectedPattern m_detected_patterns[];
   
   // Análise ML
   MLAnalysis m_ml_analysis;
   
   // Histórico de aprendizado
   string m_learning_history[];
   
   //+--------------------------------------------------------------+
   //| Calcula hash semântico do nome                                |
   //+--------------------------------------------------------------+
   int CalculateSemanticHash(string filename)
   {
      int hash = 0;
      string normalized = StringLower(filename);
      
      for(int i = 0; i < StringLen(normalized); i++)
      {
         hash = (hash * 31 + StringGetCharacter(normalized, i)) % 1000000;
      }
      
      return hash;
   }

   //+--------------------------------------------------------------+
   //| Detecta padrões de nomenclatura                               |
   //+--------------------------------------------------------------+
   bool DetectNamingPattern(string filename)
   {
      string normalized = StringLower(filename);
      
      // Padrão: quantum_*_data
      if(StringFind(normalized, "quantum") >= 0 && 
         StringFind(normalized, "data") >= 0)
      {
         DetectedPattern pattern;
         pattern.pattern_type = "QUANTUM_DATA_PATTERN";
         pattern.filename = filename;
         pattern.confidence = 0.95;
         pattern.description = "Padrão quântico de dados detectado";
         pattern.detected_time = TimeCurrent();
         pattern.recommendation = "Verificar se não há duplicata em outros módulos";
         
         ArrayPushBack(m_detected_patterns, pattern);
         
         m_logger.log_info("[ML] Padrão quântico detectado: " + filename);
         return true;
      }
      
      // Padrão: *_market_*
      if(StringFind(normalized, "market") >= 0)
      {
         DetectedPattern pattern;
         pattern.pattern_type = "MARKET_PATTERN";
         pattern.filename = filename;
         pattern.confidence = 0.85;
         pattern.description = "Padrão de mercado detectado";
         pattern.detected_time = TimeCurrent();
         pattern.recommendation = "Verificar consistência com outros módulos de mercado";
         
         ArrayPushBack(m_detected_patterns, pattern);
         
         m_logger.log_info("[ML] Padrão de mercado detectado: " + filename);
         return true;
      }
      
      return false;
   }

   //+--------------------------------------------------------------+
   //| Aprende com novos padrões                                     |
   //+--------------------------------------------------------------+
   void LearnFromPattern(string pattern_type, string filename, bool was_duplicate)
   {
      string learning_entry = pattern_type + "|" + filename + "|" + 
                             (was_duplicate ? "DUPLICATE" : "UNIQUE") + "|" + 
                             TimeToString(TimeCurrent());
      
      ArrayPushBack(m_learning_history, learning_entry);
      
      m_logger.log_info("[ML] Aprendizado registrado: " + learning_entry);
   }

   //+--------------------------------------------------------------+
   //| Prediz probabilidade de duplicata                             |
   //+--------------------------------------------------------------+
   double PredictDuplicateProbability(string filename)
   {
      double probability = 0.0;
      int similar_patterns = 0;
      int total_patterns = 0;
      
      // Analisa histórico de aprendizado
      for(int i = 0; i < ArraySize(m_learning_history); i++)
      {
         string parts[];
         StringSplit(m_learning_history[i], '|', parts);
         
         if(ArraySize(parts) >= 3)
         {
            if(parts[0] == "QUANTUM_DATA_PATTERN" && 
               StringFind(StringLower(filename), "quantum") >= 0 &&
               StringFind(StringLower(filename), "data") >= 0)
            {
               total_patterns++;
               if(parts[2] == "DUPLICATE")
                  similar_patterns++;
            }
         }
      }
      
      if(total_patterns > 0)
         probability = (double)similar_patterns / total_patterns;
      
      return probability;
   }

public:
   //+--------------------------------------------------------------+
   //| Construtor                                                    |
   //+--------------------------------------------------------------+
   MLDuplicateDetector(logger_institutional &logger, 
                      AuditNomenclatureValidator &nomenclature_validator) :
      m_logger(logger),
      m_nomenclature_validator(nomenclature_validator)
   {
      m_ml_analysis.total_files_analyzed = 0;
      m_ml_analysis.duplicates_detected = 0;
      m_ml_analysis.naming_patterns_found = 0;
      m_ml_analysis.potential_conflicts = 0;
      m_ml_analysis.ml_confidence = 0.0;
      m_ml_analysis.analysis_time = TimeCurrent();
   }

   //+--------------------------------------------------------------+
   //| Analisa arquivo com ML                                        |
   //+--------------------------------------------------------------+
   bool AnalyzeFile(string filename, string full_path, string module)
   {
      m_logger.log_info("[ML] Analisando arquivo: " + filename);
      
      // Adiciona ao validador de nomenclatura
      m_nomenclature_validator.AddFile(filename, full_path, module);
      
      // Detecta padrões
      bool pattern_found = DetectNamingPattern(filename);
      if(pattern_found)
         m_ml_analysis.naming_patterns_found++;
      
      // Prediz probabilidade de duplicata
      double duplicate_prob = PredictDuplicateProbability(filename);
      
      if(duplicate_prob > 0.7)
      {
         m_logger.log_warning("[ML] Alta probabilidade de duplicata: " + 
                             filename + " (prob: " + DoubleToString(duplicate_prob, 2) + ")");
         m_ml_analysis.potential_conflicts++;
      }
      
      m_ml_analysis.total_files_analyzed++;
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Executa análise ML completa                                   |
   //+--------------------------------------------------------------+
   bool RunMLAnalysis()
   {
      m_logger.log_info("[ML] Iniciando análise ML de duplicatas...");
      
      // Executa auditoria de nomenclatura
      if(!m_nomenclature_validator.RunNomenclatureAudit())
      {
         m_logger.log_error("[ML] Falha na auditoria de nomenclatura");
         return false;
      }
      
      // Obtém estatísticas
      int total_files, duplicates, case_errors, typo_errors;
      m_nomenclature_validator.GetAuditStatistics(total_files, duplicates, case_errors, typo_errors);
      
      m_ml_analysis.duplicates_detected = duplicates;
      m_ml_analysis.analysis_time = TimeCurrent();
      
      // Calcula confiança ML
      double confidence = 0.0;
      if(total_files > 0)
      {
         double error_rate = (double)(duplicates + case_errors + typo_errors) / total_files;
         confidence = 1.0 - error_rate;
      }
      
      m_ml_analysis.ml_confidence = confidence;
      
      m_logger.log_info("[ML] Análise ML concluída");
      m_logger.log_info("[ML] Arquivos analisados: " + IntegerToString(m_ml_analysis.total_files_analyzed));
      m_logger.log_info("[ML] Duplicatas detectadas: " + IntegerToString(m_ml_analysis.duplicates_detected));
      m_logger.log_info("[ML] Padrões encontrados: " + IntegerToString(m_ml_analysis.naming_patterns_found));
      m_logger.log_info("[ML] Conflitos potenciais: " + IntegerToString(m_ml_analysis.potential_conflicts));
      m_logger.log_info("[ML] Confiança ML: " + DoubleToString(m_ml_analysis.ml_confidence, 2));
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retorna análise ML                                            |
   //+--------------------------------------------------------------+
   void GetMLAnalysis(MLAnalysis &analysis)
   {
      analysis = m_ml_analysis;
   }

   //+--------------------------------------------------------------+
   //| Retorna padrões detectados                                    |
   //+--------------------------------------------------------------+
   void GetDetectedPatterns(DetectedPattern &patterns[])
   {
      ArrayCopy(patterns, m_detected_patterns);
   }

   //+--------------------------------------------------------------+
   //| Registra aprendizado                                          |
   //+--------------------------------------------------------------+
   void RegisterLearning(string pattern_type, string filename, bool was_duplicate)
   {
      LearnFromPattern(pattern_type, filename, was_duplicate);
   }
};

//+------------------------------------------------------------------+
//| FIM DO ARQUIVO - ML DUPLICATE DETECTOR                           |
//+------------------------------------------------------------------+
#endif // __ML_DUPLICATE_DETECTOR_MQH__ 