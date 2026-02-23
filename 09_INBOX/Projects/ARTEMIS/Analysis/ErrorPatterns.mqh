//+------------------------------------------------------------------+
//|                                       ErrorPatterns.mqh           |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"

// Padrões de erro identificados
struct ErrorPattern {
    string name;           // Nome do padrão
    string description;    // Descrição
    int severity;         // Severidade
    string type;          // Tipo
    string component;     // Componente
    string resolution;    // Resolução
    int frequency;        // Frequência
    datetime last_seen;   // Última ocorrência
    bool is_active;       // Se está ativo
    double confidence;    // Confiança
};

// Padrões identificados
ErrorPattern g_patterns[] = {
    {
        "Missing Include",
        "Erro causado por falta de include de arquivo necessário",
        0.8,
        "unexpected token",
        "declaration without type",
        "Adicionar include do arquivo necessário no início do arquivo",
        0,
        false,
        0.0
    },
    {
        "Duplicate Definition",
        "Erro causado por definição duplicada de estrutura/classe",
        0.9,
        "identifier already used",
        "CVolatilityQuantum.mqh",
        "CAgentBase.mqh",
        "Mover definição para arquivo separado e usar include",
        0,
        false,
        0.0
    },
    {
        "Function Parameter Mismatch",
        0.7,
        "wrong parameters count",
        "CStatistics.mqh",
        "Trade/HistoryOrderInfo.mqh",
        "Corrigir parâmetros da chamada de função",
        0,
        false,
        0.0
    },
    {
        "Duplicate Function",
        0.6,
        "member function already defined",
        "CStatistics.mqh",
        "CLogger.mqh",
        "Remover função duplicada e unificar lógica",
        0,
        false,
        0.0
    }
};

// Análise de correlação entre padrões
struct PatternCorrelation {
    string pattern1;         // Primeiro padrão
    string pattern2;         // Segundo padrão
    double correlation;      // Força da correlação (0-1)
    string relationship;     // Descrição da relação
};

// Correlações entre padrões
PatternCorrelation g_pattern_correlations[] = {
    {
        "Missing Include",
        "Function Parameter Mismatch",
        0.6,
        "Falta de include pode levar a uso incorreto de funções"
    },
    {
        "Missing Include",
        "Duplicate Definition",
        0.7,
        "Falta de include pode levar a definições duplicadas"
    },
    {
        "Duplicate Definition",
        "Duplicate Function",
        0.8,
        "Definições duplicadas podem levar a funções duplicadas"
    }
};

// Análise de impacto
struct ImpactAnalysis {
    string pattern;          // Padrão de erro
    int affected_files;      // Número de arquivos afetados
    int affected_modules;    // Número de módulos afetados
    double resolution_time;  // Tempo médio de resolução (minutos)
    string[] dependencies;   // Dependências afetadas
};

// Análise de impacto dos padrões
ImpactAnalysis g_impact_analysis[] = {
    {
        "Missing Include",
        4,
        3,
        15.0,
        {"CLogger.mqh", "TimeframeHierarchy.mqh", "Core/VolatilityAnalysis.mqh"}
    },
    {
        "Duplicate Definition",
        2,
        2,
        30.0,
        {"VolatilityMetrics.mqh"}
    },
    {
        "Function Parameter Mismatch",
        1,
        1,
        10.0,
        {"Trade/HistoryOrderInfo.mqh"}
    },
    {
        "Duplicate Function",
        1,
        1,
        20.0,
        {"CLogger.mqh"}
    }
};

// Recomendações baseadas na análise
struct Recommendation {
    string pattern;          // Padrão de erro
    string recommendation;   // Recomendação
    string priority;         // Prioridade (Alta/Média/Baixa)
    string[] affected_files; // Arquivos afetados
};

// Recomendações
Recommendation g_recommendations[] = {
    {
        "Missing Include",
        "Implementar sistema de verificação automática de includes",
        "Alta",
        {"WinInet.mqh", "DynamicLotManager.mqh", "AdaptiveRiskSystem.mqh"}
    },
    {
        "Duplicate Definition",
        "Criar sistema de gerenciamento de definições compartilhadas",
        "Alta",
        {"CVolatilityQuantum.mqh", "CAgentBase.mqh"}
    },
    {
        "Function Parameter Mismatch",
        "Implementar validação de parâmetros em tempo de compilação",
        "Média",
        {"CStatistics.mqh"}
    },
    {
        "Duplicate Function",
        "Implementar sistema de detecção de funções duplicadas",
        "Média",
        {"CStatistics.mqh"}
    }
};

//+------------------------------------------------------------------+
//| Classe para análise de padrões de erro                            |
//+------------------------------------------------------------------+
class CErrorPatterns : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   ErrorPattern m_patterns[];            // Array de padrões
   ErrorSequence m_sequences[];          // Array de sequências
   ErrorCorrelation m_correlations[];    // Array de correlações
   int m_pattern_count;                  // Contagem de padrões
   int m_sequence_count;                 // Contagem de sequências
   int m_correlation_count;              // Contagem de correlações
   bool m_is_initialized;                // Se está inicializado
   datetime m_last_update;               // Última atualização
   
