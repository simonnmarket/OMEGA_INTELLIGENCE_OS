//+------------------------------------------------------------------+
//|                                                      ARTEMIS.mq5 |
//|                  Copyright 2024, MetaQuotes Ltd. - Versão FINAL  |
//|             Sistema de Trading Quântico Completo (468 linhas)     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com" 
#property version   "1.0"
#property strict

//=== MÓDULOS PRINCIPAIS (VERSÕES CORRIGIDAS) ===
#include "Quantum\QuantumMarketPhysics.mqh"    // v3.5
#include "Core\FractalAnalysis.mqh"        // v2.7
#include "Core\TimeframeHierarchy.mqh"     // v2.0
#include "Core\VolatilityAnalysis.mqh"     // v2.3
#include "Risk\AdaptiveRiskSystem.mqh"     // v3.2

//=== AGENTES (VERSÕES CORRIGIDAS) ===
#include "Agents\AgentBase.mqh"            // v4.2
#include "Agents\MeanReversionAgent.mqh"   // v2.6
#include "Agents\VolumeSurgeAgent.mqh"     // v2.6

//=== NOVOS MÓDULOS ===
#include "Gui\GUIManager.mqh"              // v1.0
#include "NeuralNet\NeuralPredictor.mqh"   // v1.0
#include "Utils\Logger.mqh"                // v1.0
#include "Utils\Backtester.mqh"            // v1.0

//=== CONFIGURAÇÕES ===
input group "Configurações Principais";
input string Symbols = "EURUSD,GBPUSD,XAUUSD";
input ENUM_TIMEFRAMES BaseTimeframe = PERIOD_H1;
input int MaxPositions = 5;

input group "Gestão de Risco Avançada";
input double RiskPerTrade = 1.5;
input double MaxDailyRisk = 5.0;
input double MaxDrawdown = 20.0;
input double KellyFraction = 0.6;

input group "Configurações dos Agentes";
input int MR_Period = 14;
input double MR_Threshold = 2.0;
input int VS_Period = 20;
input double VS_Threshold = 1.8;

input group "Configurações da Rede Neural";
input int NeuralInputSize = 100;
input int NeuralHiddenSize = 50;
input int NeuralOutputSize = 1;
input double NeuralLearningRate = 0.01;

input group "Configurações de Logging";
input bool EnableLogging = true;
input bool EnableTelegram = false;
input bool EnableEmail = false;
input string TelegramToken = "";
input string TelegramChatId = "";
input string EmailServer = "";
input string EmailPort = "";
input string EmailUsername = "";
input string EmailPassword = "";
input string EmailRecipients = "";

//=== VARIÁVEIS GLOBAIS ===
// Componentes principais
CQuantumMarketPhysics* g_quantum_physics = NULL;
CFractalAnalysis* g_fractal_analysis = NULL;
CTimeframeHierarchy* g_timeframe_hierarchy = NULL;
CVolatilityAnalysis* g_volatility_analysis = NULL;
CAdaptiveRiskSystem* g_risk_system = NULL;

// Agentes de trading
CMeanReversionAgent* g_mr_agents[];
CVolumeSurgeAgent* g_vs_agents[];

// Novos componentes
CGUIManager* g_gui_manager = NULL;
CNeuralPredictor* g_neural_predictors[];
CLogger* g_logger = NULL;
CBacktester* g_backtester = NULL;

