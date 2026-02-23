#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Níveis de log
enum LogLevel {
    LOG_ERROR,    // Erro crítico
    LOG_WARNING,  // Aviso
    LOG_INFO,     // Informação
    LOG_DEBUG     // Debug
};

// Classe para logging detalhado
class CLogger {
private:
    // Estado
    bool m_isInitialized;
    string m_logFile;
    LogLevel m_minLevel;
    bool m_consoleOutput;
    
    // Métodos privados
    string GetLogLevelString(LogLevel level) {
        switch(level) {
            case LOG_ERROR: return "ERROR";
            case LOG_WARNING: return "WARNING";
            case LOG_INFO: return "INFO";
            case LOG_DEBUG: return "DEBUG";
            default: return "UNKNOWN";
        }
    }
    
    void WriteToFile(const string& message) {
        int handle = FileOpen(m_logFile, FILE_WRITE|FILE_TXT|FILE_COMMON);
        if(handle != INVALID_HANDLE) {
            FileSeek(handle, 0, SEEK_END);
            FileWriteString(handle, message + "\n");
            FileClose(handle);
        }
    }
    
    void WriteToConsole(const string& message) {
        if(m_consoleOutput) {
            Print(message);
        }
    }
    
public:
    // Construtor
    CLogger() {
        m_isInitialized = false;
        m_logFile = "Quantum_Log.log";
        m_minLevel = LOG_INFO;
        m_consoleOutput = true;
    }
    
    // Destrutor
    ~CLogger() {
        // Limpar recursos
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Log de mensagem
    void Log(LogLevel level, string message) {
        if(!m_isInitialized) return;
        if(level > m_minLevel) return;
        
        string timestamp = TimeToString(TimeCurrent());
        string levelStr = GetLogLevelString(level);
        string fullMessage = StringFormat("[%s] %s: %s", timestamp, levelStr, message);
        
        WriteToFile(fullMessage);
        WriteToConsole(fullMessage);
    }
    
    // Log de erro
    void LogError(string message) {
        Log(LOG_ERROR, message);
    }
    
    // Log de aviso
    void LogWarning(string message) {
        Log(LOG_WARNING, message);
    }
    
    // Log de informação
    void LogInfo(string message) {
        Log(LOG_INFO, message);
    }
    
    // Log de debug
    void LogDebug(string message) {
        Log(LOG_DEBUG, message);
    }
    
    // Log de ação de trading
    void LogTradeAction(string action, MqlTradeRequest& request) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("TRADE ACTION: %s - Symbol: %s, Volume: %.2f, Price: %.5f",
                                    action,
                                    request.symbol,
                                    request.volume,
                                    request.price);
        
        LogInfo(message);
    }
    
    // Log de sinal
    void LogSignal(string type, string reason) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("SIGNAL: %s - %s",
                                    type,
                                    reason);
        
        LogInfo(message);
    }
    
    // Log de métricas
    void LogMetrics(const string& component, const string& metrics) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("METRICS [%s]: %s",
                                    component,
                                    metrics);
        
        LogDebug(message);
    }
    
    // Configurações
    void SetLogFile(string filename) {
        m_logFile = filename;
    }
    
    void SetMinLevel(LogLevel level) {
        m_minLevel = level;
    }
    
    void SetConsoleOutput(bool output) {
        m_consoleOutput = output;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Logger Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Log File: ", m_logFile);
        Print("Minimum Level: ", GetLogLevelString(m_minLevel));
        Print("Console Output: ", m_consoleOutput);
    }
}; 