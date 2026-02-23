//+------------------------------------------------------------------+
//| CAnalysisModule.mqh - Validação e Análise de Módulos v2.0       |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs"
#property strict

#include "ValidationTypes.mqh"
#include "..\\..\\Utils\\CLogger.mqh"
#include "..\\..\\Risk\\CRiskManager.mqh"
#include "..\\..\\Quantum\\CQuantumMarketPhysics.mqh"
#include "..\\..\\Quantum\\CVolatilityQuantum.mqh"

//===========================================
// CLASSE: MÓDULO DE ANÁLISE
//===========================================
class CAnalysisModule {
private:
   CLogger* m_logger;
   ValidationMetrics m_metrics;
   ValidationResult m_validation_results[];
   ModuleDependency m_dependencies[];
   bool m_is_valid;
   string m_last_error;
   datetime m_last_validation;
   
   CDarkPoolModule         *m_dark_pool;
   CVolatilityQuantum      *m_volatility;
   CQuantumMarketPhysics   *m_quantum_physics;
   CRiskManager            *m_risk_manager;
   double                   m_risk_percent;
   double                   m_stop_loss_pips;
   QuantumMetrics           m_qmetrics;
   
   // Métodos privados de validação
   bool ValidateDarkPool() {
      if(!m_dark_pool) {
         SetError("Dark Pool não inicializado", SEVERITY_ERROR, 1001);
         return false;
      }
      
      DarkPoolMetrics metrics = m_dark_pool->GetMetrics();
      if(metrics.total_executed_volume < 0 || metrics.avg_execution_price <= 0) {
         SetError("Métricas do Dark Pool inválidas", SEVERITY_ERROR, 1002);
         return false;
      }
      
      return true;
   }
   
   bool ValidateVolatility() {
      if(!m_volatility) {
         SetError("Módulo de Volatilidade não inicializado", SEVERITY_ERROR, 2001);
         return false;
      }
      
      VolatilityMetrics metrics = m_volatility->GetMetrics();
      if(metrics.garch_volatility < 0 || metrics.markov_state < 0) {
         SetError("Métricas de Volatilidade inválidas", SEVERITY_ERROR, 2002);
         return false;
      }
      
      return true;
   }
   
   bool ValidateRiskManagement() {
      if(!m_risk_manager) {
         SetError("Risk Manager não inicializado", SEVERITY_ERROR, 3001);
         return false;
      }
      
      if(m_risk_percent <= 0 || m_stop_loss_pips <= 0) {
         SetError("Parâmetros de risco inválidos", SEVERITY_ERROR, 3002);
         return false;
      }
      
      return true;
   }
   
   bool ValidateQuantumPhysics() {
      if(!m_quantum_physics) {
         SetError("Quantum Physics não inicializado", SEVERITY_ERROR, 4001);
         return false;
      }
      
      if(m_qmetrics.wave_collapse_probability < 0 || m_qmetrics.wave_collapse_probability > 1) {
         SetError("Métricas quânticas inválidas", SEVERITY_ERROR, 4002);
         return false;
      }
      
      return true;
   }
   
   void SetError(const string &error, ValidationSeverity severity, int error_code) {
      m_last_error = error;
      m_metrics.last_error = error;
      m_metrics.last_error_code = error_code;
      m_metrics.current_status = STATUS_FAILED;
   }
   
   void LogValidationResult(const ValidationResult &result) {
      if(m_logger) {
         string message = StringFormat("Validação do módulo %s: %s", 
            result.module, result.success ? "SUCESSO" : "FALHA");
         if(!result.success) {
            message += StringFormat(" - Erro: %s (Severidade: %d, Código: %d)", 
               result.error, result.severity, result.error_code);
         }
         
         switch(result.severity) {
            case SEVERITY_INFO:
               m_logger.Info(message);
               break;
            case SEVERITY_WARNING:
               m_logger.Warn(message);
               break;
            case SEVERITY_ERROR:
            case SEVERITY_CRITICAL:
               m_logger.Error(message);
               break;
         }
      }
   }
   