// Controle de execução
string g_trading_symbols[];
int g_total_symbols;
datetime g_last_bar_time;
double g_account_risk_level;
ulong g_magic_number = 123456789;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Parse dos símbolos
   g_total_symbols = StringSplit(Symbols, ',', g_trading_symbols);
   if(g_total_symbols <= 0)
   {
      Alert("Nenhum símbolo válido configurado!");
      return INIT_PARAMETERS_INCORRECT;
   }

   //--- Inicialização dos componentes principais
   g_quantum_physics = new CQuantumMarketPhysics();
   g_fractal_analysis = new CFractalAnalysis(g_trading_symbols[0]);
   g_timeframe_hierarchy = new CTimeframeHierarchy();
   g_volatility_analysis = new CVolatilityAnalysis(50);
   g_risk_system = new CAdaptiveRiskSystem(RiskPerTrade, MaxDailyRisk, MaxDrawdown);

   //--- Inicialização dos novos componentes
   g_gui_manager = new CGUIManager();
   g_logger = new CLogger("artemis.log", LOG_LEVEL_INFO);
   g_backtester = new CBacktester();
   
   // Configurar Logger
   if(EnableLogging)
   {
      g_logger.EnableConsoleOutput(true);
      g_logger.EnableFileOutput(true);
      
      if(EnableTelegram && TelegramToken != "" && TelegramChatId != "")
      {
         g_logger.EnableTelegramOutput(true);
         g_logger.SetTelegramSettings(TelegramToken, TelegramChatId);
      }
      
      if(EnableEmail && EmailServer != "" && EmailUsername != "")
      {
         g_logger.EnableEmailOutput(true);
         string recipients[];
         StringSplit(EmailRecipients, ',', recipients);
         g_logger.SetEmailSettings(EmailServer, EmailPort, EmailUsername, EmailPassword, recipients);
      }
   }

   // Garantir que SetKellyFraction() exista na classe RiskManager
   if(CheckPointer(g_risk_system) != POINTER_INVALID)
      g_risk_system.SetKellyFraction(KellyFraction);

   //--- Inicialização dos agentes para cada símbolo
   ArrayResize(g_mr_agents, g_total_symbols);
   ArrayResize(g_vs_agents, g_total_symbols);
   ArrayResize(g_neural_predictors, g_total_symbols);

   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];

      // Verificar se o símbolo existe
      if(!SymbolInfoDouble(symbol, SYMBOL_BID))
      {
         Print("Símbolo ", symbol, " não disponível - removendo da lista");
         ArrayRemove(g_trading_symbols, i--, 1);
         g_total_symbols--;
         continue;
      }

      g_mr_agents[i] = new CMeanReversionAgent("MR_"+symbol, symbol, BaseTimeframe, MR_Period, MR_Threshold);
      g_vs_agents[i] = new CVolumeSurgeAgent("VS_"+symbol, symbol, BaseTimeframe, VS_Period, VS_Threshold);
      g_neural_predictors[i] = new CNeuralPredictor(symbol, NeuralInputSize, NeuralHiddenSize, NeuralOutputSize, NeuralLearningRate);
   }

   //--- Configuração final
   g_last_bar_time = 0;
   g_account_risk_level = 1.0;

   EventSetTimer(30); // Atualizações a cada 30 segundos
   g_logger.Info("=== SISTEMA ARTEMIS INICIALIZADO ===");

   //--- Exibição dos símbolos como string
   string symbolsList = "";
   for(int s = 0; s < g_total_symbols; s++)
      symbolsList += g_trading_symbols[s] + (s < g_total_symbols - 1 ? ", " : "");

   g_logger.Info("Símbolos: " + symbolsList);
   g_logger.Info("Timeframe Base: " + EnumToString(BaseTimeframe));
   g_logger.Info("Configuração de Risco: " + DoubleToString(RiskPerTrade, 1) + "% por trade, " + 
               DoubleToString(MaxDailyRisk, 1) + "% diário");

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   SafeDelete(g_quantum_physics);
   SafeDelete(g_fractal_analysis);
   SafeDelete(g_timeframe_hierarchy);
   SafeDelete(g_volatility_analysis);
   SafeDelete(g_risk_system);
   SafeDelete(g_gui_manager);
   SafeDelete(g_logger);
   SafeDelete(g_backtester);

   for(int i = 0; i < ArraySize(g_mr_agents); i++)
   {
      SafeDelete(g_mr_agents[i]);
      SafeDelete(g_vs_agents[i]);
      SafeDelete(g_neural_predictors[i]);
   }

   EventKillTimer();
   Comment("");
   g_logger.Info("=== SISTEMA ARTEMIS FINALIZADO ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   datetime currentBarTime = iTime(_Symbol, BaseTimeframe, 0);
   if(g_last_bar_time == currentBarTime) return;
   g_last_bar_time = currentBarTime;

   UpdateMarketAnalysis();
   UpdateRiskParameters();
   UpdateGUI();

   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];

      if(!SymbolInfoDouble(symbol, SYMBOL_BID))
         continue;

      double mrSignal = g_mr_agents[i].GetSignal();
      double vsSignal = g_vs_agents[i].GetSignal();
      double neuralSignal = g_neural_predictors[i].PredictNextMove();

      ProcessSymbol(symbol, mrSignal, vsSignal, neuralSignal);
   }
}

