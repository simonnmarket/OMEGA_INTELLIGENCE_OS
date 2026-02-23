// 📄 Prometheus_Bridge_v3.mq5
#property strict
#property copyright "PROMETHEUS_TRADING_SYSTEM"
#property version   "3.0"
#property description "Prometheus Bridge v3.0 - Sistema Enterprise com Correções Críticas"

#include <Trade/Trade.mqh>
#include <Arrays/ArrayString.mqh>
#include <Generic/HashMap.mqh>

// =============================================================================
// CONSTANTES NOMEADAS - ZERO MAGIC NUMBERS
// =============================================================================
#define MAGIC_NUMBER_DEFAULT 202412
#define MAX_RETRY_ATTEMPTS 3
#define FILE_OPERATION_TIMEOUT_MS 1500
#define MAX_SPREAD_VALIDATION_PCT 20.0

// =============================================================================
// ESTRUTURAS DE DADOS ROBUSTAS v3.0
// =============================================================================
struct MarketData {
    string symbol;
    double bid;
    double ask;
    datetime timestamp;
    double point;
    bool isValid;
    
    MarketData() {
        isValid = false;
        bid = 0.0;
        ask = 0.0;
        timestamp = 0;
        point = 0.0;
    }
    
    bool Validate() {
        if(bid <= 0.0 || ask <= 0.0) {
            Print("[VALIDATION] Invalid bid/ask: ", bid, "/", ask);
            return false;
        }
        if(ask < bid) {
            Print("[VALIDATION] Ask < Bid: ", ask, " < ", bid);
            return false;
        }
        double spread = ask - bid;
        double mid = (ask + bid) / 2.0;
        if(spread / mid > MAX_SPREAD_VALIDATION_PCT / 100.0) {
            Print("[VALIDATION] Spread too wide: ", DoubleToString(spread/mid*100, 2), "%");
            return false;
        }
        if(!MathIsValidNumber(bid) || !MathIsValidNumber(ask)) {
            Print("[VALIDATION] NaN/Inf detected");
            return false;
        }
        isValid = true;
        return true;
    }
};

struct TradingSignal {
    string symbol;
    string action;
    double confidence;
    datetime timestamp;
    bool isValid;
    
    TradingSignal() {
        isValid = false;
        confidence = 0.0;
    }
    
    bool Validate() {
        if(action != "BUY" && action != "SELL" && action != "HOLD") {
            Print("[SIGNAL_VALIDATION] Invalid action: ", action);
            return false;
        }
        if(confidence < 0.0 || confidence > 1.0 || !MathIsValidNumber(confidence)) {
            Print("[SIGNAL_VALIDATION] Invalid confidence: ", confidence);
            return false;
        }
        if(StringLen(symbol) == 0) {
            Print("[SIGNAL_VALIDATION] Empty symbol");
            return false;
        }
        isValid = true;
        return true;
    }
};

// =============================================================================
// GESTÃO DE ESTADO SEGURA v3.0
// =============================================================================
class SafeStateManager {
private:
    bool emergency_stop;
    datetime emergency_trigger_time;
    double daily_start_equity;
    datetime last_reset_check;
    
public:
    SafeStateManager() {
        emergency_stop = false;
        emergency_trigger_time = 0;
        daily_start_equity = AccountInfoDouble(ACCOUNT_EQUITY);
        last_reset_check = TimeCurrent();
    }
    
    bool CanTrade() {
        CheckAutoReset();
        return !emergency_stop;
    }
    
    void TriggerEmergencyStop(const string reason) {
        emergency_stop = true;
        emergency_trigger_time = TimeCurrent();
        Print("[EMERGENCY_STOP] Activated: ", reason);
    }
    
