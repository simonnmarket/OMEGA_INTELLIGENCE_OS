//+------------------------------------------------------------------+
//| Artemis.mq5 - Expert Advisor Principal                          |
//| Projeto Artemis - Versão Institucional                          |
//| Sistema de trading quântico otimizado                           |
//+------------------------------------------------------------------+

#property copyright "Projeto Artemis"
#property version   "2.0"
#property description "Sistema de trading quântico institucional"

// Includes dos módulos otimizados
#include "Core/ArtemisQuantumState.mqh"
#include "Core/ArtemisMarketField.mqh"
#include "Core/ArtemisDecisionMatrix.mqh"
#include "Agents/ArtemisAgentBase.mqh"

//+------------------------------------------------------------------+
//| Parâmetros de entrada                                           |
//+------------------------------------------------------------------+
input group "=== Configurações Gerais ==="
input bool InpEnableTrading = true;                    // Habilitar trading
input double InpLotSize = 0.1;                        // Tamanho do lote
input int InpMagicNumber = 20241206;                   // Número mágico
input string InpSymbolList = "EURUSD,GBPUSD,USDJPY";  // Lista de símbolos

input group "=== Configurações de Risco ==="
input double InpMaxRiskPercent = 2.0;                 // Risco máximo por trade (%)
input double InpStopLoss = 100;                       // Stop Loss (pontos)
input double InpTakeProfit = 200;                     // Take Profit (pontos)
input int InpMaxPositions = 3;                        // Máximo de posições simultâneas

input group "=== Configurações do Sistema ==="
input ARTEMIS_LOG_LEVEL InpLogLevel = LOG_INFO;       // Nível de log
input int InpUpdateFrequency = 1;                     // Frequência de atualização (segundos)
input double InpBaseThreshold = 0.6;                  // Threshold base para decisões

//+------------------------------------------------------------------+
//| Variáveis globais                                               |
//+------------------------------------------------------------------+
ArtemisMarketField* g_market_field;
ArtemisDecisionMatrix* g_decision_matrix;
ArtemisAgentBase* g_agents[10];
string g_symbols[];
int g_symbol_count;

// Métricas de performance
datetime g_last_update;
int g_total_trades;
double g_total_profit;
datetime g_start_time;

//+------------------------------------------------------------------+
//| Inicialização do Expert Advisor                                 |
//+------------------------------------------------------------------+
int OnInit() {
   Print("=== Inicializando Artemis v2.0 ===");
   
   // Inicializar sistema de logging
   ArtemisLogger::Initialize(InpLogLevel, "artemis.log");
   ArtemisLogger::Log(LOG_INFO, "Artemis", "Iniciando sistema...");
   
   // Inicializar cache de indicadores
   ArtemisIndicatorCache::Initialize();
   
   // Processar lista de símbolos
   if(!ProcessSymbolList()) {
      ArtemisLogger::Log(LOG_ERROR, "Artemis", "Falha ao processar lista de símbolos");
      return INIT_FAILED;
   }
   
   // Inicializar componentes principais
   g_market_field = new ArtemisMarketField(g_symbol_count);
   g_decision_matrix = new ArtemisDecisionMatrix();
   
   // Configurar threshold adaptativo
   g_decision_matrix.SetThresholdAdaptationRate(0.1);
   
   // Inicializar agentes
   if(!InitializeAgents()) {
      ArtemisLogger::Log(LOG_ERROR, "Artemis", "Falha ao inicializar agentes");
      return INIT_FAILED;
   }
   
   // Configurar variáveis de controle
   g_last_update = 0;
   g_total_trades = 0;
   g_total_profit = 0.0;
   g_start_time = TimeCurrent();
   
   ArtemisLogger::Log(LOG_INFO, "Artemis", 
                     StringFormat("Sistema inicializado com %d símbolos e %d agentes", 
                                g_symbol_count, ArraySize(g_agents)));
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Desinicialização do Expert Advisor                             |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   ArtemisLogger::Log(LOG_INFO, "Artemis", 
                     StringFormat("Finalizando sistema (razão: %d)", reason));
   
   // Gerar relatório final
   GenerateFinalReport();
   
   // Limpar agentes
   for(int i = 0; i < ArraySize(g_agents); i++) {
      if(g_agents[i] != NULL) {
         delete g_agents[i];
         g_agents[i] = NULL;
      }
   }
   
   // Limpar componentes principais
   if(g_market_field != NULL) {
      delete g_market_field;
      g_market_field = NULL;
   }
   
   if(g_decision_matrix != NULL) {
      delete g_decision_matrix;
      g_decision_matrix = NULL;
   }
   
   ArtemisLogger::Log(LOG_INFO, "Artemis", "Sistema finalizado");
}