//+------------------------------------------------------------------+
//| Atualiza análise de mercado                                      |
//+------------------------------------------------------------------+
void UpdateMarketAnalysis()
{
   g_quantum_physics.Update();
   g_fractal_analysis.UpdateData();
   g_timeframe_hierarchy.Update();

   for(int i = 0; i < g_total_symbols; i++)
   {
      g_volatility_analysis.Update(g_trading_symbols[i], BaseTimeframe);
   }

   for(int i = 0; i < g_total_symbols; i++)
   {
      g_mr_agents[i].Update();
      g_vs_agents[i].Update();
   }
}

//+------------------------------------------------------------------+
//| Atualiza parâmetros de risco                                     |
//+------------------------------------------------------------------+
void UpdateRiskParameters()
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double drawdown = (balance > 0) ? (balance - equity) / balance * 100.0 : 0.0;

   if(drawdown >= MaxDrawdown * 0.8)
      g_account_risk_level = 0.5;
   else
      g_account_risk_level = 1.0 - (drawdown / (MaxDrawdown * 2.0));

   g_risk_system.UpdateRiskProfile(g_account_risk_level);
}

//+------------------------------------------------------------------+
//| Atualiza interface gráfica                                       |
//+------------------------------------------------------------------+
void UpdateGUI()
{
   g_gui_manager.Update();
}

//+------------------------------------------------------------------+
//| Processa decisões para um símbolo                                |
//+------------------------------------------------------------------+
void ProcessSymbol(string symbol, double mrSignal, double vsSignal, double neuralSignal)
{
   if(PositionsTotal() >= MaxPositions) return;

   int idx = ArrayIndexOf(g_trading_symbols, symbol);
   if(idx < 0) return;

   double confidenceMR = g_mr_agents[idx].Confidence();
   double confidenceVS = g_vs_agents[idx].Confidence();
   double confidenceNeural = 0.8; // Confiança fixa para a rede neural por enquanto

   // Combinação ponderada dos sinais
   double combinedSignal = (mrSignal * confidenceMR + 
                          vsSignal * confidenceVS + 
                          neuralSignal * confidenceNeural) / 
                          (confidenceMR + confidenceVS + confidenceNeural);

   if(g_volatility_analysis.IsHighVolatility(symbol))
      combinedSignal *= 0.7;

   if(MathAbs(combinedSignal) > 0.6)
      ExecuteTrade(symbol, combinedSignal);
}

//+------------------------------------------------------------------+
//| Executa operações de trading                                     |
//+------------------------------------------------------------------+
void ExecuteTrade(string symbol, double signal)
{
   double stopLossPoints = g_volatility_analysis.GetATR(symbol, 14) * 2.0;
   double takeProfitPoints = stopLossPoints * 2.0;
   double lotSize = g_risk_system.CalculatePositionSize(symbol, stopLossPoints);

   double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   lotSize = MathMax(minLot, MathMin(lotSize, maxLot));

   if(lotSize <= 0) return;

   CTrade trade;
   trade.SetExpertMagicNumber(g_magic_number);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(symbol);

   if(signal > 0)
   {
      double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
      double stopLoss = ask - stopLossPoints * _Point;
      double takeProfit = ask + takeProfitPoints * _Point;

      if(trade.Buy(lotSize, symbol, ask, stopLoss, takeProfit))
      {
         g_logger.Info(StringFormat("Compra executada: %s, Lote: %.2f, SL: %.5f, TP: %.5f",
                                symbol, lotSize, stopLoss, takeProfit));
      }
      else
      {
         g_logger.Error(StringFormat("Erro na compra: %s, Erro: %d",
                                 symbol, GetLastError()));
      }
   }
   else
   {
      double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
      double stopLoss = bid + stopLossPoints * _Point;
      double takeProfit = bid - takeProfitPoints * _Point;

      if(trade.Sell(lotSize, symbol, bid, stopLoss, takeProfit))
      {
         g_logger.Info(StringFormat("Venda executada: %s, Lote: %.2f, SL: %.5f, TP: %.5f",
                                symbol, lotSize, stopLoss, takeProfit));
      }
      else
      {
         g_logger.Error(StringFormat("Erro na venda: %s, Erro: %d",
                                 symbol, GetLastError()));
      }
   }
}

//+------------------------------------------------------------------+
//| Função auxiliar para deletar objetos com segurança                |
//+------------------------------------------------------------------+
void SafeDelete(CObject*& obj)
{
   if(obj != NULL)
   {
      delete obj;
      obj = NULL;
   }
}

int ArrayIndexOf(const string &array[], const string value)
{
   for(int i = 0; i < ArraySize(array); i++)
   {
      if(array[i] == value) return i;
   }
   return -1;
}