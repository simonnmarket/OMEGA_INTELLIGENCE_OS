// utils/logger_institutional.mqh

#ifndef __LOGGER_INSTITUTIONAL_MQH__
#define __LOGGER_INSTITUTIONAL_MQH__

class logger_institutional {
public:
   void log_info(string msg)    { Print("[INFO]: " + msg); }
   void log_warning(string msg) { Print("[WARNING]: " + msg); }
   void log_error(string msg)   { Print("[ERROR]: " + msg); }
   void log_debug(string msg)   { Print("[DEBUG]: " + msg); }
};

#endif