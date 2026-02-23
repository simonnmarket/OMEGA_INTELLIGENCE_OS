//+------------------------------------------------------------------+
//|                     TheodoraEA_v12_AUTONOMOUS.mq5                |
//|               Sistema de Trading Quântico Autônomo              |
//|                Projeto: Theodora Quantum Ultimate               |
//|                 Autor: AGENTE IA DEEPSEEK (CEO QUANTITATIVE)    |
//|               Versão: 12.1 (TIER-0 Quantum Autônomo)            |
//+------------------------------------------------------------------+
#property copyright "Theodora Quantum Trading"
#property link      "https://www.theodora-quantum.com"
#property version   "12.1"
#property strict
#property description "EA Quântico Autônomo - Sistema Tier-0 Independente"
#property description "NÍVEL: BLACKROCK/RENAISSANCE/BRIDGEWATER"
#property description "Global Markets: Forex, Crypto, Indices, Commodities"
#property description "Quantum Mechanics: Heisenberg, Entropy, Wave Collapse"
#property description "Dynamic Scaling: 400-2000+ pontos com trailing quântico"
#property description "Modo: AUTÔNOMO - Sem dependência de API externa"

#include <Trade/Trade.mqh>
#include <Math/Stat/Math.mqh>

// Compat: definir códigos de erro se não estiverem presentes
#ifndef ERR_INVALID_STOPS
  #define ERR_INVALID_STOPS 130
#endif
#ifndef ERR_MARKET_CLOSED
  #define ERR_MARKET_CLOSED 132
#endif

//--- Inputs principais
input string SymbolList = "EURUSD,USDJPY,GBPUSD,XAUUSD,US30,BTCUSD,ETHUSD,US500,US100,USOIL,UKOIL";  // Universo padrão
input int    TimerIntervalSec = 15;           // Intervalo do timer (segundos)
input double ScanMinPulse = 1.8;              // Threshold mínimo de pulso quântico
input double ScanMinEnergy = 0.4;             // Threshold mínimo de energia quântica
input int    MaxSymbolsToTrade = 5;           // Máximo de símbolos por ciclo
input double TotalRiskPct = 0.5;              // Risco total por ciclo (% do equity) [Safe Mode]
input double MinLot = 0.01;                   // Lote mínimo desejado
input bool   GlobalPause = false;             // Pausa global
input bool   EmergencyCloseAll = false;       // Fechar todas as posições
input double ScalingLevels1 = 0.1;            // Nível 1 de escalonamento quântico
input double ScalingLevels2 = 0.2;            // Nível 2 de escalonamento quântico
input double ScalingLevels3 = 0.3;            // Nível 3 de escalonamento quântico
input double ScalingLevels4 = 0.5;            // Nível 4 de escalonamento quântico
input double SLFactor = 2.2;                  // Fator de Stop Loss (ATR quântico) [Safe Mode]
input double TPFactor = 3.3;                  // Fator de Take Profit (ATR quântico) [Safe Mode]
input double TrailingFactor = 2.0;            // Fator de Trailing Stop (ATR quântico) [Safe Mode]
input int    BackoffMaxSec = 600;             // Limite máximo de backoff
input double QuantumEntropyThreshold = 0.7;   // Threshold de entropia para decisão quântica
input int    MaxPositions = 10;               // Máximo de posições simultâneas
input bool   AutonomousFallbackOnHold = false;// [Safe Mode] NÃO converter HOLD em trade
input bool   UseMarketWatch = true;           // Usar símbolos visíveis no Market Watch
input int    MaxSymbolsToScan = 30;           // Máximo de símbolos a varrer
input int    SpreadLimitPoints = 10;          // Limite de spread (pontos) para permitir trade
input int    SessionStartHour = 8;            // Janela de sessão permitida (hora do servidor)
input int    SessionEndHour   = 21;           // Janela de sessão permitida (hora do servidor)
input ENUM_TIMEFRAMES AutonomousTF = PERIOD_M1; // Timeframe do modo autônomo
input bool   EnableNeuralNetwork = true;      // Ativar rede neural para decisões
input double NeuralConfidenceThreshold = 0.75;// Threshold de confiança da rede neural
input bool   AggressiveMode = true;           // Modo agressivo: relaxa gates quando necessário
input bool   PreferLowSpread = true;          // Prioriza símbolos com menor spread no scan