    void CheckAutoReset() {
        datetime current_time = TimeCurrent();
        
        // Reset diário automático às 00:00
        MqlDateTime dt;
        TimeToStruct(current_time, dt);
        if(dt.hour == 0 && dt.min == 0 && dt.sec < 30) {
            if(emergency_stop) {
                emergency_stop = false;
                daily_start_equity = AccountInfoDouble(ACCOUNT_EQUITY);
                Print("[AUTO_RESET] Daily reset completed");
            }
        }
        
        // Reset após 1 hora em emergência
        if(emergency_stop && (current_time - emergency_trigger_time) >= 3600) {
            double current_equity = AccountInfoDouble(ACCOUNT_EQUITY);
            double recovery_pct = (current_equity - daily_start_equity) / daily_start_equity * 100.0;
            
            if(recovery_pct >= -1.0) {
                emergency_stop = false;
                Print("[AUTO_RESET] Emergency reset after recovery: ", DoubleToString(recovery_pct, 2), "%");
            }
        }
        
        last_reset_check = current_time;
    }
    
    bool IsInEmergency() const { return emergency_stop; }
    datetime GetEmergencyTime() const { return emergency_trigger_time; }
    double GetDailyStartEquity() const { return daily_start_equity; }
};

// =============================================================================
// COMUNICAÇÃO ATÔMICA COM SERVIDOR AI v3.0
// =============================================================================
class AtomicFileBridge {
private:
    string common_path;
    int timeout_ms;
    
public:
    AtomicFileBridge() {
        common_path = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\";
        timeout_ms = FILE_OPERATION_TIMEOUT_MS;
    }
    
