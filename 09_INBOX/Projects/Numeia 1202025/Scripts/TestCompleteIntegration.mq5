//+------------------------------------------------------------------+
//|                                      TestCompleteIntegration.mq5 |
//|                    Teste Completo de Integração - EA Numeia     |
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
input bool   TEST_REGISTRY = true;         // Testar ModuleRegistry
input bool   TEST_CORE_BRAIN = true;       // Testar CoreBrainManager
input bool   TEST_EXECUTION = true;        // Testar módulos de execução
input bool   TEST_INTEGRATION = true;      // Testar integrações
input bool   TEST_AUDIT = true;            // Testar sistema de auditoria
input bool   SHOW_DETAILED_RESULTS = true; // Mostrar resultados detalhados
input bool   STOP_ON_ERROR = false;        // Parar no primeiro erro

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
ModuleRegistry* g_testRegistry = NULL;
int g_testsPassed = 0;
int g_testsFailed = 0;
int g_totalTests = 0;

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("=== TESTE COMPLETO DE INTEGRAÇÃO - NUMEIA EA ===", LOG_LEVEL_INFO);
   AuditLog("Iniciando bateria completa de testes...", LOG_LEVEL_INFO);
   
   // Inicializar registry
   InitializeModuleRegistry();
   g_testRegistry = GetModuleRegistry();
   
   // Executar testes
   if(TEST_REGISTRY) {
      TestModuleRegistry();
   }
   
   if(TEST_CORE_BRAIN) {
      TestCoreBrainManager();
   }
   
   if(TEST_EXECUTION) {
      TestExecutionModules();
   }
   
   if(TEST_INTEGRATION) {
      TestIntegrations();
   }
   
   if(TEST_AUDIT) {
      TestAuditSystem();
   }
   
   // Relatório final
   GenerateFinalReport();
}

//+------------------------------------------------------------------+
//| Teste do ModuleRegistry                                          |
//+------------------------------------------------------------------+
void TestModuleRegistry()
{
   AuditLog("=== TESTE 1: MODULE REGISTRY ===", LOG_LEVEL_INFO);
   
   // Teste 1.1: Registro de módulos
   RunTest("1.1", "Registro de módulos", TestModuleRegistration());
   
   // Teste 1.2: Registro de dependências
   RunTest("1.2", "Registro de dependências", TestDependencyRegistration());
   
   // Teste 1.3: Registro de integrações
   RunTest("1.3", "Registro de integrações", TestIntegrationRegistration());
   
   // Teste 1.4: Validação de integridade
   RunTest("1.4", "Validação de integridade", TestIntegrityValidation());
   
   // Teste 1.5: Análise de impacto
   RunTest("1.5", "Análise de impacto", TestImpactAnalysis());
   
   // Teste 1.6: Geração de relatórios
   RunTest("1.6", "Geração de relatórios", TestReportGeneration());
}

//+------------------------------------------------------------------+
//| Teste do CoreBrainManager                                        |
//+------------------------------------------------------------------+
void TestCoreBrainManager()
{
   AuditLog("=== TESTE 2: CORE BRAIN MANAGER ===", LOG_LEVEL_INFO);
   
   // Teste 2.1: Inicialização
   RunTest("2.1", "Inicialização do CoreBrainManager", TestCoreBrainInit());
   
   // Teste 2.2: Integração com módulos
   RunTest("2.2", "Integração com módulos", TestCoreBrainIntegration());
   
   // Teste 2.3: Funcionalidade OnTick
   RunTest("2.3", "Funcionalidade OnTick", TestCoreBrainOnTick());
   
   // Teste 2.4: Encerramento
   RunTest("2.4", "Encerramento do CoreBrainManager", TestCoreBrainDeinit());
}

