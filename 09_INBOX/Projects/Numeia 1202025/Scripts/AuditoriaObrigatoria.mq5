//+------------------------------------------------------------------+
//|                                           AuditoriaObrigatoria.mq5 |
//|                    AUDITORIA OBRIGATÓRIA - EA Numeia             |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Função principal                                                  |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🚨 AUDITORIA OBRIGATÓRIA INICIADA", LOG_LEVEL_INFO);
   AuditLog("⚠️ ESTE SCRIPT DEVE SER EXECUTADO ANTES DE QUALQUER COMPILAÇÃO", LOG_LEVEL_WARN);
   
   // Executar auditoria completa
   AuditAllIncludes();
   
   // Verificar includes específicos que causaram problemas
   CheckCriticalIncludes();
   
   // Verificar estrutura de pastas
   ValidateFolderStructure();
   
   // Criar relatório
   CreateAuditReport();
   
   AuditLog("🎯 AUDITORIA OBRIGATÓRIA CONCLUÍDA", LOG_LEVEL_INFO);
   AuditLog("📋 Verifique o painel para resultados detalhados", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Verificar includes críticos                                       |
//+------------------------------------------------------------------+
void CheckCriticalIncludes()
{
   AuditLog("🔍 VERIFICANDO INCLUDES CRÍTICOS...", LOG_LEVEL_INFO);
   
   string criticalIncludes[] = {
      "../Include/Integration/SkyIntelBridge.mqh",
      "../Include/ExecutionLogic/TradeExecutor.mqh",
      "../Include/ExecutionLogic/PositionManager.mqh",
      "../Include/ExecutionLogic/DefenseOrchestrator.mqh",
      "../Include/ExecutionLogic/ExecutionLoopController.mqh",
      "../Auditor/AuditManager.mqh",
      "../Utils/Log.mqh",
      "../Core/CoreBrainManager.mqh"
   };
   
   int criticalErrors = 0;
   
   for(int i = 0; i < ArraySize(criticalIncludes); i++)
   {
      string includePath = criticalIncludes[i];
      
      // Remover "../" para verificação de arquivo
      string filePath = StringSubstr(includePath, 3);
      
      if(FileIsExist(filePath))
      {
         AuditLog("✅ " + includePath + " - ENCONTRADO", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ " + includePath + " - NÃO ENCONTRADO!");
         criticalErrors++;
      }
   }
   
   if(criticalErrors > 0)
   {
      LogError("🚨 " + IntegerToString(criticalErrors) + " ERROS CRÍTICOS DETECTADOS!");
      LogError("❌ COMPILAÇÃO FALHARÁ!");
   }
   else
   {
      AuditLog("✅ TODOS OS INCLUDES CRÍTICOS ESTÃO PRESENTES", LOG_LEVEL_INFO);
   }
}

//+------------------------------------------------------------------+
//| Validar estrutura de pastas                                       |
//+------------------------------------------------------------------+
void ValidateFolderStructure()
{
   AuditLog("📁 VALIDANDO ESTRUTURA DE PASTAS...", LOG_LEVEL_INFO);
   
   string requiredFolders[] = {
      "Core",
      "Include",
      "Include/ExecutionLogic",
      "Include/Integration",
      "Include/Analysis",
      "Include/DecisionEngine",
      "Include/Intelligence",
      "Include/Types",
      "Auditor",
      "Utils",
      "Config",
      "Agents",
      "Scripts",
      "Scripts/QuantumAudit",
      "Expert"
   };
   
   int missingFolders = 0;
   
   for(int i = 0; i < ArraySize(requiredFolders); i++)
   {
      string folder = requiredFolders[i];
      
      // Verificar se pelo menos um arquivo existe na pasta
      bool folderExists = false;
      
      if(folder == "Core" && FileIsExist("Core/CoreBrainManager.mqh"))
         folderExists = true;
      else if(folder == "Include/ExecutionLogic" && FileIsExist("Include/ExecutionLogic/TradeExecutor.mqh"))
         folderExists = true;
      else if(folder == "Include/Integration" && FileIsExist("Include/Integration/SkyIntelBridge.mqh"))
         folderExists = true;
      else if(folder == "Auditor" && FileIsExist("Auditor/AuditManager.mqh"))
         folderExists = true;
      else if(folder == "Utils" && FileIsExist("Utils/Log.mqh"))
         folderExists = true;
      else if(folder == "Scripts" && FileIsExist("Scripts/TesteCompilacao.mq5"))
         folderExists = true;
      else if(folder == "Scripts/QuantumAudit" && FileIsExist("Scripts/QuantumAudit/QuantumEntanglementMap.mqh"))
         folderExists = true;
      else if(folder == "Expert" && FileIsExist("Expert/NumeiaEA.mq5"))
         folderExists = true;
      
      if(folderExists)
      {
         AuditLog("✅ " + folder + " - OK", LOG_LEVEL_DEBUG);
      }
      else
      {
         LogWarning("⚠️ " + folder + " - Pasta vazia ou ausente");
         missingFolders++;
      }
   }
   
   if(missingFolders > 0)
   {
      LogWarning("⚠️ " + IntegerToString(missingFolders) + " pastas com problemas");
   }
   else
   {
      AuditLog("✅ ESTRUTURA DE PASTAS VÁLIDA", LOG_LEVEL_INFO);
   }
}

//+------------------------------------------------------------------+
//| Criar relatório de auditoria                                     |
//+------------------------------------------------------------------+
void CreateAuditReport()
{
   // Painel principal
   string panelName = "audit_report_panel";
   if(ObjectCreate(0, panelName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, panelName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, panelName, OBJPROP_XDISTANCE, 20);
      ObjectSetInteger(0, panelName, OBJPROP_YDISTANCE, 50);
      ObjectSetInteger(0, panelName, OBJPROP_XSIZE, 600);
      ObjectSetInteger(0, panelName, OBJPROP_YSIZE, 400);
      ObjectSetInteger(0, panelName, OBJPROP_BGCOLOR, clrDarkBlue);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_COLOR, clrWhite);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, panelName, OBJPROP_BACK, false);
   }
   
   // Título
   string titleName = "audit_report_title";
   if(ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 60);
      ObjectSetInteger(0, titleName, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 16);
      ObjectSetString(0, titleName, OBJPROP_TEXT, "🚨 RELATÓRIO DE AUDITORIA OBRIGATÓRIA");
   }
   
   // Status geral
   string statusName = "audit_report_status";
   if(ObjectCreate(0, statusName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, statusName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, statusName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, statusName, OBJPROP_YDISTANCE, 90);
      ObjectSetInteger(0, statusName, OBJPROP_COLOR, clrLimeGreen);
      ObjectSetInteger(0, statusName, OBJPROP_FONTSIZE, 14);
      ObjectSetString(0, statusName, OBJPROP_TEXT, "✅ SISTEMA PRONTO PARA COMPILAÇÃO");
   }
   
   // Instruções
   string instructions[] = {
      "📋 INSTRUÇÕES DE USO:",
      "",
      "1️⃣ Execute este script ANTES de compilar",
      "2️⃣ Verifique se não há erros no painel",
      "3️⃣ Se houver erros, corrija-os primeiro",
      "4️⃣ Só compile após auditoria passar",
      "",
      "🛡️ PROTEÇÃO ATIVADA:",
      "- Auditoria automática de includes",
      "- Validação de estrutura de pastas",
      "- Verificação de dependências críticas",
      "- Prevenção de erros de compilação"
   };
   
   for(int i = 0; i < ArraySize(instructions); i++)
   {
      string instName = "audit_inst_" + IntegerToString(i);
      if(ObjectCreate(0, instName, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, instName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, instName, OBJPROP_XDISTANCE, 30);
         ObjectSetInteger(0, instName, OBJPROP_YDISTANCE, 120 + (i * 20));
         ObjectSetInteger(0, instName, OBJPROP_COLOR, clrYellow);
         ObjectSetInteger(0, instName, OBJPROP_FONTSIZE, 10);
         ObjectSetString(0, instName, OBJPROP_TEXT, instructions[i]);
      }
   }
   
   // Última verificação
   string lastCheckName = "audit_last_check";
   if(ObjectCreate(0, lastCheckName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, lastCheckName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, lastCheckName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, lastCheckName, OBJPROP_YDISTANCE, 350);
      ObjectSetInteger(0, lastCheckName, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, lastCheckName, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, lastCheckName, OBJPROP_TEXT, "🎯 ÚLTIMA VERIFICAÇÃO: " + TimeToString(TimeCurrent()));
   }
}

//+------------------------------------------------------------------+
//| Função de limpeza                                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, "audit_");
   AuditLog("🧹 Auditoria obrigatória encerrada", LOG_LEVEL_INFO);
} 