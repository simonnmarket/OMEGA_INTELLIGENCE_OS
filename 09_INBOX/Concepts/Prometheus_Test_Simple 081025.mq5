//+------------------------------------------------------------------+
//| Prometheus Test Simple EA - VERSÃO DE TESTE                      |
//| EA minimalista para testar comunicação EA <-> Python              |
//+------------------------------------------------------------------+
#property copyright "Prometheus v3.0"
#property link      "https://prometheus-trading.com"
#property version   "1.00"
#property strict

//--- Parâmetros de entrada
input group "=== TESTE DE COMUNICAÇÃO ==="
input int MagicNumber = 999999;           // Magic Number de Teste
input int RequestIntervalSec = 30;        // Intervalo entre requests (segundos)

//--- Variáveis globais
datetime gLastRequestTime = 0;
string gFilesDir = "";

//+------------------------------------------------------------------+
//| Função de inicialização                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   // Obter diretório de arquivos
   gFilesDir = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\";
   
   Print("[TEST_EA] Inicializado");
   Print("[TEST_EA] FilesDir: ", gFilesDir);
   Print("[TEST_EA] Intervalo de requests: ", RequestIntervalSec, " segundos");
   Print("[TEST_EA] Aguardando ", RequestIntervalSec, " segundos para primeiro request...");
   
   gLastRequestTime = TimeCurrent();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Função de desinicialização                                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("[TEST_EA] Desanexado. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Função OnTick - SEMPRE ATIVA                                     |
//+------------------------------------------------------------------+
void OnTick()
{
   // Verificar se passou o intervalo
   datetime currentTime = TimeCurrent();
   
   if((currentTime - gLastRequestTime) < RequestIntervalSec)
   {
      return; // Ainda não passou o intervalo
   }
   
   // Atualizar tempo
   gLastRequestTime = currentTime;
   
   // Obter dados de mercado
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   Print("[TEST_EA] OnTick ativo - Gerando request para ", _Symbol);
   Print("[TEST_EA] Bid: ", bid, " Ask: ", ask);
   
   // Criar request JSON
   string requestJson = CreateRequestJSON(_Symbol, bid, ask, currentTime, point);
   
   // Salvar arquivo
   string filename = "AIRequest." + _Symbol + ".json";
   int handle = FileOpen(filename, FILE_WRITE|FILE_TXT|FILE_COMMON);
   
   if(handle != INVALID_HANDLE)
   {
      FileWriteString(handle, requestJson);
      FileClose(handle);
      Print("[TEST_EA] Request salvo: ", filename);
   }
   else
   {
      Print("[TEST_EA] ERRO ao salvar request. Error: ", GetLastError());
   }
   
   // Tentar ler response (se existir)
   ReadResponse(_Symbol);
}

//+------------------------------------------------------------------+
//| Criar JSON de request                                            |
//+------------------------------------------------------------------+
string CreateRequestJSON(string symbol, double bid, double ask, datetime time, double point)
{
   string json = "{";
   json += "\"symbol\":\"" + symbol + "\",";
   json += "\"bid\":" + DoubleToString(bid, _Digits) + ",";
   json += "\"ask\":" + DoubleToString(ask, _Digits) + ",";
   json += "\"time\":" + IntegerToString(time) + ",";
   json += "\"point\":" + DoubleToString(point, _Digits + 2);
   json += "}";
   
   return json;
}

//+------------------------------------------------------------------+
//| Ler response do Python e executar trade                          |
//+------------------------------------------------------------------+
void ReadResponse(string symbol)
{
   string filename = "AIResponse." + symbol + ".json";
   
   if(!FileIsExist(filename, FILE_COMMON))
   {
      // Response ainda não foi criado
      return;
   }
   
   int handle = FileOpen(filename, FILE_READ|FILE_TXT|FILE_COMMON);
   
   if(handle == INVALID_HANDLE)
   {
      Print("[TEST_EA] Erro ao ler response. Error: ", GetLastError());
      return;
   }
   
   string responseText = "";
   while(!FileIsEnding(handle))
   {
      responseText += FileReadString(handle);
   }
   FileClose(handle);
   
   Print("[TEST_EA] Response recebido (encoded)");
   
   // Processar response e executar trade
   ProcessResponseAndTrade(symbol, responseText);
}

//+------------------------------------------------------------------+
//| Processar response e executar trade                              |
//+------------------------------------------------------------------+
void ProcessResponseAndTrade(string symbol, string responseText)
{
   // Parse simples do JSON (buscar "action")
   string action = "HOLD";
   
   if(StringFind(responseText, "BUY") >= 0)
      action = "BUY";
   else if(StringFind(responseText, "SELL") >= 0)
      action = "SELL";
   
   Print("[TEST_EA] Ação detectada: ", action);
   
   if(action == "HOLD")
   {
      Print("[TEST_EA] Ação HOLD - não executando trade");
      return;
   }
   
   // Verificar se já tem posição
   if(PositionSelect(symbol))
   {
      Print("[TEST_EA] Já existe posição para ", symbol, " - não abrindo nova");
      return;
   }
   
   // Executar trade
   ExecuteTrade(symbol, action);
}

//+------------------------------------------------------------------+
//| Executar trade                                                    |
//+------------------------------------------------------------------+
void ExecuteTrade(string symbol, string action)
{
   double volume = 0.01; // Volume mínimo para teste
   double price = 0;
   double sl = 0;
   double tp = 0;
   
   ENUM_ORDER_TYPE orderType;
   
   if(action == "BUY")
   {
      orderType = ORDER_TYPE_BUY;
      price = SymbolInfoDouble(symbol, SYMBOL_ASK);
      
      // SL e TP básicos (50 e 100 pontos)
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      sl = price - 50 * point * 10;
      tp = price + 100 * point * 10;
   }
   else if(action == "SELL")
   {
      orderType = ORDER_TYPE_SELL;
      price = SymbolInfoDouble(symbol, SYMBOL_BID);
      
      // SL e TP básicos (50 e 100 pontos)
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      sl = price + 50 * point * 10;
      tp = price - 100 * point * 10;
   }
   else
   {
      Print("[TEST_EA] Ação inválida: ", action);
      return;
   }
   
   // Criar trade request
   MqlTradeRequest request;
   MqlTradeResult result;
   ZeroMemory(request);
   ZeroMemory(result);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = orderType;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = "Prometheus Test";
   request.type_filling = ORDER_FILLING_IOC;
   
   // Enviar ordem
   if(OrderSend(request, result))
   {
      Print("[TEST_EA] TRADE EXECUTADO! ", action, " ", symbol, " @ ", price);
      Print("[TEST_EA] SL: ", sl, " TP: ", tp);
      Print("[TEST_EA] Ticket: ", result.order);
   }
   else
   {
      Print("[TEST_EA] ERRO ao executar trade. Code: ", GetLastError());
      Print("[TEST_EA] Result: ", result.retcode, " - ", result.comment);
   }
}

//+------------------------------------------------------------------+
//| Timer - Backup para gerar requests se OnTick não funcionar       |
//+------------------------------------------------------------------+
void OnTimer()
{
   Print("[TEST_EA] Timer ativo - gerando request via timer");
   OnTick(); // Força chamada do OnTick
}
//+------------------------------------------------------------------+
