//+------------------------------------------------------------------+
//|                                 SamsungGlobalMarket_EA_v2.0.1.mq5 |
//|                                      Copyright 2025, Samsung Global Market |
//|                                       https://samsungglobalmarket.com |
//+------------------------------------------------------------------+
#property copyright "Samsung Global Market"
#property link      "https://samsungglobalmarket.com"
#property version   "2.01"
#property description "File-Based Communication + Kill-Switch + Trading Logic"
#property description "FASE 2: Implementação Completa - Diretiva Conselho TIER-0"

//--- Includes necessários
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| ENTRADAS DO EXPERT ADVISOR                                       |
//+------------------------------------------------------------------+
input group "=== Configurações de Comunicação ==="
input int      REQUEST_INTERVAL = 300;              // Intervalo entre requests (segundos)
input string   SYMBOLS_TO_ANALYZE = "GBPUSD"; // Símbolos para análise (OPERAÇÃO NOTURNA: apenas GBPUSD)

input group "=== Configurações de Trading ==="
input ulong    InpMagicNumber = 12345;              // Número Mágico (Identificação)
input double   InpRiskPercent = 1.0;                // Risco por Operação (% do saldo)
input double   InpConfidenceThreshold = 0.50;       // Threshold de Confiança (TEMPORÁRIO - Meta: 0.70)
input int      InpSlippage = 10;                    // Slippage Máximo (pontos)

input group "=== Configurações de Segurança (KILL-SWITCH) ==="
input double   InpKillSwitchDrawdown = 15.0;        // Kill-Switch: Drawdown máximo permitido (%)
input double   InpMaxDailyLossPercent = 5.0;        // Kill-Switch: Perda diária máxima (%)

//+------------------------------------------------------------------+
//| VARIÁVEIS GLOBAIS                                                |
//+------------------------------------------------------------------+
string g_symbols[];
int g_symbolCount = 0;
datetime g_lastRequestTime[];

//--- Kill-Switch: Balanço inicial da conta (para cálculo de drawdown)
double g_initialBalance = 0.0;
bool   g_killSwitchActivated = false;

//--- Kill-Switch: Controle diário
datetime g_dayStart = 0;
double g_dayStartBalance = 0.0;

//--- Executor de trades
CTrade tradeExecutor;

//+------------------------------------------------------------------+
//| FUNÇÕES DE LOGGING                                               |
//+------------------------------------------------------------------+
void Log(string level, string message)
{
   Print("[", level, "] ", message);
}

//+------------------------------------------------------------------+
//| FUNÇÕES DE COMUNICAÇÃO BASEADA EM ARQUIVOS                       |
//+------------------------------------------------------------------+

//--- Enviar request para análise ML
void SendRequestForSymbol(const string symbol)
{
   // Obter tick atual
   MqlTick tick;
   if(!SymbolInfoTick(symbol, tick))
   {
      Log("ERROR", "Falha ao obter tick para " + symbol);
      return;
   }
   
   // Obter informações do símbolo
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double spread = (tick.ask - tick.bid) / point;
   
   // Construir payload JSON
   string fname = "AIRequest." + symbol + ".json";
   string payload = StringFormat(
      "{\"symbol\":\"%s\",\"bid\":%.10f,\"ask\":%.10f,\"spread\":%.2f,\"time\":%I64d,\"point\":%.10f,\"ea_version\":\"2.0.0\"}",
      symbol, tick.bid, tick.ask, spread, (long)tick.time, point
   );
   
   // Escrever arquivo
   int handle = FileOpen(fname, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle == INVALID_HANDLE)
   {
      int error = GetLastError();
      Log("ERROR", StringFormat("Falha ao criar arquivo %s. Erro: %d", fname, error));
      return;
   }
   
   FileWriteString(handle, payload);
   FileClose(handle);
   
   Log("INFO", StringFormat("[REQUEST] %s enviado (%d bytes)", symbol, StringLen(payload)));
}

