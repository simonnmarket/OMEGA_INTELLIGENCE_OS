//+------------------------------------------------------------------+
//| TestVolatilityManager.mq5 - Test Suite for Volatility Management  |
//| Version 3.0 - Unified and Enhanced (2025)                        |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property link      "https://www.quantumtrading.foundation"
#property version   "3.0"
#property strict

#include "CVolatilityManager.mqh"
#include "..\Utils\CLogger.mqh"

//===========================================
// GLOBAL VARIABLES
//===========================================
CLogger* g_logger = NULL;
CVolatilityManager* g_volatility = NULL;

//===========================================
// INITIALIZATION
//===========================================
int OnInit() {
   // Inicializa logger
   g_logger = new CLogger("VolatilityTest");
   if(!g_logger) {
      Print("Erro ao criar logger");
      return INIT_FAILED;
   }
   
   // Inicializa VolatilityManager
   g_volatility = new CVolatilityManager(g_logger);
   if(!g_volatility) {
      Print("Erro ao criar VolatilityManager");
      return INIT_FAILED;
   }
   
   // Configura VolatilityManager
   VolatilityConfig config;
   config.symbol = Symbol();
   config.timeframe = PERIOD_CURRENT;
   config.lookback_period = 100;
   config.atr_period = 14;
   config.volatility_threshold = 0.002;
   config.method = METHOD_HYBRID;
   config.use_quantum = true;
   config.monte_carlo_paths = 1000;
   config.min_data_points = 30;
   
   if(!g_volatility.Initialize(config)) {
      Print("Erro ao inicializar VolatilityManager");
      return INIT_FAILED;
   }
   
   // Executa testes
   RunTests();
   
   return INIT_SUCCEEDED;
}

//===========================================
// DEINITIALIZATION
//===========================================
void OnDeinit(const int reason) {
   if(g_volatility) {
      delete g_volatility;
      g_volatility = NULL;
   }
   
   if(g_logger) {
      delete g_logger;
      g_logger = NULL;
   }
}

//===========================================
// MAIN LOOP
//===========================================
void OnTick() {
   // Atualiza métricas
   double volatility = g_volatility.GetVolatility();
   VolatilityMetrics metrics = g_volatility.GetMetrics();
   
   // Exibe informações
   string info = StringFormat(
      "Volatilidade: %.6f\n" +
      "Regime: %d\n" +
      "Probabilidade: %.2f\n" +
      "GARCH: %.6f\n" +
      "Filtro: %.6f",
      volatility,
      g_volatility.GetCurrentRegime(),
      metrics.regime_probability,
      metrics.garch_volatility,
      metrics.combined_filter
   );
   
   Comment(info);
}

//===========================================
// TEST FUNCTIONS
//===========================================
void RunTests() {
   // Teste 1: Cálculo de Volatilidade
   TestVolatilityCalculation();
   
   // Teste 2: Ajuste de Sinal
   TestSignalAdjustment();
   
   // Teste 3: Detecção de Regime
   TestRegimeDetection();
   
   // Teste 4: Métricas
   TestMetrics();
}

void TestVolatilityCalculation() {
   double volatility = g_volatility.GetVolatility();
   
   if(volatility > 0) {
      g_logger.LogInfo("Teste de Cálculo de Volatilidade: OK");
      g_logger.LogInfo(StringFormat("Volatilidade: %.6f", volatility));
   } else {
      g_logger.LogError("Teste de Cálculo de Volatilidade: FALHA");
   }
}

void TestSignalAdjustment() {
   double original_signal = 1.0;
   double adjusted_signal = g_volatility.AdjustSignal(original_signal);
   
   if(adjusted_signal >= 0.1 && adjusted_signal <= 1.0) {
      g_logger.LogInfo("Teste de Ajuste de Sinal: OK");
      g_logger.LogInfo(StringFormat("Sinal Original: %.2f", original_signal));
      g_logger.LogInfo(StringFormat("Sinal Ajustado: %.2f", adjusted_signal));
   } else {
      g_logger.LogError("Teste de Ajuste de Sinal: FALHA");
   }
}

void TestRegimeDetection() {
   VolatilityRegime regime = g_volatility.GetCurrentRegime();
   
   if(regime >= REGIME_LOW && regime <= REGIME_EXTREME) {
      g_logger.LogInfo("Teste de Detecção de Regime: OK");
      g_logger.LogInfo(StringFormat("Regime Atual: %d", regime));
   } else {
      g_logger.LogError("Teste de Detecção de Regime: FALHA");
   }
}

void TestMetrics() {
   VolatilityMetrics metrics = g_volatility.GetMetrics();
   
   if(metrics.last_update > 0) {
      g_logger.LogInfo("Teste de Métricas: OK");
      g_logger.LogInfo(StringFormat("Última Atualização: %s", TimeToString(metrics.last_update)));
      g_logger.LogInfo(StringFormat("GARCH: %.6f", metrics.garch_volatility));
      g_logger.LogInfo(StringFormat("Filtro: %.6f", metrics.combined_filter));
   } else {
      g_logger.LogError("Teste de Métricas: FALHA");
   }
} 