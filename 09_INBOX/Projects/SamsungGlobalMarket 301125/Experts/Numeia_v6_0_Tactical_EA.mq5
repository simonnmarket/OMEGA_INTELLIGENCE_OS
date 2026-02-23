//+------------------------------------------------------------------+
//|                           Numeia_v6_0_Tactical_EA.mq5            |
//|                      Copyright 2025, Numeia Trading System v6.0 |
//|                           TACTICAL WAR ROOM - AGRESSÃO TOTAL    |
//+------------------------------------------------------------------+
#property copyright "Numeia Trading System v6.0"
#property version   "6.00"
#property description "TACTICAL MULTI-STRATEGY EA"
#property description "Lê TacticalSignals.json e executa trades agressivos"
#property description "Múltiplas estratégias: Momentum, Breakout, Mean Reversion"
#property description "FILOSOFIA: Testar TUDO. Refutar RÁPIDO. Aprovar ou Descartar."

//--- Includes
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| INPUTS - CONFIGURAÇÃO TÁTICA                                     |
//+------------------------------------------------------------------+
input group "=== CONFIGURAÇÃO TÁTICA ==="
input int      InpCheckInterval = 60;           // Intervalo de verificação (segundos)
input double   InpMaxPositions = 20;            // Máximo de posições simultâneas
input double   InpRiskPerTrade = 2.0;           // Risco por trade (% do balanço)
input double   InpMinConfidence = 0.50;         // Confidence mínima para executar
input bool     InpAllowMultiplePositions = true; // Permitir múltiplas posições no mesmo símbolo

input group "=== GESTÃO DE RISCO ==="
input double   InpMaxDrawdown = 25.0;           // Kill-Switch: Drawdown máximo (%)
input double   InpMaxDailyLoss = 5.0;           // Perda diária máxima (%)
input double   InpPositionSizingMultiplier = 1.0; // Multiplicador de tamanho

input group "=== IDENTIFICAÇÃO ==="
input ulong    InpMagicNumber = 60000;          // Magic Number (v6.0)
input string   InpEAComment = "Numeia_v6.0";    // Comentário das ordens

//+------------------------------------------------------------------+
//| ESTRUTURA DE SINAL TÁTICO                                        |
//+------------------------------------------------------------------+
struct TacticalSignal
{
   string symbol;
   string action;           // BUY ou SELL
   double entry_price;
   double stop_loss;
   double take_profit;
   double confidence;
   string strategy;         // momentum, breakout, etc
   string reason;
   datetime timestamp;
};

//+------------------------------------------------------------------+
//| VARIÁVEIS GLOBAIS                                                |
//+------------------------------------------------------------------+
CTrade trade;
TacticalSignal g_currentSignals[];
int g_numSignals = 0;
datetime g_lastFileRead = 0;
double g_initialBalance = 0.0;
double g_dailyStartBalance = 0.0;
datetime g_lastDayCheck = 0;
bool g_killSwitchActive = false;

double g_activeMinConfidence = 0.0;
double g_confidenceAdjuster = 1.0;
double g_riskMultiplier = 1.0;
string g_currentRegime = "UNKNOWN";

