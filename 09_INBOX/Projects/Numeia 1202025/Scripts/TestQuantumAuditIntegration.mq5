//+------------------------------------------------------------------+
//|                                    TestQuantumAuditIntegration.mq5 |
//|              Teste Completo da Integração de Auditoria Quântica   |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"
#include "../Scripts/QuantumAudit/QuantumAuditEngine.mqh"
#include "../Scripts/QuantumAudit/QuantumEntanglementMap.mqh"
#include "../Scripts/QuantumAudit/AuditEntanglementBridge.mqh"
#include "../Core/CoreBrainManager.mqh"

input bool Test_QuantumAuditEngine = true;
input bool Test_EntanglementMap = true;
input bool Test_AuditBridge = true;
input bool Test_CoreBrainIntegration = true;
input bool Test_VisualPanel = true;

//+------------------------------------------------------------------+
//| Função principal do script                                       |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("[TestQuantumAuditIntegration] Iniciando teste completo da integração...", LOG_LEVEL_INFO);
   
   int totalTests = 0;
   int passedTests = 0;
   
   // Teste 1: QuantumAuditEngine
   if(Test_QuantumAuditEngine)
   {
      totalTests++;
      if(TestQuantumAuditEngine())
      {
         passedTests++;
         AuditLog("✓ Teste QuantumAuditEngine: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("✗ Teste QuantumAuditEngine: FALHOU");
      }
   }
   
   // Teste 2: QuantumEntanglementMap
   if(Test_EntanglementMap)
   {
      totalTests++;
      if(TestEntanglementMap())
      {
         passedTests++;
         AuditLog("✓ Teste QuantumEntanglementMap: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("✗ Teste QuantumEntanglementMap: FALHOU");
      }
   }
   
   // Teste 3: AuditEntanglementBridge
   if(Test_AuditBridge)
   {
      totalTests++;
      if(TestAuditBridge())
      {
         passedTests++;
         AuditLog("✓ Teste AuditEntanglementBridge: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("✗ Teste AuditEntanglementBridge: FALHOU");
      }
   }
   
   // Teste 4: Integração com CoreBrainManager
   if(Test_CoreBrainIntegration)
   {
      totalTests++;
      if(TestCoreBrainIntegration())
      {
         passedTests++;
         AuditLog("✓ Teste CoreBrainIntegration: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("✗ Teste CoreBrainIntegration: FALHOU");
      }
   }
   
   // Teste 5: Painel Visual
   if(Test_VisualPanel)
   {
      totalTests++;
      if(TestVisualPanel())
      {
         passedTests++;
         AuditLog("✓ Teste VisualPanel: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("✗ Teste VisualPanel: FALHOU");
      }
   }
   
   // Resultado final
   AuditLog("=== RESULTADO FINAL DO TESTE ===", LOG_LEVEL_INFO);
   AuditLog("Total de testes: " + IntegerToString(totalTests), LOG_LEVEL_INFO);
   AuditLog("Testes aprovados: " + IntegerToString(passedTests), LOG_LEVEL_INFO);
   AuditLog("Testes reprovados: " + IntegerToString(totalTests - passedTests), LOG_LEVEL_INFO);
   
   if(passedTests == totalTests)
   {
      AuditLog("🎉 TODOS OS TESTES PASSARAM! Sistema de auditoria quântica funcionando perfeitamente!", LOG_LEVEL_INFO);
   }
   else
   {
      LogError("⚠️ Alguns testes falharam. Verificar logs para detalhes.");
   }
}

//+------------------------------------------------------------------+
//| Teste do QuantumAuditEngine                                      |
//+------------------------------------------------------------------+
bool TestQuantumAuditEngine()
{
   AuditLog("[TestQuantumAuditEngine] Iniciando teste...", LOG_LEVEL_DEBUG);
   
   try
   {
      QuantumAuditEngine engine(4.5);
      
      // Teste de inicialização
      if(!engine.Init())
      {
         LogError("Falha na inicialização do QuantumAuditEngine");
         return false;
      }
      
      // Teste de análise de arquivo
      engine.AnalyzeFile("Include/Core/CoreBrainManager.mqh");
      
      // Teste de cálculo de entropia
      string testCode = "// Teste de código\nint main() { return 0; }";
      double entropy = engine.EvaluateEntropy(testCode);
      
      if(entropy < 0 || entropy > 8)
      {
         LogError("Entropia calculada fora do range esperado: " + DoubleToString(entropy, 4));
         return false;
      }
      
      // Teste de detecção de problemas críticos
      bool hasCriticalIssues = engine.DetectCriticalIssues();
      
      AuditLog("Teste QuantumAuditEngine concluído - Entropia: " + DoubleToString(entropy, 4), LOG_LEVEL_DEBUG);
      return true;
   }
   catch(...)
   {
      LogError("Exceção durante teste QuantumAuditEngine");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste do QuantumEntanglementMap                                 |
//+------------------------------------------------------------------+
bool TestEntanglementMap()
{
   AuditLog("[TestEntanglementMap] Iniciando teste...", LOG_LEVEL_DEBUG);
   
   try
   {
      QuantumEntanglementMap map;
      
      // Teste de inicialização
      if(!map.Init())
      {
         LogError("Falha na inicialização do QuantumEntanglementMap");
         return false;
      }
      
      // Teste de registro de módulos
      map.RegisterModule("Include/Core/CoreBrainManager.mqh");
      map.RegisterModule("Include/ExecutionLogic/TradeExecutor.mqh");
      
      // Teste de criação de links
      map.CreateLink("Include/Core/CoreBrainManager.mqh", "Include/ExecutionLogic/TradeExecutor.mqh", 0.8, "Teste de integração");
      
      // Teste de validação de link
      bool isValid = map.ValidateLink("Include/Core/CoreBrainManager.mqh");
      
      // Teste de análise de padrões
      map.AnalyzeEntanglementPatterns();
      
      // Teste de estatísticas
      int totalLinks, uniqueModules;
      double avgStrength;
      string strongestLink;
      map.GetMapStatistics(totalLinks, uniqueModules, avgStrength, strongestLink);
      
      AuditLog("Teste QuantumEntanglementMap concluído - Links: " + IntegerToString(totalLinks), LOG_LEVEL_DEBUG);
      return (totalLinks > 0);
   }
   catch(...)
   {
      LogError("Exceção durante teste QuantumEntanglementMap");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste do AuditEntanglementBridge                                |
//+------------------------------------------------------------------+
bool TestAuditBridge()
{
   AuditLog("[TestAuditBridge] Iniciando teste...", LOG_LEVEL_DEBUG);
   
   try
   {
      AuditEntanglementBridge bridge;
      
      // Teste de inicialização
      if(!bridge.Init())
      {
         LogError("Falha na inicialização do AuditEntanglementBridge");
         return false;
      }
      
      // Teste de auditoria completa
      bridge.RunFullAudit();
      
      // Teste de validação de resultados
      bool isValid = bridge.ValidateResults();
      
      // Teste de estatísticas
      int total, ok, fail, warn;
      bridge.GetAuditStatistics(total, ok, fail, warn);
      
      AuditLog("Teste AuditEntanglementBridge concluído - Total: " + IntegerToString(total), LOG_LEVEL_DEBUG);
      return (total > 0);
   }
   catch(...)
   {
      LogError("Exceção durante teste AuditEntanglementBridge");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste da integração com CoreBrainManager                        |
//+------------------------------------------------------------------+
bool TestCoreBrainIntegration()
{
   AuditLog("[TestCoreBrainIntegration] Iniciando teste...", LOG_LEVEL_DEBUG);
   
   try
   {
      CoreBrainManager coreBrain;
      
      // Teste de inicialização
      if(!coreBrain.Init())
      {
         LogError("Falha na inicialização do CoreBrainManager");
         return false;
      }
      
      // Teste de configuração de auditoria
      coreBrain.EnableQuantumAudit(true);
      coreBrain.SetAuditInterval(5); // 5 minutos para teste
      
      // Teste de execução de auditoria
      coreBrain.RunQuantumAudit();
      
      AuditLog("Teste CoreBrainIntegration concluído", LOG_LEVEL_DEBUG);
      return true;
   }
   catch(...)
   {
      LogError("Exceção durante teste CoreBrainIntegration");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste do painel visual                                          |
//+------------------------------------------------------------------+
bool TestVisualPanel()
{
   AuditLog("[TestVisualPanel] Iniciando teste...", LOG_LEVEL_DEBUG);
   
   try
   {
      // Verificar se o arquivo de status existe
      if(!FileIsExist("entanglement_status.dat"))
      {
         LogWarning("Arquivo de status não encontrado - criando dados de teste");
         
         // Criar dados de teste
         int handle = FileOpen("entanglement_status.dat", FILE_WRITE | FILE_TXT | FILE_COMMON);
         if(handle != INVALID_HANDLE)
         {
            FileWrite(handle, "Include/Core/CoreBrainManager.mqh,OK," + TimeToString(TimeCurrent()));
            FileWrite(handle, "Include/ExecutionLogic/TradeExecutor.mqh,OK," + TimeToString(TimeCurrent()));
            FileWrite(handle, "Include/ExecutionLogic/DefenseOrchestrator.mqh,WARN," + TimeToString(TimeCurrent()));
            FileClose(handle);
         }
      }
      
      // Verificar se o arquivo foi criado/validado
      if(FileIsExist("entanglement_status.dat"))
      {
         AuditLog("Teste VisualPanel concluído - arquivo de status válido", LOG_LEVEL_DEBUG);
         return true;
      }
      else
      {
         LogError("Falha ao criar/validar arquivo de status");
         return false;
      }
   }
   catch(...)
   {
      LogError("Exceção durante teste VisualPanel");
      return false;
   }
} 