public:
   // Construtor
   CErrorPatterns(CLogger* logger)
   {
      m_logger = logger;
      m_pattern_count = 0;
      m_sequence_count = 0;
      m_correlation_count = 0;
      m_is_initialized = false;
      m_last_update = 0;
      
      if(m_logger != NULL)
      {
         m_logger.Info("Sistema de análise de padrões de erro inicializado");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CErrorPatterns()
   {
      if(m_logger != NULL)
         m_logger.Info("Sistema de análise de padrões de erro finalizado");
   }
   
   // Adiciona padrão
   bool AddPattern(const ErrorPattern& pattern)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      ArrayResize(m_patterns, m_pattern_count + 1);
      m_patterns[m_pattern_count] = pattern;
      m_pattern_count++;
      
      m_logger.Info("Padrão adicionado: " + pattern.name);
      return true;
   }
   
   // Adiciona sequência
   bool AddSequence(const ErrorSequence& sequence)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      ArrayResize(m_sequences, m_sequence_count + 1);
      m_sequences[m_sequence_count] = sequence;
      m_sequence_count++;
      
      m_logger.Info("Sequência adicionada: " + sequence.pattern);
      return true;
   }
   
   // Adiciona correlação
   bool AddCorrelation(const ErrorCorrelation& correlation)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      ArrayResize(m_correlations, m_correlation_count + 1);
      m_correlations[m_correlation_count] = correlation;
      m_correlation_count++;
      
      m_logger.Info("Correlação adicionada: " + correlation.pattern1 + " -> " + correlation.pattern2);
      return true;
   }
   
   // Obtém padrões por severidade
   ErrorPattern[] GetPatternsBySeverity(int severity)
   {
      ErrorPattern result[];
      int count = 0;
      
      for(int i = 0; i < m_pattern_count; i++)
      {
         if(m_patterns[i].severity == severity)
         {
            ArrayResize(result, count + 1);
            result[count] = m_patterns[i];
            count++;
         }
      }
      
      return result;
   }
   
   // Obtém sequências ativas
   ErrorSequence[] GetActiveSequences()
   {
      ErrorSequence result[];
      int count = 0;
      
      for(int i = 0; i < m_sequence_count; i++)
      {
         if(m_sequences[i].is_complete)
         {
            ArrayResize(result, count + 1);
            result[count] = m_sequences[i];
            count++;
         }
      }
      
      return result;
   }
   
   // Obtém correlações significativas
   ErrorCorrelation[] GetSignificantCorrelations()
   {
      ErrorCorrelation result[];
      int count = 0;
      
      for(int i = 0; i < m_correlation_count; i++)
      {
         if(m_correlations[i].is_significant)
         {
            ArrayResize(result, count + 1);
            result[count] = m_correlations[i];
            count++;
         }
      }
      
      return result;
   }
   
   // Atualiza estatísticas
   void UpdateStatistics()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Atualiza frequências
      for(int i = 0; i < m_pattern_count; i++)
      {
         m_patterns[i].frequency = CalculateFrequency(m_patterns[i].name);
      }
      
      // Atualiza probabilidades
      for(int i = 0; i < m_sequence_count; i++)
      {
         m_sequences[i].probability = CalculateProbability(m_sequences[i]);
      }
      
      // Atualiza correlações
      for(int i = 0; i < m_correlation_count; i++)
      {
         m_correlations[i].correlation = CalculateCorrelation(m_correlations[i]);
         m_correlations[i].is_significant = (m_correlations[i].correlation > 0.7);
      }
      
      m_last_update = TimeCurrent();
   }
   
private:
   // Calcula frequência
   int CalculateFrequency(string pattern_name)
   {
      int frequency = 0;
      
      for(int i = 0; i < m_sequence_count; i++)
      {
         for(int j = 0; j < ArraySize(m_sequences[i].sequence); j++)
         {
            if(m_sequences[i].sequence[j] == pattern_name)
               frequency++;
         }
      }
      
      return frequency;
   }
   
   // Calcula probabilidade
   double CalculateProbability(const ErrorSequence& sequence)
   {
      double probability = 0.0;
      
      if(sequence.count > 0)
      {
         int total_sequences = 0;
         
         for(int i = 0; i < m_sequence_count; i++)
         {
            if(m_sequences[i].pattern == sequence.pattern)
               total_sequences++;
         }
         
         if(total_sequences > 0)
            probability = (double)sequence.count / total_sequences;
      }
      
      return probability;
   }
   
   // Calcula correlação
   double CalculateCorrelation(const ErrorCorrelation& correlation)
   {
      double correlation_value = 0.0;
      
      if(correlation.count > 0)
      {
         int total_pattern1 = 0;
         int total_pattern2 = 0;
         
         for(int i = 0; i < m_pattern_count; i++)
         {
            if(m_patterns[i].name == correlation.pattern1)
               total_pattern1++;
            else if(m_patterns[i].name == correlation.pattern2)
               total_pattern2++;
         }
         
         if(total_pattern1 > 0 && total_pattern2 > 0)
         {
            correlation_value = (double)correlation.count / 
                              (total_pattern1 * total_pattern2);
         }
      }
      
      return correlation_value;
   }
}; 