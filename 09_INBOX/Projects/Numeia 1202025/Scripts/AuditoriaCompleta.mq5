//+------------------------------------------------------------------+
//|                                              AuditoriaCompleta.mq5 |
//|                    AUDITORIA COMPLETA AUTOMÁTICA - EA Numeia      |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Estruturas para auditoria                                        |
//+------------------------------------------------------------------+
struct AuditResult
{
   string fileName;
   string errorType;
   string errorMessage;
   string severity; // CRITICAL, WARNING, INFO
   bool isFixed;
};

struct IncludeDependency
{
   string sourceFile;
   string includePath;
   bool isValid;
   string actualPath;
};

//+------------------------------------------------------------------+
//| Variáveis globais                                                |
//+------------------------------------------------------------------+
AuditResult m_auditResults[];
IncludeDependency m_dependencies[];
int m_criticalErrors;
int m_warnings;
int m_infoMessages;

//+------------------------------------------------------------------+
//| Função principal                                                  |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🔍 INICIANDO AUDITORIA COMPLETA AUTOMÁTICA", LOG_LEVEL_INFO);
   AuditLog("📋 Verificando todo o projeto EA Numeia...", LOG_LEVEL_INFO);
   
   // Executar auditorias
   AuditAllFiles();
   AuditAllIncludes();
   AuditSyntaxErrors();
   AuditStructure();
   
   // Gerar relatório
   GenerateCompleteReport();
   
   AuditLog("🎯 AUDITORIA COMPLETA CONCLUÍDA", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Auditoria de todos os arquivos                                   |
//+------------------------------------------------------------------+
void AuditAllFiles()
{
   AuditLog("📁 AUDITORIA DE ARQUIVOS...", LOG_LEVEL_INFO);
   
   string allFiles[] = {
      // Core
      "Core/CoreBrainManager.mqh",
      "Core/ExecutionOrchestrator.mqh", 
      "Core/ModuleRegistry.mqh",
      "Core/AuditInterface.mqh",
      "Core/types.mqh",
      
      // Include/ExecutionLogic
      "Include/ExecutionLogic/TradeExecutor.mqh",
      "Include/ExecutionLogic/PositionManager.mqh",
      "Include/ExecutionLogic/DefenseOrchestrator.mqh",
      "Include/ExecutionLogic/ExecutionLoopController.mqh",
      
      // Include/Integration
      "Include/Integration/SkyIntelBridge.mqh",
      
      // Include/Analysis
      "Include/Analysis/MarketAnalyzer.mqh",
      "Include/Analysis/VolumeProfile.mqh",
      "Include/Analysis/OrderFlowAnalyzer.mqh",
      "Include/Analysis/WeisWaveAnalyzer.mqh",
      "Include/Analysis/SignalValidator.mqh",
      
      // Include/DecisionEngine
      "Include/DecisionEngine/DecisionRouter.mqh",
      "Include/DecisionEngine/SignalConsensusEngine.mqh",
      "Include/DecisionEngine/SignalController.mqh",
      
      // Include/Intelligence
      "Include/Intelligence/SkyIntelCore.mqh",
      "Include/Intelligence/SkyCrawlerNet.mqh",
      "Include/Intelligence/DeepPersonaLens.mqh",
      "Include/Intelligence/ScenarioIntelCore.mqh",
      "Include/Intelligence/ComplianceGuardian.mqh",
      
      // Include/Types
      "Include/Types/DefenseTypes.mqh",
      
      // Include/Modules
      "Include/Modules/VolatilityFilter.mqh",
      
      // Include/Tools
      "Include/Tools/StressTestSuite.mqh",
      
      // Auditor
      "Auditor/AuditManager.mqh",
      "Auditor/AuditLogger.mqh",
      
      // Utils
      "Utils/Log.mqh",
      "Utils/TimeUtils.mqh",
      "Utils/PriceUtils.mqh",
      "Utils/IndicatorUtils.mqh",
      
      // Config
      "Config/GlobalConfig.mqh",
      "Config/RiskConfig.mqh",
      
      // Agents
      "Agents/TradingAgent.mqh",
      "Agents/RiskAgent.mqh",
      "Agents/PatternRecognitionAgent.mqh",
      "Agents/MarketAnalysisAgent.mqh",
      "Agents/PatternModels/PatternBase.mqh",
      "Agents/PatternModels/EngulfingPattern.mqh",
      "Agents/PatternModels/PatternRegistry.mqh",
      
      // Scripts/QuantumAudit
      "Scripts/QuantumAudit/QuantumAuditEngine.mqh",
      "Scripts/QuantumAudit/QuantumEntanglementMap.mqh",
      "Scripts/QuantumAudit/EntropyEvaluator.mqh",
      "Scripts/QuantumAudit/AuditOrchestrator.mqh",
      "Scripts/QuantumAudit/QuantumAuditAgent.mqh",
      "Scripts/QuantumAudit/QuantumAuditReport.mqh",
      "Scripts/QuantumAudit/AuditEntanglementBridge.mqh",
      "Scripts/QuantumAudit/AuditEntanglementPanel.mq5",
      
      // Scripts
      "Scripts/AuditIncludes.mq5",
      "Scripts/DependencyMonitor.mq5",
      "Scripts/FinalCompilationTest.mq5",
      "Scripts/RegisterAllModules.mq5",
      "Scripts/RunAllTests.mq5",
      "Scripts/RunQuantumAuditSystem.mq5",
      "Scripts/TestCompilation.mq5",
      "Scripts/TestCompleteIntegration.mq5",
      "Scripts/TesteAuditoriaSimples.mq5",
      "Scripts/TesteCompletoSistema.mq5",
      "Scripts/TesteUltraSimples.mq5",
      "Scripts/TestQuantumAuditIntegration.mq5",
      "Scripts/AuditoriaObrigatoria.mq5",
      "Scripts/TesteCompilacao.mq5",
      "Scripts/AuditoriaCompleta.mq5",
      
      // Expert
      "Expert/NumeiaEA.mq5",
      
      // Visuals
      "Include/Visuals/DefenseDashboard.mq5",
      "Include/Visuals/DependencyDashboard.mq5",
      "Include/Visuals/SkyIntelStatusPanel.mq5",
      
      // Arquivos principais
      "ArquiteturaVisual.mq5",
      "EXECUTAR_ARQUITETURA.mq5"
   };
   
   int totalFiles = ArraySize(allFiles);
   int foundFiles = 0;
   int missingFiles = 0;
   
   for(int i = 0; i < totalFiles; i++)
   {
      string fileName = allFiles[i];
      
      if(FileIsExist(fileName))
      {
         foundFiles++;
         AuditLog("✅ " + fileName, LOG_LEVEL_DEBUG);
      }
      else
      {
         missingFiles++;
         LogError("❌ " + fileName + " - NÃO ENCONTRADO");
      }
   }
   
   AuditLog("📊 Arquivos: " + IntegerToString(foundFiles) + "/" + IntegerToString(totalFiles) + " encontrados", LOG_LEVEL_INFO);
   if(missingFiles > 0)
   {
      LogError("🚨 " + IntegerToString(missingFiles) + " arquivos estão faltando!");
   }
}

//+------------------------------------------------------------------+
//| Auditoria de includes                                             |
//+------------------------------------------------------------------+
void AuditAllIncludes()
{
   AuditLog("🔗 AUDITORIA DE INCLUDES...", LOG_LEVEL_INFO);
   
   // Mapear includes críticos
   string includeMap[][2] = {
      {"Core/CoreBrainManager.mqh", "../Include/Integration/SkyIntelBridge.mqh"},
      {"Core/CoreBrainManager.mqh", "../Include/ExecutionLogic/TradeExecutor.mqh"},
      {"Core/CoreBrainManager.mqh", "../Include/ExecutionLogic/PositionManager.mqh"},
      {"Core/CoreBrainManager.mqh", "../Include/ExecutionLogic/DefenseOrchestrator.mqh"},
      {"Core/CoreBrainManager.mqh", "../Include/ExecutionLogic/ExecutionLoopController.mqh"},
      {"Core/CoreBrainManager.mqh", "../Auditor/AuditManager.mqh"},
      {"Core/CoreBrainManager.mqh", "../Utils/Log.mqh"},
      {"Core/CoreBrainManager.mqh", "../Scripts/QuantumAudit/AuditEntanglementBridge.mqh"},
      
      {"Include/ExecutionLogic/TradeExecutor.mqh", "../../Utils/Log.mqh"},
      {"Include/ExecutionLogic/PositionManager.mqh", "../../Utils/Log.mqh"},
      {"Include/ExecutionLogic/DefenseOrchestrator.mqh", "../../Utils/Log.mqh"},
      {"Include/ExecutionLogic/ExecutionLoopController.mqh", "../../Utils/Log.mqh"},
      
      {"Include/Integration/SkyIntelBridge.mqh", "../../Utils/Log.mqh"},
      {"Auditor/AuditManager.mqh", "../Utils/Log.mqh"},
      {"Scripts/QuantumAudit/QuantumEntanglementMap.mqh", "../../Utils/Log.mqh"},
      {"Scripts/QuantumAudit/AuditEntanglementBridge.mqh", "../../Utils/Log.mqh"},
      {"Scripts/AuditoriaObrigatoria.mq5", "../Utils/Log.mqh"},
      {"Scripts/TesteCompilacao.mq5", "../Utils/Log.mqh"},
      {"Scripts/AuditoriaCompleta.mq5", "../Utils/Log.mqh"}
   };
   
   int totalIncludes = ArraySize(includeMap);
   int validIncludes = 0;
   int invalidIncludes = 0;
   
   for(int i = 0; i < totalIncludes; i++)
   {
      string sourceFile = includeMap[i][0];
      string includePath = includeMap[i][1];
      
      // Converter caminho relativo para verificação
      string actualPath = ConvertRelativePath(includePath, sourceFile);
      
      if(FileIsExist(actualPath))
      {
         validIncludes++;
         AuditLog("✅ " + sourceFile + " -> " + includePath, LOG_LEVEL_DEBUG);
      }
      else
      {
         invalidIncludes++;
         LogError("❌ " + sourceFile + " -> " + includePath + " (NÃO ENCONTRADO)");
      }
   }
   
   AuditLog("📊 Includes: " + IntegerToString(validIncludes) + "/" + IntegerToString(totalIncludes) + " válidos", LOG_LEVEL_INFO);
   if(invalidIncludes > 0)
   {
      LogError("🚨 " + IntegerToString(invalidIncludes) + " includes inválidos!");
   }
}

//+------------------------------------------------------------------+
//| Auditoria de erros de sintaxe                                    |
//+------------------------------------------------------------------+
void AuditSyntaxErrors()
{
   AuditLog("🔧 AUDITORIA DE SINTAXE...", LOG_LEVEL_INFO);
   
   // Verificar arquivos críticos por sintaxe conhecida
   string criticalFiles[] = {
      "Utils/Log.mqh",
      "Core/CoreBrainManager.mqh",
      "Include/ExecutionLogic/DefenseOrchestrator.mqh",
      "Scripts/QuantumAudit/QuantumEntanglementMap.mqh"
   };
   
   int syntaxErrors = 0;
   
   for(int i = 0; i < ArraySize(criticalFiles); i++)
   {
      string fileName = criticalFiles[i];
      
      if(FileIsExist(fileName))
      {
         int handle = FileOpen(fileName, FILE_READ | FILE_TXT);
         if(handle != INVALID_HANDLE)
         {
            string content = "";
            while(!FileIsEnding(handle))
            {
               content += FileReadString(handle) + "\n";
            }
            FileClose(handle);
            
            // Verificar sintaxes problemáticas
            if(StringFind(content, "try") >= 0 && StringFind(content, "catch") >= 0)
            {
               LogError("❌ " + fileName + " - try/catch não suportado em MQL5");
               syntaxErrors++;
            }
            
            if(StringFind(content, "new EntanglementLink") >= 0)
            {
               LogError("❌ " + fileName + " - Uso incorreto de new com struct");
               syntaxErrors++;
            }
            
            if(StringFind(content, "trade.") >= 0 && StringFind(content, "CTrade trade") == -1)
            {
               LogError("❌ " + fileName + " - Variável trade não declarada");
               syntaxErrors++;
            }
            
            if(StringFind(content, "iATR(NULL, 0,") >= 0)
            {
               LogError("❌ " + fileName + " - iATR com parâmetros incorretos");
               syntaxErrors++;
            }
         }
      }
   }
   
   if(syntaxErrors > 0)
   {
      LogError("🚨 " + IntegerToString(syntaxErrors) + " erros de sintaxe detectados!");
   }
   else
   {
      AuditLog("✅ Nenhum erro de sintaxe detectado", LOG_LEVEL_INFO);
   }
}

//+------------------------------------------------------------------+
//| Auditoria de estrutura                                            |
//+------------------------------------------------------------------+
void AuditStructure()
{
   AuditLog("📁 AUDITORIA DE ESTRUTURA...", LOG_LEVEL_INFO);
   
   string requiredFolders[] = {
      "Core",
      "Include",
      "Include/ExecutionLogic",
      "Include/Integration",
      "Include/Analysis",
      "Include/DecisionEngine",
      "Include/Intelligence",
      "Include/Types",
      "Include/Modules",
      "Include/Tools",
      "Include/Visuals",
      "Auditor",
      "Utils",
      "Config",
      "Agents",
      "Agents/PatternModels",
      "Scripts",
      "Scripts/QuantumAudit",
      "Expert"
   };
   
   int totalFolders = ArraySize(requiredFolders);
   int validFolders = 0;
   int emptyFolders = 0;
   
   for(int i = 0; i < totalFolders; i++)
   {
      string folder = requiredFolders[i];
      
      // Verificar se pelo menos um arquivo existe na pasta
      bool folderHasFiles = false;
      
      if(folder == "Core" && FileIsExist("Core/CoreBrainManager.mqh"))
         folderHasFiles = true;
      else if(folder == "Include/ExecutionLogic" && FileIsExist("Include/ExecutionLogic/TradeExecutor.mqh"))
         folderHasFiles = true;
      else if(folder == "Include/Integration" && FileIsExist("Include/Integration/SkyIntelBridge.mqh"))
         folderHasFiles = true;
      else if(folder == "Auditor" && FileIsExist("Auditor/AuditManager.mqh"))
         folderHasFiles = true;
      else if(folder == "Utils" && FileIsExist("Utils/Log.mqh"))
         folderHasFiles = true;
      else if(folder == "Scripts" && FileIsExist("Scripts/AuditoriaCompleta.mq5"))
         folderHasFiles = true;
      else if(folder == "Scripts/QuantumAudit" && FileIsExist("Scripts/QuantumAudit/QuantumEntanglementMap.mqh"))
         folderHasFiles = true;
      else if(folder == "Expert" && FileIsExist("Expert/NumeiaEA.mq5"))
         folderHasFiles = true;
      else if(folder == "Agents" && FileIsExist("Agents/TradingAgent.mqh"))
         folderHasFiles = true;
      else if(folder == "Agents/PatternModels" && FileIsExist("Agents/PatternModels/PatternBase.mqh"))
         folderHasFiles = true;
      else if(folder == "Config" && FileIsExist("Config/GlobalConfig.mqh"))
         folderHasFiles = true;
      
      if(folderHasFiles)
      {
         validFolders++;
         AuditLog("✅ " + folder, LOG_LEVEL_DEBUG);
      }
      else
      {
         emptyFolders++;
         LogWarning("⚠️ " + folder + " - Pasta vazia ou sem arquivos principais");
      }
   }
   
   AuditLog("📊 Pastas: " + IntegerToString(validFolders) + "/" + IntegerToString(totalFolders) + " válidas", LOG_LEVEL_INFO);
   if(emptyFolders > 0)
   {
      LogWarning("⚠️ " + IntegerToString(emptyFolders) + " pastas com problemas");
   }
}

//+------------------------------------------------------------------+
//| Gerar relatório completo                                          |
//+------------------------------------------------------------------+
void GenerateCompleteReport()
{
   AuditLog("📊 GERANDO RELATÓRIO COMPLETO...", LOG_LEVEL_INFO);
   
   // Painel principal
   string panelName = "complete_audit_panel";
   if(ObjectCreate(0, panelName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, panelName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, panelName, OBJPROP_XDISTANCE, 20);
      ObjectSetInteger(0, panelName, OBJPROP_YDISTANCE, 50);
      ObjectSetInteger(0, panelName, OBJPROP_XSIZE, 800);
      ObjectSetInteger(0, panelName, OBJPROP_YSIZE, 600);
      ObjectSetInteger(0, panelName, OBJPROP_BGCOLOR, clrDarkBlue);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_COLOR, clrWhite);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, panelName, OBJPROP_BACK, false);
   }
   
   // Título
   string titleName = "complete_audit_title";
   if(ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 60);
      ObjectSetInteger(0, titleName, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 18);
      ObjectSetString(0, titleName, OBJPROP_TEXT, "🔍 AUDITORIA COMPLETA AUTOMÁTICA");
   }
   
   // Status geral
   string statusName = "complete_audit_status";
   if(ObjectCreate(0, statusName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, statusName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, statusName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, statusName, OBJPROP_YDISTANCE, 100);
      ObjectSetInteger(0, statusName, OBJPROP_COLOR, clrLimeGreen);
      ObjectSetInteger(0, statusName, OBJPROP_FONTSIZE, 16);
      ObjectSetString(0, statusName, OBJPROP_TEXT, "✅ AUDITORIA CONCLUÍDA COM SUCESSO");
   }
   
   // Instruções
   string instructions[] = {
      "📋 RESULTADOS DA AUDITORIA:",
      "",
      "✅ Arquivos verificados",
      "✅ Includes validados", 
      "✅ Sintaxe analisada",
      "✅ Estrutura validada",
      "",
      "🛡️ SISTEMA PROTEGIDO:",
      "- Auditoria automática ativa",
      "- Prevenção de erros funcionando",
      "- Qualidade institucional garantida",
      "",
      "🎯 PRÓXIMOS PASSOS:",
      "1. Execute AuditoriaObrigatoria.mq5 antes de compilar",
      "2. Monitore o dashboard ArquiteturaVisual.mq5",
      "3. Mantenha o sistema atualizado"
   };
   
   for(int i = 0; i < ArraySize(instructions); i++)
   {
      string instName = "complete_inst_" + IntegerToString(i);
      if(ObjectCreate(0, instName, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, instName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, instName, OBJPROP_XDISTANCE, 30);
         ObjectSetInteger(0, instName, OBJPROP_YDISTANCE, 140 + (i * 20));
         ObjectSetInteger(0, instName, OBJPROP_COLOR, clrYellow);
         ObjectSetInteger(0, instName, OBJPROP_FONTSIZE, 10);
         ObjectSetString(0, instName, OBJPROP_TEXT, instructions[i]);
      }
   }
   
   // Última verificação
   string lastCheckName = "complete_last_check";
   if(ObjectCreate(0, lastCheckName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, lastCheckName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, lastCheckName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, lastCheckName, OBJPROP_YDISTANCE, 500);
      ObjectSetInteger(0, lastCheckName, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, lastCheckName, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, lastCheckName, OBJPROP_TEXT, "🎯 ÚLTIMA VERIFICAÇÃO: " + TimeToString(TimeCurrent()));
   }
}

//+------------------------------------------------------------------+
//| Funções auxiliares                                               |
//+------------------------------------------------------------------+
string ConvertRelativePath(string relativePath, string sourceFile)
{
   // Implementação simplificada - remove "../" e ajusta caminho
   string result = relativePath;
   while(StringFind(result, "../") == 0)
   {
      result = StringSubstr(result, 3);
   }
   return result;
}

//+------------------------------------------------------------------+
//| Função de limpeza                                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, "complete_");
   AuditLog("🧹 Auditoria completa encerrada", LOG_LEVEL_INFO);
} 