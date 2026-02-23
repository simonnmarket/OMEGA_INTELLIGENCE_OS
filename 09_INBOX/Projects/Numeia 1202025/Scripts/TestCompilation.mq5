//+------------------------------------------------------------------+
//|                                              TestCompilation.mq5 |
//|                    Teste de Compilação - EA Numeia              |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

//+------------------------------------------------------------------+
//| Includes de Teste                                                |
//+------------------------------------------------------------------+
#include "../Core/CoreBrainManager.mqh"
#include "../Include/ExecutionLogic/TradeExecutor.mqh"
#include "../Include/ExecutionLogic/PositionManager.mqh"
#include "../Include/ExecutionLogic/DefenseOrchestrator.mqh"
#include "../Include/ExecutionLogic/ExecutionLoopController.mqh"
#include "../Include/Integration/SkyIntelBridge.mqh"
#include "../Auditor/AuditManager.mqh"
#include "../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
input bool   TEST_ALL_MODULES = true;    // Testar todos os módulos
input bool   SHOW_DETAILS = true;        // Mostrar detalhes dos testes

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("=== TESTE DE COMPILAÇÃO - NUMEIA EA ===", LOG_LEVEL_INFO);
   AuditLog("Iniciando testes de todos os módulos...", LOG_LEVEL_INFO);
   
   int testsPassed = 0;
   int testsFailed = 0;
   
   // Teste 1: CoreBrainManager
   if(TestCoreBrainManager()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ CoreBrainManager: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ CoreBrainManager: FALHOU");
   }
   
   // Teste 2: TradeExecutor
   if(TestTradeExecutor()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ TradeExecutor: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ TradeExecutor: FALHOU");
   }
   
   // Teste 3: PositionManager
   if(TestPositionManager()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ PositionManager: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ PositionManager: FALHOU");
   }
   
   // Teste 4: DefenseOrchestrator
   if(TestDefenseOrchestrator()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ DefenseOrchestrator: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ DefenseOrchestrator: FALHOU");
   }
   
   // Teste 5: ExecutionLoopController
   if(TestExecutionLoopController()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ ExecutionLoopController: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ ExecutionLoopController: FALHOU");
   }
   
   // Teste 6: SkyIntelBridge
   if(TestSkyIntelBridge()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ SkyIntelBridge: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ SkyIntelBridge: FALHOU");
   }
   
   // Teste 7: AuditManager
   if(TestAuditManager()) {
      testsPassed++;
      if(SHOW_DETAILS) AuditLog("✓ AuditManager: OK", LOG_LEVEL_DEBUG);
   } else {
      testsFailed++;
      LogError("✗ AuditManager: FALHOU");
   }
   
   // Resultado Final
   AuditLog("=== RESULTADO DOS TESTES ===", LOG_LEVEL_INFO);
   AuditLog("Testes aprovados: " + IntegerToString(testsPassed), LOG_LEVEL_INFO);
   AuditLog("Testes falharam: " + IntegerToString(testsFailed), LOG_LEVEL_ERROR);
   
   if(testsFailed == 0) {
      AuditLog("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.", LOG_LEVEL_INFO);
   } else {
      LogError("❌ ALGUNS TESTES FALHARAM! Verificar erros acima.");
   }
}

//+------------------------------------------------------------------+
//| Funções de Teste                                                 |
//+------------------------------------------------------------------+
bool TestCoreBrainManager()
{
   CoreBrainManager brain;
   return brain.Init();
}

bool TestTradeExecutor()
{
   TradeExecutor executor;
   return executor.Init();
}

bool TestPositionManager()
{
   PositionManager manager;
   return manager.Init();
}

bool TestDefenseOrchestrator()
{
   DefenseOrchestrator defense;
   return defense.Init();
}

bool TestExecutionLoopController()
{
   ExecutionLoopController controller;
   return controller.Init();
}

bool TestSkyIntelBridge()
{
   SkyIntelBridge bridge;
   return bridge.Init();
}

bool TestAuditManager()
{
   AuditManager audit;
   return audit.Init();
} 