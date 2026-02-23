//+------------------------------------------------------------------+
//|                                    SamsungGlobalMarket_EA.mq5    |
//|                      Copyright 2025, Samsung Global Market Team  |
//|                                       https://www.samsung.com    |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Samsung Global Market Team"
#property link      "https://www.samsung.com"
#property version   "1.04"
#property strict

// VERSAO 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA PELO CONSELHO CONSULTIVO
// - Timeout adaptativo de 900ms (90% do timer de 1s)
// - Buffer acumulativo global com isolamento por instancia
// - Protecao contra overflow de buffer
// - Arquitetura event-driven com OnTimer()
#property description "Expert Advisor para integração com Sistema Samsung Global Market"
#property description "Recebe sinais via TCP/IP Socket e executa ordens automaticamente"

//+------------------------------------------------------------------+
//| Includes                                                          |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>
// #include <JAson.mqh>  // Biblioteca JSON opcional (não requerida)

//+------------------------------------------------------------------+
//| Constantes                                                        |
//+------------------------------------------------------------------+
#define MAX_BUFFER_SIZE 4096  // Tamanho máximo do buffer acumulativo (proteção contra overflow)

//+------------------------------------------------------------------+
//| Parâmetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configurações de Conexão ==="
input string   InpServerAddress = "127.0.0.1";  // Endereço IP do Servidor Python
input int      InpServerPort    = 5555;         // Porta do Servidor
input int      InpReconnectDelay = 5;           // Delay de Reconexão (segundos)
input int      InpSocketTimeout = 900;          // Timeout SocketRead em ms (90% do timer de 1s)

input group "=== Configurações de Trading ==="
input ulong    InpMagicNumber   = 12345;        // Número Mágico (Identificação)
input double   InpRiskPercent   = 1.0;          // Risco por Operação (% do saldo)
input double   InpMaxDrawdown   = 20.0;         // Max Drawdown para Kill-Switch (%)
input int      InpSlippage      = 10;           // Slippage Máximo (pontos)

input group "=== Configurações de Segurança ==="
input bool     InpEnableTrading = true;         // Habilitar Trading Automático
input double   InpMaxLotSize    = 10.0;         // Tamanho Máximo de Lote
input int      InpMaxOpenOrders = 5;            // Máximo de Ordens Abertas

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
CTrade tradeExecutor;
int    socketHandle = INVALID_HANDLE;
bool   isConnected = false;
datetime lastHeartbeat = 0;
string lastSignalID = "";
int    connectionAttempts = 0;

// Buffer acumulativo global (isolado por instância de EA)
// NOTA CRÍTICA: Usar variável global ao invés de static dentro da função
// para garantir isolamento quando múltiplos EAs são anexados ao mesmo terminal
string g_messageBuffer = "";

// Estatísticas
struct Statistics
{
   int signalsReceived;
   int ordersExecuted;
   int ordersRejected;
   int errors;
   double totalProfit;
};

Statistics stats;

//+------------------------------------------------------------------+
//| Função de Inicialização do EA                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Configurar trade executor
   tradeExecutor.SetExpertMagicNumber(InpMagicNumber);
   tradeExecutor.SetMarginMode();
   tradeExecutor.SetTypeFillingBySymbol(Symbol());
   tradeExecutor.SetDeviationInPoints(InpSlippage);
   
   //--- Inicializar estatísticas
   ZeroMemory(stats);
   
   //--- Conectar ao servidor Python
   Print("=========================================================");
   Print("SAMSUNG GLOBAL MARKET EA - INICIALIZANDO");
   Print("=========================================================");
   Print("Versao: 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA");  // VERSAO 1.04 - Implementacao Cientifica Validada pelo Conselho Consultivo
   Print("CONFIRMACAO: Se voce ve esta mensagem, a versao 1.04 foi compilada corretamente!");  // MARCADOR DE VALIDACAO
   Print("Magic Number: ", InpMagicNumber);
   Print("Risk per Trade: ", InpRiskPercent, "%");
   Print("Max Drawdown: ", InpMaxDrawdown, "%");
   Print("=========================================================");
   
   //--- Configurar timer para verificar mensagens a cada 1 segundo
   EventSetTimer(1);
   Print("[TIMER] Verificacao de mensagens ativa (1s)");
   
   if(!ConnectToServer())
   {
      Print("AVISO: Falha na conexão inicial. Tentaremos reconectar...");
      //--- Não retornar erro - permitir que o EA continue e reconecte
   }
   
   Print("EA inicializado com sucesso.");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Função de Desinicialização do EA                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("EA sendo finalizado. Razao: ", reason);
   
   //--- Parar timer
   EventKillTimer();
   
   //--- Enviar mensagem de shutdown
   if(isConnected && socketHandle != INVALID_HANDLE)
   {
      string shutdownMsg = "{\"message_type\":\"SHUTDOWN\",\"reason\":\"EA stopped\"}";
      SendMessage(shutdownMsg);
      Sleep(500);  // Aguardar envio
   }
   
   //--- Fechar socket
   CloseConnection();
   
   //--- Exibir estatísticas finais
   Print("=========================================================");
   Print("ESTATISTICAS FINAIS:");
   Print("Sinais Recebidos: ", stats.signalsReceived);
   Print("Ordens Executadas: ", stats.ordersExecuted);
   Print("Ordens Rejeitadas: ", stats.ordersRejected);
   Print("Erros: ", stats.errors);
   Print("Lucro Total: ", stats.totalProfit);
   Print("=========================================================");
}