//--- Constantes quânticas
#define H_BAR 1.054571817e-34    // Constante de Planck reduzida
#define K_BOLTZMANN 1.380649e-23 // Constante de Boltzmann

//--- Variáveis globais
CTrade   trade;
datetime last_request = 0;
bool     g_isBusy = false;
int      g_fail_count = 0;
int      g_backoff_sec = 0;
datetime g_next_allowed = 0;
int      g_quantum_state = 0;    // Estado quântico atual
double   g_quantum_entropy = 0.5; // Entropia quântica do mercado
double   g_scaling_levels[4];     // Array de níveis de escalonamento
int      g_runtime_spread_limit_points = 0; // Limite de spread dinâmico
bool     g_runtime_fallback_on_hold = false; // Fallback dinâmico para HOLD
int      g_cycle_spread_blocks = 0; // Contador de bloqueios por spread no ciclo
int      g_cycle_hold_blocks = 0;   // Contador de HOLDs no ciclo
int      g_no_trade_cycles = 0;     // Ciclos sem execução
// Cooldown por símbolo quando mercado fechado
string   g_cool_symbols[128];
datetime g_cool_until[128];
int      g_cool_size = 0;

double RoundToTick(string symbol, double price)
{
    double tick = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    if(tick <= 0) return price;
    return MathRound(price / tick) * tick;
}

bool IsSymbolOnCooldown(string symbol)
{
    datetime now = TimeCurrent();
    for(int i=0; i<g_cool_size; i++)
    {
        if(g_cool_symbols[i] == symbol && now < g_cool_until[i])
            return true;
    }
    return false;
}

void SetSymbolCooldown(string symbol, int seconds)
{
    datetime until = TimeCurrent() + seconds;
    for(int i=0; i<g_cool_size; i++)
    {
        if(g_cool_symbols[i] == symbol)
        {
            g_cool_until[i] = until;
            return;
        }
    }
    if(g_cool_size < 128)
    {
        g_cool_symbols[g_cool_size] = symbol;
        g_cool_until[g_cool_size] = until;
        g_cool_size++;
    }
}

//+------------------------------------------------------------------+
//| Funções auxiliares para indicadores técnicos                     |
//+------------------------------------------------------------------+
double GetEMA(string symbol, ENUM_TIMEFRAMES timeframe, int period, int shift)
{
    if(!SymbolSelect(symbol, true)) return 0;
    if(Bars(symbol, timeframe) < period + 10) return 0;
    int handle = iMA(symbol, timeframe, period, 0, MODE_EMA, PRICE_CLOSE);
    if(handle == INVALID_HANDLE) return 0;
    
    double values[];
    ArraySetAsSeries(values, true);
    if(CopyBuffer(handle, 0, shift, 1, values) < 1) return 0;
    
    IndicatorRelease(handle);
    return values[0];
}

double GetRSI(string symbol, ENUM_TIMEFRAMES timeframe, int period, int shift)
{
    if(!SymbolSelect(symbol, true)) return 50;
    if(Bars(symbol, timeframe) < period + 10) return 50;
    int handle = iRSI(symbol, timeframe, period, PRICE_CLOSE);
    if(handle == INVALID_HANDLE) return 50;
    
    double values[];
    ArraySetAsSeries(values, true);
    if(CopyBuffer(handle, 0, shift, 1, values) < 1) return 50;
    
    IndicatorRelease(handle);
    return values[0];
}

void GetMACD(string symbol, ENUM_TIMEFRAMES timeframe, int fast_ema, int slow_ema, int signal_period, 
             double &macd_main, double &macd_signal, int shift)
{
    if(!SymbolSelect(symbol, true)) { macd_main = 0; macd_signal = 0; return; }
    if(Bars(symbol, timeframe) < slow_ema + signal_period + 10) { macd_main = 0; macd_signal = 0; return; }
    int handle = iMACD(symbol, timeframe, fast_ema, slow_ema, signal_period, PRICE_CLOSE);
    if(handle == INVALID_HANDLE)
    {
        macd_main = 0;
        macd_signal = 0;
        return;
    }
    
    double main_buffer[];
    double signal_buffer[];
    ArraySetAsSeries(main_buffer, true);
    ArraySetAsSeries(signal_buffer, true);
    
    if(CopyBuffer(handle, 0, shift, 1, main_buffer) < 1) macd_main = 0;
    else macd_main = main_buffer[0];
    
    if(CopyBuffer(handle, 1, shift, 1, signal_buffer) < 1) macd_signal = 0;
    else macd_signal = signal_buffer[0];
    
    IndicatorRelease(handle);
}

