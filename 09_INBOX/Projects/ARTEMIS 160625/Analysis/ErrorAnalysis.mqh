//+------------------------------------------------------------------+
//|                                        ErrorAnalysis.mqh          |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"

// Estrutura para armazenar informações sobre um erro
struct ErrorInfo {
    string file;           // Arquivo onde o erro ocorreu
    int line;             // Linha do erro
    string error_type;    // Tipo do erro (ex: "undeclared identifier", "unexpected token")
    string message;       // Mensagem de erro
    string context;       // Contexto do erro (código ao redor)
    datetime timestamp;   // Quando o erro foi detectado
    bool resolved;        // Se o erro foi resolvido
    string resolution;    // Como foi resolvido
    string dependencies;  // Dependências afetadas
};

// Estrutura para análise de correlação entre erros
struct ErrorCorrelation {
    string error1;        // Primeiro erro
    string error2;        // Segundo erro
    double correlation;   // Força da correlação (0-1)
    string relationship;  // Descrição da relação
    bool causal;          // Se é uma relação causal
};

// Estrutura para análise de dependências
struct DependencyInfo {
    string source_file;
    string target_file;
    string dependency_type;  // "include", "class", "struct"
    bool is_circular;
    int severity;
};

// Estrutura para análise de propagação de erros
struct ErrorPropagation {
    string source_error;
    string propagated_error;
    string affected_files[];
    int propagation_level;
    bool is_circular;
};

class CErrorAnalyzer : public CObject {
private:
    ErrorInfo m_errors[];           // Lista de erros
    ErrorCorrelation m_correlations[]; // Correlações entre erros
    DependencyInfo m_dependencies[];   // Informações de dependências
    ErrorPropagation m_propagations[]; // Informações de propagação de erros
    CLogger* m_logger;              // Logger para debug
    
    // Métodos privados
    void AnalyzeErrorPatterns();
    void AnalyzeDependencies();
    void FindErrorCorrelations();
    void AnalyzeErrorPropagation();
    
public:
    CErrorAnalyzer(CLogger* logger = NULL) {
        m_logger = logger;
        AnalyzeDependencies();
        AnalyzeErrorPropagation();
    }
    
    ~CErrorAnalyzer() {
        m_logger = NULL;
    }
    
    // Adiciona um novo erro para análise
    void AddError(const ErrorInfo &error) {
        int size = ArraySize(m_errors);
        ArrayResize(m_errors, size + 1);
        m_errors[size] = error;
        
        // Atualiza análise
        AnalyzeErrorPatterns();
        AnalyzeDependencies();
        FindErrorCorrelations();
    }
    
    // Analisa um módulo específico
    void AnalyzeModule(string module_name) {
        for(int i = 0; i < ArraySize(m_dependencies); i++) {
            if(m_dependencies[i].source_file == module_name || m_dependencies[i].target_file == module_name) {
                if(m_logger != NULL) {
                    m_logger.LogInfo("Analisando módulo: " + module_name);
                    m_logger.LogInfo("Dependências: " + m_dependencies[i].dependency_type);
                }
                break;
            }
        }
    }
    
    // Gera um relatório de análise
    string GenerateAnalysisReport() {
        string report = "=== Relatório de Análise de Erros ===\n\n";
        
        // Estatísticas gerais
        report += "Total de erros: " + IntegerToString(ArraySize(m_errors)) + "\n";
        report += "Total de correlações: " + IntegerToString(ArraySize(m_correlations)) + "\n";
        report += "Total de módulos: " + IntegerToString(ArraySize(m_dependencies)) + "\n\n";
        
        // Análise por tipo de erro
        report += "=== Análise por Tipo de Erro ===\n";
        string error_types[];
        int error_counts[];
        
        for(int i = 0; i < ArraySize(m_errors); i++) {
            bool found = false;
            for(int j = 0; j < ArraySize(error_types); j++) {
                if(error_types[j] == m_errors[i].error_type) {
                    error_counts[j]++;
                    found = true;
                    break;
                }
            }
            if(!found) {
                int size = ArraySize(error_types);
                ArrayResize(error_types, size + 1);
                ArrayResize(error_counts, size + 1);
                error_types[size] = m_errors[i].error_type;
                error_counts[size] = 1;
            }
        }
        
        for(int i = 0; i < ArraySize(error_types); i++) {
            report += error_types[i] + ": " + IntegerToString(error_counts[i]) + " ocorrências\n";
        }
        report += "\n";
        
        // Análise por módulo
        report += "=== Análise por Módulo ===\n";
        for(int i = 0; i < ArraySize(m_dependencies); i++) {
            report += "Módulo: " + (m_dependencies[i].source_file + " -> " + m_dependencies[i].target_file) + "\n";
            report += "  Dependências: " + m_dependencies[i].dependency_type + "\n";
            report += "  Circular: " + (m_dependencies[i].is_circular ? "Sim" : "Não") + "\n";
            report += "  Severidade: " + IntegerToString(m_dependencies[i].severity) + "\n\n";
        }
        
        // Correlações mais fortes
        report += "=== Correlações Mais Fortes ===\n";
        for(int i = 0; i < ArraySize(m_correlations); i++) {
            if(m_correlations[i].correlation > 0.7) {
                report += m_correlations[i].error1 + " <-> " + m_correlations[i].error2 + "\n";
                report += "  Correlação: " + DoubleToString(m_correlations[i].correlation, 2) + "\n";
                report += "  Relação: " + m_correlations[i].relationship + "\n";
                report += "  Causal: " + (m_correlations[i].causal ? "Sim" : "Não") + "\n\n";
            }
        }
        
        return report;
    }
    