//+------------------------------------------------------------------+
//| Função principal de tick                                        |
//+------------------------------------------------------------------+
void OnTick() {
   datetime current_time = TimeCurrent();
   
   // Verificar frequência de atualização
   if(current_time - g_last_update < InpUpdateFrequency) {
      return;
   }
   
   // Atualizar análise de mercado
   if(!UpdateMarketAnalysis()) {
      ArtemisLogger::Log(LOG_WARN, "Artemis", "Falha na atualização da análise");
      return;
   }
   
   // Processar decisões de trading
   if(InpEnableTrading) {
      ProcessTradingDecisions();
   }
   
   // Atualizar métricas
   UpdatePerformanceMetrics();
   
   g_last_update = current_time;
}

//+------------------------------------------------------------------+
//| Processamento da lista de símbolos                             |
//+------------------------------------------------------------------+
bool ProcessSymbolList() {
   string symbol_list = InpSymbolList;
   
   // Contar símbolos
   g_symbol_count = 1;
   for(int i = 0; i < StringLen(symbol_list); i++) {
      if(StringGetCharacter(symbol_list, i) == ',') {
         g_symbol_count++;
      }
   }
   
   // Redimensionar array
   ArrayResize(g_symbols, g_symbol_count);
   
   // Extrair símbolos
   int start = 0;
   int symbol_index = 0;
   
   for(int i = 0; i <= StringLen(symbol_list); i++) {
      if(i == StringLen(symbol_list) || StringGetCharacter(symbol_list, i) == ',') {
         if(i > start) {
            g_symbols[symbol_index] = StringSubstr(symbol_list, start, i - start);
            
            // Validar símbolo
            if(!SymbolSelect(g_symbols[symbol_index], true)) {
               ArtemisLogger::Log(LOG_WARN, "Artemis", 
                                 StringFormat("Símbolo %s não disponível", g_symbols[symbol_index]));
            }
            
            symbol_index++;
         }
         start = i + 1;
      }
   }
   
   ArtemisLogger::Log(LOG_INFO, "Artemis", 
                     StringFormat("Processados %d símbolos", g_symbol_count));
   
   return g_symbol_count > 0;
}

//+------------------------------------------------------------------+
//| Inicialização dos agentes                                      |
//+------------------------------------------------------------------+
bool InitializeAgents() {
   // Criar agentes de momentum
   for(int i = 0; i < 3; i++) {
      g_agents[i] = new ArtemisMomentumAgent(StringFormat("Momentum_%d", i + 1));
      if(!g_agents[i].Initialize()) {
         ArtemisLogger::Log(LOG_ERROR, "Artemis", 
                           StringFormat("Falha ao inicializar agente %d", i));
         return false;
      }
   }
   
   // Redimensionar array para o número real de agentes
   ArrayResize(g_agents, 3);
   
   return true;
}

//+------------------------------------------------------------------+
//| Atualização da análise de mercado                              |
//+------------------------------------------------------------------+
bool UpdateMarketAnalysis() {
   if(g_market_field == NULL) return false;
   
   // Analisar todos os símbolos
   bool success = g_market_field.AnalyzeAll(g_symbols, g_symbol_count, PERIOD_M1);
   
   if(success) {
      ArtemisLogger::Log(LOG_TRACE, "Artemis", "Análise de mercado atualizada");
   }
   
   return success;
}

//+------------------------------------------------------------------+
//| Processamento das decisões de trading                          |
//+------------------------------------------------------------------+
void ProcessTradingDecisions() {
   if(g_decision_matrix == NULL) return;
   
   // Verificar número máximo de posições
   if(PositionsTotal() >= InpMaxPositions) {
      return;
   }
   
   // Processar cada símbolo
   for(int i = 0; i < g_symbol_count; i++) {
      string symbol = g_symbols[i];
      
      // Verificar se já existe posição para este símbolo
      if(HasPosition(symbol)) {
         continue;
      }
      
      // Obter volatilidade atual para threshold adaptativo
      double volatility = iATR(symbol, PERIOD_M1, 14, 0);
      
      // Tomar decisão coletiva
      ARTEMIS_SIGNAL decision = g_decision_matrix.CollectiveDecision(g_agents, symbol, volatility);
      
      // Executar ordem se necessário
      if(decision != SIGNAL_NEUTRAL) {
         ExecuteOrder(symbol, decision);
      }
   }
}

