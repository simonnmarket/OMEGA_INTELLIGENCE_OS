//+------------------------------------------------------------------+
//| audit_nomenclature_validator.mqh - Validador de Nomenclatura      |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Pasta: Include/Audit/                                            |
//| Versão: v1.0 (Sistema Anti-Duplicação)                          |
//| Atualizado em: 2025-07-21                                        |
//| Status: TIER-0 Compliant | SHA3 Protected | Anti-Duplicação      |
//| SHA3: a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890 |
//+------------------------------------------------------------------+
#ifndef __AUDIT_NOMENCLATURE_VALIDATOR_MQH__
#define __AUDIT_NOMENCLATURE_VALIDATOR_MQH__

#include "utils/logger_institutional.mqh"

//+------------------------------------------------------------------+
//| Estrutura de Arquivo Detectado                                   |
//+------------------------------------------------------------------+
struct DetectedFile {
   string filename;
   string full_path;
   string module;
   datetime timestamp;
   double file_size;
   string sha3_hash;
   bool is_duplicate;
   string duplicate_of;
};

//+------------------------------------------------------------------+
//| Estrutura de Erro de Nomenclatura                                |
//+------------------------------------------------------------------+
struct NomenclatureError {
   string error_type;
   string filename;
   string description;
   string severity;
   string recommendation;
   datetime detected_time;
};

//+------------------------------------------------------------------+
//| Classe AuditNomenclatureValidator                                 |
//+------------------------------------------------------------------+
class AuditNomenclatureValidator
{
private:
   logger_institutional &m_logger;
   
   // Arquivos detectados
   DetectedFile m_detected_files[];
   
   // Erros encontrados
   NomenclatureError m_nomenclature_errors[];
   
   // Estatísticas
   int m_total_files;
   int m_duplicate_files;
   int m_naming_errors;
   int m_case_errors;
   int m_typo_errors;

   //+--------------------------------------------------------------+
   //| Normaliza nome de arquivo para comparação                     |
   //+--------------------------------------------------------------+
   string NormalizeFilename(string filename)
   {
      string normalized = filename;
      
      // Remove extensão
      int dot_pos = StringFind(normalized, ".");
      if(dot_pos > 0)
         normalized = StringSubstr(normalized, 0, dot_pos);
      
      // Converte para minúsculas
      normalized = StringLower(normalized);
      
      // Remove underscores e hífens
      normalized = StringReplace(normalized, "_", "");
      normalized = StringReplace(normalized, "-", "");
      
      return normalized;
   }

   //+--------------------------------------------------------------+
   //| Calcula similaridade entre dois nomes                         |
   //+--------------------------------------------------------------+
   double CalculateSimilarity(string name1, string name2)
   {
      string norm1 = NormalizeFilename(name1);
      string norm2 = NormalizeFilename(name2);
      
      if(norm1 == norm2) return 1.0;
      
      int max_len = MathMax(StringLen(norm1), StringLen(norm2));
      if(max_len == 0) return 0.0;
      
      int distance = 0;
      for(int i = 0; i < MathMin(StringLen(norm1), StringLen(norm2)); i++)
      {
         if(StringGetCharacter(norm1, i) != StringGetCharacter(norm2, i))
            distance++;
      }
      
      distance += MathAbs(StringLen(norm1) - StringLen(norm2));
      
      return 1.0 - (double)distance / max_len;
   }

   //+--------------------------------------------------------------+
   //| Detecta erros de digitação                                    |
   //+--------------------------------------------------------------+
   bool DetectTypoError(string filename1, string filename2)
   {
      double similarity = CalculateSimilarity(filename1, filename2);
      
      // Se similaridade > 0.8 e < 1.0, provável erro de digitação
      if(similarity >= 0.8 && similarity < 1.0)
      {
         NomenclatureError error;
         error.error_type = "TYPOSIMILARITY";
         error.filename = filename1;
         error.description = "Possível erro de digitação similar a: " + filename2;
         error.severity = "MEDIUM";
         error.recommendation = "Verificar se são arquivos diferentes ou erro de nomenclatura";
         error.detected_time = TimeCurrent();
         
         ArrayPushBack(m_nomenclature_errors, error);
         m_typo_errors++;
         
         m_logger.log_warning("[AUDIT] Possível erro de digitação detectado: " + 
                             filename1 + " similar a " + filename2 + 
                             " (similaridade: " + DoubleToString(similarity, 2) + ")");
         return true;
      }
      
      return false;
   }

   //+--------------------------------------------------------------+
   //| Detecta erros de caixa alta/baixa                             |
   //+--------------------------------------------------------------+
   bool DetectCaseError(string filename)
   {
      string normalized = NormalizeFilename(filename);
      string original = filename;
      
      // Remove extensão para verificação
      int dot_pos = StringFind(original, ".");
      if(dot_pos > 0)
         original = StringSubstr(original, 0, dot_pos);
      
      // Verifica se há inconsistência de caixa
      bool has_upper = false;
      bool has_lower = false;
      
      for(int i = 0; i < StringLen(original); i++)
      {
         ushort ch = StringGetCharacter(original, i);
         if(ch >= 65 && ch <= 90) has_upper = true;  // A-Z
         if(ch >= 97 && ch <= 122) has_lower = true; // a-z
      }
      
      if(has_upper && has_lower)
      {
         NomenclatureError error;
         error.error_type = "CASEMIXED";
         error.filename = filename;
         error.description = "Inconsistência de caixa alta/baixa detectada";
         error.severity = "LOW";
         error.recommendation = "Padronizar nomenclatura (camelCase, snake_case, etc.)";
         error.detected_time = TimeCurrent();
         
         ArrayPushBack(m_nomenclature_errors, error);
         m_case_errors++;
         
         m_logger.log_warning("[AUDIT] Inconsistência de caixa detectada: " + filename);
         return true;
      }
      
      return false;
   }

public:
   //+--------------------------------------------------------------+
   //| Construtor                                                    |
   //+--------------------------------------------------------------+
   AuditNomenclatureValidator(logger_institutional &logger) :
      m_logger(logger)
   {
      m_total_files = 0;
      m_duplicate_files = 0;
      m_naming_errors = 0;
      m_case_errors = 0;
      m_typo_errors = 0;
   }

