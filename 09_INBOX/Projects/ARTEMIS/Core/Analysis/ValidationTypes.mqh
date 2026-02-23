//+------------------------------------------------------------------+
//| ValidationTypes.mqh - Tipos e Estruturas para Validação v2.0     |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

//===========================================
// ENUMS
//===========================================
enum ValidationSeverity {
   SEVERITY_INFO = 0,
   SEVERITY_WARNING = 1,
   SEVERITY_ERROR = 2,
   SEVERITY_CRITICAL = 3
};

enum ValidationStatus {
   STATUS_PENDING = 0,
   STATUS_RUNNING = 1,
   STATUS_COMPLETED = 2,
   STATUS_FAILED = 3
};

//===========================================
// STRUCTURES
//===========================================
struct ValidationResult {
   string module;                 // Nome do módulo validado
   bool success;                 // Status da validação
   string error;                 // Mensagem de erro (se houver)
   datetime timestamp;           // Timestamp da validação
   ValidationSeverity severity;  // Severidade do problema
   string details;               // Detalhes adicionais
   int error_code;               // Código de erro específico
};

struct ValidationMetrics {
   int total_validations;
   int successful_validations;
   int failed_validations;
   double success_rate;
   datetime last_validation;
   ValidationStatus current_status;
   string last_error;
   int last_error_code;

   int info_count;
   int warning_count;
   int error_count;
   int critical_count;
};

struct ModuleDependency {
   string module_name;
   string required_version;
   bool is_optional;
   string dependencies[];
}; 