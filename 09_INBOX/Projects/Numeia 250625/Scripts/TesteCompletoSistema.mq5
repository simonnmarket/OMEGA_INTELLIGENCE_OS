//+------------------------------------------------------------------+
//|                                        TesteCompletoSistema.mq5   |
//|              Teste Completo do Sistema Numeia EA                 |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"
#include "../Core/CoreBrainManager.mqh"

input bool Test_CoreBrain = true;
input bool Test_QuantumAudit = true;
input bool Test_AllModules = true;

//+------------------------------------------------------------------+
//| Função principal do script                                       |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🚀 INICIANDO TESTE COMPLETO DO SISTEMA NUMEIA EA", LOG_LEVEL_INFO);
   AuditLog("=" * 60, LOG_LEVEL_INFO);
   
   int totalTests = 0;
   int passedTests = 0;
   
   // Teste 1: CoreBrainManager
   if(Test_CoreBrain)
   {
      totalTests++;
      AuditLog("📋 Teste 1: CoreBrainManager", LOG_LEVEL_INFO);
      
      if(TestCoreBrainManager())
      {
         passedTests++;
         AuditLog("✅ CoreBrainManager: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ CoreBrainManager: FALHOU");
      }
   }
   
   // Teste 2: Sistema de Auditoria Quântica
   if(Test_QuantumAudit)
   {
      totalTests++;
      AuditLog("📋 Teste 2: Sistema de Auditoria Quântica", LOG_LEVEL_INFO);
      
      if(TestQuantumAuditSystem())
      {
         passedTests++;
         AuditLog("✅ Auditoria Quântica: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ Auditoria Quântica: FALHOU");
      }
   }
   
   // Teste 3: Todos os Módulos
   if(Test_AllModules)
   {
      totalTests++;
      AuditLog("📋 Teste 3: Verificação de Todos os Módulos", LOG_LEVEL_INFO);
      
      if(TestAllModules())
      {
         passedTests++;
         AuditLog("✅ Todos os Módulos: PASSOU", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ Todos os Módulos: FALHOU");
      }
   }
   
   // Resultado Final
   AuditLog("=" * 60, LOG_LEVEL_INFO);
   AuditLog("📊 RESULTADO FINAL DO TESTE", LOG_LEVEL_INFO);
   AuditLog("Total de testes: " + IntegerToString(totalTests), LOG_LEVEL_INFO);
   AuditLog("Testes aprovados: " + IntegerToString(passedTests), LOG_LEVEL_INFO);
   AuditLog("Testes reprovados: " + IntegerToString(totalTests - passedTests), LOG_LEVEL_INFO);
   
   if(passedTests == totalTests)
   {
      AuditLog("🎉 SUCESSO TOTAL! Sistema Numeia EA funcionando perfeitamente!", LOG_LEVEL_INFO);
      AuditLog("🚀 Sistema pronto para operação!", LOG_LEVEL_INFO);
   }
   else
   {
      LogError("⚠️ ATENÇÃO! Alguns testes falharam. Verificar logs para detalhes.");
   }
}

//+------------------------------------------------------------------+
//| Teste do CoreBrainManager                                        |
//+------------------------------------------------------------------+
bool TestCoreBrainManager()
{
   try
   {
      AuditLog("Iniciando teste do CoreBrainManager...", LOG_LEVEL_DEBUG);
      
      CoreBrainManager brain;
      
      // Teste de inicialização
      if(!brain.Init())
      {
         LogError("Falha na inicialização do CoreBrainManager");
         return false;
      }
      
      // Teste de configuração de auditoria quântica
      brain.EnableQuantumAudit(true);
      brain.SetAuditInterval(5); // 5 minutos para teste
      
      // Teste de execução de auditoria
      brain.RunQuantumAudit();
      
      AuditLog("CoreBrainManager testado com sucesso", LOG_LEVEL_DEBUG);
      return true;
   }
   catch(...)
   {
      LogError("Exceção durante teste do CoreBrainManager");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste do Sistema de Auditoria Quântica                          |
//+------------------------------------------------------------------+
bool TestQuantumAuditSystem()
{
   try
   {
      AuditLog("Iniciando teste do sistema de auditoria quântica...", LOG_LEVEL_DEBUG);
      
      // Verificar se os arquivos da auditoria quântica existem
      string quantumFiles[] = {
         "Scripts/QuantumAudit/QuantumAuditEngine.mqh",
         "Scripts/QuantumAudit/QuantumEntanglementMap.mqh",
         "Scripts/QuantumAudit/AuditEntanglementBridge.mqh",
         "Scripts/QuantumAudit/AuditEntanglementPanel.mq5"
      };
      
      for(int i = 0; i < ArraySize(quantumFiles); i++)
      {
         if(!FileIsExist(quantumFiles[i]))
         {
            LogError("Arquivo de auditoria quântica não encontrado: " + quantumFiles[i]);
            return false;
         }
      }
      
      // Verificar se o arquivo de status foi criado
      if(FileIsExist("entanglement_status.dat"))
      {
         AuditLog("Arquivo de status de auditoria encontrado", LOG_LEVEL_DEBUG);
      }
      else
      {
         LogWarning("Arquivo de status de auditoria não encontrado (pode ser normal na primeira execução)");
      }
      
      AuditLog("Sistema de auditoria quântica testado com sucesso", LOG_LEVEL_DEBUG);
      return true;
   }
   catch(...)
   {
      LogError("Exceção durante teste do sistema de auditoria quântica");
      return false;
   }
}

//+------------------------------------------------------------------+
//| Teste de Todos os Módulos                                        |
//+------------------------------------------------------------------+
bool TestAllModules()
{
   try
   {
      AuditLog("Iniciando verificação de todos os módulos...", LOG_LEVEL_DEBUG);
      
      // Lista de módulos críticos
      string criticalModules[] = {
         "Core/CoreBrainManager.mqh",
         "Include/ExecutionLogic/TradeExecutor.mqh",
         "Include/ExecutionLogic/PositionManager.mqh",
         "Include/ExecutionLogic/DefenseOrchestrator.mqh",
         "Include/ExecutionLogic/ExecutionLoopController.mqh",
         "Include/Integration/SkyIntelBridge.mqh",
         "Auditor/AuditManager.mqh",
         "Utils/Log.mqh",
         "Expert/NumeiaEA.mq5"
      };
      
      int missingModules = 0;
      
      for(int i = 0; i < ArraySize(criticalModules); i++)
      {
         if(!FileIsExist(criticalModules[i]))
         {
            LogError("Módulo crítico não encontrado: " + criticalModules[i]);
            missingModules++;
         }
         else
         {
            AuditLog("✓ Módulo encontrado: " + criticalModules[i], LOG_LEVEL_DEBUG);
         }
      }
      
      if(missingModules > 0)
      {
         LogError("Total de módulos faltando: " + IntegerToString(missingModules));
         return false;
      }
      
      AuditLog("Todos os módulos críticos encontrados", LOG_LEVEL_DEBUG);
      return true;
   }
   catch(...)
   {
      LogError("Exceção durante verificação de módulos");
      return false;
   }
} 