// Estatísticas
int g_totalTrades = 0;
int g_totalWins = 0;
int g_totalLosses = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("NUMEIA v6.0 - TACTICAL WAR ROOM");
   Print("AGRESSÃO TOTAL - TESTE DE MÚLTIPLAS ESTRATÉGIAS");
   Print("========================================");
   Print("Versão: 6.00");
   Print("Magic Number: ", InpMagicNumber);
   Print("Risco por trade: ", InpRiskPerTrade, "%");
   Print("Max posições: ", (int)InpMaxPositions);
   Print("Min confidence: ", InpMinConfidence);
   Print("Confidence Dinâmica inicial: aguardando servidor");
   Print("========================================");
   
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(10);
   trade.SetTypeFilling(ORDER_FILLING_FOK);
   trade.SetAsyncMode(false);
   
   g_initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   g_dailyStartBalance = g_initialBalance;
   g_lastDayCheck = TimeCurrent();
   
   Print("Balanço Inicial: $", g_initialBalance);
   Print("Arquivo de sinais: TacticalSignals.json");
   Print("========================================");
   Print("");
   Print("⏳ Aguardando sinais do servidor Python...");
   Print("");
   
   // Timer para verificar sinais periodicamente
   EventSetTimer(InpCheckInterval);
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   
   Print("========================================");
   Print("NUMEIA v6.0 - Desligando");
   Print("Razão: ", reason);
   Print("Total Trades: ", g_totalTrades);
   Print("Wins: ", g_totalWins, " | Losses: ", g_totalLosses);
   if(g_totalTrades > 0)
   {
      double winRate = (double)g_totalWins / (double)g_totalTrades * 100.0;
      Print("Win Rate: ", DoubleToString(winRate, 2), "%");
   }
   Print("========================================");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Verificações básicas em cada tick
   
   // 1. Verificar Kill-Switch
   if(CheckKillSwitch())
   {
      if(!g_killSwitchActive)
      {
         Print("🚨 KILL-SWITCH ATIVADO!");
         Print("   Drawdown máximo excedido: ", InpMaxDrawdown, "%");
         g_killSwitchActive = true;
         CloseAllPositions();
      }
      return;
   }
   
   // 2. Verificar perda diária
   if(CheckDailyLoss())
   {
      Print("⚠️ Perda diária máxima atingida. Aguardando próximo dia.");
      return;
   }
   
   // 3. Gerenciar posições existentes (SL/TP trailing, etc)
   ManageOpenPositions();
}

//+------------------------------------------------------------------+
//| Timer function - Verifica novos sinais                          |
//+------------------------------------------------------------------+
void OnTimer()
{
   // Ler arquivo de sinais
   if(ReadTacticalSignals())
   {
      Print("");
      Print("========================================");
      Print("📥 NOVOS SINAIS RECEBIDOS: ", g_numSignals);
      Print("========================================");
      
      // Processar sinais
      ProcessSignals();
   }
}

//+------------------------------------------------------------------+
//| Ler arquivo TacticalSignals.json                                |
//+------------------------------------------------------------------+
bool ReadTacticalSignals()
{
   string filename = "TacticalSignals.json";
   
   // Verificar se arquivo existe
   if(!FileIsExist(filename, FILE_COMMON))
   {
      return false;
   }
   
   // Verificar timestamp do arquivo
   datetime fileTime = (datetime)FileGetInteger(filename, FILE_MODIFY_DATE, FILE_COMMON);
   if(fileTime <= g_lastFileRead)
   {
      return false;  // Arquivo não mudou
   }
   
   // Ler arquivo
   int handle = FileOpen(filename, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle == INVALID_HANDLE)
   {
      Print("❌ Erro ao abrir arquivo de sinais: ", GetLastError());
      return false;
   }
   
   string jsonContent = "";
   while(!FileIsEnding(handle))
   {
      jsonContent += FileReadString(handle);
   }
   FileClose(handle);

   // Atualizar metadados dinâmicos
    double parsedMinConf = ExtractJSONDouble(jsonContent, "min_confidence");
    if(parsedMinConf > 0.0)
    {
       g_activeMinConfidence = parsedMinConf;
    }
    else
    {
       g_activeMinConfidence = 0.0;
    }
    double parsedAdjuster = ExtractJSONDouble(jsonContent, "confidence_adjuster");
    if(parsedAdjuster > 0.0)
    {
       g_confidenceAdjuster = parsedAdjuster;
    }
    else
    {
       g_confidenceAdjuster = 1.0;
    }
    double parsedRiskMult = ExtractJSONDouble(jsonContent, "risk_multiplier");
    if(parsedRiskMult > 0.0)
    {
       g_riskMultiplier = parsedRiskMult;
    }
    else
    {
       g_riskMultiplier = 1.0;
    }
    string parsedRegime = ExtractJSONString(jsonContent, "regime");
    if(StringLen(parsedRegime) > 0)
    {
       g_currentRegime = parsedRegime;
    }
   
   // Parse JSON (simplificado - produção deve usar biblioteca robusta)
   if(!ParseTacticalSignalsJSON(jsonContent))
   {
      Print("❌ Erro ao fazer parse do JSON");
      return false;
   }
   
   g_lastFileRead = fileTime;
   return true;
}