//--- Tentar ler response da análise ML
bool TryReadResponse(const string symbol, string &action, double &confidence, string &reason)
{
   string fname = "AIResponse." + symbol + ".json";
   
   // Tentar abrir arquivo
   int h = FileOpen(fname, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(h == INVALID_HANDLE)
   {
      // Arquivo ainda não existe (servidor ainda processando)
      return false;
   }
   
   // Ler conteúdo completo (remover quebras de linha e espaços)
   string text = "";
   while(!FileIsEnding(h))
   {
      string line = FileReadString(h);
      // Remover espaços e quebras de linha (normalizar JSON)
      StringReplace(line, " ", "");
      StringReplace(line, "\r", "");
      StringReplace(line, "\n", "");
      StringReplace(line, "\t", "");
      text += line;
   }
   FileClose(h);
   
   // Debug: Log do JSON recebido (primeiros 200 chars)
   string debugJson = StringSubstr(text, 0, MathMin(200, StringLen(text)));
   Log("DEBUG", StringFormat("[JSON] %s: %s...", symbol, debugJson));
   
   // Parsing JSON simples (buscar campos)
   // Formato esperado: {"action":"BUY","confidence":0.85,"reason":"..."}
   // OU formato indentado normalizado: {"action":"BUY",...}
   
   // Extrair action - suporta "action":" e "action":
   int actionPos = StringFind(text, "\"action\"");
   if(actionPos >= 0)
   {
      // Encontrar os dois pontos após "action"
      int colonPos = StringFind(text, ":", actionPos);
      if(colonPos >= 0)
      {
         // Encontrar primeira aspas após os dois pontos
         int quoteStart = StringFind(text, "\"", colonPos);
         if(quoteStart >= 0)
         {
            int actionStart = quoteStart + 1;
            int quoteEnd = StringFind(text, "\"", actionStart);
            if(quoteEnd > actionStart)
            {
               action = StringSubstr(text, actionStart, quoteEnd - actionStart);
            }
         }
      }
   }
   
   // Extrair confidence
   int confPos = StringFind(text, "\"confidence\"");
   if(confPos >= 0)
   {
      int colonPos = StringFind(text, ":", confPos);
      if(colonPos >= 0)
      {
         // Ler número até vírgula ou chave
         int confStart = colonPos + 1;
         int commaPos = StringFind(text, ",", confStart);
         int bracePos = StringFind(text, "}", confStart);
         int confEnd = commaPos;
         if(confEnd < 0 || (bracePos >= 0 && bracePos < confEnd))
            confEnd = bracePos;
         
         if(confEnd > confStart)
         {
            string confStr = StringSubstr(text, confStart, confEnd - confStart);
            confidence = StringToDouble(confStr);
         }
      }
   }
   
   // Extrair reason
   int reasonPos = StringFind(text, "\"reason\"");
   if(reasonPos >= 0)
   {
      int colonPos = StringFind(text, ":", reasonPos);
      if(colonPos >= 0)
      {
         int quoteStart = StringFind(text, "\"", colonPos);
         if(quoteStart >= 0)
         {
            int reasonStart = quoteStart + 1;
            int quoteEnd = StringFind(text, "\"", reasonStart);
            if(quoteEnd > reasonStart)
            {
               reason = StringSubstr(text, reasonStart, quoteEnd - reasonStart);
            }
         }
      }
   }
   
   // Deletar arquivo após processar
   FileDelete(fname, FILE_COMMON);
   
   Log("SUCCESS", StringFormat("[RESPONSE] %s: action=%s, confidence=%.2f, reason=%s", 
                                symbol, action, confidence, reason));
   
   return true;
}

//+------------------------------------------------------------------+
//| FUNÇÕES DE TRADING                                               |
//+------------------------------------------------------------------+

//--- Verificar Kill-Switch (PRIORIDADE ABSOLUTA - TIER-0)
bool CheckKillSwitch()
{
   // Se já ativado, retornar true (bloquear tudo)
   if(g_killSwitchActivated)
      return true;
   
   // Se balanço inicial não foi registrado, não verificar ainda
   if(g_initialBalance <= 0)
      return false;
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   //--- Resetar balanço diário à meia-noite
   MqlDateTime currentTime, dayStartTime;
   TimeToStruct(TimeCurrent(), currentTime);
   TimeToStruct(g_dayStart, dayStartTime);
   
   if(currentTime.day != dayStartTime.day || currentTime.mon != dayStartTime.mon || currentTime.year != dayStartTime.year)
   {
      g_dayStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      g_dayStart = TimeCurrent();
      Log("INFO", "Novo dia iniciado. Balanco diario resetado: " + DoubleToString(g_dayStartBalance, 2));
   }
   
   //--- Calcular drawdown total
   double currentDrawdown = (g_initialBalance - currentEquity) / g_initialBalance * 100.0;
   
   //--- Calcular perda diária
   double dailyLoss = (g_dayStartBalance - currentEquity) / g_dayStartBalance * 100.0;
   
   //--- Verificar drawdown total
   bool killSwitchByDrawdown = (currentDrawdown >= InpKillSwitchDrawdown);
   
   //--- Verificar perda diária máxima
   bool killSwitchByDailyLoss = (dailyLoss >= InpMaxDailyLossPercent);
   
   if(killSwitchByDrawdown || killSwitchByDailyLoss)
   {
      g_killSwitchActivated = true;
      
      string reason = "";
      if(killSwitchByDrawdown && killSwitchByDailyLoss)
         reason = "Drawdown total E perda diaria maxima";
      else if(killSwitchByDrawdown)
         reason = "Drawdown total";
      else
         reason = "Perda diaria maxima";
      
      Log("CRITICAL", StringFormat("KILL-SWITCH ATIVADO! Razao: %s | Drawdown: %.2f%% | Perda Diaria: %.2f%% | Equity: %.2f", 
          reason, currentDrawdown, dailyLoss, currentEquity));
      
      Print("========================================");
      Print("[KILL-SWITCH] ATIVADO - DRAWDOWN CRITICO");
      Print("========================================");
      Print("Razao: ", reason);
      Print("Drawdown Total: ", DoubleToString(currentDrawdown, 2), "% (Limite: ", DoubleToString(InpKillSwitchDrawdown, 2), "%)");
      Print("Perda Diaria: ", DoubleToString(dailyLoss, 2), "% (Limite: ", DoubleToString(InpMaxDailyLossPercent, 2), "%)");
      Print("Equity Atual: ", DoubleToString(currentEquity, 2));
      Print("Balanco Inicial: ", DoubleToString(g_initialBalance, 2));
      Print("Balanco Diario: ", DoubleToString(g_dayStartBalance, 2));
      Print("Fechando todas as posicoes...");
      Print("========================================");
      
      //--- Fechar todas as posições do EA
      CloseAllPositions();
      
      //--- Remover EA do gráfico
      ExpertRemove();
      return true;
   }
   
   return false;
}

//--- Fechar todas as posições do EA
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            tradeExecutor.PositionClose(ticket);
            Log("INFO", StringFormat("Posicao fechada pelo Kill-Switch. Ticket: %I64u", ticket));
         }
      }
   }
}