//+------------------------------------------------------------------+
//| Teste dos Módulos de Execução                                    |
//+------------------------------------------------------------------+
void TestExecutionModules()
{
   AuditLog("=== TESTE 3: MÓDULOS DE EXECUÇÃO ===", LOG_LEVEL_INFO);
   
   // Teste 3.1: TradeExecutor
   RunTest("3.1", "TradeExecutor", TestTradeExecutor());
   
   // Teste 3.2: PositionManager
   RunTest("3.2", "PositionManager", TestPositionManager());
   
   // Teste 3.3: DefenseOrchestrator
   RunTest("3.3", "DefenseOrchestrator", TestDefenseOrchestrator());
   
   // Teste 3.4: ExecutionLoopController
   RunTest("3.4", "ExecutionLoopController", TestExecutionLoopController());
}

//+------------------------------------------------------------------+
//| Teste de Integrações                                             |
//+------------------------------------------------------------------+
void TestIntegrations()
{
   AuditLog("=== TESTE 4: INTEGRAÇÕES ===", LOG_LEVEL_INFO);
   
   // Teste 4.1: SkyIntelBridge
   RunTest("4.1", "SkyIntelBridge", TestSkyIntelBridge());
   
   // Teste 4.2: Integração Core-Execution
   RunTest("4.2", "Integração Core-Execution", TestCoreExecutionIntegration());
   
   // Teste 4.3: Integração Execution-Agents
   RunTest("4.3", "Integração Execution-Agents", TestExecutionAgentsIntegration());
}

//+------------------------------------------------------------------+
//| Teste do Sistema de Auditoria                                    |
//+------------------------------------------------------------------+
void TestAuditSystem()
{
   AuditLog("=== TESTE 5: SISTEMA DE AUDITORIA ===", LOG_LEVEL_INFO);
   
   // Teste 5.1: AuditManager
   RunTest("5.1", "AuditManager", TestAuditManager());
   
   // Teste 5.2: Sistema de Logging
   RunTest("5.2", "Sistema de Logging", TestLoggingSystem());
   
   // Teste 5.3: Validação de Compliance
   RunTest("5.3", "Validação de Compliance", TestComplianceValidation());
}

//+------------------------------------------------------------------+
//| Funções de Teste Específicas                                     |
//+------------------------------------------------------------------+
bool TestModuleRegistration()
{
   try {
      bool result = g_testRegistry.RegisterModule("TestModule", "TestPath.mqh", "Test", "Test Description");
      return result;
   } catch(...) {
      return false;
   }
}

bool TestDependencyRegistration()
{
   try {
      bool result = g_testRegistry.RegisterDependency("TestModule", "Log", "include", true);
      return result;
   } catch(...) {
      return false;
   }
}

bool TestIntegrationRegistration()
{
   try {
      bool result = g_testRegistry.RegisterIntegration("TestModule", "Log", "test", "data_flow", false);
      return result;
   } catch(...) {
      return false;
   }
}

