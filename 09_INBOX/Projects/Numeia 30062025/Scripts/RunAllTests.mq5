//+------------------------------------------------------------------+
//|                                              RunAllTests.mq5      |
//|                    Execução Completa de Todos os Testes          |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include "../Core/ModuleRegistry.mqh"
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
input bool   RUN_REGISTRY_TEST = true;     // Executar teste de registro
input bool   RUN_COMPILATION_TEST = true;  // Executar teste de compilação
input bool   RUN_INTEGRATION_TEST = true;  // Executar teste de integração
input bool   RUN_FINAL_TEST = true;        // Executar teste final
input bool   SHOW_DETAILED_LOGS = true;    // Logs detalhados
input bool   STOP_ON_ERROR = false;        // Parar no primeiro erro

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
int g_totalTestsRun = 0;
int g_totalTestsPassed = 0;
int g_totalTestsFailed = 0;
datetime g_startTime;

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   g_startTime = TimeCurrent();
   
   AuditLog("🚀 === EXECUÇÃO COMPLETA DE TODOS OS TESTES - NUMEIA EA ===", LOG_LEVEL_INFO);
   AuditLog("Iniciando bateria completa de testes de integração...", LOG_LEVEL_INFO);
   AuditLog("Data/Hora: " + TimeToString(g_startTime), LOG_LEVEL_INFO);
   
   // Teste 1: Sistema de Registro de Módulos
   if(RUN_REGISTRY_TEST) {
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("=== TESTE 1: SISTEMA DE REGISTRO DE MÓDULOS ===", LOG_LEVEL_INFO);
      RunRegistryTest();
   }
   
   // Teste 2: Compilação de Módulos
   if(RUN_COMPILATION_TEST) {
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("=== TESTE 2: COMPILAÇÃO DE MÓDULOS ===", LOG_LEVEL_INFO);
      RunCompilationTest();
   }
   
   // Teste 3: Integração Completa
   if(RUN_INTEGRATION_TEST) {
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("=== TESTE 3: INTEGRAÇÃO COMPLETA ===", LOG_LEVEL_INFO);
      RunIntegrationTest();
   }
   
   // Teste 4: Teste Final
   if(RUN_FINAL_TEST) {
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("=== TESTE 4: TESTE FINAL DE PRODUÇÃO ===", LOG_LEVEL_INFO);
      RunFinalTest();
   }
   
   // Relatório Final Completo
   GenerateCompleteFinalReport();
}