//--- Abrir posição
bool OpenPosition(const string symbol, ENUM_ORDER_TYPE orderType, double confidence)
{
   // Verificar Kill-Switch ANTES de abrir posição
   if(CheckKillSwitch())
   {
      Log("ERROR", "Tentativa de abrir posicao bloqueada - Kill-Switch ativado");
      return false;
   }
   
   // Validar símbolo
   if(!SymbolInfoInteger(symbol, SYMBOL_SELECT))
   {
      Log("ERROR", "Simbolo nao disponivel: " + symbol);
      return false;
   }
   
   // Calcular tamanho da posição
   double lotSize = CalculatePositionSize(symbol, confidence);
   if(lotSize <= 0)
   {
      Log("ERROR", "Tamanho de lote invalido: " + DoubleToString(lotSize, 2));
      return false;
   }
   
   // Obter preços
   double price = (orderType == ORDER_TYPE_BUY) ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
   
   // Normalizar preço
   double normalizedPrice = NormalizeDouble(price, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
   
   // Calcular Stop Loss e Take Profit (simples - 50 pips SL, 100 pips TP)
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double slDistance = 50.0 * point;
   double tpDistance = 100.0 * point;
   
   double sl = 0, tp = 0;
   if(orderType == ORDER_TYPE_BUY)
   {
      sl = NormalizeDouble(normalizedPrice - slDistance, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
      tp = NormalizeDouble(normalizedPrice + tpDistance, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
   }
   else // SELL
   {
      sl = NormalizeDouble(normalizedPrice + slDistance, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
      tp = NormalizeDouble(normalizedPrice - tpDistance, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
   }
   
   // Configurar executor
   tradeExecutor.SetExpertMagicNumber(InpMagicNumber);
   tradeExecutor.SetDeviationInPoints(InpSlippage);
   tradeExecutor.SetTypeFilling(ORDER_FILLING_FOK);
   
   // Executar trade
   bool result = tradeExecutor.PositionOpen(symbol, orderType, lotSize, normalizedPrice, sl, tp, 
                                            StringFormat("EA v2.0.1 | Conf: %.2f", confidence));
   
   if(result)
   {
      Log("SUCCESS", StringFormat("[TRADE EXECUTED] %s %s %.2f lotes @ %.5f | SL: %.5f | TP: %.5f | Conf: %.2f",
                                   symbol, (orderType == ORDER_TYPE_BUY ? "BUY" : "SELL"), 
                                   lotSize, normalizedPrice, sl, tp, confidence));
   }
   else
   {
      int error = GetLastError();
      Log("ERROR", StringFormat("Falha ao abrir posicao %s. Erro: %d", symbol, error));
      ResetLastError();
   }
   
   return result;
}

//--- Calcular tamanho da posição baseado em risco
double CalculatePositionSize(const string symbol, double confidence)
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * (InpRiskPercent / 100.0);
   
   // Ajustar tamanho baseado em confiança (maior confiança = maior posição, até máximo de 2x)
   double confidenceMultiplier = MathMin(1.0 + confidence, 2.0);
   riskAmount *= confidenceMultiplier;
   
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   
   // Calcular lotes baseado em risco (assumindo SL de 50 pips)
   double slInPrice = 50.0 * point;
   double lotSize = (riskAmount * tickSize) / (slInPrice * tickValue);
   
   // Normalizar tamanho do lote
   double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   lotSize = MathFloor(lotSize / lotStep) * lotStep;
   lotSize = MathMax(minLot, MathMin(maxLot, lotSize));
   
   return NormalizeDouble(lotSize, 2);
}

//--- Executar ação de trading baseada na análise ML
void ExecuteTradeAction(const string symbol, const string action, const double confidence, const string reason)
{
   // Verificar Kill-Switch PRIMEIRO
   if(CheckKillSwitch())
   {
      Log("WARN", "Tentativa de executar trade bloqueada - Kill-Switch ativado");
      return;
   }
   
   // Verificar confiança mínima (AJUSTADO PARA 0.50 - TEMPORÁRIO)
   if(confidence < InpConfidenceThreshold)
   {
      Log("INFO", StringFormat("[TRADE] %s: Confiança muito baixa (%.2f < %.2f) - ignorando", 
                                symbol, confidence, InpConfidenceThreshold));
      return;
   }
   
   // Determinar ação
   if(action == "BUY")
   {
      Log("INFO", StringFormat("[TRADE] %s: Sinal de COMPRA (conf=%.2f, reason=%s)", symbol, confidence, reason));
      OpenPosition(symbol, ORDER_TYPE_BUY, confidence);
   }
   else if(action == "SELL")
   {
      Log("INFO", StringFormat("[TRADE] %s: Sinal de VENDA (conf=%.2f, reason=%s)", symbol, confidence, reason));
      OpenPosition(symbol, ORDER_TYPE_SELL, confidence);
   }
   else if(action == "HOLD")
   {
      Log("INFO", StringFormat("[TRADE] %s: Sinal de AGUARDAR (conf=%.2f, reason=%s)", symbol, confidence, reason));
      // Não fazer nada
   }
   else
   {
      Log("WARN", StringFormat("[TRADE] %s: Ação desconhecida '%s'", symbol, action));
   }
}

//+------------------------------------------------------------------+
//| FUNÇÕES DE EVENTO DO EXPERT ADVISOR                              |
//+------------------------------------------------------------------+

int OnInit()
{
   // Inicializar timer (1 segundo)
   EventSetTimer(1);
   
   // *** CRÍTICO: Registrar balanço inicial para Kill-Switch ***
   g_initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   g_killSwitchActivated = false;
   
   // *** CRÍTICO: Inicializar controle diário ***
   g_dayStart = TimeCurrent();
   g_dayStartBalance = g_initialBalance;
   
   // Parsear símbolos
   string symbolsStr = SYMBOLS_TO_ANALYZE;
   StringReplace(symbolsStr, " ", ""); // Remover espaços
   
   g_symbolCount = StringSplit(symbolsStr, ',', g_symbols);
   
   if(g_symbolCount == 0)
   {
      Log("ERROR", "Nenhum símbolo configurado para análise");
      return(INIT_FAILED);
   }
   
   // Inicializar array de timestamps
   ArrayResize(g_lastRequestTime, g_symbolCount);
   for(int i = 0; i < g_symbolCount; i++)
   {
      g_lastRequestTime[i] = 0; // Enviar request imediatamente no primeiro ciclo
   }
   
   // Configurar executor de trades
   tradeExecutor.SetExpertMagicNumber(InpMagicNumber);
   
   Print("=========================================================");
   Print("SAMSUNG GLOBAL MARKET EA v2.0.1 - FASE 2");
   Print("=========================================================");
   Print("Kill-Switch: ATIVADO (Drawdown: ", InpKillSwitchDrawdown, "% | Diario: ", InpMaxDailyLossPercent, "%)");
   Print("Confidence Threshold: ", InpConfidenceThreshold, " (TEMPORARIO - Meta: 0.70)");
   Print("Magic Number: ", InpMagicNumber);
   Print("Risk per Trade: ", InpRiskPercent, "%");
   Print("Balanco Inicial: ", DoubleToString(g_initialBalance, 2));
   Print("=========================================================");
   
   Log("INFO", StringFormat("EA inicializado. Versão: %s", "2.0.1"));
   Log("INFO", StringFormat("Símbolos para análise: %s", SYMBOLS_TO_ANALYZE));
   Log("INFO", StringFormat("Intervalo entre requests: %d segundos", REQUEST_INTERVAL));
   
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   EventKillTimer();
   Log("INFO", "EA desinicializado");
}

void OnTick()
{
   // Verificar Kill-Switch em cada tick (PRIORIDADE ABSOLUTA)
   CheckKillSwitch();
}

void OnTimer()
{
   // Verificar Kill-Switch em cada timer (backup)
   if(CheckKillSwitch())
      return; // Se Kill-Switch ativado, não processar mais nada
   
   datetime currentTime = TimeCurrent();
   
   // Processar cada símbolo
   for(int i = 0; i < g_symbolCount; i++)
   {
      string symbol = g_symbols[i];
      
      // Verificar se é hora de enviar novo request
      if(currentTime - g_lastRequestTime[i] >= REQUEST_INTERVAL)
      {
         SendRequestForSymbol(symbol);
         g_lastRequestTime[i] = currentTime;
      }
      
      // Tentar ler response (se existir)
      string action = "";
      double confidence = 0.0;
      string reason = "";
      
      if(TryReadResponse(symbol, action, confidence, reason))
      {
         // Response recebido - executar ação de trading
         ExecuteTradeAction(symbol, action, confidence, reason);
      }
   }
}

//+------------------------------------------------------------------+
//| FASE 2 IMPLEMENTADA:                                             |
//| ✅ Kill-Switch (Drawdown Total + Diário)                        |
//| ✅ Abertura de Posições (BUY/SELL)                               |
//| ✅ Gestão de Risco (SL/TP)                                       |
//| ✅ Fechamento de Posições (Kill-Switch)                          |
//| ✅ Threshold Ajustado (0.50 - TEMPORÁRIO)                        |
//+------------------------------------------------------------------+

