//+------------------------------------------------------------------+
//|                                                      Logger.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Arrays\ArrayString.mqh>

// Enumerações
enum ENUM_LOG_LEVEL
{
   LOG_LEVEL_DEBUG,   // Debug
   LOG_LEVEL_INFO,    // Informação
   LOG_LEVEL_WARNING, // Aviso
   LOG_LEVEL_ERROR    // Erro
};

// Classe principal de registro
class CLogger
{
private:
   string m_log_file;
   bool m_console_output;
   bool m_file_output;
   ENUM_LOG_LEVEL m_min_level;
   CArrayString m_log_buffer;
   int m_max_buffer_size;
   
public:
   // Construtor
   CLogger()
   {
      m_log_file = "GALEX_Log.txt";
      m_console_output = true;
      m_file_output = true;
      m_min_level = LOG_LEVEL_INFO;
      m_max_buffer_size = 1000;
      m_log_buffer.Clear();
   }
   
   // Inicialização
   bool Init(string log_file = "", bool console_output = true, bool file_output = true,
             ENUM_LOG_LEVEL min_level = LOG_LEVEL_INFO, int max_buffer_size = 1000)
   {
      if(log_file != "")
         m_log_file = log_file;
         
      m_console_output = console_output;
      m_file_output = file_output;
      m_min_level = min_level;
      m_max_buffer_size = max_buffer_size;
      m_log_buffer.Clear();
      
      if(m_file_output)
      {
         int handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT);
         if(handle == INVALID_HANDLE)
         {
            Print("Erro ao abrir arquivo de log: ", GetLastError());
            return false;
         }
         FileClose(handle);
      }
      
      return true;
   }
   
   // Registrar mensagem
   void Log(ENUM_LOG_LEVEL level, string message)
   {
      if(level < m_min_level)
         return;
         
      string level_str = GetLevelString(level);
      string time_str = TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS);
      string log_message = StringFormat("%s [%s] %s", time_str, level_str, message);
      
      // Adicionar ao buffer
      if(m_log_buffer.Total() >= m_max_buffer_size)
         m_log_buffer.Delete(0);
      m_log_buffer.Add(log_message);
      
      // Saída no console
      if(m_console_output)
      {
         switch(level)
         {
            case LOG_LEVEL_DEBUG:
               Print(log_message);
               break;
            case LOG_LEVEL_INFO:
               Print(log_message);
               break;
            case LOG_LEVEL_WARNING:
               Print("AVISO: ", log_message);
               break;
            case LOG_LEVEL_ERROR:
               Print("ERRO: ", log_message);
               break;
         }
      }
      
      // Saída em arquivo
      if(m_file_output)
      {
         int handle = FileOpen(m_log_file, FILE_READ|FILE_WRITE|FILE_TXT);
         if(handle != INVALID_HANDLE)
         {
            FileSeek(handle, 0, SEEK_END);
            FileWriteString(handle, log_message + "\n");
            FileClose(handle);
         }
      }
   }
   
   // Registrar debug
   void Debug(string message)
   {
      Log(LOG_LEVEL_DEBUG, message);
   }
   
   // Registrar informação
   void Info(string message)
   {
      Log(LOG_LEVEL_INFO, message);
   }
   
   // Registrar aviso
   void Warning(string message)
   {
      Log(LOG_LEVEL_WARNING, message);
   }
   
   // Registrar erro
   void Error(string message)
   {
      Log(LOG_LEVEL_ERROR, message);
   }
   
   // Obter buffer de log
   bool GetLogBuffer(string &buffer[], int &count)
   {
      count = m_log_buffer.Total();
      ArrayResize(buffer, count);
      
      for(int i = 0; i < count; i++)
      {
         buffer[i] = m_log_buffer.At(i);
      }
      
      return count > 0;
   }
   
   // Limpar buffer de log
   void ClearBuffer()
   {
      m_log_buffer.Clear();
   }
   
private:
   // Obter string do nível
   string GetLevelString(ENUM_LOG_LEVEL level)
   {
      switch(level)
      {
         case LOG_LEVEL_DEBUG:
            return "DEBUG";
         case LOG_LEVEL_INFO:
            return "INFO";
         case LOG_LEVEL_WARNING:
            return "WARNING";
         case LOG_LEVEL_ERROR:
            return "ERROR";
         default:
            return "UNKNOWN";
      }
   }
}; 