    // Métodos para obter resultados da análise
    bool HasCircularDependency(const string &file) {
        for(int i = 0; i < ArraySize(m_dependencies); i++) {
            if((m_dependencies[i].source_file == file && m_dependencies[i].target_file == file) ||
               (m_dependencies[i].target_file == file && m_dependencies[i].source_file == file)) {
                return true;
            }
        }
        return false;
    }
    
    string[] GetAffectedFiles(const string &error) {
        string affected_files[];
        for(int i = 0; i < ArraySize(m_propagations); i++) {
            if(m_propagations[i].source_error == error) {
                return m_propagations[i].affected_files;
            }
        }
        string empty[];
        return empty;
    }
    
    int GetPropagationLevel(const string &error) {
        for(int i = 0; i < ArraySize(m_propagations); i++) {
            if(m_propagations[i].source_error == error) {
                return m_propagations[i].propagation_level;
            }
        }
        return -1;
    }
    
    string[] GetDependencyChain(const string &file) {
        string chain[];
        for(int i = 0; i < ArraySize(m_dependencies); i++) {
            if(m_dependencies[i].source_file == file || m_dependencies[i].target_file == file) {
                int size = ArraySize(chain);
                ArrayResize(chain, size + 1);
                chain[size] = (m_dependencies[i].source_file + " -> " + m_dependencies[i].target_file);
            }
        }
        return chain;
    }
    
    // Métodos para adicionar novas informações
    void AddDependency(const string &source, const string &target, const string &type) {
        int size = ArraySize(m_dependencies);
        ArrayResize(m_dependencies, size + 1);
        m_dependencies[size].source_file = source;
        m_dependencies[size].target_file = target;
        m_dependencies[size].dependency_type = type;
        m_dependencies[size].is_circular = false;
        m_dependencies[size].severity = SEVERITY_LOW;
    }
    
    void AddErrorPropagation(const string &source, const string &target, const string &files[]) {
        int size = ArraySize(m_propagations);
        ArrayResize(m_propagations, size + 1);
        m_propagations[size].source_error = source;
        m_propagations[size].propagated_error = target;
        ArrayCopy(m_propagations[size].affected_files, files);
        m_propagations[size].propagation_level = 1;
        m_propagations[size].is_circular = false;
    }
    
    // Métodos para obter recomendações
    string[] GetRecommendations(const string &error) {
        string recommendations[];
        
        if(error == "Missing Include") {
            ArrayResize(recommendations, 2);
            recommendations[0] = "Use Common.mqh for standard includes";
            recommendations[1] = "Check for circular dependencies";
        }
        else if(error == "Duplicate Definition") {
            ArrayResize(recommendations, 2);
            recommendations[0] = "Move shared structures to Common.mqh";
            recommendations[1] = "Use forward declarations when possible";
        }
        
        return recommendations;
    }
    
    string[] GetDependencyRecommendations(const string &file) {
        string recommendations[];
        for(int i = 0; i < ArraySize(m_dependencies); i++) {
            if(m_dependencies[i].source_file == file || m_dependencies[i].target_file == file) {
                int size = ArraySize(recommendations);
                ArrayResize(recommendations, size + 1);
                recommendations[size] = (m_dependencies[i].source_file + " -> " + m_dependencies[i].target_file);
            }
        }
        return recommendations;
    }
    
private:
    // Converte array para string
    string ArrayToString(const string &arr[]) {
        string result = "";
        for(int i = 0; i < ArraySize(arr); i++) {
            if(i > 0) result += ", ";
            result += arr[i];
        }
        return result;
    }
    
    // Analisa padrões de erro
    void AnalyzeErrorPatterns() {
        // Implementar análise de padrões
        // - Frequência de tipos de erro
        // - Sequência de erros
        // - Tempo entre erros
    }
    
    // Analisa dependências
    void AnalyzeDependencies() {
        // Implementar análise de dependências
        // - Mapear dependências entre arquivos
        // - Identificar ciclos
        // - Calcular complexidade
    }
    
    // Encontra correlações entre erros
    void FindErrorCorrelations() {
        // Implementar análise de correlação
        // - Correlação temporal
        // - Correlação de tipo
        // - Correlação de contexto
    }
    
    // Analisa propagação de erros
    void AnalyzeErrorPropagation() {
        // Implementar análise de propagação de erros
        // - Identificar caminhos de propagação
        // - Calcular nível de propagação
        // - Identificar ciclos de propagação
    }
}; 