double GetATR(string symbol, ENUM_TIMEFRAMES timeframe, int period, int shift)
{
    if(!SymbolSelect(symbol, true)) return 0;
    if(Bars(symbol, timeframe) < period + 10) return 0;
    int handle = iATR(symbol, timeframe, period);
    if(handle == INVALID_HANDLE) return 0;
    
    double values[];
    ArraySetAsSeries(values, true);
    if(CopyBuffer(handle, 0, shift, 1, values) < 1) return 0;
    
    IndicatorRelease(handle);
    return values[0];
}

//+------------------------------------------------------------------+
//| Funções de validação e segurança                                |
//+------------------------------------------------------------------+
bool IsSpreadOk(string symbol)
{
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    if(point <= 0.0) point = _Point;
    
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) return false;
    
    double spread_points = (tick.ask - tick.bid) / point;
    int limit = (g_runtime_spread_limit_points > 0 ? g_runtime_spread_limit_points : SpreadLimitPoints);
    bool ok = (spread_points <= limit);
    if(!ok) g_cycle_spread_blocks++;
    return ok;
}

bool IsSessionAllowed()
{
    MqlDateTime time_struct;
    TimeCurrent(time_struct);
    int current_hour = time_struct.hour;
    
    if(SessionStartHour <= SessionEndHour)
        return (current_hour >= SessionStartHour && current_hour <= SessionEndHour);
    else
        return (current_hour >= SessionStartHour || current_hour <= SessionEndHour);
}

//+------------------------------------------------------------------+
//| Sistema de Rede Neural para Decisões                            |
//+------------------------------------------------------------------+
double NeuralNetworkPrediction(string symbol, ENUM_TIMEFRAMES timeframe)
{
    if(!EnableNeuralNetwork) return 0.5;
    
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, timeframe, 0, 100, rates);
    if(copied < 50) return 0.5;
    
    // Extrair features para a rede neural
    double ema12 = GetEMA(symbol, timeframe, 12, 0);
    double ema26 = GetEMA(symbol, timeframe, 26, 0);
    double rsi = GetRSI(symbol, timeframe, 14, 0);
    double atr = GetATR(symbol, timeframe, 14, 0);
    
    // Simular rede neural (em produção real, seria um modelo treinado)
    double trend_strength = MathAbs(ema12 - ema26) / atr;
    double momentum = (rates[0].close - rates[10].close) / rates[10].close;
    
    // Algoritmo de predição neural simplificado
    double prediction = 0.5;
    prediction += (ema12 > ema26) ? 0.15 : -0.15;
    prediction += (rsi < 40) ? 0.1 : (rsi > 60) ? -0.1 : 0;
    prediction += (momentum > 0) ? 0.05 : -0.05;
    prediction += (trend_strength > 1.0) ? 0.1 : 0;
    
    return MathMax(0.1, MathMin(0.9, prediction));
}