    bool SendRequest(const string symbol) {
        MarketData data = GetMarketData(symbol);
        if(!data.Validate()) {
            Print("[BRIDGE] Invalid market data for ", symbol);
            return false;
        }
        
        // Usar nomes relativos com FILE_COMMON para operar em Common/Files
        string temp_file = "AIRequest." + symbol + ".tmp";
        string final_file = "AIRequest." + symbol + ".json";
        
        string payload = StringFormat(
            "{\"symbol\":\"%s\",\"bid\":%.10f,\"ask\":%.10f,\"time\":%I64d,\"point\":%.10f}",
            symbol, data.bid, data.ask, (long)data.timestamp, data.point
        );
        
        // Escreve em arquivo temporário primeiro - CORREÇÃO CEO
        Print("[BRIDGE_DEBUG] Attempting to create: ", temp_file);
        Print("[BRIDGE_DEBUG] Common path: ", common_path);
        
        int handle = FileOpen(temp_file, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
        if(handle == INVALID_HANDLE) {
            int error = GetLastError();
            Print("[BRIDGE_ERROR] Failed to open temp file: ", temp_file, " Error: ", error);
            Print("[BRIDGE_ERROR] Common path exists: ", FileIsExist(common_path));
            return false;
        }
        Print("[BRIDGE_DEBUG] File handle created successfully: ", handle);
        
        // Escrever payload com logs detalhados
        FileWriteString(handle, payload);
        Print("[BRIDGE_DEBUG] Payload written, length: ", StringLen(payload));
        
        // Flush com verificação
        FileFlush(handle);
        Print("[BRIDGE_DEBUG] File flushed");
        
        // Close com verificação
        FileClose(handle);
        Print("[BRIDGE_DEBUG] File closed");
        
        // Verificar se arquivo foi criado
        if(FileIsExist(temp_file, FILE_COMMON)) {
            Print("[BRIDGE_DEBUG] Temp file exists after write: ", temp_file);
        } else {
            Print("[BRIDGE_ERROR] Temp file NOT created: ", temp_file);
        }
        
        // CORREÇÃO: Usar caminho absoluto para FileMove() - FILE_COMMON não funciona
        string temp_path = common_path + temp_file;
        string final_path = common_path + final_file;
        
        Print("[BRIDGE_DEBUG] Attempting absolute move: ", temp_path, " -> ", final_path);
        
        // CORREÇÃO CEO: Deletar arquivo final se existir antes do copy
        if(FileIsExist(final_file, FILE_COMMON)) {
            FileDelete(final_file, FILE_COMMON);
            Print("[BRIDGE_DEBUG] Deleted existing final file: ", final_file);
        }
        
        // Usar CopyFile + DeleteFile em vez de FileMove
        if(!FileCopy(temp_file, FILE_COMMON, final_file, FILE_COMMON)) {
            int copy_error = GetLastError();
            Print("[BRIDGE_ERROR] File copy failed: ", copy_error);
            FileDelete(temp_file, FILE_COMMON);
            return false;
        }
        
        // Deletar arquivo temporário
        if(!FileDelete(temp_file, FILE_COMMON)) {
            Print("[BRIDGE_WARNING] Failed to delete temp file: ", GetLastError());
        }
        
        Print("[BRIDGE_DEBUG] File copy successful");
        Print("[BRIDGE_DEBUG] Final file exists: ", FileIsExist(final_file, FILE_COMMON));
        
        return true;
    }
    
    bool ReceiveResponse(const string symbol, TradingSignal &signal) {
        // Usar nomes relativos com FILE_COMMON para leitura segura do Common/Files
        string response_file = "AIResponse." + symbol + ".json";
        string temp_file = "AIResponse." + symbol + ".tmp";
        
        uint start_ms = GetTickCount();
        while(GetTickCount() - start_ms < (uint)timeout_ms) {
            if(FileIsExist(response_file, FILE_COMMON)) {
                int handle = FileOpen(response_file, FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_COMMON);
                if(handle != INVALID_HANDLE) {
                    string content = FileReadString(handle, (int)FileSize(handle));
                    FileClose(handle);
                    if(ParseSignal(content, signal) && signal.Validate()) {
                        FileMove(response_file, FILE_COMMON, temp_file, FILE_REWRITE);
                        FileDelete(temp_file, FILE_COMMON);
                        return true;
                    }
                }
            }
            Sleep(10);
        }
        
        return false;
    }
    
private:
    MarketData GetMarketData(const string symbol) {
        MarketData data;
        data.symbol = symbol;
        
        MqlTick tick;
        if(SymbolInfoTick(symbol, tick)) {
            data.bid = tick.bid;
            data.ask = tick.ask;
            data.timestamp = tick.time;
            data.point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        }
        
        return data;
    }
    
    bool ParseSignal(const string json_content, TradingSignal &signal) {
        Print("[PARSER_DEBUG] JSON content: ", json_content);
        Print("[PARSER_DEBUG] JSON length: ", StringLen(json_content));
        
        // Método mais robusto: usar StringSplit para dividir o JSON
        string parts[];
        int count = StringSplit(json_content, ',', parts);
        
        if(count < 3) {
            Print("[PARSER_ERROR] Invalid JSON format - not enough parts");
            return false;
        }
        
        // Processar cada parte
        for(int i = 0; i < count; i++) {
            string part = parts[i];
            StringTrimLeft(part);
            StringTrimRight(part);
            
            Print("[PARSER_DEBUG] Processing part ", i, ": ", part);
            
            // Extrair campo "symbol"
            if(StringFind(part, "\"symbol\"") >= 0) {
                int colon_pos = StringFind(part, ":");
                if(colon_pos >= 0) {
                    string value = StringSubstr(part, colon_pos + 1);
                    StringTrimLeft(value);
                    StringTrimRight(value);
                    // Remover aspas
                    if(StringFind(value, "\"") >= 0) {
                        int start = StringFind(value, "\"") + 1;
                        int end = StringFind(value, "\"", start);
                        if(end > start) {
                            signal.symbol = StringSubstr(value, start, end - start);
                            Print("[PARSER_DEBUG] Found symbol: ", signal.symbol);
                        }
                    }
                }
            }
            
            // Extrair campo "action"
            if(StringFind(part, "\"action\"") >= 0) {
                int colon_pos = StringFind(part, ":");
                if(colon_pos >= 0) {
                    string value = StringSubstr(part, colon_pos + 1);
                    StringTrimLeft(value);
                    StringTrimRight(value);
                    // Remover aspas
                    if(StringFind(value, "\"") >= 0) {
                        int start = StringFind(value, "\"") + 1;
                        int end = StringFind(value, "\"", start);
                        if(end > start) {
                            signal.action = StringSubstr(value, start, end - start);
                            Print("[PARSER_DEBUG] Found action: ", signal.action);
                        }
                    }
                }
            }
            
            // Extrair campo "confidence"
            if(StringFind(part, "\"confidence\"") >= 0) {
                int colon_pos = StringFind(part, ":");
                if(colon_pos >= 0) {
                    string value = StringSubstr(part, colon_pos + 1);
                    StringTrimLeft(value);
                    StringTrimRight(value);
                    // Remover chaves finais se existirem
                    if(StringFind(value, "}") >= 0) {
                        value = StringSubstr(value, 0, StringFind(value, "}"));
                    }
                    signal.confidence = StringToDouble(value);
                    Print("[PARSER_DEBUG] Found confidence: ", signal.confidence);
                }
            }
        }
        
        // Validar se todos os campos foram encontrados
        if(StringLen(signal.symbol) == 0) {
            Print("[PARSER_ERROR] Symbol not found");
            return false;
        }
        if(StringLen(signal.action) == 0) {
            Print("[PARSER_ERROR] Action not found");
            return false;
        }
        if(signal.confidence < 0 || signal.confidence > 1) {
            Print("[PARSER_ERROR] Invalid confidence: ", signal.confidence);
            return false;
        }
        
        signal.timestamp = TimeCurrent();
        Print("[PARSER_SUCCESS] Parsed signal: ", signal.symbol, " ", signal.action, " ", signal.confidence);
        return true;
    }
};

// =============================================================================
// GESTÃO DE RISCO AVANÇADA v3.0
// =============================================================================
class RobustRiskManager {
private:
    double max_risk_pct;
    double kelly_rr;
    double kelly_min_frac;
    double kelly_max_frac;
    double confidence_discount;
    
public:
    RobustRiskManager(double risk_pct = 0.5, double rr = 1.5, double min_frac = 0.05, double max_frac = 0.5) {
        max_risk_pct = risk_pct;
        kelly_rr = rr;
        kelly_min_frac = min_frac;
        kelly_max_frac = max_frac;
        confidence_discount = 0.7;
    }
    
