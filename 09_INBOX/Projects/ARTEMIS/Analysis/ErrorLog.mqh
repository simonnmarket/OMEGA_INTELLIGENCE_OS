//+------------------------------------------------------------------+
//|                                          ErrorLog.mqh             |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Constantes para níveis de severidade                              |
//+------------------------------------------------------------------+
#define SEVERITY_LOW      1
#define SEVERITY_MEDIUM   2
#define SEVERITY_HIGH     3
#define SEVERITY_CRITICAL 4

//+------------------------------------------------------------------+
//| Constantes para tipos de erro                                     |
//+------------------------------------------------------------------+
#define ERROR_TYPE_SYSTEM     "SYSTEM"
#define ERROR_TYPE_NETWORK    "NETWORK"
#define ERROR_TYPE_DATABASE   "DATABASE"
#define ERROR_TYPE_BUSINESS   "BUSINESS"
#define ERROR_TYPE_SECURITY   "SECURITY"
#define ERROR_TYPE_PERFORMANCE "PERFORMANCE"

//+------------------------------------------------------------------+
//| Constantes para componentes                                       |
//+------------------------------------------------------------------+
#define COMPONENT_CORE        "CORE"
#define COMPONENT_QUANTUM     "QUANTUM"
#define COMPONENT_AGENT       "AGENT"
#define COMPONENT_RISK        "RISK"
#define COMPONENT_ANALYSIS    "ANALYSIS"
#define COMPONENT_GUI         "GUI"
#define COMPONENT_NEURAL      "NEURAL"

//+------------------------------------------------------------------+
//| Classe para registro de erros                                     |
//+------------------------------------------------------------------+
class CErrorLog : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   string m_log_file;                    // Arquivo de log
   bool m_is_initialized;                // Se está inicializado
   datetime m_last_update;               // Última atualização
   int m_error_count;                    // Contagem de erros
   int m_warning_count;                  // Contagem de avisos
   int m_critical_count;                 // Contagem de erros críticos
   
public:
   // Construtor
   CErrorLog(CLogger* logger)
   {
      m_logger = logger;
      m_log_file = "error_log.txt";
      m_is_initialized = false;
      m_error_count = 0;
      m_warning_count = 0;
      m_critical_count = 0;
      m_last_update = 0;
      
      if(m_logger != NULL)
      {
         m_logger.Info("Sistema de registro de erros inicializado");
         m_is_initialized = true;
      }
   }
   
   // Destrutor
   ~CErrorLog()
   {
      if(m_logger != NULL)
         m_logger.Info("Sistema de registro de erros finalizado");
   }
   
   // Registra erro
   bool LogError(string message, string source, int severity, string type = ERROR_TYPE_SYSTEM)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      // Atualiza contadores
      m_error_count++;
      if(severity == SEVERITY_CRITICAL)
         m_critical_count++;
      else if(severity == SEVERITY_LOW)
         m_warning_count++;
         
      // Registra no arquivo
      string log_entry = StringFormat("%s [%s] %s: %s", 
                                    TimeToString(TimeCurrent()),
                                    type,
                                    source,
                                    message);
                                    
      if(!WriteToFile(log_entry))
         m_logger.Warning("Falha ao escrever no arquivo de log");
         
      m_last_update = TimeCurrent();
      return true;
   }
   
   // Registra propagação de erro
   bool LogPropagation(string source, string target, string message, int severity)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      // Registra no arquivo
      string log_entry = StringFormat("%s [PROPAGATION] %s -> %s: %s",
                                    TimeToString(TimeCurrent()),
                                    source,
                                    target,
                                    message);
                                    
      if(!WriteToFile(log_entry))
         m_logger.Warning("Falha ao escrever no arquivo de log");
         
      m_last_update = TimeCurrent();
      return true;
   }
   
   // Registra dependência
   bool LogDependency(string component, string dependency, string type, int severity)
   {
      if(!m_is_initialized || m_logger == NULL)
         return false;
         
      // Registra no arquivo
      string log_entry = StringFormat("%s [DEPENDENCY] %s -> %s: %s",
                                    TimeToString(TimeCurrent()),
                                    component,
                                    dependency,
                                    type);
                                    
      if(!WriteToFile(log_entry))
         m_logger.Warning("Falha ao escrever no arquivo de log");
         
      m_last_update = TimeCurrent();
      return true;
   }
   
   // Obtém estatísticas
   void GetStatistics(int& total_errors, int& critical_errors,
                     int& total_propagations, int& total_dependencies)
   {
      total_errors = m_error_count;
      critical_errors = m_critical_count;
      total_propagations = 0;
      total_dependencies = 0;
   }
   
   // Limpa dados antigos
   void CleanupOldData(int days)
   {
      // Implementar limpeza de dados antigos
   }
   
private:
   // Escreve no arquivo de log
   bool WriteToFile(string content)
   {
      int handle = FileOpen(m_log_file, FILE_WRITE|FILE_READ|FILE_TXT);
      
      if(handle != INVALID_HANDLE)
      {
         FileSeek(handle, 0, SEEK_END);
         FileWriteString(handle, content + "\n");
         FileClose(handle);
         return true;
      }
      
      return false;
   }
}; 