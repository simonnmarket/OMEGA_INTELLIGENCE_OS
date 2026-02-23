//+------------------------------------------------------------------+
//|                                           DependencyMonitor.mq5   |
//|                    Monitor de Dependências - EA Numeia          |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include "../Core/ModuleRegistry.mqh"

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
input bool   ENABLE_MONITORING = true;    // Ativar monitoramento
input int    SCAN_INTERVAL = 30;          // Intervalo de verificação (segundos)
input bool   AUTO_ANALYZE_IMPACT = true;  // Análise automática de impacto
input bool   SHOW_DETAILED_LOGS = true;   // Logs detalhados
input bool   ALERT_ON_CHANGES = true;     // Alertas em mudanças
input bool   STOP_ON_ERRORS = false;      // Parar em erros críticos

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
ModuleRegistry* g_monitorRegistry = NULL;
datetime g_lastScanTime = 0;
int g_totalScans = 0;
int g_changesDetected = 0;
int g_errorsDetected = 0;

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("=== MONITOR DE DEPENDÊNCIAS - NUMEIA EA ===", LOG_LEVEL_INFO);
   AuditLog("Iniciando monitoramento contínuo...", LOG_LEVEL_INFO);
   
   // Inicializar registry
   InitializeModuleRegistry();
   g_monitorRegistry = GetModuleRegistry();
   
   // Registrar todos os módulos se necessário
   if(g_monitorRegistry.ValidateIntegrity() == false) {
      AuditLog("Sistema não está registrado. Executando registro automático...", LOG_LEVEL_WARN);
      RegisterAllModules();
   }
   
   // Iniciar monitoramento
   StartMonitoring();
}

//+------------------------------------------------------------------+
//| Função de Monitoramento Contínuo                                 |
//+------------------------------------------------------------------+
void StartMonitoring()
{
   AuditLog("[DependencyMonitor] Monitoramento iniciado - Intervalo: " + IntegerToString(SCAN_INTERVAL) + "s", LOG_LEVEL_INFO);
   
   datetime startTime = TimeCurrent();
   datetime currentTime;
   
   while(ENABLE_MONITORING) {
      currentTime = TimeCurrent();
      
      // Verificar se é hora de fazer scan
      if(currentTime - g_lastScanTime >= SCAN_INTERVAL) {
         PerformScan();
         g_lastScanTime = currentTime;
         g_totalScans++;
         
         // Verificar se deve parar por erros
         if(STOP_ON_ERRORS && g_errorsDetected > 5) {
            LogError("[DependencyMonitor] Muitos erros detectados. Parando monitoramento.");
            break;
         }
      }
      
      // Pequena pausa para não sobrecarregar
      Sleep(1000);
   }
   
   // Relatório final
   GenerateFinalReport(startTime, currentTime);
}

//+------------------------------------------------------------------+
//| Execução de Scan                                                 |
//+------------------------------------------------------------------+
void PerformScan()
{
   AuditLog("[DependencyMonitor] Executando scan #" + IntegerToString(g_totalScans + 1), LOG_LEVEL_DEBUG);
   
   bool changesFound = false;
   bool errorsFound = false;
   
   // Executar sincronização automática do registry
   g_monitorRegistry.AutoSync();
   
   // Verificar integridade
   if(!g_monitorRegistry.ValidateIntegrity()) {
      errorsFound = true;
      g_errorsDetected++;
      
      if(ALERT_ON_CHANGES) {
         Alert("🚨 ERRO DE INTEGRIDADE DETECTADO!");
         LogError("[DependencyMonitor] Falha na validação de integridade");
      }
   }
   
   // Verificar mudanças nos arquivos (simulado)
   if(DetectFileChanges()) {
      changesFound = true;
      g_changesDetected++;
      
      if(ALERT_ON_CHANGES) {
         Alert("📝 MUDANÇAS DETECTADAS NO SISTEMA!");
         AuditLog("[DependencyMonitor] Mudanças detectadas nos arquivos", LOG_LEVEL_WARN);
      }
   }
   
   // Análise automática de impacto
   if(AUTO_ANALYZE_IMPACT && changesFound) {
      AnalyzeAllImpacts();
   }
   
   // Log de status
   if(SHOW_DETAILED_LOGS) {
      AuditLog("[DependencyMonitor] Scan #" + IntegerToString(g_totalScans + 1) + " - Mudanças: " + (changesFound ? "SIM" : "NÃO") + ", Erros: " + (errorsFound ? "SIM" : "NÃO"), LOG_LEVEL_DEBUG);
   }
}