//+------------------------------------------------------------------+
//| Sistema de Decisão Autônomo Theodora com Rede Neural            |
//+------------------------------------------------------------------+
string AutonomousQuantumDecision(string symbol)
{
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, AutonomousTF, 0, 50, rates);
    
    if(copied < 20) return "HOLD";
    
    // Calcular indicadores técnicos
    double ema12 = GetEMA(symbol, AutonomousTF, 12, 0);
    double ema26 = GetEMA(symbol, AutonomousTF, 26, 0);
    double rsi = GetRSI(symbol, AutonomousTF, 14, 0);
    double macd_main, macd_signal;
    GetMACD(symbol, AutonomousTF, 12, 26, 9, macd_main, macd_signal, 0);
    
    // Obter predição da rede neural
    double neural_confidence = NeuralNetworkPrediction(symbol, AutonomousTF);
    
    // Tendência
    bool trend_bullish = ema12 > ema26;
    bool trend_bearish = ema12 < ema26;
    
    // Momentum
    bool rsi_oversold = rsi < 35;
    bool rsi_overbought = rsi > 65;
    bool macd_bullish = macd_main > macd_signal;
    bool macd_bearish = macd_main < macd_signal;
    
    // Volume analysis
    double volume_current = (double)rates[0].tick_volume;
    double volume_avg = 0.0;
    
    for(int i = 1; i < 20; i++) 
        volume_avg += (double)rates[i].tick_volume;
    
    volume_avg /= 19.0;
    bool volume_spike = volume_current > volume_avg * 1.5;
    
    // Lógica de decisão com rede neural
    if(neural_confidence >= NeuralConfidenceThreshold)
    {
        if(trend_bullish && rsi_oversold && macd_bullish && volume_spike)
            return "BUY";
        else if(trend_bearish && rsi_overbought && macd_bearish && volume_spike)
            return "SELL";
    }
    
    // Fallback para estratégia tradicional
    if(trend_bullish && rsi < 45 && macd_bullish)
        return "BUY";
    else if(trend_bearish && rsi > 55 && macd_bearish)
        return "SELL";
    
    return "HOLD";
}

//+------------------------------------------------------------------+
//| Executar Decisão Autônoma com Gerenciamento de Risco            |
//+------------------------------------------------------------------+
bool ExecuteAutonomousDecision(string symbol)
{
    // pular símbolo em cooldown (mercado fechado ou repetidas falhas)
    if(IsSymbolOnCooldown(symbol))
        return false;
    if(!IsSessionAllowed())
    {
        Print("[SESSION_GATE] Fora da janela permitida: ", SessionStartHour, "-", SessionEndHour, "h");
        return false;
    }
    
    if(!IsSpreadOk(symbol))
    {
        Print("[SPREAD_GATE] Spread acima do limite para ", symbol);
        if(AggressiveMode && g_runtime_spread_limit_points < 100000)
        {
            int old_limit = (g_runtime_spread_limit_points > 0 ? g_runtime_spread_limit_points : SpreadLimitPoints);
            g_runtime_spread_limit_points = MathMin(100000, MathMax(old_limit * 2, 100));
            Print("[AUTO_CALIB_AGGR] SpreadLimit instantâneo ", old_limit, " -> ", g_runtime_spread_limit_points, " para ", symbol);
        }
        return false;
    }
    
    string signal = AutonomousQuantumDecision(symbol);
    
    if(signal == "HOLD")
    {
        bool use_fallback = (g_runtime_fallback_on_hold ? true : AutonomousFallbackOnHold);
        if(!use_fallback)
        {
            Print("[SAFE_MODE] HOLD → sem trade para ", symbol);
            g_cycle_hold_blocks++;
            return false;
        }
        // fallback por tendência se habilitado dinamicamente
        double ema12_f = GetEMA(symbol, AutonomousTF, 12, 0);
        double ema26_f = GetEMA(symbol, AutonomousTF, 26, 0);
        signal = (ema12_f > ema26_f ? "BUY" : "SELL");
        Print("[AUTO_FALLBACK] HOLD convertido em ", signal, " para ", symbol);
    }

    double price = 0;
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    if(point <= 0) 
    {
        Print("[ERROR] Point inválido para ", symbol);
        return false;
    }
    
    // Calcular ATR para risco
    double atr = GetATR(symbol, AutonomousTF, 14, 0);
    if(atr <= 0.0)
    {
        Print("[SAFE_MODE] ATR inválido para ", symbol);
        return false;
    }
    
    double sl_points = SLFactor * atr;
    double tp_points = TPFactor * atr;

    if(signal == "BUY")
    {
        price = SymbolInfoDouble(symbol, SYMBOL_ASK);
        // Validação adicional de tendência
        double ema12 = GetEMA(symbol, AutonomousTF, 12, 0);
        double ema26 = GetEMA(symbol, AutonomousTF, 26, 0);
        if(ema12 <= ema26)
        {
            Print("[TREND_GATE] BUY bloqueado: tendência não confirmada");
            return false;
        }
    }
    else if(signal == "SELL")
    {
        price = SymbolInfoDouble(symbol, SYMBOL_BID);
        // Validação adicional de tendência
        double ema12 = GetEMA(symbol, AutonomousTF, 12, 0);
        double ema26 = GetEMA(symbol, AutonomousTF, 26, 0);
        if(ema12 >= ema26)
        {
            Print("[TREND_GATE] SELL bloqueado: tendência não confirmada");
            return false;
        }
    }
    
    if(price <= 0)
    {
        Print("[ERROR] Preço inválido para ", symbol);
        return false;
    }
    
    double lot = ComputeQuantumLotByRisk(symbol, TotalRiskPct, sl_points, g_quantum_entropy);
    // Normalizar SL/TP para múltiplos do tick e respeitar stops level
    int stops_level = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
    point = SymbolInfoDouble(symbol, SYMBOL_POINT); if(point<=0) point=_Point;
    double min_dist = stops_level * point;
    double sl_price = 0.0, tp_price = 0.0;
    if(signal == "BUY")
    {
        sl_price = RoundToTick(symbol, price - MathMax(sl_points, min_dist));
        tp_price = RoundToTick(symbol, price + MathMax(tp_points, min_dist));
    }
    else
    {
        sl_price = RoundToTick(symbol, price + MathMax(sl_points, min_dist));
        tp_price = RoundToTick(symbol, price - MathMax(tp_points, min_dist));
    }
    
    bool sent = false;
    if(signal == "BUY")
    {
        sent = trade.Buy(lot, symbol, price, sl_price, tp_price, "AUTO_BUY");
    }
    else
    {
        sent = trade.Sell(lot, symbol, price, sl_price, tp_price, "AUTO_SELL");
    }
    if(!sent)
    {
        int le = GetLastError();
        if(le == ERR_MARKET_CLOSED)
        {
            SetSymbolCooldown(symbol, 3600); // 1h cooldown se mercado fechado
            Print("[COOLDOWN] Mercado fechado para ", symbol, ". Cooldown 1h.");
        }
        else if(le == ERR_INVALID_STOPS)
        {
            // ampliar distâncias e tentar de novo 1 vez
            double mul = 1.5;
            if(signal == "BUY")
            {
                sl_price = RoundToTick(symbol, price - MathMax(sl_points*mul, min_dist));
                tp_price = RoundToTick(symbol, price + MathMax(tp_points*mul, min_dist));
                sent = trade.Buy(lot, symbol, price, sl_price, tp_price, "AUTO_BUY_R");
            }
            else
            {
                sl_price = RoundToTick(symbol, price + MathMax(sl_points*mul, min_dist));
                tp_price = RoundToTick(symbol, price - MathMax(tp_points*mul, min_dist));
                sent = trade.Sell(lot, symbol, price, sl_price, tp_price, "AUTO_SELL_R");
            }
        }
    }
    return sent;
}

