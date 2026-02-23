//+------------------------------------------------------------------+
//|                                                      ARTEMIS.mq5 |
//|                  Copyright 2024, MetaQuotes Ltd. - Versão FINAL  |
//|             Sistema de Trading Quântico Completo (Versão Final)  |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"  
#property version   "1.0"
#property strict

//=== MÓDULOS PRINCIPAIS ===
#include "..\\Core\\CAgentBase.mqh"              // v8.0
#include "..\\Quantum\\CQuantumMarketPhysics.mqh"   // v3.5
#include "..\\Core\\CTimeframeHierarchy.mqh"     // v2.0
#include "..\\Core\\CAdaptiveMemory.mqh"         // v1.0
#include "..\\Core\\CSafetyNetGuardian.mqh"      // v1.0
#include "..\\Core\\CGameTheoryConsensus.mqh"    // v1.0
#include "..\\Core\\CQuantumPriceEngine.mqh"     // v1.0
#include "..\\Core\\CMarketRegimeDetector.mqh"   // v1.0
#include "..\\Include\\Crypt\\CHash.mqh"          // v3.0

//=== AGENTES ===
#include "..\\Agents\\MeanReversionAgent.mqh"    // v2.6
#include "..\\Agents\\VolumeSurgeAgent.mqh"      // v2.6

//=== UTILITÁRIOS ===
#include "..\\Utils\\CLogger.mqh"                // v1.0
#include "..\\Utils\\CBacktester.mqh"            // v1.0
#include "..\\Risk\\CRiskManager.mqh"            // v1.0
#include "..\\Gui\\CGUIManager.mqh"              // v1.0

//=== NOVOS MÓDULOS ===
#include "..\\Neural\\NeuralPredictor.mqh"   // v1.0

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

input group "Configurações Quânticas";
input double QuantumEntropyThreshold = 0.7;
input double QuantumSuperpositionThreshold = 0.5;
input double QuantumTunnelingThreshold = 0.3;
input int QuantumCorrelationPeriod = 30;

input group "Configurações de Memória Adaptativa";
input int MemoryLookbackPeriod = 100;
input double MemoryConfidenceThreshold = 0.7;
input double MemoryMinDuration = 3600;
input double MemoryForgetRate = 0.1;

input group "Configurações do Guardião de Segurança";
input double SafetyMaxDrawdown = 15.0;
input double SafetyMaxExposure = 50.0;
input double SafetyVolatilityThreshold = 0.2;
input double SafetySpreadThreshold = 5.0;
input int SafetyMaxConsecutiveLosses = 5;

input group "Configurações de Consenso";
input double ConsensusAgreementThreshold = 0.7;
input double ConsensusDivergenceThreshold = 0.3;
input double ConsensusNashWeight = 0.6;
input double ConsensusMinimaxWeight = 0.4;

input group "Configurações do Motor de Preços";
input double PriceDecoherenceRate = 0.1;
input double PriceEntanglementThreshold = 0.5;
input double PriceSuperpositionFactor = 0.3;
input int PriceProjectionPeriods = 10;
input double PriceConfidenceThreshold = 0.7;

input group "Configurações de Regime de Mercado";
input int RegimeLookbackPeriod = 100;
input double RegimeConfidenceThreshold = 0.7;
input double RegimeMinDuration = 3600;
input double RegimeFeatureWeights[] = {0.2, 0.2, 0.2, 0.15, 0.15, 0.1};

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
string g_trading_symbols[];
int g_total_symbols;
datetime g_last_bar_time;
double g_account_risk_level;
ulong g_magic_number = 123456789;

// Componentes principais
CQuantumMarketPhysics* g_quantum_physics = NULL;
CAdaptiveMemory* g_adaptive_memory = NULL;
CSafetyNetGuardian* g_safety_guardian = NULL;
CGameTheoryConsensus* g_consensus = NULL;
CQuantumPriceEngine* g_price_engine = NULL;
CMarketRegimeDetector* g_regime_detector = NULL;
CRiskManager* g_risk_manager = NULL;