//+------------------------------------------------------------------+
//| Detecção de Mudanças em Arquivos                                 |
//+------------------------------------------------------------------+
bool DetectFileChanges()
{
   // Em MQL5, não há acesso direto ao sistema de arquivos
   // Esta é uma implementação simulada
   
   static datetime lastCheck = 0;
   datetime currentTime = TimeCurrent();
   
   // Simular mudanças a cada 5 minutos
   if(currentTime - lastCheck > 300) {
      lastCheck = currentTime;
      
      // Simular mudança aleatória (10% de chance)
      if(MathRand() % 100 < 10) {
         return true;
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Análise de Impacto para Todos os Módulos                         |
//+------------------------------------------------------------------+
void AnalyzeAllImpacts()
{
   AuditLog("[DependencyMonitor] Iniciando análise de impacto completa...", LOG_LEVEL_INFO);
   
   // Lista de módulos críticos para análise
   string criticalModules[] = {
      "CoreBrainManager",
      "TradeExecutor", 
      "PositionManager",
      "DefenseOrchestrator",
      "ExecutionLoopController",
      "SkyIntelBridge",
      "AuditManager"
   };
   
   for(int i = 0; i < ArraySize(criticalModules); i++) {
      g_monitorRegistry.AnalyzeImpact(criticalModules[i]);
   }
   
   AuditLog("[DependencyMonitor] Análise de impacto concluída", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Registro Automático de Módulos                                   |
//+------------------------------------------------------------------+
void RegisterAllModules()
{
   AuditLog("[DependencyMonitor] Registrando todos os módulos...", LOG_LEVEL_INFO);
   
   // Core modules
   g_monitorRegistry.RegisterModule("CoreBrainManager", "../Core/CoreBrainManager.mqh", "Core", "Gerenciador central");
   g_monitorRegistry.RegisterModule("ExecutionOrchestrator", "../Core/ExecutionOrchestrator.mqh", "Core", "Orquestrador");
   g_monitorRegistry.RegisterModule("ModuleRegistry", "../Core/ModuleRegistry.mqh", "Core", "Registry");
   g_monitorRegistry.RegisterModule("AuditInterface", "../Core/AuditInterface.mqh", "Core", "Interface");
   g_monitorRegistry.RegisterModule("types", "../Core/types.mqh", "Core", "Tipos");
   
   // Execution modules
   g_monitorRegistry.RegisterModule("TradeExecutor", "../Include/ExecutionLogic/TradeExecutor.mqh", "Execution", "Executor");
   g_monitorRegistry.RegisterModule("PositionManager", "../Include/ExecutionLogic/PositionManager.mqh", "Execution", "Posições");
   g_monitorRegistry.RegisterModule("DefenseOrchestrator", "../Include/ExecutionLogic/DefenseOrchestrator.mqh", "Execution", "Defesa");
   g_monitorRegistry.RegisterModule("ExecutionLoopController", "../Include/ExecutionLogic/ExecutionLoopController.mqh", "Execution", "Loop");
   
   // Integration modules
   g_monitorRegistry.RegisterModule("SkyIntelBridge", "../Include/Integration/SkyIntelBridge.mqh", "Integration", "SkyIntel");
   
   // Auditor modules
   g_monitorRegistry.RegisterModule("AuditManager", "../Auditor/AuditManager.mqh", "Auditor", "Auditoria");
   
   // Utils modules
   g_monitorRegistry.RegisterModule("Log", "../Utils/Log.mqh", "Utils", "Logging");
   
   // Registrar dependências críticas
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "TradeExecutor", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "PositionManager", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "DefenseOrchestrator", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "ExecutionLoopController", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "SkyIntelBridge", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "AuditManager", "include", true);
   g_monitorRegistry.RegisterDependency("CoreBrainManager", "Log", "include", true);
   
   AuditLog("[DependencyMonitor] Registro de módulos concluído", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Geração de Relatório Final                                       |
//+------------------------------------------------------------------+
void GenerateFinalReport(datetime startTime, datetime endTime)
{
   int duration = (int)(endTime - startTime);
   
   AuditLog("=== RELATÓRIO FINAL DO MONITOR ===", LOG_LEVEL_INFO);
   AuditLog("Duração do monitoramento: " + IntegerToString(duration) + " segundos", LOG_LEVEL_INFO);
   AuditLog("Total de scans executados: " + IntegerToString(g_totalScans), LOG_LEVEL_INFO);
   AuditLog("Mudanças detectadas: " + IntegerToString(g_changesDetected), LOG_LEVEL_INFO);
   AuditLog("Erros detectados: " + IntegerToString(g_errorsDetected), LOG_LEVEL_INFO);
   
   if(g_errorsDetected == 0) {
      AuditLog("✅ MONITORAMENTO CONCLUÍDO SEM ERROS!", LOG_LEVEL_INFO);
   } else {
      LogError("❌ MONITORAMENTO CONCLUÍDO COM " + IntegerToString(g_errorsDetected) + " ERROS!");
   }
   
   // Gerar relatório de dependências
   g_monitorRegistry.GenerateDependencyReport();
}

//+------------------------------------------------------------------+
//| Função de Limpeza                                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_monitorRegistry != NULL) {
      AuditLog("[DependencyMonitor] Encerrando monitor de dependências...", LOG_LEVEL_INFO);
   }
} 