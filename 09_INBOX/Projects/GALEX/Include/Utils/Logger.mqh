//+------------------------------------------------------------------+
//|                                                    Logger.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Constantes de log
#define LOG_LEVEL_INFO 0
#define LOG_LEVEL_WARNING 1
#define LOG_LEVEL_ERROR 2
#define LOG_LEVEL_DEBUG 3

// Classe principal de logging
class CLogger : public ILogger
{
private:
   string m_log_file;
   int m_log_level;
   bool m_console_output;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CLogger()
   {
      m_log_file = "GALEX_Log.txt";
      m_log_level = LOG_LEVEL_INFO;
      m_console_output = true;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_log_file = "GALEX_Log.txt";
      m_log_level = LOG_LEVEL_INFO;
      m_console_output = true;
      m_status = "Initialized";
      m_is_initialized = true;
      
      // Criar arquivo de log
      int file_handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT);
      if(file_handle != INVALID_HANDLE)
      {
         FileClose(file_handle);
         return true;
      }
      
      return false;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      
      int file_handle = FileOpen(m_log_file, FILE_READ|FILE_TXT);
      if(file_handle != INVALID_HANDLE)
      {
         FileClose(file_handle);
         return true;
      }
      
      return false;
   }
   
   void Cleanup() override
   {
      m_log_file = "GALEX_Log.txt";
      m_log_level = LOG_LEVEL_INFO;
      m_console_output = true;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "Logger"; }
   
   // Implementação de ILogger
   bool Log(const string message, const int level = LOG_LEVEL_INFO) override
   {
      if(!m_is_initialized || level < m_log_level) return false;
      
      string level_str = GetLevelString(level);
      string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS);
      string log_message = StringFormat("%s [%s] %s", timestamp, level_str, message);
      
      // Escrever no arquivo de log
      int file_handle = FileOpen(m_log_file, FILE_READ|FILE_WRITE|FILE_TXT);
      if(file_handle != INVALID_HANDLE)
      {
         FileSeek(file_handle, 0, SEEK_END);
         FileWriteString(file_handle, log_message + "\n");
         FileClose(file_handle);
      }
      
      // Escrever no console
      if(m_console_output)
         Print(log_message);
      
      return true;
   }
   
   bool SetLogLevel(const int level) override
   {
      if(!m_is_initialized) return false;
      
      if(level >= LOG_LEVEL_INFO && level <= LOG_LEVEL_DEBUG)
      {
         m_log_level = level;
         return true;
      }
      
      return false;
   }
   
   // Métodos específicos do Logger
   bool Init(const string log_file, const int log_level, const bool console_output)
   {
      m_log_file = log_file;
      m_log_level = log_level;
      m_console_output = console_output;
      
      // Criar arquivo de log
      int file_handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT);
      if(file_handle != INVALID_HANDLE)
      {
         FileClose(file_handle);
         return true;
      }
      
      return false;
   }
   
   // Getters
   string GetLogFile() const { return m_log_file; }
   int GetLogLevel() const { return m_log_level; }
   bool GetConsoleOutput() const { return m_console_output; }
   
private:
   string GetLevelString(const int level)
   {
      switch(level)
      {
         case LOG_LEVEL_INFO: return "INFO";
         case LOG_LEVEL_WARNING: return "WARNING";
         case LOG_LEVEL_ERROR: return "ERROR";
         case LOG_LEVEL_DEBUG: return "DEBUG";
         default: return "UNKNOWN";
      }
   }
}; 