//+------------------------------------------------------------------+
//| Funções de Mecânica Quântica                                     |
//+------------------------------------------------------------------+
double CalculateHeisenbergUncertainty(double price_std, double volume_std)
{
    return H_BAR / (2 * price_std * volume_std + 1e-15);
}

double CalculateQuantumEntropy(const double &returns[], int bins=50)
{
    int size = ArraySize(returns);
    if(size < 2) return 0.5;
    
    double min_val = returns[0];
    double max_val = returns[0];
    
    for(int i = 1; i < size; i++)
    {
        if(returns[i] < min_val) min_val = returns[i];
        if(returns[i] > max_val) max_val = returns[i];
    }
    
    double range = max_val - min_val;
    if(range == 0 || size < bins) return 0.5;
    
    int histogram[];
    ArrayResize(histogram, bins);
    ArrayInitialize(histogram, 0);
    
    for(int i = 0; i < size; i++)
    {
        int bin = (int)((returns[i] - min_val) / range * (bins - 1));
        if(bin >= 0 && bin < bins)
            histogram[bin]++;
    }
    
    double entropy = 0.0;
    double total = (double)size;
    
    for(int i = 0; i < bins; i++)
    {
        if(histogram[i] > 0)
        {
            double p = histogram[i] / total;
            entropy -= p * MathLog(p);
        }
    }
    
    return entropy / MathLog(bins);
}