    // CORREÇÃO CRÍTICA: Função CalculateKellyFraction corrigida
    double CalculateKellyFraction(double raw_confidence) {
        double adjusted_confidence = 0.5 + (raw_confidence - 0.5) * confidence_discount;
        adjusted_confidence = MathMin(MathMax(adjusted_confidence, 0.0), 1.0);
        
        double p = adjusted_confidence;
        double r = MathMax(kelly_rr, 0.1);
        double kelly_raw = p - (1.0 - p) / r;
        
        double kelly_clamped = MathMax(0.0, MathMin(kelly_raw, kelly_max_frac));
        return MathMax(kelly_min_frac, kelly_clamped);
    }
    
    // CORREÇÃO CRÍTICA: Função CalculatePositionSize completamente reescrita
    double CalculatePositionSize(const string symbol, double stop_distance, double confidence) {
        // Validações rigorosas
        if(stop_distance <= 0.0) {
            Print("[RISK] Invalid stop distance: ", stop_distance);
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        }
        
        if(!SymbolSelect(symbol, true)) {
            Print("[RISK] Symbol not available: ", symbol);
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        }
        
        double kelly_frac = CalculateKellyFraction(confidence);
        double risk_pct = MathMin(max_risk_pct, kelly_frac * max_risk_pct);
        
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        if(balance <= 0.0) {
            Print("[RISK] Invalid account balance: ", balance);
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        }
        
        double risk_money = balance * (risk_pct / 100.0);
        
        // Cálculo preciso do valor do tick
        double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double tick_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double contract_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
        
        if(tick_value <= 0.0 && contract_size > 0.0 && tick_size > 0.0) {
            // Calcula tick_value se não disponível
            tick_value = tick_size * contract_size;
        }
        
        if(tick_value <= 0.0) {
            Print("[RISK] Cannot calculate tick value for: ", symbol);
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        }
        
        double ticks = stop_distance / tick_size;
        if(ticks <= 0.0) {
            Print("[RISK] Invalid ticks calculation: ", ticks);
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        }
        
        double lots = risk_money / (ticks * tick_value);
        return NormalizeLotSize(symbol, lots);
    }
    