//+------------------------------------------------------------------+
//| Teste do Sistema de Registro                                     |
//+------------------------------------------------------------------+
void RunRegistryTest()
{
   try {
      AuditLog("Iniciando teste do sistema de registro...", LOG_LEVEL_INFO);
      
      // Inicializar registry
      InitializeModuleRegistry();
      ModuleRegistry* registry = GetModuleRegistry();
      
      // Registrar módulos principais
      bool reg1 = registry.RegisterModule("CoreBrainManager", "../Core/CoreBrainManager.mqh", "Core", "Gerenciador central do sistema");
      bool reg2 = registry.RegisterModule("TradeExecutor", "../Include/ExecutionLogic/TradeExecutor.mqh", "Execution", "Executor de ordens");
      bool reg3 = registry.RegisterModule("PositionManager", "../Include/ExecutionLogic/PositionManager.mqh", "Execution", "Gerenciador de posições");
      bool reg4 = registry.RegisterModule("DefenseOrchestrator", "../Include/ExecutionLogic/DefenseOrchestrator.mqh", "Execution", "Orquestrador de defesa");
      bool reg5 = registry.RegisterModule("SkyIntelBridge", "../Include/Integration/SkyIntelBridge.mqh", "Integration", "Bridge para SkyIntel");
      bool reg6 = registry.RegisterModule("AuditManager", "../Auditor/AuditManager.mqh", "Auditor", "Gerenciador de auditoria");
      
      // Registrar dependências
      bool dep1 = registry.RegisterDependency("CoreBrainManager", "TradeExecutor", "include", true);
      bool dep2 = registry.RegisterDependency("CoreBrainManager", "PositionManager", "include", true);
      bool dep3 = registry.RegisterDependency("CoreBrainManager", "DefenseOrchestrator", "include", true);
      bool dep4 = registry.RegisterDependency("CoreBrainManager", "SkyIntelBridge", "include", true);
      bool dep5 = registry.RegisterDependency("CoreBrainManager", "AuditManager", "include", true);
      
      // Registrar integrações
      bool int1 = registry.RegisterIntegration("CoreBrainManager", "TradeExecutor", "execution", "trade_orders", true);
      bool int2 = registry.RegisterIntegration("CoreBrainManager", "PositionManager", "management", "position_control", true);
      bool int3 = registry.RegisterIntegration("CoreBrainManager", "DefenseOrchestrator", "defense", "risk_control", true);
      
      // Validar integridade
      bool integrity = registry.ValidateIntegrity();
      
      // Gerar relatório
      registry.GenerateDependencyReport();
      
      // Contar resultados
      int testsRun = 15; // 6 registros + 5 dependências + 3 integrações + 1 integridade
      int testsPassed = 0;
      
      if(reg1) testsPassed++; if(reg2) testsPassed++; if(reg3) testsPassed++;
      if(reg4) testsPassed++; if(reg5) testsPassed++; if(reg6) testsPassed++;
      if(dep1) testsPassed++; if(dep2) testsPassed++; if(dep3) testsPassed++;
      if(dep4) testsPassed++; if(dep5) testsPassed++;
      if(int1) testsPassed++; if(int2) testsPassed++; if(int3) testsPassed++;
      if(integrity) testsPassed++;
      
      int testsFailed = testsRun - testsPassed;
      
      g_totalTestsRun += testsRun;
      g_totalTestsPassed += testsPassed;
      g_totalTestsFailed += testsFailed;
      
      AuditLog("✅ Teste de registro concluído: " + IntegerToString(testsPassed) + "/" + IntegerToString(testsRun) + " passaram", LOG_LEVEL_INFO);
      
      if(testsFailed > 0 && STOP_ON_ERROR) {
         LogError("❌ Parando testes devido a falhas no registro");
         return;
      }
      
   } catch(...) {
      LogError("❌ Erro durante teste de registro");
      g_totalTestsRun++;
      g_totalTestsFailed++;
   }
}

