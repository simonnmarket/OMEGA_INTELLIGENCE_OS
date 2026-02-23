//+------------------------------------------------------------------+
//|                            Log.mqh                               |
//|        Utilitário genérico de logging para a EA Numeia          |
//+------------------------------------------------------------------+
#ifndef __LOG_MQH__
#define __LOG_MQH__

//+------------------------------------------------------------------+
//| Constantes de Logging                                            |
//+------------------------------------------------------------------+
#define LOG_LEVEL_ERROR   0
#define LOG_LEVEL_WARN    1
#define LOG_LEVEL_INFO    2
#define LOG_LEVEL_DEBUG   3

// Log principal formatado
void LogPrint(string message, string source = "SYSTEM") {
   string full_message = StringFormat("ℹ️ [INFO] [%s] %s", source, message);
   Print(full_message);
}

// Versões simplificadas
void LogInfo(string msg, string src = "SYSTEM")    { LogPrint(msg, src); }
void LogWarn(string msg, string src = "SYSTEM")    { Print("⚠️ [WARN] [" + src + "] " + msg); }
void LogErr(string msg, string src = "SYSTEM")     { Print("❌ [ERROR] [" + src + "] " + msg); }
void LogOK(string msg, string src = "SYSTEM")      { Print("✅ [OK] [" + src + "] " + msg); }

// Função Log genérica
void Log(string msg, string src = "SYSTEM")        { LogPrint(msg, src); }

// Versão auditável para módulos institucionais
void AuditLog(const string origin, const string symbol, const string message)
{
   string full_message = StringFormat("[AUDIT] [%s] %s >> %s", origin, symbol, message);
   Print(full_message);
}

//+------------------------------------------------------------------+
//| Função: AuditLog                                                 |
//+------------------------------------------------------------------+
void AuditLog(string message, int level = LOG_LEVEL_INFO)
{
   string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
   string levelStr = "";
   
   switch(level)
   {
      case LOG_LEVEL_ERROR: levelStr = "ERROR"; break;
      case LOG_LEVEL_WARN:  levelStr = "WARN";  break;
      case LOG_LEVEL_INFO:  levelStr = "INFO";  break;
      case LOG_LEVEL_DEBUG: levelStr = "DEBUG"; break;
   }
   
   Print("[", timestamp, "] [", levelStr, "] ", message);
}

//+------------------------------------------------------------------+
//| Função: LogFormat                                                |
//+------------------------------------------------------------------+
void LogFormat(string format, string param1 = "", string param2 = "", string param3 = "")
{
   string message = StringFormat(format, param1, param2, param3);
   AuditLog(message);
}

//+------------------------------------------------------------------+
//| Função: LogError                                                 |
//+------------------------------------------------------------------+
void LogError(string message)
{
   AuditLog(message, LOG_LEVEL_ERROR);
}

//+------------------------------------------------------------------+
//| Função: LogWarning                                               |
//+------------------------------------------------------------------+
void LogWarning(string message)
{
   AuditLog(message, LOG_LEVEL_WARN);
}

//+------------------------------------------------------------------+
//| Função: LogDebug                                                 |
//+------------------------------------------------------------------+
void LogDebug(string message)
{
   AuditLog(message, LOG_LEVEL_DEBUG);
}

//+------------------------------------------------------------------+
//| Função: ValidateIncludePath                                      |
//+------------------------------------------------------------------+
bool ValidateIncludePath(string includePath, string fileName)
{
   string fullPath = includePath + "\\" + fileName;
   int fileHandle = FileOpen(fullPath, FILE_READ|FILE_TXT);
   
   if(fileHandle != INVALID_HANDLE)
   {
      FileClose(fileHandle);
      AuditLog("✓ Include válido: " + fileName, LOG_LEVEL_DEBUG);
      return true;
   }
   else
   {
      LogError("✗ Include INVALIDO: " + fileName + " em " + includePath);
      LogError("  Path completo: " + fullPath);
      return false;
   }
}

//+------------------------------------------------------------------+
//| Função: AuditAllIncludes                                         |
//+------------------------------------------------------------------+
void AuditAllIncludes()
{
   AuditLog("=== AUDITORIA DE INCLUDES INICIADA ===", LOG_LEVEL_INFO);
   
   // Lista de includes críticos para validar
   string includes[] = {
      "Include/ExecutionLogic/TradeExecutor.mqh",
      "Include/ExecutionLogic/PositionManager.mqh", 
      "Include/ExecutionLogic/DefenseOrchestrator.mqh",
      "Include/ExecutionLogic/ExecutionLoopController.mqh",
      "Include/ExecutionLogic/SignalExecutionAgent.mqh",
      "Include/ExecutionLogic/TradeExecutorSkyIntel.mqh",
      "Include/ExecutionLogic/DefenseAgent.mqh",
      "Include/ExecutionLogic/SessionManager.mqh",
      "Include/Integration/SkyIntelBridge.mqh",
      "Auditor/AuditManager.mqh",
      "Utils/Log.mqh",
      "Core/types.mqh",
      "Core/ModuleRegistry.mqh",
      "Core/ExecutionOrchestrator.mqh",
      "Core/AuditInterface.mqh",
      "Agents/TradingAgent.mqh",
      "Agents/RiskAgent.mqh",
      "Agents/PatternRecognitionAgent.mqh",
      "Agents/MarketAnalysisAgent.mqh",
      "Include/Analysis/MarketAnalyzer.mqh",
      "Include/Analysis/VolumeProfile.mqh",
      "Include/Analysis/OrderFlowAnalyzer.mqh",
      "Include/Analysis/WeisWaveAnalyzer.mqh",
      "Include/Analysis/SignalValidator.mqh",
      "Include/DecisionEngine/DecisionRouter.mqh",
      "Include/DecisionEngine/SignalConsensusEngine.mqh",
      "Include/DecisionEngine/SignalController.mqh",
      "Include/Intelligence/SkyIntelCore.mqh",
      "Include/Intelligence/SkyCrawlerNet.mqh",
      "Include/Intelligence/DeepPersonaLens.mqh",
      "Include/Intelligence/ScenarioIntelCore.mqh",
      "Include/Intelligence/ComplianceGuardian.mqh",
      "Config/GlobalConfig.mqh",
      "Config/RiskConfig.mqh",
      "Utils/TimeUtils.mqh",
      "Utils/PriceUtils.mqh",
      "Utils/IndicatorUtils.mqh"
   };
   
   int totalFiles = ArraySize(includes);
   int validFiles = 0;
   int invalidFiles = 0;
   
   for(int i = 0; i < totalFiles; i++)
   {
      if(ValidateIncludePath("Numeia", includes[i]))
         validFiles++;
      else
         invalidFiles++;
   }
   
   AuditLog("=== RESULTADO DA AUDITORIA ===", LOG_LEVEL_INFO);
   AuditLog("Total de arquivos verificados: " + IntegerToString(totalFiles), LOG_LEVEL_INFO);
   AuditLog("Arquivos válidos: " + IntegerToString(validFiles), LOG_LEVEL_INFO);
   AuditLog("Arquivos inválidos: " + IntegerToString(invalidFiles), LOG_LEVEL_ERROR);
   
   if(invalidFiles > 0)
   {
      LogError("AUDITORIA FALHOU! Existem includes inválidos que impedirão a compilação.");
   }
   else
   {
      AuditLog("✓ AUDITORIA PASSOU! Todos os includes estão válidos.", LOG_LEVEL_INFO);
   }
}

#endif // __LOG_MQH__ 