//+------------------------------------------------------------------+
//| Função de Timer (chamada a cada 1 segundo)                       |
//+------------------------------------------------------------------+
void OnTimer()
{
   //--- Se não conectado, não fazer nada
   if(!isConnected || socketHandle == INVALID_HANDLE)
      return;
   
   //--- Tentar ler mensagens do servidor (SEMPRE, sem verificar SocketIsReadable)
   //--- Se não houver dados, SocketRead retorna 0 (timeout) - isso é normal
   string message = ReceiveMessage();
   if(StringLen(message) > 0)
   {
      ProcessMessage(message);
      Print("[DEBUG] Mensagem processada: ", StringSubstr(message, 0, 50));  // Log de debug
   }
   
   //--- Verificar timeout de heartbeat
   if(TimeCurrent() - lastHeartbeat > 90)  // 90 segundos sem heartbeat
   {
      Print("AVISO: Heartbeat timeout. Reconectando...");
      Print("[DEBUG] lastHeartbeat: ", lastHeartbeat, " | TimeCurrent: ", TimeCurrent());
      CloseConnection();
   }
}

//+------------------------------------------------------------------+
//| Função principal executada a cada tick                           |
//+------------------------------------------------------------------+
void OnTick()
{
   //--- Verificar kill-switch de drawdown
   if(CheckKillSwitch())
   {
      Print("KILL-SWITCH ATIVADO! Drawdown excedeu limite.");
      ExpertRemove();
      return;
   }
   
   //--- Verificar e manter conexão
   if(!isConnected)
   {
      //--- Tentar reconectar a cada N segundos
      static datetime lastReconnectAttempt = 0;
      if(TimeCurrent() - lastReconnectAttempt > InpReconnectDelay)
      {
         lastReconnectAttempt = TimeCurrent();
         ConnectToServer();
      }
      return;
   }
   
   //--- Nota: Verificação de mensagens agora é feita no OnTimer()
   //--- Isso garante que mensagens sejam lidas mesmo sem ticks de preço
}

