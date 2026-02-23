//+------------------------------------------------------------------+
//|                                               MarketCore.mqh |
//|                                  Copyright 2024, Raio X Universal |
//|                                             https://www.raio-x.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Raio X Universal"
#property link      "https://www.raio-x.com"
#property version   "1.00"
#property strict

// Logger Class
class CLogger
{
private:
    string m_name;
    bool m_debugMode;
    
public:
    CLogger(string name, bool debugMode = false)
    {
        m_name = name;
        m_debugMode = debugMode;
    }
    
    void Info(string message)
    {
        if(m_debugMode)
        {
            Print("[", m_name, "] INFO: ", message);
        }
    }
    
    void Warning(string message)
    {
        if(m_debugMode)
        {
            Print("[", m_name, "] WARNING: ", message);
        }
    }
    
    void Error(string message)
    {
        Print("[", m_name, "] ERROR: ", message);
    }
    
    void Debug(string message)
    {
        if(m_debugMode)
        {
            Print("[", m_name, "] DEBUG: ", message);
        }
    }
};