   void UpdateMetrics(bool success, ValidationSeverity severity) {
      m_metrics.total_validations++;
      if(success) {
         m_metrics.successful_validations++;
      } else {
         m_metrics.failed_validations++;
      }
      m_metrics.success_rate = (double)m_metrics.successful_validations / m_metrics.total_validations;
      m_metrics.last_validation = TimeCurrent();
      
      // Atualizar contadores de severidade
      switch(severity) {
         case SEVERITY_INFO:
            m_metrics.info_count++;
            break;
         case SEVERITY_WARNING:
            m_metrics.warning_count++;
            break;
         case SEVERITY_ERROR:
            m_metrics.error_count++;
            break;
         case SEVERITY_CRITICAL:
            m_metrics.critical_count++;
            break;
      }
   }
   
   bool ValidateDependencies() {
      for(int i = 0; i < ArraySize(m_dependencies); i++) {
         if(!ValidateModuleDependency(m_dependencies[i])) {
            return false;
         }
      }
      return true;
   }
   
   bool ValidateModuleDependency(const ModuleDependency &dep) {
      if(dep.module_name == "" || dep.required_version == "")
         return false;
      return true;
   }

public:
   CAnalysisModule(CLogger* logger = NULL) :
      m_logger(logger)
   {
      Initialize();
   }
   
   void Initialize() {
      m_is_valid = false;
      m_last_validation = 0;
      m_metrics.total_validations = 0;
      m_metrics.successful_validations = 0;
      m_metrics.failed_validations = 0;
      m_metrics.success_rate = 0;
      m_metrics.current_status = STATUS_PENDING;
      m_metrics.last_error = "";
      m_metrics.last_error_code = 0;
      m_metrics.info_count = 0;
      m_metrics.warning_count = 0;
      m_metrics.error_count = 0;
      m_metrics.critical_count = 0;
      ArrayResize(m_validation_results, 0);
      ArrayResize(m_dependencies, 0);
   }
   
   bool ValidateAll() {
      m_metrics.current_status = STATUS_RUNNING;
      m_is_valid = true;
      m_last_validation = TimeCurrent();
      
      // Validar dependências primeiro
      if(!ValidateDependencies()) {
         m_metrics.current_status = STATUS_FAILED;
         return false;
      }
      
      // Validação do Dark Pool
      ValidationResult dp_result;
      dp_result.module = "Dark Pool";
      dp_result.success = ValidateDarkPool();
      dp_result.timestamp = TimeCurrent();
      if(!dp_result.success) {
         dp_result.error = m_last_error;
         dp_result.severity = SEVERITY_ERROR;
         m_is_valid = false;
      }
      ArrayResize(m_validation_results, ArraySize(m_validation_results) + 1);
      m_validation_results[ArraySize(m_validation_results) - 1] = dp_result;
      LogValidationResult(dp_result);
      UpdateMetrics(dp_result.success, dp_result.severity);
      
      // Validação da Volatilidade
      ValidationResult vol_result;
      vol_result.module = "Volatilidade";
      vol_result.success = ValidateVolatility();
      vol_result.timestamp = TimeCurrent();
      if(!vol_result.success) {
         vol_result.error = m_last_error;
         vol_result.severity = SEVERITY_ERROR;
         m_is_valid = false;
      }
      ArrayResize(m_validation_results, ArraySize(m_validation_results) + 1);
      m_validation_results[ArraySize(m_validation_results) - 1] = vol_result;
      LogValidationResult(vol_result);
      UpdateMetrics(vol_result.success, vol_result.severity);
      
      // Validação do Risk Management
      ValidationResult risk_result;
      risk_result.module = "Risk Management";
      risk_result.success = ValidateRiskManagement();
      risk_result.timestamp = TimeCurrent();
      if(!risk_result.success) {
         risk_result.error = m_last_error;
         risk_result.severity = SEVERITY_ERROR;
         m_is_valid = false;
      }
      ArrayResize(m_validation_results, ArraySize(m_validation_results) + 1);
      m_validation_results[ArraySize(m_validation_results) - 1] = risk_result;
      LogValidationResult(risk_result);
      UpdateMetrics(risk_result.success, risk_result.severity);
      
      // Validação da Física Quântica
      ValidationResult quantum_result;
      quantum_result.module = "Quantum Physics";
      quantum_result.success = ValidateQuantumPhysics();
      quantum_result.timestamp = TimeCurrent();
      if(!quantum_result.success) {
         quantum_result.error = m_last_error;
         quantum_result.severity = SEVERITY_ERROR;
         m_is_valid = false;
      }
      ArrayResize(m_validation_results, ArraySize(m_validation_results) + 1);
      m_validation_results[ArraySize(m_validation_results) - 1] = quantum_result;
      LogValidationResult(quantum_result);
      UpdateMetrics(quantum_result.success, quantum_result.severity);
      
      m_metrics.current_status = m_is_valid ? STATUS_COMPLETED : STATUS_FAILED;
      return m_is_valid;
   }
   