// Agentes de trading
CMeanReversionAgent* g_mr_agents[];
CVolumeSurgeAgent* g_vs_agents[];
CNeuralPredictor* g_neural_predictors[];

// Componentes de interface e utilidades
CGUIManager* g_gui_manager = NULL;
CLogger* g_logger = NULL;
CBacktester* g_backtester = NULL;

// Cache de dados
struct MarketData {
   double price;
   double volume;
   double volatility;
   double entropy;
   double superposition;
   datetime time;
};
MarketData g_market_cache[];

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
   g_logger = new CLogger();
   g_quantum_physics = new CQuantumMarketPhysics(g_logger);
   g_adaptive_memory = new CAdaptiveMemory(g_logger);
   g_safety_guardian = new CSafetyNetGuardian(g_logger);
   g_consensus = new CGameTheoryConsensus(g_logger);
   g_price_engine = new CQuantumPriceEngine(g_logger);
   g_regime_detector = new CMarketRegimeDetector(g_logger);
   g_risk_manager = new CRiskManager(g_logger);

   //--- Inicialização dos componentes de interface
   g_gui_manager = new CGUIManager();
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

   // Configurar componentes
   g_quantum_physics.SetParameters(20, 50, QuantumCorrelationPeriod, QuantumTunnelingThreshold);
   g_adaptive_memory.SetLookbackPeriod(MemoryLookbackPeriod);
   g_adaptive_memory.SetConfidenceThreshold(MemoryConfidenceThreshold);
   g_safety_guardian.SetThresholds(SafetyMaxDrawdown, SafetyMaxExposure, SafetyVolatilityThreshold, 
                                 SafetySpreadThreshold, SafetyMaxConsecutiveLosses);
   g_consensus.SetThresholds(ConsensusAgreementThreshold, ConsensusDivergenceThreshold);
   g_consensus.SetWeights(ConsensusNashWeight, ConsensusMinimaxWeight);
   g_price_engine.SetParameters(PriceDecoherenceRate, PriceEntanglementThreshold, 
                              PriceSuperpositionFactor, PriceProjectionPeriods, PriceConfidenceThreshold);
   g_regime_detector.SetParameters(RegimeLookbackPeriod, RegimeConfidenceThreshold, 
                                 RegimeMinDuration, RegimeFeatureWeights);
   g_risk_manager.SetParameters(RiskPerTrade, MaxDailyRisk, MaxDrawdown, KellyFraction);

   //--- Inicialização dos agentes para cada símbolo
   ArrayResize(g_mr_agents, g_total_symbols);
   ArrayResize(g_vs_agents, g_total_symbols);
   ArrayResize(g_neural_predictors, g_total_symbols);
   ArrayResize(g_market_cache, g_total_symbols);

   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];
      if(!SymbolInfoDouble(symbol, SYMBOL_BID))
      {
         Print("Símbolo ", symbol, " não disponível");
         continue;
      }

      g_mr_agents[i] = new CMeanReversionAgent("MR_"+symbol, symbol, BaseTimeframe, MR_Period, MR_Threshold);
      g_vs_agents[i] = new CVolumeSurgeAgent("VS_"+symbol, symbol, BaseTimeframe, VS_Period, VS_Threshold);
      g_neural_predictors[i] = new CNeuralPredictor(symbol, NeuralInputSize, NeuralHiddenSize, NeuralOutputSize, NeuralLearningRate);
      
      // Adicionar agentes ao consenso
      g_consensus.AddAgent(g_mr_agents[i]);
      g_consensus.AddAgent(g_vs_agents[i]);
   }

   //--- Configuração final
   g_last_bar_time = 0;
   g_account_risk_level = 1.0;
   EventSetTimer(30); // Atualizações a cada 30 segundos

   g_logger.Info("=== SISTEMA ARTEMIS INICIALIZADO ===");
   g_logger.Info("Símbolos: " + Symbols);
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
   // Limpar memória
   if(g_logger != NULL) delete g_logger;
   if(g_quantum_physics != NULL) delete g_quantum_physics;
   if(g_adaptive_memory != NULL) delete g_adaptive_memory;
   if(g_safety_guardian != NULL) delete g_safety_guardian;
   if(g_consensus != NULL) delete g_consensus;
   if(g_price_engine != NULL) delete g_price_engine;
   if(g_regime_detector != NULL) delete g_regime_detector;
   if(g_risk_manager != NULL) delete g_risk_manager;
   if(g_gui_manager != NULL) delete g_gui_manager;
   if(g_backtester != NULL) delete g_backtester;

   // Limpar arrays
   ArrayFree(g_trading_symbols);
   ArrayFree(g_market_cache);
   ArrayFree(g_mr_agents);
   ArrayFree(g_vs_agents);
   ArrayFree(g_neural_predictors);

   EventKillTimer();
   Comment("");
   g_logger.Info("=== SISTEMA ARTEMIS FINALIZADO ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Atualizar cache de dados
   UpdateMarketCache();

   // Verificar segurança
   if(!g_safety_guardian.CheckSafety())
   {
      g_logger.Warn("Verificações de segurança falharam - Trading pausado");
      return;
   }

   // Detectar regime de mercado
   MarketRegime regime = g_regime_detector.DetectRegime();
   g_logger.Info("Regime de mercado detectado: " + EnumToString(regime));

   // Atualizar memória adaptativa
   g_adaptive_memory.Update(regime);

   // Obter consenso dos agentes
   double consensus = g_consensus.GetConsensus();
   g_logger.Info("Consenso dos agentes: " + DoubleToString(consensus, 2));

   // Atualizar física quântica
   g_quantum_physics.Update();

   // Atualizar motor de preços
   g_price_engine.Update();

   // Gerenciar posições existentes
   ManagePositions();

   // Verificar novas oportunidades
   if(CanOpenNewPosition())
   {
      CheckForNewSignals();
   }
}