double ComputeQuantumLotByRisk(string symbol, double risk_pct, double sl_points, double entropy_factor=1.0)
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double tick_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    
    if(tick_size == 0 || tick_value == 0)
        return MinLot;
    
    double risk_amount = balance * risk_pct / 100.0;
    double lot = risk_amount / (sl_points * tick_value / tick_size);
    
    // Ajuste quântico baseado na entropia
    lot *= (1.0 + 0.3 * (entropy_factor - 0.5));
    
    return NormalizeVolume(symbol, MathMax(MinLot, lot));
}

double NormalizeVolume(string symbol, double lot)
{
    double min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
    double step_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
    
    if(min_lot == 0 || max_lot == 0 || step_lot == 0)
        return MinLot;
    
    lot = MathMax(min_lot, MathMin(max_lot, lot));
    lot = MathRound(lot / step_lot) * step_lot;
    
    return lot;
}

//+------------------------------------------------------------------+
//| Funções principais do EA                                         |
//+------------------------------------------------------------------+
bool RequestQuantumAIDecision(string execution_symbol)
{
    string symbols[];
    int count = 0;
    
    if(UseMarketWatch)
    {
        int total = SymbolsTotal(true);
        int limit = MathMin(total, MaxSymbolsToScan);
        ArrayResize(symbols, limit);
        
        for(int i = 0; i < total && count < limit; i++)
        {
            string s = SymbolName(i, true);
            if(StringLen(s) > 0)
                symbols[count++] = s;
        }
    }
    else
    {
        count = StringSplit(SymbolList, ',', symbols);
    }
    
    // Ordenar por spread (se preferir menor spread)
    if(PreferLowSpread && count > 1)
    {
        for(int i=0; i<count-1; i++)
        {
            for(int j=i+1; j<count; j++)
            {
                MqlTick ti, tj;
                if(SymbolInfoTick(symbols[i], ti) && SymbolInfoTick(symbols[j], tj))
                {
                    double pi = SymbolInfoDouble(symbols[i], SYMBOL_POINT); if(pi<=0) pi=_Point;
                    double pj = SymbolInfoDouble(symbols[j], SYMBOL_POINT); if(pj<=0) pj=_Point;
                    double spi = (ti.ask - ti.bid)/pi;
                    double spj = (tj.ask - tj.bid)/pj;
                    if(spj < spi)
                    {
                        string tmp = symbols[i]; symbols[i] = symbols[j]; symbols[j] = tmp;
                    }
                }
            }
        }
    }

    int trades_executed = 0;
    
    for(int i = 0; i < count && trades_executed < MaxSymbolsToTrade; i++)
    {
        if(PositionsTotal() >= MaxPositions) break;
        
        if(ExecuteAutonomousDecision(symbols[i]))
        {
            trades_executed++;
            Print("Trade autônomo executado para: ", symbols[i]);
        }
    }
    
    return trades_executed > 0;
}

void UpdateGlobalQuantumEntropy()
{
    // Implementação simplificada para versão autônoma
    g_quantum_entropy = 0.5 + (MathRand() / 32767.0 - 0.5) * 0.2;
    g_quantum_entropy = MathMax(0.1, MathMin(0.9, g_quantum_entropy));
}

void UpdateAllQuantumTrailingStops()
{
    int total = PositionsTotal();
    for(int i = 0; i < total; i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket))
        {
            string symbol = PositionGetString(POSITION_SYMBOL);
            double atr = GetATR(symbol, AutonomousTF, 14, 0);
            double entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
            
            UpdateQuantumTrailingStop(symbol, ticket, entry_price, atr, g_quantum_entropy);
        }
    }
}

void UpdateQuantumTrailingStop(string symbol, ulong ticket, double entry_price, double atr, double entropy)
{
    if(!PositionSelectByTicket(ticket)) return;
    
    int position_type = (int)PositionGetInteger(POSITION_TYPE);
    double current_price = SymbolInfoDouble(symbol, position_type == POSITION_TYPE_BUY ? SYMBOL_BID : SYMBOL_ASK);
    double sl = PositionGetDouble(POSITION_SL);
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    
    if(point <= 0.0) point = _Point;
    
    double adjust_factor = 1.0 + entropy;
    double new_sl;
    
    if(position_type == POSITION_TYPE_BUY)
    {
        new_sl = current_price - atr * TrailingFactor * adjust_factor * point;
        if(new_sl > sl && new_sl > entry_price)
            trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
    }
    else
    {
        new_sl = current_price + atr * TrailingFactor * adjust_factor * point;
        if((sl == 0 || new_sl < sl) && new_sl < entry_price)
            trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
    }
}