   string GetValidationReport() const {
      string report = "=== Relatório de Validação v2.0 ===\n";
      report += StringFormat("Última validação: %s\n", TimeToString(m_last_validation));
      report += StringFormat("Status geral: %s\n", m_is_valid ? "VÁLIDO" : "INVÁLIDO");
      report += StringFormat("Status atual: %d\n", m_metrics.current_status);
      report += StringFormat("Taxa de sucesso: %.2f%%\n", m_metrics.success_rate * 100);
      report += "\n=== Contadores de Severidade ===\n";
      report += StringFormat("Info: %d\n", m_metrics.info_count);
      report += StringFormat("Warning: %d\n", m_metrics.warning_count);
      report += StringFormat("Error: %d\n", m_metrics.error_count);
      report += StringFormat("Critical: %d\n", m_metrics.critical_count);
      report += "\n=== Último Erro ===\n";
      report += StringFormat("Mensagem: %s\n", m_metrics.last_error);
      report += StringFormat("Código: %d\n\n", m_metrics.last_error_code);
      
      for(int i = 0; i < ArraySize(m_validation_results); i++) {
         report += StringFormat("Módulo: %s\n", m_validation_results[i].module);
         report += StringFormat("Status: %s\n", m_validation_results[i].success ? "OK" : "ERRO");
         if(!m_validation_results[i].success) {
            report += StringFormat("Erro: %s\n", m_validation_results[i].error);
            report += StringFormat("Severidade: %d\n", m_validation_results[i].severity);
            report += StringFormat("Código: %d\n", m_validation_results[i].error_code);
            if(StringLen(m_validation_results[i].details) > 0) {
               report += StringFormat("Detalhes: %s\n", m_validation_results[i].details);
            }
         }
         report += StringFormat("Timestamp: %s\n\n", TimeToString(m_validation_results[i].timestamp));
      }
      
      return report;
   }
   
   bool IsValid() const {
      return m_is_valid;
   }
   
   string GetLastError() const {
      return m_last_error;
   }
   
   ValidationMetrics GetMetrics() const {
      return m_metrics;
   }
   
   void AddDependency(const ModuleDependency &dependency) {
      ArrayResize(m_dependencies, ArraySize(m_dependencies) + 1);
      m_dependencies[ArraySize(m_dependencies) - 1] = dependency;
   }

   // Setters para injeção de dependências
   void SetDarkPool(CDarkPoolModule *dark_pool) {
      m_dark_pool = dark_pool;
   }

   void SetVolatility(CVolatilityQuantum *volatility) {
      m_volatility = volatility;
   }

   void SetQuantumPhysics(CQuantumMarketPhysics *physics, QuantumMetrics &metrics) {
      m_quantum_physics = physics;
      m_qmetrics = metrics;
   }

   void SetRiskManager(CRiskManager *risk, double risk_pct, double sl_pips) {
      m_risk_manager = risk;
      m_risk_percent = risk_pct;
      m_stop_loss_pips = sl_pips;
   }

   // Acessores
   ValidationResult GetValidationResult(int index) {
      return (index >= 0 && index < ArraySize(m_validation_results)) ? m_validation_results[index] : (ValidationResult){"",false,"",0,SEVERITY_INFO,"",0};
   }

   int GetValidationCount() {
      return ArraySize(m_validation_results);
   }

   void Reset() {
      ArrayFree(m_validation_results);
      ZeroMemory(m_metrics);
   }
}; 