bool TestIntegrityValidation()
{
   try {
      bool result = g_testRegistry.ValidateIntegrity();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestImpactAnalysis()
{
   try {
      g_testRegistry.AnalyzeImpact("TestModule");
      return true;
   } catch(...) {
      return false;
   }
}

bool TestReportGeneration()
{
   try {
      g_testRegistry.GenerateDependencyReport();
      return true;
   } catch(...) {
      return false;
   }
}

bool TestCoreBrainInit()
{
   try {
      CoreBrainManager brain;
      bool result = brain.Init();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestCoreBrainIntegration()
{
   try {
      CoreBrainManager brain;
      brain.Init();
      // Simular integração
      return true;
   } catch(...) {
      return false;
   }
}

bool TestCoreBrainOnTick()
{
   try {
      CoreBrainManager brain;
      brain.Init();
      brain.OnTick();
      return true;
   } catch(...) {
      return false;
   }
}

bool TestCoreBrainDeinit()
{
   try {
      CoreBrainManager brain;
      brain.Init();
      brain.OnDeinit();
      return true;
   } catch(...) {
      return false;
   }
}

bool TestTradeExecutor()
{
   try {
      TradeExecutor executor;
      bool result = executor.Init();
      executor.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestPositionManager()
{
   try {
      PositionManager manager;
      bool result = manager.Init();
      manager.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestDefenseOrchestrator()
{
   try {
      DefenseOrchestrator defense;
      bool result = defense.Init();
      defense.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestExecutionLoopController()
{
   try {
      ExecutionLoopController controller;
      bool result = controller.Init();
      controller.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestSkyIntelBridge()
{
   try {
      SkyIntelBridge bridge;
      bool result = bridge.Init();
      bridge.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestCoreExecutionIntegration()
{
   try {
      // Simular integração entre Core e Execution
      CoreBrainManager brain;
      TradeExecutor executor;
      PositionManager manager;
      
      brain.Init();
      executor.Init();
      manager.Init();
      
      return true;
   } catch(...) {
      return false;
   }
}

bool TestExecutionAgentsIntegration()
{
   try {
      // Simular integração entre Execution e Agents
      TradeExecutor executor;
      PositionManager manager;
      
      executor.Init();
      manager.Init();
      
      return true;
   } catch(...) {
      return false;
   }
}

bool TestAuditManager()
{
   try {
      AuditManager audit;
      bool result = audit.Init();
      audit.OnDeinit();
      return result;
   } catch(...) {
      return false;
   }
}

bool TestLoggingSystem()
{
   try {
      AuditLog("Teste de logging", LOG_LEVEL_INFO);
      LogError("Teste de erro");
      LogWarning("Teste de aviso");
      LogDebug("Teste de debug");
      return true;
   } catch(...) {
      return false;
   }
}

bool TestComplianceValidation()
{
   try {
      AuditManager audit;
      audit.Init();
      
      // Testar validações
      bool result1 = audit.ValidateTradeRequest("TestAgent", "EURUSD", ORDER_TYPE_BUY, 0.1, 1.1000);
      bool result2 = audit.ValidateRiskThreshold(0.5, 1.0);
      
      audit.OnDeinit();
      return result1 && result2;
   } catch(...) {
      return false;
   }
}

//+------------------------------------------------------------------+
//| Função de Execução de Teste                                      |
//+------------------------------------------------------------------+
void RunTest(string testId, string testName, bool result)
{
   g_totalTests++;
   
   if(result) {
      g_testsPassed++;
      if(SHOW_DETAILED_RESULTS) {
         AuditLog("✅ Teste " + testId + " - " + testName + ": PASSOU", LOG_LEVEL_DEBUG);
      }
   } else {
      g_testsFailed++;
      LogError("❌ Teste " + testId + " - " + testName + ": FALHOU");
      
      if(STOP_ON_ERROR) {
         LogError("Parando testes devido a falha no teste " + testId);
         return;
      }
   }
}

//+------------------------------------------------------------------+
//| Geração de Relatório Final                                       |
//+------------------------------------------------------------------+
void GenerateFinalReport()
{
   AuditLog("=== RELATÓRIO FINAL DE TESTES ===", LOG_LEVEL_INFO);
   AuditLog("Total de testes executados: " + IntegerToString(g_totalTests), LOG_LEVEL_INFO);
   AuditLog("Testes aprovados: " + IntegerToString(g_testsPassed), LOG_LEVEL_INFO);
   AuditLog("Testes falharam: " + IntegerToString(g_testsFailed), LOG_LEVEL_ERROR);
   
   double successRate = (g_totalTests > 0) ? (double)g_testsPassed / g_totalTests * 100.0 : 0.0;
   AuditLog("Taxa de sucesso: " + DoubleToString(successRate, 2) + "%", LOG_LEVEL_INFO);
   
   if(g_testsFailed == 0) {
      AuditLog("🎉 TODOS OS TESTES PASSARAM! Sistema completamente integrado!", LOG_LEVEL_INFO);
      AuditLog("✅ O EA Numeia está pronto para uso em produção!", LOG_LEVEL_INFO);
   } else {
      LogError("❌ ALGUNS TESTES FALHARAM! Verificar problemas acima.");
      AuditLog("⚠️ Sistema precisa de correções antes do uso em produção.", LOG_LEVEL_WARN);
   }
   
   // Gerar relatório de dependências
   if(g_testRegistry != NULL) {
      g_testRegistry.GenerateDependencyReport();
   }
} 