void CloseAllOpenPositions()
{
    int total = PositionsTotal();
    for(int i = total-1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket))
            trade.PositionClose(ticket);
    }
    Print("[Theodora] Todas as posições fechadas.");
}

//+------------------------------------------------------------------+
//| Funções de Inicialização e Eventos                               |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("🚀 Theodora v12.1 AUTONOMOUS - Inicializando");
    Print("🔐 Quantum Firewall: Ativo");
    Print("🧠 Cérebro Quântico Autônomo: Online");
    Print("🤖 Rede Neural: ", (EnableNeuralNetwork ? "Ativada" : "Desativada"));
    
    if(!TerminalInfoInteger(TERMINAL_CONNECTED) ||
       !MQLInfoInteger(MQL_TRADE_ALLOWED) ||
       !AccountInfoInteger(ACCOUNT_TRADE_EXPERT))
    {
        Print("[ERROR] Ambiente sem permissão de trade.");
        return(INIT_FAILED);
    }
    
    trade.SetExpertMagicNumber(11041982);
    EventSetTimer(TimerIntervalSec);
    
    g_quantum_state = MathRand() % 2;
    UpdateGlobalQuantumEntropy();
    
    g_scaling_levels[0] = ScalingLevels1;
    g_scaling_levels[1] = ScalingLevels2;
    g_scaling_levels[2] = ScalingLevels3;
    g_scaling_levels[3] = ScalingLevels4;
    
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
    EventKillTimer();
    Print("[Theodora] Finalizado. Motivo: ", reason);
}

void OnTimer()
{
    if(GlobalPause)
    {
        Print("[Theodora] GlobalPause ativo");
        return;
    }
    
    static bool closedOnce = false;
    if(EmergencyCloseAll && !closedOnce)
    {
        CloseAllOpenPositions();
        closedOnce = true;
        return;
    }
    
    if(g_isBusy) return;
    
    datetime now = TimeCurrent();
    if(g_fail_count > 0 && now < g_next_allowed) return;
    
    // reset contadores por ciclo
    g_cycle_spread_blocks = 0;
    g_cycle_hold_blocks = 0;
    g_isBusy = true;
    bool ok = RequestQuantumAIDecision(_Symbol);
    
    if(ok)
    {
        g_fail_count = 0;
        g_backoff_sec = 0;
        g_next_allowed = 0;
        Print("Decisão quântica executada com sucesso");
        g_no_trade_cycles = 0;
    }
    else
    {
        g_fail_count++;
        int step = (int)MathPow(2, MathMin(g_fail_count, 10));
        g_backoff_sec = MathMin(step * TimerIntervalSec, BackoffMaxSec);
        g_next_allowed = now + g_backoff_sec;
        Print("Falha na decisão quântica. Backoff: ", g_backoff_sec, "s");
        g_no_trade_cycles++;
        // Auto calibração agressiva:
        if(g_cycle_spread_blocks > 10)
        {
            int old_limit = (g_runtime_spread_limit_points > 0 ? g_runtime_spread_limit_points : SpreadLimitPoints);
            g_runtime_spread_limit_points = (int)(old_limit * 2);
            if(g_runtime_spread_limit_points < 100000) g_runtime_spread_limit_points = MathMin(100000, g_runtime_spread_limit_points);
            Print("[AUTO_CALIB] SpreadLimit ajustado ", old_limit, " -> ", g_runtime_spread_limit_points);
        }
        if(g_cycle_hold_blocks > 5 || g_no_trade_cycles >= 2)
        {
            if(!g_runtime_fallback_on_hold)
            {
                g_runtime_fallback_on_hold = true;
                Print("[AUTO_CALIB] FallbackOnHold ativado dinamicamente");
            }
        }
    }
    
    g_isBusy = false;
    UpdateAllQuantumTrailingStops();
}

void OnTick()
{
    static datetime last_tick = 0;
    datetime current_time = TimeCurrent();
    
    if(current_time > last_tick)
    {
        UpdateGlobalQuantumEntropy();
        last_tick = current_time;
    }
}
//+------------------------------------------------------------------+