    bool ValidateMarketConditions(const string symbol) {
        if(!SymbolSelect(symbol, true)) {
            Print("[RISK] Symbol not selected: ", symbol);
            return false;
        }
        
        MqlTick tick;
        if(!SymbolInfoTick(symbol, tick)) {
            Print("[RISK] Cannot get tick data for ", symbol);
            return false;
        }
        
        // Validação rigorosa de preços
        if(tick.bid <= 0.0 || tick.ask <= 0.0) {
            Print("[RISK] Invalid prices: bid=", tick.bid, " ask=", tick.ask);
            return false;
        }
        
        if(tick.ask < tick.bid) {
            Print("[RISK] Negative spread: ask=", tick.ask, " bid=", tick.bid);
            return false;
        }
        
        double spread = tick.ask - tick.bid;
        double mid = (tick.ask + tick.bid) / 2.0;
        double spread_pct = (spread / mid) * 100.0;
        
        if(spread_pct > MAX_SPREAD_VALIDATION_PCT) {
            Print("[RISK] Spread too wide: ", DoubleToString(spread_pct, 2), "%");
            return false;
        }
        
        if(!MathIsValidNumber(tick.bid) || !MathIsValidNumber(tick.ask)) {
            Print("[RISK] NaN/Inf detected in prices");
            return false;
        }
        
        return true;
    }
    
private:
    double NormalizeLotSize(const string symbol, double lots) {
        double min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        double step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        
        if(min_lot <= 0.0) min_lot = 0.01;
        if(max_lot <= 0.0) max_lot = 100.0;
        if(step <= 0.0) step = 0.01;
        
        // Normalização precisa
        if(step > 0.0) {
            lots = MathRound(lots / step) * step;
        }
        
        lots = MathMax(min_lot, MathMin(lots, max_lot));
        
        // Arredondamento para casas decimais apropriadas
        int digits = (int)MathMax(-MathLog10(step), 2);
        lots = NormalizeDouble(lots, digits);
        
        return lots;
    }
};

// =============================================================================
// CONFIGURAÇÃO DE INPUTS v3.0
// =============================================================================
input group "=== CORE CONFIGURATION ==="
input string   EA_Name = "PROMETHEUS_BRIDGE_V3";
input int      Magic_Number = MAGIC_NUMBER_DEFAULT;
input bool     Enable_Trading = true;

input group "=== RISK MANAGEMENT ==="  
input double   Max_Risk_Percent = 0.5;
input double   Kelly_Reward_Risk = 1.5;
input double   Kelly_Min_Fraction = 0.05;
input double   Kelly_Max_Fraction = 0.5;
input double   Confidence_Discount = 0.7;

input group "=== CIRCUIT BREAKERS ==="
input bool     Use_Circuit_Breakers = false;
input double   Max_Daily_Loss_Pct = 3.0;
input double   Max_Position_Loss_Pct = 1.0;
input int      Cycle_Interval_Sec = 5;

// =============================================================================
// VARIÁVEIS GLOBAIS CORRIGIDAS v3.0
// =============================================================================
CTrade *Trade; // CORREÇÃO: Usar ponteiro para controle preciso
SafeStateManager state_mgr;
AtomicFileBridge file_bridge;
RobustRiskManager *risk_mgr = NULL; // CORREÇÃO: Inicialização explícita

datetime last_cycle = 0;
string current_symbol = "";

// =============================================================================
// FUNÇÕES PRINCIPAIS CORRIGIDAS v3.0
// =============================================================================
int OnInit() {
    Print("[PROMETHEUS_V3] Initializing Enterprise Edition...");
    
    // CORREÇÃO: Inicialização adequada do objeto Trade
    Trade = new CTrade();
    if(Trade == NULL) {
        Print("[ERROR] Failed to create Trade object");
        return INIT_FAILED;
    }
    
    // Configuração do trade
    Trade.SetExpertMagicNumber(Magic_Number);
    Trade.SetDeviationInPoints(10);
    
    // CORREÇÃO: Inicialização do risk manager com verificação
    risk_mgr = new RobustRiskManager(Max_Risk_Percent, Kelly_Reward_Risk,
                                     Kelly_Min_Fraction, Kelly_Max_Fraction);
    if(risk_mgr == NULL) {
        Print("[ERROR] Failed to create Risk Manager");
        delete Trade;
        return INIT_FAILED;
    }
    
    current_symbol = _Symbol;
    Print("[PROMETHEUS_V3] Initialization complete. Trading: ", current_symbol);

    // Ativa timer para garantir ciclos mesmo sem ticks (smoke/diagnóstico)
    EventSetTimer(Cycle_Interval_Sec);
    Print("[PROMETHEUS_V3] Timer set to ", Cycle_Interval_Sec, "s");
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    Print("[PROMETHEUS_V3] Deinitializing. Reason: ", reason);
    
    // CORREÇÃO: Limpeza segura dos ponteiros
    if(CheckPointer(Trade) == POINTER_DYNAMIC) {
        delete Trade;
    }
    if(CheckPointer(risk_mgr) == POINTER_DYNAMIC) {
        delete risk_mgr;
    }

    // Desarma timer
    EventKillTimer();
}

void OnTick() {
    // CORREÇÃO: Verificação de tempo robusta
    datetime current_time = TimeCurrent();
    if(current_time - last_cycle < Cycle_Interval_Sec) return;
    last_cycle = current_time;
    
    if(!state_mgr.CanTrade()) {
        static datetime last_safety_log = 0;
        if(current_time - last_safety_log >= 60) {
            Print("[SAFETY] Trading blocked by circuit breaker");
            last_safety_log = current_time;
        }
        return;
    }
    
    ProcessTradingCycle();
    EnforceSafetyMeasures();
}

// Garante ciclos periódicos mesmo sem ticks
void OnTimer() {
    datetime current_time = TimeCurrent();
    if(current_time - last_cycle < Cycle_Interval_Sec) return;
    last_cycle = current_time;

    if(!state_mgr.CanTrade()) {
        static datetime last_safety_log = 0;
        if(current_time - last_safety_log >= 60) {
            Print("[SAFETY] Trading blocked by circuit breaker");
            last_safety_log = current_time;
        }
        return;
    }

    ProcessTradingCycle();
    EnforceSafetyMeasures();
}

void ProcessTradingCycle() {
    string symbol = current_symbol;
    Print("[CYCLE] Start for ", symbol);
    
    // CORREÇÃO: Validação expandida
    if(!IsSymbolValid(symbol)) {
        Print("[CYCLE] Symbol invalid: ", symbol);
        return;
    }
    
    if(!risk_mgr.ValidateMarketConditions(symbol)) {
        Print("[CYCLE] Market conditions invalid for ", symbol);
        return;
    }
    
    // Comunicação com servidor AI
    if(!file_bridge.SendRequest(symbol)) {
        Print("[CYCLE] Failed to send request for ", symbol);
        return;
    } else {
        Print("[CYCLE] Request written for ", symbol);
    }
    
    TradingSignal signal;
    if(file_bridge.ReceiveResponse(symbol, signal)) {
        ExecuteValidatedSignal(signal);
    } else {
        Print("[CYCLE] No AIResponse yet for ", symbol);
    }
}

void ExecuteValidatedSignal(const TradingSignal &signal) {
    if(!signal.isValid || signal.action == "HOLD") {
        return;
    }
    
    if(!Enable_Trading) {
        Print("[EXEC] Trading disabled by configuration");
        return;
    }
    
    // CORREÇÃO: Validações adicionais
    if(!IsSymbolValid(signal.symbol)) {
        Print("[EXEC] Invalid symbol in signal: ", signal.symbol);
        return;
    }
    
    if(!risk_mgr.ValidateMarketConditions(signal.symbol)) {
        Print("[EXEC] Safety check failed for ", signal.symbol);
        return;
    }
    
    MqlTick tick;
    if(!SymbolInfoTick(signal.symbol, tick)) {
        Print("[EXEC] Cannot get current tick for ", signal.symbol);
        return;
    }
    
    ENUM_ORDER_TYPE order_type = (signal.action == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    double price = (order_type == ORDER_TYPE_BUY) ? tick.ask : tick.bid;
    
    // CORREÇÃO CRÍTICA: Cálculo de posição corrigido
    double atr = CalculateATR(signal.symbol);
    double stop_distance = atr * 2.0;
    
    // CORREÇÃO: Chamada correta da função CalculatePositionSize
    double lots = risk_mgr.CalculatePositionSize(signal.symbol, stop_distance, signal.confidence);
    
    if(lots <= 0.0) {
        Print("[EXEC] Invalid lot size calculated: ", lots);
        return;
    }
    
    if(!ExecuteOrderWithFallback(signal.symbol, order_type, lots, price)) {
        Print("[EXEC] Order execution failed after retries");
    }
}

// CORREÇÃO: Função completamente reescrita
bool ExecuteOrderWithFallback(const string symbol, ENUM_ORDER_TYPE type, double lots, double price) {
    double sl = 0.0, tp = 0.0;
    CalculateStops(symbol, type, price, sl, tp);
    
    for(int attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
        ResetLastError();
        
        if(Trade.PositionOpen(symbol, type, lots, price, sl, tp, "PROMETHEUS_V3")) {
            Print("[EXEC_SUCCESS] ", symbol, " ", EnumToString(type), " ", DoubleToString(lots, 2), 
                  " SL:", DoubleToString(sl, 5), " TP:", DoubleToString(tp, 5));
            return true;
        }
        
        int error = GetLastError();
        Print("[EXEC_ATTEMPT ", attempt + 1, "] Error: ", error, " - ", GetErrorDescription(error));
        
        if(IsStopLevelError(error)) {
            // Tenta sem stops primeiro
            if(Trade.PositionOpen(symbol, type, lots, price, 0, 0, "PROMETHEUS_V3_NO_STOPS")) {
                Sleep(100);
                if(SetStopsAfterOpen(symbol, sl, tp)) {
                    return true;
                }
            }
        }
        
        Sleep(100 * (attempt + 1));
    }
    
    return false;
}

void EnforceSafetyMeasures() {
    if(!Use_Circuit_Breakers) return;
    
    CheckDailyDrawdown();
    CheckPositionLossLimits();
}

void CheckDailyDrawdown() {
    double current_equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double start_eq = state_mgr.GetDailyStartEquity();
    
    if(start_eq <= 0.0) {
        state_mgr.TriggerEmergencyStop("Invalid start equity");
        return;
    }
    
    double daily_drawdown_pct = (start_eq - current_equity) / start_eq * 100.0;
    
    if(daily_drawdown_pct >= Max_Daily_Loss_Pct) {
        state_mgr.TriggerEmergencyStop("Daily drawdown limit: " + DoubleToString(daily_drawdown_pct, 2) + "%");
    }
}

void CheckPositionLossLimits() {
    double total_risk = 0.0;
    int positions = PositionsTotal();
    
    for(int i = 0; i < positions; i++) {
        ulong ticket = PositionGetTicket(i);
        if(ticket > 0 && PositionGetString(POSITION_SYMBOL) == current_symbol) {
            double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
            double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
            double volume = PositionGetDouble(POSITION_VOLUME);
            
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                total_risk += (open_price - current_price) * volume;
            } else {
                total_risk += (current_price - open_price) * volume;
            }
        }
    }
    
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if(balance > 0.0 && MathAbs(total_risk) / balance * 100.0 >= Max_Position_Loss_Pct) {
        state_mgr.TriggerEmergencyStop("Position loss limit exceeded");
    }
}

// =============================================================================
// FUNÇÕES AUXILIARES CORRIGIDAS v3.0
// =============================================================================
double CalculateATR(const string symbol, int period = 14, ENUM_TIMEFRAMES tf = PERIOD_M5) {
    int handle = iATR(symbol, tf, period);
    if(handle == INVALID_HANDLE) {
        Print("[ATR] Failed to create ATR handle for ", symbol);
        return 0.0;
    }
    
    double values[];
    int copied = CopyBuffer(handle, 0, 0, 1, values);
    IndicatorRelease(handle);
    
    if(copied <= 0) {
        Print("[ATR] No ATR data for ", symbol);
        return 0.0;
    }
    
    return values[0];
}

void CalculateStops(const string symbol, ENUM_ORDER_TYPE type, double price, double &sl, double &tp) {
    double atr = CalculateATR(symbol);
    if(atr <= 0.0) {
        // Fallback: usa percentual fixo se ATR não disponível
        atr = price * 0.002; // 0.2% como fallback
    }
    
    if(type == ORDER_TYPE_BUY) {
        sl = price - (atr * 2.0);
        tp = price + (atr * 3.0);
    } else {
        sl = price + (atr * 2.0);
        tp = price - (atr * 3.0);
    }
    
    // Garante que stops são válidos respeitando distância mínima
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    double min_stop_distance = SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
    
    // Normaliza preços para múltiplos do point
    sl = NormalizeDouble(sl, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
    tp = NormalizeDouble(tp, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
    
    if(type == ORDER_TYPE_BUY) {
        // Para BUY: SL deve estar pelo menos min_stop_distance abaixo do preço
        double min_sl = price - min_stop_distance;
        if(sl > min_sl) {
            sl = min_sl;
        }
        // TP deve estar pelo menos min_stop_distance acima do preço
        double min_tp = price + min_stop_distance;
        if(tp < min_tp) {
            tp = min_tp;
        }
    } else {
        // Para SELL: SL deve estar pelo menos min_stop_distance acima do preço
        double max_sl = price + min_stop_distance;
        if(sl < max_sl) {
            sl = max_sl;
        }
        // TP deve estar pelo menos min_stop_distance abaixo do preço
        double max_tp = price - min_stop_distance;
        if(tp > max_tp) {
            tp = max_tp;
        }
    }
    
    Print("[STOPS_DEBUG] Symbol: ", symbol, " Price: ", DoubleToString(price, 5), 
          " MinDistance: ", DoubleToString(min_stop_distance, 5),
          " SL: ", DoubleToString(sl, 5), " TP: ", DoubleToString(tp, 5));
}

bool IsStopLevelError(int error) {
    return (error == 130 || error == 131 || error == 132 || error == 4756);
}

bool SetStopsAfterOpen(const string symbol, double sl, double tp) {
    for(int attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
        if(Trade.PositionModify(symbol, sl, tp)) {
            Print("[STOPS_SUCCESS] SL/TP set for ", symbol, " SL:", DoubleToString(sl, 5), " TP:", DoubleToString(tp, 5));
            return true;
        }
        Sleep(50);
    }
    Print("[STOPS_FAILED] Could not set SL/TP for ", symbol);
    return false;
}

// NOVA FUNÇÃO: Validação de símbolo
bool IsSymbolValid(const string symbol) {
    if(StringLen(symbol) == 0) {
        return false;
    }
    
    if(!SymbolSelect(symbol, true)) {
        return false;
    }
    
    // Verifica modo de negociação disponível
    long trade_mode = SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE);
    if(trade_mode == SYMBOL_TRADE_MODE_DISABLED || trade_mode == SYMBOL_TRADE_MODE_CLOSEONLY) {
        return false;
    }
    
    // Tick atual deve ser válido com preços positivos
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) {
        return false;
    }
    if(tick.bid <= 0.0 || tick.ask <= 0.0) {
        return false;
    }
    if(!MathIsValidNumber(tick.bid) || !MathIsValidNumber(tick.ask)) {
        return false;
    }
    
    return true;
}

// NOVA FUNÇÃO: Descrição de erro
string GetErrorDescription(int error) {
    switch(error) {
        case 0: return "No error";
        case 1: return "No error returned, but result is unknown";
        case 2: return "Common error";
        case 3: return "Invalid trade parameters";
        case 4: return "Trade server is busy";
        case 5: return "Old version of the client terminal";
        case 6: return "No connection with trade server";
        case 7: return "Not enough rights";
        case 8: return "Too frequent requests";
        case 9: return "Malfunctional trade operation";
        case 64: return "Account disabled";
        case 65: return "Invalid account";
        case 128: return "Trade timeout";
        case 129: return "Invalid price";
        case 130: return "Invalid stops";
        case 131: return "Invalid trade volume";
        case 132: return "Market is closed";
        case 133: return "Trade is disabled";
        case 134: return "Not enough money";
        case 135: return "Price changed";
        case 136: return "Off quotes";
        case 137: return "Broker is busy";
        case 138: return "Requote";
        case 139: return "Order is locked";
        case 140: return "Long positions only allowed";
        case 141: return "Too many requests";
        case 145: return "Modification denied because order is too close to market";
        case 146: return "Trade context is busy";
        case 147: return "Expirations are denied by broker";
        case 148: return "Too many open and pending orders";
        case 149: return "Hedging is prohibited";
        case 150: return "Prohibited by FIFO rule";
        default: return "Unknown error";
    }
}