#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "4.0"

//+------------------------------------------------------------------+
//| Classe para gerenciamento de logs do sistema                       |
//+------------------------------------------------------------------+
class CQuantumLogger {
private:
    string systemName;
    string logFileName;
    bool logToFile;
    bool logToTerminal;
    
    void WriteToFile(const string &message) {
        if(!logToFile) return;
        
        int handle = FileOpen(logFileName, FILE_WRITE|FILE_READ|FILE_TXT);
        if(handle != INVALID_HANDLE) {
            FileSeek(handle, 0, SEEK_END);
            FileWriteString(handle, message + "\n");
            FileClose(handle);
        }
    }
    
    string FormatMessage(const string &level, const string &message) {
        string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS);
        return StringFormat("[%s][%s][%s] %s", timestamp, systemName, level, message);
    }
    
public:
    CQuantumLogger(const string name, bool toFile = true, bool toTerminal = true) {
        systemName = name;
        logToFile = toFile;
        logToTerminal = toTerminal;
        logFileName = "QuantumLogs\\" + name + "_" + TimeToString(TimeCurrent(), TIME_DATE) + ".log";
        
        // Criar diretório de logs se não existir
        string dirPath = "QuantumLogs";
        if(!FolderCreate(dirPath)) {
            Print("Erro ao criar diretório de logs: ", GetLastError());
        }
    }
    
    void Info(const string &message) {
        string formattedMsg = FormatMessage("INFO", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
    }
    
    void Warning(const string &message) {
        string formattedMsg = FormatMessage("WARNING", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
    }
    
    void Error(const string &message) {
        string formattedMsg = FormatMessage("ERROR", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
    }
    
    void Debug(const string &message) {
        #ifdef _DEBUG
        string formattedMsg = FormatMessage("DEBUG", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
        #endif
    }
    
    void Trade(const string &message) {
        string formattedMsg = FormatMessage("TRADE", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
    }
    
    void Performance(const string &message) {
        string formattedMsg = FormatMessage("PERFORMANCE", message);
        if(logToTerminal) Print(formattedMsg);
        WriteToFile(formattedMsg);
    }
};