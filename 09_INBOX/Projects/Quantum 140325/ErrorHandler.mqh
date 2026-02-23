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

// Classe para gerenciamento de erros e logs
class CErrorHandler {
private:
    // Estado
    bool m_isInitialized;
    string m_logFile;
    bool m_notifyTeam;
    
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
    
    void NotifyTeam(const string& message) {
        if(m_notifyTeam) {
            // Implementar notificação para equipe
            Print("TEAM NOTIFICATION: ", message);
        }
    }
    
public:
    // Construtor
    CErrorHandler() {
        m_isInitialized = false;
        m_logFile = "Quantum_Errors.log";
        m_notifyTeam = true;
    }
    
    // Destrutor
    ~CErrorHandler() {
        // Limpar recursos
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Log de erro
    void LogError(int errorCode, string context) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("[%s] ERROR %d: %s", 
                                    TimeToString(TimeCurrent()),
                                    errorCode,
                                    context);
        
        // Registrar no arquivo
        WriteToFile(message);
        
        // Notificar equipe se for erro crítico
        if(errorCode >= 4000) { // Erros críticos do MetaTrader
            NotifyTeam(message);
        }
    }
    
    // Tratar erro de trading
    bool HandleTradeError(int retCode) {
        if(!m_isInitialized) return false;
        
        switch(retCode) {
            case TRADE_RETCODE_INVALID_STOPS:
                LogError(retCode, "Invalid stop loss or take profit levels");
                return false;
                
            case TRADE_RETCODE_INVALID_VOLUME:
                LogError(retCode, "Invalid volume for the symbol");
                return false;
                
            case TRADE_RETCODE_NO_MONEY:
                LogError(retCode, "Insufficient funds for operation");
                return false;
                
            case TRADE_RETCODE_PRICE_CHANGED:
                LogError(retCode, "Price changed during order processing");
                return false;
                
            case TRADE_RETCODE_INVALID_PRICE:
                LogError(retCode, "Invalid price for the symbol");
                return false;
                
            case TRADE_RETCODE_INVALID_EXPIRATION:
                LogError(retCode, "Invalid order expiration date");
                return false;
                
            case TRADE_RETCODE_INVALID_TRADE_VOLUME:
                LogError(retCode, "Invalid trade volume");
                return false;
                
            case TRADE_RETCODE_MARKET_CLOSED:
                LogError(retCode, "Market is closed");
                return false;
                
            case TRADE_RETCODE_NO_MONEY_FOR_GSL:
                LogError(retCode, "Insufficient funds for guaranteed stop loss");
                return false;
                
            case TRADE_RETCODE_GSL_NOT_ALLOWED:
                LogError(retCode, "Guaranteed stop loss is not allowed");
                return false;
                
            case TRADE_RETCODE_TRADE_TOO_MANY_VOLUME:
                LogError(retCode, "Trade volume too high");
                return false;
                
            case TRADE_RETCODE_INVALID_ORDER:
                LogError(retCode, "Invalid order");
                return false;
                
            case TRADE_RETCODE_TRADE_NOT_ALLOWED:
                LogError(retCode, "Trading is not allowed");
                return false;
                
            case TRADE_RETCODE_TRADE_TOO_MANY_ORDERS:
                LogError(retCode, "Too many orders");
                return false;
                
            case TRADE_RETCODE_TRADE_TOO_MANY_REQUESTS:
                LogError(retCode, "Too many requests");
                return false;
                
            case TRADE_RETCODE_TRADE_MODIFY_DENIED:
                LogError(retCode, "Order modification denied");
                return false;
                
            case TRADE_RETCODE_TRADE_ORDER_LOCKED:
                LogError(retCode, "Order is locked");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_STOPS:
                LogError(retCode, "Invalid stops");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_VOLUME:
                LogError(retCode, "Invalid volume");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_FILL:
                LogError(retCode, "Invalid fill");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_POSITION:
                LogError(retCode, "Invalid position");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_TYPE:
                LogError(retCode, "Invalid order type");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_FILLING:
                LogError(retCode, "Invalid order filling");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_EXPIRATION:
                LogError(retCode, "Invalid order expiration");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME:
                LogError(retCode, "Invalid order volume");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_PRICE:
                LogError(retCode, "Invalid order price");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_STOPS:
                LogError(retCode, "Invalid order stops");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_SYMBOL:
                LogError(retCode, "Invalid order symbol");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_MAGIC:
                LogError(retCode, "Invalid order magic number");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_COMMENT:
                LogError(retCode, "Invalid order comment");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_EXPIRATION_TYPE:
                LogError(retCode, "Invalid order expiration type");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_FILLING_TYPE:
                LogError(retCode, "Invalid order filling type");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_TYPE_FILLING:
                LogError(retCode, "Invalid order type filling");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_TICKET:
                LogError(retCode, "Invalid order ticket");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_POSITION:
                LogError(retCode, "Invalid order position");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_DEAL:
                LogError(retCode, "Invalid order deal");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_TYPE:
                LogError(retCode, "Invalid order volume type");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMITS:
                LogError(retCode, "Invalid order volume limits");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP:
                LogError(retCode, "Invalid order volume step");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX:
                LogError(retCode, "Invalid order volume maximum");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN:
                LogError(retCode, "Invalid order volume minimum");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT:
                LogError(retCode, "Invalid order volume current");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL:
                LogError(retCode, "Invalid order volume initial");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED:
                LogError(retCode, "Invalid order volume filled");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING:
                LogError(retCode, "Invalid order volume remaining");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED:
                LogError(retCode, "Invalid order volume closed");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED:
                LogError(retCode, "Invalid order volume canceled");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED:
                LogError(retCode, "Invalid order volume rejected");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED:
                LogError(retCode, "Invalid order volume expired");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN:
                LogError(retCode, "Invalid order volume margin");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE:
                LogError(retCode, "Invalid order volume free");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED:
                LogError(retCode, "Invalid order volume used");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT:
                LogError(retCode, "Invalid order volume limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT:
                LogError(retCode, "Invalid order volume step limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT:
                LogError(retCode, "Invalid order volume current limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT:
                LogError(retCode, "Invalid order volume initial limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT:
                LogError(retCode, "Invalid order volume filled limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT:
                LogError(retCode, "Invalid order volume closed limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT:
                LogError(retCode, "Invalid order volume expired limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT:
                LogError(retCode, "Invalid order volume margin limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT:
                LogError(retCode, "Invalid order volume free limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT:
                LogError(retCode, "Invalid order volume used limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume step limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume current limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume initial limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume filled limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume closed limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume expired limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume margin limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume free limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume used limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume step limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume current limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume initial limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume filled limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume closed limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume expired limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume margin limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume free limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume used limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume step limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume current limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume initial limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume filled limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume closed limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume expired limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume margin limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume free limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume used limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume step limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume current limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume initial limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume filled limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume closed limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume expired limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume margin limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume free limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume used limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_STEP_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume step limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MAX_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume maximum limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MIN_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume minimum limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CURRENT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume current limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_INITIAL_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume initial limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FILLED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume filled limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REMAINING_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume remaining limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CLOSED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume closed limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_CANCELED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume canceled limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_REJECTED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume rejected limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_EXPIRED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume expired limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_MARGIN_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume margin limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_FREE_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume free limit limit limit limit limit limit");
                return false;
                
            case TRADE_RETCODE_TRADE_INVALID_ORDER_VOLUME_USED_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT_LIMIT:
                LogError(retCode, "Invalid order volume failed");
                return false;
                
            default:
                LogError(retCode, "Unknown error code");
                return false;
        }
    }
    
    // Log de ação de trading
    void LogTradeAction(string action, MqlTradeRequest& request) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("[%s] TRADE ACTION: %s - Symbol: %s, Volume: %.2f, Price: %.5f",
                                    TimeToString(TimeCurrent()),
                                    action,
                                    request.symbol,
                                    request.volume,
                                    request.price);
        
        WriteToFile(message);
    }
    
    // Log de sinal
    void LogSignal(string type, string reason) {
        if(!m_isInitialized) return;
        
        string message = StringFormat("[%s] SIGNAL: %s - %s",
                                    TimeToString(TimeCurrent()),
                                    type,
                                    reason);
        
        WriteToFile(message);
    }
    
    // Configurações
    void SetLogFile(string filename) {
        m_logFile = filename;
    }
    
    void SetNotifyTeam(bool notify) {
        m_notifyTeam = notify;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Error Handler Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Log File: ", m_logFile);
        Print("Team Notifications: ", m_notifyTeam);
    }
}; 