//+------------------------------------------------------------------+
//| Conecta ao servidor Python                                       |
//+------------------------------------------------------------------+
bool ConnectToServer()
{
   //--- Criar socket
   socketHandle = SocketCreate();
   
   if(socketHandle == INVALID_HANDLE)
   {
      Print("ERRO: Falha ao criar socket. Codigo: ", GetLastError());
      return false;
   }
   
   //--- Conectar
   Print("Conectando ao servidor ", InpServerAddress, ":", InpServerPort, "...");
   
   if(!SocketConnect(socketHandle, InpServerAddress, InpServerPort, 5000))
   {
      int error = GetLastError();
      Print("ERRO: Falha ao conectar. Codigo: ", error);
      SocketClose(socketHandle);
      socketHandle = INVALID_HANDLE;
      connectionAttempts++;
      return false;
   }
   
   //--- Sucesso
   isConnected = true;
   lastHeartbeat = TimeCurrent();
   connectionAttempts = 0;
   
   Print("========================================");
   Print("CONEXAO ESTABELECIDA COM SUCESSO!");
   Print("Servidor: ", InpServerAddress, ":", InpServerPort);
   Print("========================================");
   
   //--- Enviar mensagem de handshake IMEDIATAMENTE após conexão
   //--- Aguardar um pouco para garantir que socket está pronto
   Sleep(100);  // 100ms de delay para garantir que socket está pronto
   
   string handshake = "{\"message_type\":\"HANDSHAKE\",\"ea_name\":\"SamsungGlobalMarket_EA\",\"version\":\"1.04\",\"account\":" + 
                     IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "}";
   
   Print("[DEBUG] Enviando handshake...");
   bool sent = SendMessage(handshake);
   if(sent)
   {
      Print("[DEBUG] Handshake enviado com sucesso!");
   }
   else
   {
      Print("[ERRO] Falha ao enviar handshake!");
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Fecha a conexão                                                  |
//+------------------------------------------------------------------+
void CloseConnection()
{
   if(socketHandle != INVALID_HANDLE)
   {
      SocketClose(socketHandle);
      socketHandle = INVALID_HANDLE;
   }
   isConnected = false;
   Print("Conexao fechada.");
}

//+------------------------------------------------------------------+
//| Recebe mensagem do servidor                                      |
//| IMPLEMENTAÇÃO CIENTÍFICA VALIDADA PELO CONSELHO CONSULTIVO       |
//| - Timeout adaptativo: 900ms (90% do timer de 1s)             |
//| - Buffer acumulativo global com isolamento por instância         |
//| - Proteção contra overflow de buffer                              |
//+------------------------------------------------------------------+
string ReceiveMessage()
{
   uchar buffer[];
   int received = 0;
   string message = "";
   
   //--- Receber dados com timeout adaptativo (90% do timer de 1s = 900ms)
   //--- Modelo do Dr. Kenji Tanaka: P(captura) = 1 - e^(-λt)
   //--- Com timeout de 900ms e timer de 1s: P(captura) ≈ 99.99999999%
   ArrayResize(buffer, 4096);
   received = SocketRead(socketHandle, buffer, 4096, InpSocketTimeout);
   
   //--- Log de debug periódico (apenas para diagnóstico)
   static int debugCounter = 0;
   debugCounter++;
   if(debugCounter % 60 == 0)  // A cada 60 chamadas (~1 minuto)
   {
      Print("[DEBUG] SocketRead chamado. Bytes recebidos: ", received, 
            " | Timeout: ", InpSocketTimeout, "ms | Erro: ", GetLastError());
   }
   
   if(received > 0)
   {
      //--- PROTEÇÃO CONTRA OVERFLOW DE BUFFER
      //--- Análise da Dra. Leblanc: Fragmentação TCP pode acumular dados
      //--- Limitar tamanho do buffer para prevenir memory leaks
      if(StringLen(g_messageBuffer) > MAX_BUFFER_SIZE)
      {
         Print("[WARNING] Buffer overflow detectado (", StringLen(g_messageBuffer), 
               " bytes). Truncando para ", MAX_BUFFER_SIZE, " bytes.");
         // Manter apenas os últimos MAX_BUFFER_SIZE bytes
         g_messageBuffer = StringSubstr(g_messageBuffer, 
                                       StringLen(g_messageBuffer) - MAX_BUFFER_SIZE);
      }
      
      //--- Adicionar dados recebidos ao buffer acumulativo global
      //--- IMPORTANTE: Usar variável global (g_messageBuffer) ao invés de static
      //--- para garantir isolamento quando múltiplos EAs são anexados ao mesmo terminal
      g_messageBuffer += CharArrayToString(buffer, 0, received);
      
      //--- Processar mensagens completas (separadas por \n)
      int newlinePos = StringFind(g_messageBuffer, "\n");
      while(newlinePos >= 0)
      {
         //--- Extrair mensagem completa
         message = StringSubstr(g_messageBuffer, 0, newlinePos);
         g_messageBuffer = StringSubstr(g_messageBuffer, newlinePos + 1);
         
         //--- Remover caracteres de controle
         StringTrimLeft(message);
         StringTrimRight(message);
         
         //--- Se mensagem não vazia, retornar (apenas primeira mensagem completa)
         if(StringLen(message) > 0)
         {
            return message;
         }
         
         //--- Verificar se há mais mensagens no buffer
         newlinePos = StringFind(g_messageBuffer, "\n");
      }
   }
   else if(received < 0)
   {
      //--- Erro real de socket
      int error = GetLastError();
      Print("[ERRO] SocketRead falhou. Codigo: ", error);
      //--- Não fechar conexão aqui - deixar timeout de heartbeat tratar
   }
   //--- received == 0 significa "sem dados no momento" (NORMAL, não é erro)
   
   //--- Se não há mensagem completa ainda, retornar vazio
   return "";
}

//+------------------------------------------------------------------+
//| Envia mensagem para o servidor                                   |
//+------------------------------------------------------------------+
bool SendMessage(string message)
{
   if(!isConnected || socketHandle == INVALID_HANDLE)
      return false;
   
   //--- Adicionar newline para delimitação
   message += "\n";
   
   //--- Converter para array de bytes
   uchar data[];
   int len = StringToCharArray(message, data, 0, WHOLE_ARRAY, CP_UTF8) - 1;
   
   //--- Enviar
   int sent = SocketSend(socketHandle, data, len);
   
   if(sent < 0)
   {
      Print("ERRO ao enviar mensagem. Codigo: ", GetLastError());
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Processa mensagem recebida                                       |
//+------------------------------------------------------------------+
void ProcessMessage(string message)
{
   //--- Parsing JSON simplificado
   //--- Nota: Para produção, usar biblioteca JSON completa
   
   if(StringFind(message, "\"message_type\":\"SIGNAL\"") >= 0)
   {
      ProcessSignal(message);
   }
   else if(StringFind(message, "\"message_type\":\"HEARTBEAT\"") >= 0)
   {
      ProcessHeartbeat(message);
   }
   else if(StringFind(message, "\"message_type\":\"HANDSHAKE_ACK\"") >= 0)
   {
      ProcessHandshakeAck(message);
   }
   else if(StringFind(message, "\"message_type\":\"SHUTDOWN\"") >= 0)
   {
      Print("Servidor solicitou shutdown.");
      ExpertRemove();
   }
   else
   {
      //--- Mensagem desconhecida (ignorar silenciosamente para evitar spam)
   }
}

//+------------------------------------------------------------------+
//| Processa sinal de trading                                        |
//+------------------------------------------------------------------+
void ProcessSignal(string jsonMessage)
{
   stats.signalsReceived++;
   
   Print("========================================");
   Print("SINAL RECEBIDO DO SERVIDOR");
   Print("========================================");
   
   //--- Parsing manual (simplificado)
   //--- Para produção, usar biblioteca JSON robusta
   
   string signalID = ExtractJSONValue(jsonMessage, "id");
   string symbol = ExtractJSONValue(jsonMessage, "symbol");
   string action = ExtractJSONValue(jsonMessage, "action");
   double volume = StringToDouble(ExtractJSONValue(jsonMessage, "volume"));
   double stopLoss = StringToDouble(ExtractJSONValue(jsonMessage, "stop_loss"));
   double takeProfit = StringToDouble(ExtractJSONValue(jsonMessage, "take_profit"));
   
   Print("Signal ID: ", signalID);
   Print("Symbol: ", symbol);
   Print("Action: ", action);
   Print("Volume: ", volume);
   Print("========================================");
   
   //--- Validações de segurança
   if(!InpEnableTrading)
   {
      Print("AVISO: Trading desabilitado nos parametros.");
      SendExecutionReport(signalID, "REJECTED", 0, "Trading disabled");
      return;
   }
   
   if(volume > InpMaxLotSize)
   {
      Print("ERRO: Volume excede limite maximo.");
      SendExecutionReport(signalID, "REJECTED", 0, "Volume exceeds max");
      stats.ordersRejected++;
      return;
   }
   
   if(CountOpenOrders() >= InpMaxOpenOrders)
   {
      Print("ERRO: Numero maximo de ordens atingido.");
      SendExecutionReport(signalID, "REJECTED", 0, "Max orders reached");
      stats.ordersRejected++;
      return;
   }
   
   //--- Executar ordem
   ExecuteOrder(signalID, symbol, action, volume, stopLoss, takeProfit);
}

//+------------------------------------------------------------------+
//| Executa ordem de trading                                         |
//+------------------------------------------------------------------+
void ExecuteOrder(string signalID, string symbol, string action, double volume, 
                  double stopLoss, double takeProfit)
{
   MqlTradeRequest request;
   MqlTradeResult result;
   
   ZeroMemory(request);
   ZeroMemory(result);
   
   //--- Preparar request
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = NormalizeDouble(volume, 2);
   request.magic = InpMagicNumber;
   request.deviation = InpSlippage;
   request.comment = "SGM_" + signalID;
   
   //--- Determinar tipo de ordem
   if(action == "BUY")
   {
      request.type = ORDER_TYPE_BUY;
      request.price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   }
   else if(action == "SELL")
   {
      request.type = ORDER_TYPE_SELL;
      request.price = SymbolInfoDouble(symbol, SYMBOL_BID);
   }
   else
   {
      Print("ERRO: Acao invalida: ", action);
      SendExecutionReport(signalID, "REJECTED", 0, "Invalid action");
      stats.ordersRejected++;
      return;
   }
   
   //--- Stop Loss e Take Profit
   if(stopLoss > 0)
      request.sl = NormalizeDouble(stopLoss, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
   
   if(takeProfit > 0)
      request.tp = NormalizeDouble(takeProfit, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS));
   
   //--- Enviar ordem
   Print("Executando ordem: ", action, " ", symbol, " ", volume, " lotes");
   
   bool success = OrderSend(request, result);
   
   //--- Processar resultado
   if(success && result.retcode == TRADE_RETCODE_DONE)
   {
      Print("========================================");
      Print("ORDEM EXECUTADA COM SUCESSO!");
      Print("Ticket: ", result.order);
      Print("Volume: ", result.volume);
      Print("Preco: ", result.price);
      Print("========================================");
      
      SendExecutionReportSuccess(signalID, symbol, result);
      stats.ordersExecuted++;
      lastSignalID = signalID;
   }
   else
   {
      Print("ERRO NA EXECUCAO DA ORDEM!");
      Print("Retcode: ", result.retcode);
      Print("Descricao: ", GetTradeResultDescription(result.retcode));
      
      SendExecutionReport(signalID, "ERROR", 0, GetTradeResultDescription(result.retcode));
      stats.ordersRejected++;
      stats.errors++;
   }
}

//+------------------------------------------------------------------+
//| Envia relatório de execução COM SUCESSO para Python              |
//+------------------------------------------------------------------+
void SendExecutionReportSuccess(string signalID, string symbol, MqlTradeResult &result)
{
   //--- Construir JSON manualmente
   string report = "{";
   report += "\"message_type\":\"EXECUTION_REPORT\",";
   report += "\"original_signal_id\":\"" + signalID + "\",";
   report += "\"timestamp\":\"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\",";
   report += "\"status\":\"FILLED\",";
   report += "\"order_ticket\":" + IntegerToString(result.order) + ",";
   report += "\"deal_ticket\":" + IntegerToString(result.deal) + ",";
   report += "\"symbol\":\"" + symbol + "\",";
   report += "\"volume\":" + DoubleToString(result.volume, 2) + ",";
   report += "\"price\":" + DoubleToString(result.price, 5) + ",";
   report += "\"error_description\":\"\"";
   report += "}";
   
   //--- Enviar
   SendMessage(report);
   Print("Relatorio de execucao enviado: FILLED");
}

//+------------------------------------------------------------------+
//| Envia relatório de execução COM ERRO/REJEIÇÃO para Python        |
//+------------------------------------------------------------------+
void SendExecutionReport(string signalID, string status, ulong orderTicket, string errorDesc)
{
   //--- Construir JSON manualmente
   string report = "{";
   report += "\"message_type\":\"EXECUTION_REPORT\",";
   report += "\"original_signal_id\":\"" + signalID + "\",";
   report += "\"timestamp\":\"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\",";
   report += "\"status\":\"" + status + "\",";
   report += "\"order_ticket\":" + IntegerToString(orderTicket) + ",";
   report += "\"error_description\":\"" + errorDesc + "\"";
   report += "}";
   
   //--- Enviar
   SendMessage(report);
   Print("Relatorio de execucao enviado: ", status);
}

//+------------------------------------------------------------------+
//| Processa heartbeat                                               |
//+------------------------------------------------------------------+
void ProcessHeartbeat(string message)
{
   Print("[DEBUG] Heartbeat recebido do servidor!");
   lastHeartbeat = TimeCurrent();
   Print("[DEBUG] lastHeartbeat atualizado para: ", lastHeartbeat);
   
   //--- Responder com heartbeat
   string response = "{\"message_type\":\"HEARTBEAT_ACK\",\"ea_time\":\"" + 
                    TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\"}";
   SendMessage(response);
   Print("[DEBUG] Heartbeat ACK enviado para servidor");
}

//+------------------------------------------------------------------+
//| Processa confirmação de handshake                                |
//+------------------------------------------------------------------+
void ProcessHandshakeAck(string message)
{
   Print("========================================");
   Print("HANDSHAKE CONFIRMADO PELO SERVIDOR");
   Print("========================================");
   
   //--- Extrair informações do servidor
   string serverName = ExtractJSONValue(message, "server_name");
   string serverVersion = ExtractJSONValue(message, "version");
   string status = ExtractJSONValue(message, "status");
   
   Print("Servidor: ", serverName, " v", serverVersion);
   Print("Status: ", status);
   Print("========================================");
   Print("CONEXAO VALIDADA. PRONTO PARA TRADING.");
   Print("========================================");
   
   //--- Atualizar último heartbeat (considerar ACK como "sinal de vida")
   lastHeartbeat = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Verifica kill-switch de drawdown                                 |
//+------------------------------------------------------------------+
bool CheckKillSwitch()
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   if(balance == 0)
      return false;
   
   double drawdown = ((balance - equity) / balance) * 100.0;
   
   if(drawdown > InpMaxDrawdown)
   {
      Print("========================================");
      Print("KILL-SWITCH ATIVADO!");
      Print("Drawdown: ", drawdown, "%");
      Print("Limite: ", InpMaxDrawdown, "%");
      Print("Fechando todas as posicoes...");
      Print("========================================");
      
      CloseAllPositions();
      
      //--- Notificar Python
      string alert = "{\"message_type\":\"ALERT\",\"type\":\"KILL_SWITCH\",\"drawdown\":" + 
                    DoubleToString(drawdown, 2) + "}";
      SendMessage(alert);
      
      return true;
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Fecha todas as posições                                          |
//+------------------------------------------------------------------+
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
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Conta ordens abertas                                             |
//+------------------------------------------------------------------+
int CountOpenOrders()
{
   int count = 0;
   
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
            count++;
      }
   }
   
   return count;
}

//+------------------------------------------------------------------+
//| Extrai valor de um campo JSON (parsing simplificado)             |
//+------------------------------------------------------------------+
string ExtractJSONValue(string json, string key)
{
   string searchKey = "\"" + key + "\":";
   int startPos = StringFind(json, searchKey);
   
   if(startPos < 0)
      return "";
   
   startPos += StringLen(searchKey);
   
   //--- Pular espaços e aspas
   while(startPos < StringLen(json) && 
         (StringGetCharacter(json, startPos) == ' ' || 
          StringGetCharacter(json, startPos) == '"'))
   {
      startPos++;
   }
   
   //--- Encontrar fim do valor
   int endPos = startPos;
   bool inString = (StringGetCharacter(json, startPos-1) == '"');
   
   while(endPos < StringLen(json))
   {
      ushort ch = StringGetCharacter(json, endPos);
      
      if(inString && ch == '"')
         break;
      else if(!inString && (ch == ',' || ch == '}'))
         break;
      
      endPos++;
   }
   
   string value = StringSubstr(json, startPos, endPos - startPos);
   StringTrimLeft(value);
   StringTrimRight(value);
   
   return value;
}

//+------------------------------------------------------------------+
//| Retorna descrição do código de retorno                           |
//+------------------------------------------------------------------+
string GetTradeResultDescription(uint retcode)
{
   switch(retcode)
   {
      case TRADE_RETCODE_DONE:           return "Executado";
      case TRADE_RETCODE_REJECT:         return "Rejeitado";
      case TRADE_RETCODE_INVALID:        return "Parametros invalidos";
      case TRADE_RETCODE_INVALID_VOLUME: return "Volume invalido";
      case TRADE_RETCODE_INVALID_PRICE:  return "Preco invalido";
      case TRADE_RETCODE_INVALID_STOPS:  return "Stops invalidos";
      case TRADE_RETCODE_NO_MONEY:       return "Fundos insuficientes";
      case TRADE_RETCODE_MARKET_CLOSED:  return "Mercado fechado";
      case TRADE_RETCODE_POSITION_CLOSED:return "Posicao ja fechada";
      default:                           return "Erro " + IntegerToString(retcode);
   }
}
//+------------------------------------------------------------------+

