//+------------------------------------------------------------------+
//| CLogger.mqh - Advanced Logging System                            |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

//+------------------------------------------------------------------+
//| Níveis de log                                                     |
//+------------------------------------------------------------------+
enum ENUM_LOG_LEVEL
{
   LOG_LEVEL_DEBUG,    // Debug
   LOG_LEVEL_INFO,     // Info
   LOG_LEVEL_WARNING,  // Warning
   LOG_LEVEL_ERROR,    // Error
   LOG_LEVEL_CRITICAL  // Critical
};

class CLogger : public CObject {
private:
   string m_filename;
   ENUM_LOG_LEVEL m_level;
   bool m_is_initialized;
   
public:
   CLogger(string filename = "log.txt", ENUM_LOG_LEVEL level = LOG_LEVEL_INFO) {
      m_filename = filename;
      m_level = level;
      m_is_initialized = false;
      
      int handle = FileOpen(m_filename, FILE_WRITE|FILE_READ|FILE_TXT);
      if(handle != INVALID_HANDLE) {
         FileClose(handle);
         m_is_initialized = true;
      }
   }
   
   ~CLogger() {
   }
   
   void SetLevel(ENUM_LOG_LEVEL level) {
      m_level = level;
   }
   
   void Debug(string message) {
      if(m_level <= LOG_LEVEL_DEBUG)
         WriteLog("DEBUG", message);
   }
   
   void Info(string message) {
      if(m_level <= LOG_LEVEL_INFO)
         WriteLog("INFO", message);
   }
   
   void Warning(string message) {
      if(m_level <= LOG_LEVEL_WARNING)
         WriteLog("WARNING", message);
   }
   
   void Error(string message) {
      if(m_level <= LOG_LEVEL_ERROR)
         WriteLog("ERROR", message);
   }
   
   void Critical(string message) {
      if(m_level <= LOG_LEVEL_CRITICAL)
         WriteLog("CRITICAL", message);
   }
   
private:
   void WriteLog(string level, string message) {
      if(!m_is_initialized)
         return;
         
      int handle = FileOpen(m_filename, FILE_WRITE|FILE_READ|FILE_TXT);
      if(handle != INVALID_HANDLE) {
         FileSeek(handle, 0, SEEK_END);
         string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS);
         string log_entry = StringFormat("%s [%s] %s\n", timestamp, level, message);
         FileWriteString(handle, log_entry);
         FileClose(handle);
      }
   }
};