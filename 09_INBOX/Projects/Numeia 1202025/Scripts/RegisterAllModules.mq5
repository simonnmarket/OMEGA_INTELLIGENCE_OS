//+------------------------------------------------------------------+
//|                                         RegisterAllModules.mq5   |
//|                    Registro Automático de Módulos - EA Numeia   |
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
input bool   REGISTER_CORE = true;        // Registrar módulos Core
input bool   REGISTER_AGENTS = true;      // Registrar módulos Agents
input bool   REGISTER_ANALYSIS = true;    // Registrar módulos Analysis
input bool   REGISTER_EXECUTION = true;   // Registrar módulos Execution
input bool   REGISTER_INTEGRATION = true; // Registrar módulos Integration
input bool   REGISTER_AUDITOR = true;     // Registrar módulos Auditor
input bool   REGISTER_UTILS = true;       // Registrar módulos Utils
input bool   REGISTER_CONFIG = true;      // Registrar módulos Config
input bool   AUTO_REGISTER_DEPENDENCIES = true; // Registrar dependências automaticamente

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("=== REGISTRO AUTOMÁTICO DE MÓDULOS - NUMEIA EA ===", LOG_LEVEL_INFO);
   
   // Inicializar o registry
   InitializeModuleRegistry();
   ModuleRegistry* registry = GetModuleRegistry();
   
   int modulesRegistered = 0;
   int dependenciesRegistered = 0;
   int integrationsRegistered = 0;
   
   // Registrar módulos Core
   if(REGISTER_CORE) {
      modulesRegistered += RegisterCoreModules(registry);
   }
   
   // Registrar módulos Agents
   if(REGISTER_AGENTS) {
      modulesRegistered += RegisterAgentModules(registry);
   }
   
   // Registrar módulos Analysis
   if(REGISTER_ANALYSIS) {
      modulesRegistered += RegisterAnalysisModules(registry);
   }
   
   // Registrar módulos Execution
   if(REGISTER_EXECUTION) {
      modulesRegistered += RegisterExecutionModules(registry);
   }
   
   // Registrar módulos Integration
   if(REGISTER_INTEGRATION) {
      modulesRegistered += RegisterIntegrationModules(registry);
   }
   
   // Registrar módulos Auditor
   if(REGISTER_AUDITOR) {
      modulesRegistered += RegisterAuditorModules(registry);
   }
   
   // Registrar módulos Utils
   if(REGISTER_UTILS) {
      modulesRegistered += RegisterUtilsModules(registry);
   }
   
   // Registrar módulos Config
   if(REGISTER_CONFIG) {
      modulesRegistered += RegisterConfigModules(registry);
   }
   
   // Registrar dependências automáticas
   if(AUTO_REGISTER_DEPENDENCIES) {
      dependenciesRegistered += RegisterAutomaticDependencies(registry);
   }
   
   // Registrar integrações automáticas
   integrationsRegistered += RegisterAutomaticIntegrations(registry);
   
   // Validar integridade
   bool integrityOK = registry.ValidateIntegrity();
   
   // Gerar relatório
   registry.GenerateDependencyReport();
   
   // Resultado final
   AuditLog("=== RESULTADO DO REGISTRO ===", LOG_LEVEL_INFO);
   AuditLog("Módulos registrados: " + IntegerToString(modulesRegistered), LOG_LEVEL_INFO);
   AuditLog("Dependências registradas: " + IntegerToString(dependenciesRegistered), LOG_LEVEL_INFO);
   AuditLog("Integrações registradas: " + IntegerToString(integrationsRegistered), LOG_LEVEL_INFO);
   AuditLog("Integridade do sistema: " + (integrityOK ? "OK" : "FALHOU"), integrityOK ? LOG_LEVEL_INFO : LOG_LEVEL_ERROR);
   
   if(integrityOK) {
      AuditLog("🎉 SISTEMA DE REGISTRO CONFIGURADO COM SUCESSO!", LOG_LEVEL_INFO);
   } else {
      LogError("❌ PROBLEMAS DETECTADOS NO SISTEMA DE REGISTRO!");
   }
}