//+------------------------------------------------------------------+
//| Parse JSON de sinais (simplificado)                             |
//+------------------------------------------------------------------+
bool ParseTacticalSignalsJSON(string json)
{
   // Reset sinais
   ArrayResize(g_currentSignals, 0);
   g_numSignals = 0;
   
   // Buscar array de sinais
   int signalsStart = StringFind(json, "\"signals\":");
   if(signalsStart < 0)
   {
      Print("❌ Campo 'signals' não encontrado no JSON");
      return false;
   }
   
   // Buscar array [ ]
   int arrayStart = StringFind(json, "[", signalsStart);
   int arrayEnd = StringFind(json, "]", arrayStart);
   
   if(arrayStart < 0 || arrayEnd < 0)
   {
      Print("❌ Array de sinais malformado");
      return false;
   }
   
   string signalsArray = StringSubstr(json, arrayStart + 1, arrayEnd - arrayStart - 1);
   
   // Parse cada sinal (buscar objetos { })
   int pos = 0;
   while(pos < StringLen(signalsArray))
   {
      int objStart = StringFind(signalsArray, "{", pos);
      if(objStart < 0) break;
      
      int objEnd = StringFind(signalsArray, "}", objStart);
      if(objEnd < 0) break;
      
      string signalObj = StringSubstr(signalsArray, objStart, objEnd - objStart + 1);
      
      // Parse individual signal
      TacticalSignal signal;
      if(ParseSignalObject(signalObj, signal))
      {
         ArrayResize(g_currentSignals, g_numSignals + 1);
         g_currentSignals[g_numSignals] = signal;
         g_numSignals++;
      }
      
      pos = objEnd + 1;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Parse um objeto de sinal individual                              |
//+------------------------------------------------------------------+
bool ParseSignalObject(string json, TacticalSignal &signal)
{
   // Extrair campos do JSON
   signal.symbol = ExtractJSONString(json, "symbol");
   signal.action = ExtractJSONString(json, "action");
   signal.entry_price = ExtractJSONDouble(json, "entry_price");
   signal.stop_loss = ExtractJSONDouble(json, "stop_loss");
   signal.take_profit = ExtractJSONDouble(json, "take_profit");
   signal.confidence = ExtractJSONDouble(json, "confidence");
   signal.strategy = ExtractJSONString(json, "strategy");
   signal.reason = ExtractJSONString(json, "reason");
   signal.timestamp = TimeCurrent();
   
   // Validar campos obrigatórios
   if(StringLen(signal.symbol) == 0 || StringLen(signal.action) == 0)
   {
      return false;
   }
   
   if(signal.action != "BUY" && signal.action != "SELL")
   {
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Extrair string de JSON                                           |
//+------------------------------------------------------------------+
string ExtractJSONString(string json, string key)
{
   string searchKey = "\"" + key + "\":";
   int keyPos = StringFind(json, searchKey);
   if(keyPos < 0) return "";
   
   int valueStart = StringFind(json, "\"", keyPos + StringLen(searchKey));
   if(valueStart < 0) return "";
   
   valueStart++;
   int valueEnd = StringFind(json, "\"", valueStart);
   if(valueEnd < 0) return "";
   
   return StringSubstr(json, valueStart, valueEnd - valueStart);
}

//+------------------------------------------------------------------+
//| Extrair double de JSON                                           |
//+------------------------------------------------------------------+
double ExtractJSONDouble(string json, string key)
{
   string searchKey = "\"" + key + "\":";
   int keyPos = StringFind(json, searchKey);
   if(keyPos < 0) return 0.0;
   
   int valueStart = keyPos + StringLen(searchKey);
   
   // Remover espaços
   while(valueStart < StringLen(json) && 
         (StringGetCharacter(json, valueStart) == ' ' || 
          StringGetCharacter(json, valueStart) == '\t'))
   {
      valueStart++;
   }
   
   // Encontrar fim do número (até vírgula ou chave)
   int valueEnd = valueStart;
   while(valueEnd < StringLen(json))
   {
      ushort ch = StringGetCharacter(json, valueEnd);
      if(ch == ',' || ch == '}' || ch == '\n' || ch == '\r' || ch == ' ')
         break;
      valueEnd++;
   }
   
   string valueStr = StringSubstr(json, valueStart, valueEnd - valueStart);
   return StringToDouble(valueStr);
}

//+------------------------------------------------------------------+
//| Processar sinais recebidos                                       |
//+------------------------------------------------------------------+
void ProcessSignals()
{
   double activeMinConfidence = InpMinConfidence;
   if(g_activeMinConfidence > 0.0)
   {
      activeMinConfidence = g_activeMinConfidence;
   }

   Print("   Regime: ", g_currentRegime, " | Confidence Ajustado: ", DoubleToString(g_confidenceAdjuster, 2));
   Print("   Min Confidence dinâmico: ", DoubleToString(activeMinConfidence, 2),
         " | Risk Multiplier: ", DoubleToString(g_riskMultiplier, 2));

   for(int i = 0; i < g_numSignals; i++)
   {
      TacticalSignal signal = g_currentSignals[i];
      
      Print("");
      Print("📊 SINAL #", i+1, "/", g_numSignals);
      Print("   Symbol: ", signal.symbol);
      Print("   Action: ", signal.action);
      Print("   Entry: ", signal.entry_price);
      Print("   SL: ", signal.stop_loss, " | TP: ", signal.take_profit);
      Print("   Confidence: ", DoubleToString(signal.confidence, 2));
      Print("   Strategy: ", signal.strategy);
      Print("   Reason: ", signal.reason);
      
      // Verificar confidence mínima
      if(signal.confidence < activeMinConfidence)
      {
         Print("   ⚠️ IGNORADO: Confidence < ", activeMinConfidence);
         continue;
      }
      
      // Verificar se já temos posição neste símbolo
      if(!InpAllowMultiplePositions && HasPosition(signal.symbol))
      {
         Print("   ⚠️ JÁ TEMOS POSIÇÃO: ", signal.symbol);
         continue;
      }
      
      // Verificar limite de posições
      if(CountOpenPositions() >= (int)InpMaxPositions)
      {
         Print("   ⚠️ LIMITE DE POSIÇÕES ATINGIDO: ", InpMaxPositions);
         break;
      }
      
      // Executar trade
      if(ExecuteSignal(signal))
      {
         Print("   ✅ TRADE EXECUTADO");
         g_totalTrades++;
      }
      else
      {
         Print("   ❌ FALHA NA EXECUÇÃO");
      }
   }
   
   Print("========================================");
}

//+------------------------------------------------------------------+
//| Executar sinal tático                                            |
//+------------------------------------------------------------------+
bool ExecuteSignal(TacticalSignal &signal)
{
   // Verificar se símbolo está disponível
   if(!SymbolSelect(signal.symbol, true))
   {
      Print("❌ Símbolo não disponível: ", signal.symbol);
      return false;
   }
   
   if(!IsMarketOpen(signal.symbol))
   {
      Print("⚠️ Mercado fechado ou sem ticks recentes: ", signal.symbol);
      return false;
   }
   
   MqlTick symbolTick;
   if(!SymbolInfoTick(signal.symbol, symbolTick))
   {
      Print("❌ Falha ao obter tick para símbolo: ", signal.symbol);
      return false;
   }
   
   // Calcular volume baseado no risco
   double volume = CalculateVolume(signal.symbol, signal.entry_price, signal.stop_loss);
   
   if(volume <= 0)
   {
      Print("❌ Volume calculado inválido: ", volume);
      return false;
   }
   
   double price = (signal.action == "BUY") ? symbolTick.ask : symbolTick.bid;
   if(price <= 0.0)
      price = signal.entry_price;
   
   double sl = signal.stop_loss;
   double tp = signal.take_profit;
   if(!PrepareStops(signal.symbol, signal.action, price, sl, tp))
   {
      Print("❌ Não foi possível preparar SL/TP para ", signal.symbol);
      return false;
   }
   
   // Executar ordem
   bool result = false;
   
   if(signal.action == "BUY")
   {
      result = trade.Buy(volume, signal.symbol, 0, sl, tp, InpEAComment);
   }
   else if(signal.action == "SELL")
   {
      result = trade.Sell(volume, signal.symbol, 0, sl, tp, InpEAComment);
   }
   
   if(result)
   {
      Print("✅ Ordem aberta: ", signal.symbol, " ", signal.action);
      Print("   Volume: ", volume);
      Print("   SL: ", sl, " | TP: ", tp);
      Print("   Ticket: ", trade.ResultOrder());
   }
   else
   {
      Print("❌ Erro ao abrir ordem: ", trade.ResultRetcodeDescription());
   }
   
   return result;
}

//+------------------------------------------------------------------+
//| Verificar se o mercado está aberto e com ticks atuais            |
//+------------------------------------------------------------------+
bool IsMarketOpen(const string symbol)
{
   datetime now = TimeCurrent();
   
   MqlTick tick;
   if(SymbolInfoTick(symbol, tick))
   {
      if((now - tick.time) > 900) // 15 minutos sem ticks => provavelmente fechado
         return false;
   }
   else
   {
      return false;
   }
   
   MqlDateTime nowStruct;
   TimeToStruct(now, nowStruct);
   ENUM_DAY_OF_WEEK day = (ENUM_DAY_OF_WEEK)nowStruct.day_of_week;
   datetime sessionFrom, sessionTo;
   bool hasSession = false;
   datetime dayStart = now - (nowStruct.hour * 3600 + nowStruct.min * 60 + nowStruct.sec);
   
   for(int i = 0; ; i++)
   {
      if(!SymbolInfoSessionTrade(symbol, day, i, sessionFrom, sessionTo))
         break;
      
      hasSession = true;
      datetime absFrom = dayStart + sessionFrom;
      datetime absTo = dayStart + sessionTo;
      
      if(sessionTo < sessionFrom)
         absTo += 24 * 3600; // sessão atravessa meia-noite
      
      if(now >= absFrom && now <= absTo)
         return true;
   }
   
   if(!hasSession)
      return true; // símbolo 24/7 (ex.: crypto)
   
   return false;
}

//+------------------------------------------------------------------+
//| Ajustar SL/TP respeitando distâncias mínimas                     |
//+------------------------------------------------------------------+
bool PrepareStops(const string symbol, const string action, const double price, double &sl, double &tp)
{
   int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double stopsLevel = (double)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
   double freezeLevel = (double)SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL) * point;
   double minDistance = MathMax(stopsLevel, freezeLevel);
   bool adjusted = false;
   
   if(action == "BUY")
   {
      if(sl > 0.0)
      {
         if(sl >= price)
         {
            sl = price - minDistance;
            adjusted = true;
         }
         if(minDistance > 0.0 && (price - sl) < minDistance)
         {
            sl = price - minDistance;
            adjusted = true;
         }
         if(sl <= 0.0)
         {
            sl = 0.0;
            adjusted = true;
         }
      }
      if(tp > 0.0)
      {
         if(tp <= price)
         {
            tp = price + minDistance;
            adjusted = true;
         }
         if(minDistance > 0.0 && (tp - price) < minDistance)
         {
            tp = price + minDistance;
            adjusted = true;
         }
      }
   }
   else // SELL
   {
      if(sl > 0.0)
      {
         if(sl <= price)
         {
            sl = price + minDistance;
            adjusted = true;
         }
         if(minDistance > 0.0 && (sl - price) < minDistance)
         {
            sl = price + minDistance;
            adjusted = true;
         }
      }
      if(tp > 0.0)
      {
         if(tp >= price)
         {
            tp = price - minDistance;
            adjusted = true;
         }
         if(minDistance > 0.0 && (price - tp) < minDistance)
         {
            tp = price - minDistance;
            adjusted = true;
         }
      }
   }
   
   if(action == "BUY")
   {
      if(sl >= price) sl = 0.0;
      if(tp <= price) tp = 0.0;
   }
   else
   {
      if(sl <= price) sl = 0.0;
      if(tp >= price) tp = 0.0;
   }
   
   if(sl > 0.0)
      sl = NormalizeDouble(sl, digits);
   if(tp > 0.0)
      tp = NormalizeDouble(tp, digits);
   
   if(adjusted)
   {
      Print("   ℹ️ Stops ajustados para respeitar distância mínima de ", DoubleToString(minDistance, digits), " pontos.");
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Calcular volume baseado no risco                                 |
//+------------------------------------------------------------------+
double CalculateVolume(string symbol, double entryPrice, double stopLoss)
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskMultiplier = g_riskMultiplier;
   if(riskMultiplier <= 0.0)
      riskMultiplier = 1.0;
   double riskAmount = balance * (InpRiskPerTrade / 100.0) * InpPositionSizingMultiplier * riskMultiplier;
   
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   double minVolume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxVolume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double volumeStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   // Calcular distância em ticks
   double slDistance = MathAbs(entryPrice - stopLoss);
   double ticks = slDistance / tickSize;
   
   if(ticks <= 0)
   {
      Print("❌ SL muito próximo do entry");
      return 0;
   }
   
   // Volume = Risco / (Ticks * TickValue)
   double volume = riskAmount / (ticks * tickValue);
   
   // Normalizar volume
   volume = MathFloor(volume / volumeStep) * volumeStep;
   volume = MathMax(volume, minVolume);
   volume = MathMin(volume, maxVolume);
   
   return volume;
}

//+------------------------------------------------------------------+
//| Verificar se já temos posição no símbolo                         |
//+------------------------------------------------------------------+
bool HasPosition(string symbol)
{
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber &&
            PositionGetString(POSITION_SYMBOL) == symbol)
         {
            return true;
         }
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Contar posições abertas deste EA                                 |
//+------------------------------------------------------------------+
int CountOpenPositions()
{
   int count = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            count++;
         }
      }
   }
   return count;
}

//+------------------------------------------------------------------+
//| Gerenciar posições abertas                                       |
//+------------------------------------------------------------------+
void ManageOpenPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber)
            continue;
         
         // Aqui pode adicionar lógica de trailing stop, break-even, etc
         // Por enquanto, deixamos SL/TP fixos
      }
   }
}

//+------------------------------------------------------------------+
//| Verificar Kill-Switch                                            |
//+------------------------------------------------------------------+
bool CheckKillSwitch()
{
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double drawdown = (g_initialBalance - currentBalance) / g_initialBalance * 100.0;
   
   return (drawdown > InpMaxDrawdown);
}

//+------------------------------------------------------------------+
//| Verificar perda diária                                           |
//+------------------------------------------------------------------+
bool CheckDailyLoss()
{
   // Resetar no início do dia
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   
   MqlDateTime lastDayDt;
   TimeToStruct(g_lastDayCheck, lastDayDt);
   
   if(dt.day != lastDayDt.day)
   {
      g_dailyStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      g_lastDayCheck = TimeCurrent();
      return false;
   }
   
   // Calcular perda diária
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double dailyLoss = (g_dailyStartBalance - currentBalance) / g_dailyStartBalance * 100.0;
   
   return (dailyLoss > InpMaxDailyLoss);
}

//+------------------------------------------------------------------+
//| Fechar todas as posições                                         |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   Print("🚨 Fechando todas as posições...");
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            trade.PositionClose(PositionGetTicket(i));
         }
      }
   }
}
//+------------------------------------------------------------------+