//+------------------------------------------------------------------+
//| Funções auxiliares                                               |
//+------------------------------------------------------------------+
void UpdateMarketCache()
{
   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];
      MarketData data;
      data.price = SymbolInfoDouble(symbol, SYMBOL_BID);
      data.volume = iVolume(symbol, BaseTimeframe, 0);
      data.volatility = g_quantum_physics.GetVolatility();
      data.entropy = g_quantum_physics.GetEntropy();
      data.superposition = g_quantum_physics.GetSuperposition();
      data.time = TimeCurrent();
      
      ArrayResize(g_market_cache, ArraySize(g_market_cache) + 1);
      g_market_cache[ArraySize(g_market_cache) - 1] = data;
   }
}

bool CanOpenNewPosition()
{
   return g_risk_manager.CanOpenNewPosition();
}

void CheckForNewSignals()
{
   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];
      
      // Verificar sinais dos agentes
      double mr_signal = g_mr_agents[i].GetSignal();
      double vs_signal = g_vs_agents[i].GetSignal();
      double neural_signal = g_neural_predictors[i].GetSignal();
      
      // Combinar sinais
      double combined_signal = (mr_signal + vs_signal + neural_signal) / 3.0;
      
      // Aplicar filtros quânticos
      combined_signal = g_quantum_physics.FilterSignal(combined_signal);
      
      // Verificar consenso
      if(g_consensus.ValidateSignal(combined_signal))
      {
         // Executar trade
         ExecuteTrade(symbol, combined_signal);
      }
   }
}

void ExecuteTrade(string symbol, double signal)
{
   if(signal > 0)
   {
      g_risk_manager.OpenLongPosition(symbol);
   }
   else if(signal < 0)
   {
      g_risk_manager.OpenShortPosition(symbol);
   }
}

void ManagePositions()
{
   for(int i = 0; i < g_total_symbols; i++)
   {
      string symbol = g_trading_symbols[i];
      g_risk_manager.ManagePosition(symbol);
   }
}