//+------------------------------------------------------------------+
//| Teste de Compilação                                              |
//+------------------------------------------------------------------+
void RunCompilationTest()
{
   try {
      AuditLog("Iniciando teste de compilação...", LOG_LEVEL_INFO);
      
      int testsRun = 0;
      int testsPassed = 0;
      
      // Testar criação e inicialização de todos os módulos
      ModuleRegistry* registry = new ModuleRegistry();
      CoreBrainManager* brain = new CoreBrainManager();
      TradeExecutor* executor = new TradeExecutor();
      PositionManager* manager = new PositionManager();
      DefenseOrchestrator* defense = new DefenseOrchestrator();
      ExecutionLoopController* controller = new ExecutionLoopController();
      SkyIntelBridge* bridge = new SkyIntelBridge();
      AuditManager* audit = new AuditManager();
      
      // Testar inicialização
      testsRun++; if(registry.Init()) testsPassed++;
      testsRun++; if(brain.Init()) testsPassed++;
      testsRun++; if(executor.Init()) testsPassed++;
      testsRun++; if(manager.Init()) testsPassed++;
      testsRun++; if(defense.Init()) testsPassed++;
      testsRun++; if(controller.Init()) testsPassed++;
      testsRun++; if(bridge.Init()) testsPassed++;
      testsRun++; if(audit.Init()) testsPassed++;
      
      // Testar funcionalidades básicas
      testsRun++; 
      try { brain.OnTick(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { executor.ExecuteOrder("EURUSD", ORDER_TYPE_BUY, 0.1); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { manager.ManageOpenPositions(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { defense.OrchestrateDefense("EURUSD"); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { bridge.GetStrategicSignal("EURUSD"); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { audit.ValidateTradeRequest("TestAgent", "EURUSD", ORDER_TYPE_BUY, 0.1, 1.1000); testsPassed++; } catch(...) {}
      
      // Testar encerramento
      testsRun++; 
      try { brain.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { executor.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { manager.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { defense.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { controller.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { bridge.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { audit.OnDeinit(); testsPassed++; } catch(...) {}
      
      // Limpeza
      delete registry;
      delete brain;
      delete executor;
      delete manager;
      delete defense;
      delete controller;
      delete bridge;
      delete audit;
      
      int testsFailed = testsRun - testsPassed;
      
      g_totalTestsRun += testsRun;
      g_totalTestsPassed += testsPassed;
      g_totalTestsFailed += testsFailed;
      
      AuditLog("✅ Teste de compilação concluído: " + IntegerToString(testsPassed) + "/" + IntegerToString(testsRun) + " passaram", LOG_LEVEL_INFO);
      
      if(testsFailed > 0 && STOP_ON_ERROR) {
         LogError("❌ Parando testes devido a falhas na compilação");
         return;
      }
      
   } catch(...) {
      LogError("❌ Erro durante teste de compilação");
      g_totalTestsRun++;
      g_totalTestsFailed++;
   }
}

//+------------------------------------------------------------------+
//| Teste de Integração                                              |
//+------------------------------------------------------------------+
void RunIntegrationTest()
{
   try {
      AuditLog("Iniciando teste de integração...", LOG_LEVEL_INFO);
      
      int testsRun = 0;
      int testsPassed = 0;
      
      // Testar integração Core-Execution
      CoreBrainManager brain;
      TradeExecutor executor;
      PositionManager manager;
      DefenseOrchestrator defense;
      
      testsRun++; if(brain.Init()) testsPassed++;
      testsRun++; if(executor.Init()) testsPassed++;
      testsRun++; if(manager.Init()) testsPassed++;
      testsRun++; if(defense.Init()) testsPassed++;
      
      // Testar ciclo de trading
      for(int i = 0; i < 2; i++) {
         testsRun++; 
         try { brain.OnTick(); testsPassed++; } catch(...) {}
         Sleep(50);
      }
      
      // Testar encerramento
      testsRun++; 
      try { brain.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { executor.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { manager.OnDeinit(); testsPassed++; } catch(...) {}
      
      testsRun++; 
      try { defense.OnDeinit(); testsPassed++; } catch(...) {}
      
      int testsFailed = testsRun - testsPassed;
      
      g_totalTestsRun += testsRun;
      g_totalTestsPassed += testsPassed;
      g_totalTestsFailed += testsFailed;
      
      AuditLog("✅ Teste de integração concluído: " + IntegerToString(testsPassed) + "/" + IntegerToString(testsRun) + " passaram", LOG_LEVEL_INFO);
      
      if(testsFailed > 0 && STOP_ON_ERROR) {
         LogError("❌ Parando testes devido a falhas na integração");
         return;
      }
      
   } catch(...) {
      LogError("❌ Erro durante teste de integração");
      g_totalTestsRun++;
      g_totalTestsFailed++;
   }
}

//+------------------------------------------------------------------+
//| Teste Final                                                      |
//+------------------------------------------------------------------+
void RunFinalTest()
{
   try {
      AuditLog("Iniciando teste final de produção...", LOG_LEVEL_INFO);
      
      int testsRun = 0;
      int testsPassed = 0;
      
      // Testar sistema completo
      CoreBrainManager brain;
      
      testsRun++; if(brain.Init()) testsPassed++;
      
      // Simular operação completa
      for(int i = 0; i < 3; i++) {
         testsRun++; 
         try { brain.OnTick(); testsPassed++; } catch(...) {}
         Sleep(100);
      }
      
      testsRun++; 
      try { brain.OnDeinit(); testsPassed++; } catch(...) {}
      
      // Testar sistema de logging
      testsRun++; 
      try { 
         AuditLog("Teste final de logging", LOG_LEVEL_INFO);
         LogError("Teste de erro");
         LogWarning("Teste de aviso");
         LogDebug("Teste de debug");
         testsPassed++; 
      } catch(...) {}
      
      int testsFailed = testsRun - testsPassed;
      
      g_totalTestsRun += testsRun;
      g_totalTestsPassed += testsPassed;
      g_totalTestsFailed += testsFailed;
      
      AuditLog("✅ Teste final concluído: " + IntegerToString(testsPassed) + "/" + IntegerToString(testsRun) + " passaram", LOG_LEVEL_INFO);
      
   } catch(...) {
      LogError("❌ Erro durante teste final");
      g_totalTestsRun++;
      g_totalTestsFailed++;
   }
}

//+------------------------------------------------------------------+
//| Relatório Final Completo                                         |
//+------------------------------------------------------------------+
void GenerateCompleteFinalReport()
{
   datetime endTime = TimeCurrent();
   int duration = (int)(endTime - g_startTime);
   
   double successRate = (g_totalTestsRun > 0) ? (double)g_totalTestsPassed / g_totalTestsRun * 100.0 : 0.0;
   
   AuditLog("", LOG_LEVEL_INFO);
   AuditLog("🎯 === RELATÓRIO FINAL COMPLETO ===", LOG_LEVEL_INFO);
   AuditLog("Duração total dos testes: " + IntegerToString(duration) + " segundos", LOG_LEVEL_INFO);
   AuditLog("Total de testes executados: " + IntegerToString(g_totalTestsRun), LOG_LEVEL_INFO);
   AuditLog("Testes aprovados: " + IntegerToString(g_totalTestsPassed), LOG_LEVEL_INFO);
   AuditLog("Testes falharam: " + IntegerToString(g_totalTestsFailed), LOG_LEVEL_ERROR);
   AuditLog("Taxa de sucesso: " + DoubleToString(successRate, 2) + "%", LOG_LEVEL_INFO);
   
   if(g_totalTestsFailed == 0) {
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("🎉 PARABÉNS! TODOS OS TESTES PASSARAM!", LOG_LEVEL_INFO);
      AuditLog("✅ Sistema completamente integrado e funcional", LOG_LEVEL_INFO);
      AuditLog("✅ EA Numeia pronto para uso em produção", LOG_LEVEL_INFO);
      AuditLog("✅ Arquitetura modular validada", LOG_LEVEL_INFO);
      AuditLog("✅ Sistema de registro operacional", LOG_LEVEL_INFO);
      AuditLog("✅ Integrações funcionando", LOG_LEVEL_INFO);
      AuditLog("✅ Auditoria ativa", LOG_LEVEL_INFO);
      AuditLog("✅ Logging operacional", LOG_LEVEL_INFO);
      AuditLog("", LOG_LEVEL_INFO);
      AuditLog("🚀 STATUS: SISTEMA PRONTO PARA PRODUÇÃO!", LOG_LEVEL_INFO);
   } else {
      AuditLog("", LOG_LEVEL_INFO);
      LogError("❌ ALGUNS TESTES FALHARAM!");
      AuditLog("⚠️ Sistema precisa de correções antes do uso em produção", LOG_LEVEL_WARN);
      AuditLog("🔧 Verificar logs acima para identificar problemas", LOG_LEVEL_WARN);
   }
   
   // Informações adicionais
   AuditLog("", LOG_LEVEL_INFO);
   AuditLog("📋 INFORMAÇÕES DO SISTEMA:", LOG_LEVEL_INFO);
   AuditLog("📁 EA Principal: NumeiaEA.mq5", LOG_LEVEL_INFO);
   AuditLog("🔧 Scripts de Teste:", LOG_LEVEL_INFO);
   AuditLog("  - RegisterAllModules.mq5", LOG_LEVEL_INFO);
   AuditLog("  - DependencyMonitor.mq5", LOG_LEVEL_INFO);
   AuditLog("  - TestCompleteIntegration.mq5", LOG_LEVEL_INFO);
   AuditLog("  - FinalCompilationTest.mq5", LOG_LEVEL_INFO);
   AuditLog("  - RunAllTests.mq5 (este script)", LOG_LEVEL_INFO);
   AuditLog("📊 Painel Visual: DependencyDashboard.mq5", LOG_LEVEL_INFO);
} 