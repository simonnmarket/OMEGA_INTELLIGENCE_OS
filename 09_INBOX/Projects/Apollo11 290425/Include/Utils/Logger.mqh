//+------------------------------------------------------------------+
//|                                                    Logger.mqh |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

class CLogger {
private:
    string logFileName;
    bool isInitialized;
    
public:
    CLogger() {
        logFileName = "Apollo11_" + TimeToString(TimeCurrent(), TIME_DATE) + ".log";
        isInitialized = false;
    }
    
    bool Initialize() {
        int handle = FileOpen(logFileName, FILE_WRITE|FILE_READ|FILE_TXT);
        if(handle == INVALID_HANDLE) {
            Print("Erro ao inicializar arquivo de log: ", GetLastError());
            return false;
        }
        FileClose(handle);
        isInitialized = true;
        return true;
    }
    
    void Log(string message, bool printToConsole = true) {
        if(!isInitialized) {
            if(!Initialize()) return;
        }
        
        string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
        string logMessage = timestamp + " - " + message;
        
        if(printToConsole) Print(logMessage);
        
        int handle = FileOpen(logFileName, FILE_WRITE|FILE_READ|FILE_TXT);
        if(handle != INVALID_HANDLE) {
            FileSeek(handle, 0, SEEK_END);
            FileWrite(handle, logMessage);
            FileClose(handle);
        }
    }
    
    void LogError(string message, int errorCode) {
        Log("ERRO [" + IntegerToString(errorCode) + "]: " + message);
    }
    
    void LogTrade(string symbol, double lotSize, double price, double sl, double tp, string type) {
        string message = "TRADE " + type + " - " + symbol + 
                        " | Lote: " + DoubleToString(lotSize, 2) +
                        " | Preço: " + DoubleToString(price, _Digits) +
                        " | SL: " + DoubleToString(sl, _Digits) +
                        " | TP: " + DoubleToString(tp, _Digits);
        Log(message);
    }
    
    void LogPositionClosed(ulong ticket, double profit) {
        string message = "POSIÇÃO FECHADA - Ticket: " + IntegerToString(ticket) +
                        " | Lucro: " + DoubleToString(profit, 2);
        Log(message);
    }
}; 