//+------------------------------------------------------------------+
//| Funções de Registro por Categoria                                |
//+------------------------------------------------------------------+
int RegisterCoreModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Core...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Core modules
   if(registry.RegisterModule("CoreBrainManager", "../Core/CoreBrainManager.mqh", "Core", "Gerenciador central do sistema")) count++;
   if(registry.RegisterModule("ExecutionOrchestrator", "../Core/ExecutionOrchestrator.mqh", "Core", "Orquestrador de execução")) count++;
   if(registry.RegisterModule("ModuleRegistry", "../Core/ModuleRegistry.mqh", "Core", "Sistema de registro de módulos")) count++;
   if(registry.RegisterModule("AuditInterface", "../Core/AuditInterface.mqh", "Core", "Interface de auditoria")) count++;
   if(registry.RegisterModule("types", "../Core/types.mqh", "Core", "Definições de tipos")) count++;
   
   return count;
}

int RegisterAgentModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Agents...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Agent modules
   if(registry.RegisterModule("TradingAgent", "../Agents/TradingAgent.mqh", "Agent", "Agente de trading")) count++;
   if(registry.RegisterModule("RiskAgent", "../Agents/RiskAgent.mqh", "Agent", "Agente de gestão de risco")) count++;
   if(registry.RegisterModule("PatternRecognitionAgent", "../Agents/PatternRecognitionAgent.mqh", "Agent", "Agente de reconhecimento de padrões")) count++;
   if(registry.RegisterModule("MarketAnalysisAgent", "../Agents/MarketAnalysisAgent.mqh", "Agent", "Agente de análise de mercado")) count++;
   
   return count;
}

int RegisterAnalysisModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Analysis...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Analysis modules
   if(registry.RegisterModule("MarketAnalyzer", "../Include/Analysis/MarketAnalyzer.mqh", "Analysis", "Analisador de mercado")) count++;
   if(registry.RegisterModule("VolumeProfile", "../Include/Analysis/VolumeProfile.mqh", "Analysis", "Perfil de volume")) count++;
   if(registry.RegisterModule("OrderFlowAnalyzer", "../Include/Analysis/OrderFlowAnalyzer.mqh", "Analysis", "Analisador de fluxo de ordens")) count++;
   if(registry.RegisterModule("WeisWaveAnalyzer", "../Include/Analysis/WeisWaveAnalyzer.mqh", "Analysis", "Analisador Weis Wave")) count++;
   if(registry.RegisterModule("SignalValidator", "../Include/Analysis/SignalValidator.mqh", "Analysis", "Validador de sinais")) count++;
   
   return count;
}

int RegisterExecutionModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Execution...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Execution modules
   if(registry.RegisterModule("TradeExecutor", "../Include/ExecutionLogic/TradeExecutor.mqh", "Execution", "Executor de ordens")) count++;
   if(registry.RegisterModule("PositionManager", "../Include/ExecutionLogic/PositionManager.mqh", "Execution", "Gerenciador de posições")) count++;
   if(registry.RegisterModule("DefenseOrchestrator", "../Include/ExecutionLogic/DefenseOrchestrator.mqh", "Execution", "Orquestrador de defesa")) count++;
   if(registry.RegisterModule("ExecutionLoopController", "../Include/ExecutionLogic/ExecutionLoopController.mqh", "Execution", "Controlador de loop de execução")) count++;
   if(registry.RegisterModule("SignalExecutionAgent", "../Include/ExecutionLogic/SignalExecutionAgent.mqh", "Execution", "Agente de execução de sinais")) count++;
   if(registry.RegisterModule("TradeExecutorSkyIntel", "../Include/ExecutionLogic/TradeExecutorSkyIntel.mqh", "Execution", "Executor SkyIntel")) count++;
   if(registry.RegisterModule("DefenseAgent", "../Include/ExecutionLogic/DefenseAgent.mqh", "Execution", "Agente de defesa")) count++;
   if(registry.RegisterModule("SessionManager", "../Include/ExecutionLogic/SessionManager.mqh", "Execution", "Gerenciador de sessões")) count++;
   
   return count;
}

int RegisterIntegrationModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Integration...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Integration modules
   if(registry.RegisterModule("SkyIntelBridge", "../Include/Integration/SkyIntelBridge.mqh", "Integration", "Ponte SkyIntel")) count++;
   
   return count;
}

int RegisterAuditorModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Auditor...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Auditor modules
   if(registry.RegisterModule("AuditManager", "../Auditor/AuditManager.mqh", "Auditor", "Gerenciador de auditoria")) count++;
   
   return count;
}

int RegisterUtilsModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Utils...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Utils modules
   if(registry.RegisterModule("Log", "../Utils/Log.mqh", "Utils", "Sistema de logging")) count++;
   if(registry.RegisterModule("TimeUtils", "../Utils/TimeUtils.mqh", "Utils", "Utilitários de tempo")) count++;
   if(registry.RegisterModule("PriceUtils", "../Utils/PriceUtils.mqh", "Utils", "Utilitários de preço")) count++;
   if(registry.RegisterModule("IndicatorUtils", "../Utils/IndicatorUtils.mqh", "Utils", "Utilitários de indicadores")) count++;
   
   return count;
}

int RegisterConfigModules(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando módulos Config...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Config modules
   if(registry.RegisterModule("GlobalConfig", "../Config/GlobalConfig.mqh", "Config", "Configurações globais")) count++;
   if(registry.RegisterModule("RiskConfig", "../Config/RiskConfig.mqh", "Config", "Configurações de risco")) count++;
   
   return count;
}

//+------------------------------------------------------------------+
//| Registro Automático de Dependências                              |
//+------------------------------------------------------------------+
int RegisterAutomaticDependencies(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando dependências automáticas...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Dependências críticas do Core
   if(registry.RegisterDependency("CoreBrainManager", "TradeExecutor", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "PositionManager", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "DefenseOrchestrator", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "ExecutionLoopController", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "SkyIntelBridge", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "AuditManager", "include", true)) count++;
   if(registry.RegisterDependency("CoreBrainManager", "Log", "include", true)) count++;
   
   // Dependências de Execution
   if(registry.RegisterDependency("TradeExecutor", "Log", "include", false)) count++;
   if(registry.RegisterDependency("PositionManager", "Log", "include", false)) count++;
   if(registry.RegisterDependency("DefenseOrchestrator", "Log", "include", false)) count++;
   if(registry.RegisterDependency("ExecutionLoopController", "Log", "include", false)) count++;
   
   // Dependências de Agents
   if(registry.RegisterDependency("TradingAgent", "Log", "include", false)) count++;
   if(registry.RegisterDependency("RiskAgent", "Log", "include", false)) count++;
   if(registry.RegisterDependency("PatternRecognitionAgent", "Log", "include", false)) count++;
   if(registry.RegisterDependency("MarketAnalysisAgent", "Log", "include", false)) count++;
   
   // Dependências de Analysis
   if(registry.RegisterDependency("MarketAnalyzer", "Log", "include", false)) count++;
   if(registry.RegisterDependency("VolumeProfile", "Log", "include", false)) count++;
   if(registry.RegisterDependency("OrderFlowAnalyzer", "Log", "include", false)) count++;
   if(registry.RegisterDependency("WeisWaveAnalyzer", "Log", "include", false)) count++;
   if(registry.RegisterDependency("SignalValidator", "Log", "include", false)) count++;
   
   return count;
}

//+------------------------------------------------------------------+
//| Registro Automático de Integrações                               |
//+------------------------------------------------------------------+
int RegisterAutomaticIntegrations(ModuleRegistry* registry)
{
   AuditLog("[RegisterAllModules] Registrando integrações automáticas...", LOG_LEVEL_DEBUG);
   
   int count = 0;
   
   // Integrações Core-Execution
   if(registry.RegisterIntegration("CoreBrainManager", "TradeExecutor", "execution", "trade_orders", true)) count++;
   if(registry.RegisterIntegration("CoreBrainManager", "PositionManager", "management", "position_control", true)) count++;
   if(registry.RegisterIntegration("CoreBrainManager", "DefenseOrchestrator", "defense", "risk_control", true)) count++;
   
   // Integrações Execution-Agents
   if(registry.RegisterIntegration("TradeExecutor", "TradingAgent", "signals", "trade_signals", false)) count++;
   if(registry.RegisterIntegration("PositionManager", "RiskAgent", "risk", "risk_limits", false)) count++;
   
   // Integrações Analysis-Execution
   if(registry.RegisterIntegration("SignalValidator", "TradeExecutor", "validation", "signal_validation", false)) count++;
   if(registry.RegisterIntegration("MarketAnalyzer", "TradingAgent", "analysis", "market_data", false)) count++;
   
   return count;
} 