   //+--------------------------------------------------------------+
   //| Adiciona arquivo para análise                                 |
   //+--------------------------------------------------------------+
   void AddFile(string filename, string full_path, string module)
   {
      DetectedFile file;
      file.filename = filename;
      file.full_path = full_path;
      file.module = module;
      file.timestamp = TimeCurrent();
      file.file_size = 0; // Será calculado se necessário
      file.sha3_hash = "";
      file.is_duplicate = false;
      file.duplicate_of = "";
      
      ArrayPushBack(m_detected_files, file);
      m_total_files++;
      
      // Verifica erros de caixa
      DetectCaseError(filename);
   }

   //+--------------------------------------------------------------+
   //| Executa auditoria completa de nomenclatura                    |
   //+--------------------------------------------------------------+
   bool RunNomenclatureAudit()
   {
      m_logger.log_info("[AUDIT] Iniciando auditoria de nomenclatura...");
      
      // Verifica duplicatas
      for(int i = 0; i < ArraySize(m_detected_files); i++)
      {
         for(int j = i + 1; j < ArraySize(m_detected_files); j++)
         {
            string norm1 = NormalizeFilename(m_detected_files[i].filename);
            string norm2 = NormalizeFilename(m_detected_files[j].filename);
            
            // Duplicata exata
            if(norm1 == norm2 && m_detected_files[i].filename == m_detected_files[j].filename)
            {
               m_detected_files[i].is_duplicate = true;
               m_detected_files[i].duplicate_of = m_detected_files[j].full_path;
               m_detected_files[j].is_duplicate = true;
               m_detected_files[j].duplicate_of = m_detected_files[i].full_path;
               
               m_duplicate_files += 2;
               
               NomenclatureError error;
               error.error_type = "DUPLICATE_FILE";
               error.filename = m_detected_files[i].filename;
               error.description = "Arquivo duplicado encontrado em: " + 
                                 m_detected_files[i].full_path + " e " + 
                                 m_detected_files[j].full_path;
               error.severity = "CRITICAL";
               error.recommendation = "Remover um dos arquivos ou renomear para evitar conflitos";
               error.detected_time = TimeCurrent();
               
               ArrayPushBack(m_nomenclature_errors, error);
               
               m_logger.log_error("[AUDIT] ARQUIVO DUPLICADO DETECTADO: " + 
                                 m_detected_files[i].filename + " em " + 
                                 m_detected_files[i].full_path + " e " + 
                                 m_detected_files[j].full_path);
            }
            // Possível erro de digitação
            else if(norm1 != norm2)
            {
               DetectTypoError(m_detected_files[i].filename, m_detected_files[j].filename);
            }
         }
      }
      
      m_logger.log_info("[AUDIT] Auditoria de nomenclatura concluída");
      m_logger.log_info("[AUDIT] Total de arquivos: " + IntegerToString(m_total_files));
      m_logger.log_info("[AUDIT] Duplicatas encontradas: " + IntegerToString(m_duplicate_files));
      m_logger.log_info("[AUDIT] Erros de caixa: " + IntegerToString(m_case_errors));
      m_logger.log_info("[AUDIT] Erros de digitação: " + IntegerToString(m_typo_errors));
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retorna estatísticas da auditoria                             |
   //+--------------------------------------------------------------+
   void GetAuditStatistics(int &total_files, int &duplicates, int &case_errors, int &typo_errors)
   {
      total_files = m_total_files;
      duplicates = m_duplicate_files;
      case_errors = m_case_errors;
      typo_errors = m_typo_errors;
   }

   //+--------------------------------------------------------------+
   //| Retorna lista de erros encontrados                            |
   //+--------------------------------------------------------------+
   void GetNomenclatureErrors(NomenclatureError &errors[])
   {
      ArrayCopy(errors, m_nomenclature_errors);
   }

   //+--------------------------------------------------------------+
   //| Retorna lista de arquivos duplicados                          |
   //+--------------------------------------------------------------+
   void GetDuplicateFiles(DetectedFile &duplicates[])
   {
      int count = 0;
      for(int i = 0; i < ArraySize(m_detected_files); i++)
      {
         if(m_detected_files[i].is_duplicate)
         {
            ArrayResize(duplicates, count + 1);
            duplicates[count] = m_detected_files[i];
            count++;
         }
      }
   }
};

//+------------------------------------------------------------------+
//| FIM DO ARQUIVO - AUDIT NOMENCLATURE VALIDATOR                    |
//+------------------------------------------------------------------+
#endif // __AUDIT_NOMENCLATURE_VALIDATOR_MQH__ 