//+------------------------------------------------------------------+
//| Execução de ordens                                             |
//+------------------------------------------------------------------+
void ExecuteOrder(string symbol, ARTEMIS_SIGNAL signal) {
   if(signal == SIGNAL_NEUTRAL) return;
   
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   // Configurar request básico
   request.symbol = symbol;
   request.volume = InpLotSize;
   request.magic = InpMagicNumber;
   request.type_filling = ORDER_FILLING_FOK;
   
   // Obter preços atuais
   double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   
   if(signal == SIGNAL_BUY) {
      request.action = TRADE_ACTION_DEAL;
      request.type = ORDER_TYPE_BUY;
      request.price = ask;
      
      if(InpStopLoss > 0) {
         request.sl = ask - InpStopLoss * point;
      }
      if(InpTakeProfit > 0) {
         request.tp = ask + InpTakeProfit * point;
      }
   } else if(signal == SIGNAL_SELL) {
      request.action = TRADE_ACTION_DEAL;
      request.type = ORDER_TYPE_SELL;
      request.price = bid;
      
      if(InpStopLoss > 0) {
         request.sl = bid + InpStopLoss * point;
      }
      if(InpTakeProfit > 0) {
         request.tp = bid - InpTakeProfit * point;
      }
   }
   
   // Executar ordem
   if(OrderSend(request, result)) {
      g_total_trades++;
      ArtemisLogger::Log(LOG_INFO, "Artemis", 
                        StringFormat("Ordem executada: %s %s %.2f @ %.5f", 
                                   symbol, 
                                   (signal == SIGNAL_BUY) ? "BUY" : "SELL",
                                   request.volume, request.price));
   } else {
      ArtemisLogger::Log(LOG_ERROR, "Artemis", 
                        StringFormat("Falha na execução: %d - %s", 
                                   result.retcode, result.comment));
   }
}

//+------------------------------------------------------------------+
//| Verificar se existe posição para o símbolo                     |
//+------------------------------------------------------------------+
bool HasPosition(string symbol) {
   for(int i = 0; i < PositionsTotal(); i++) {
      if(PositionGetSymbol(i) == symbol && 
         PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
         return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Atualização das métricas de performance                        |
//+------------------------------------------------------------------+
void UpdatePerformanceMetrics() {
   // Calcular P&L total
   double current_profit = 0.0;
   
   for(int i = 0; i < PositionsTotal(); i++) {
      if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
         current_profit += PositionGetDouble(POSITION_PROFIT);
      }
   }
   
   g_total_profit = current_profit;
   
   // Log periódico de status
   static datetime last_status_log = 0;
   datetime current_time = TimeCurrent();
   
   if(current_time - last_status_log >= 300) { // A cada 5 minutos
      ArtemisLogger::Log(LOG_INFO, "Artemis", 
                        StringFormat("Status: Trades=%d, P&L=%.2f, Posições=%d", 
                                   g_total_trades, g_total_profit, PositionsTotal()));
      last_status_log = current_time;
   }
}

//+------------------------------------------------------------------+
//| Geração de relatório final                                     |
//+------------------------------------------------------------------+
void GenerateFinalReport() {
   datetime end_time = TimeCurrent();
   double runtime_hours = (double)(end_time - g_start_time) / 3600.0;
   
   string report = StringFormat(
      "\n=== RELATÓRIO FINAL ARTEMIS ===\n" +
      "Tempo de execução: %.2f horas\n" +
      "Total de trades: %d\n" +
      "P&L total: %.2f\n" +
      "Posições abertas: %d\n" +
      "Símbolos monitorados: %d\n" +
      "Agentes ativos: %d\n",
      runtime_hours,
      g_total_trades,
      g_total_profit,
      PositionsTotal(),
      g_symbol_count,
      ArraySize(g_agents)
   );
   
   if(g_decision_matrix != NULL) {
      report += "\n" + g_decision_matrix.GenerateStatusReport();
   }
   
   if(g_market_field != NULL) {
      report += "\n" + g_market_field.GetStatusReport();
   }
   
   Print(report);
   ArtemisLogger::Log(LOG_INFO, "Artemis", report);
}

//+------------------------------------------------------------------+
//| Tratamento de eventos de timer                                 |
//+------------------------------------------------------------------+
void OnTimer() {
   // Implementar lógica de timer se necessário
   UpdatePerformanceMetrics();
}

//+------------------------------------------------------------------+
//| Tratamento de eventos de trade                                 |
//+------------------------------------------------------------------+
void OnTrade() {
   // Atualizar métricas quando trades são executados
   UpdatePerformanceMetrics();
   
   ArtemisLogger::Log(LOG_DEBUG, "Artemis", "Evento de trade processado");
}

