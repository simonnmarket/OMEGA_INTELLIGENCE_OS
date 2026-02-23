//+------------------------------------------------------------------+
//|                                              AuditIncludes.mq5 |
//|                    Auditoria de Includes - EA Numeia          |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include "../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
input bool   AUDIT_INCLUDES = true;     // Executar auditoria de includes
input bool   SHOW_DETAILS = true;       // Mostrar detalhes de cada arquivo
input bool   STOP_ON_ERROR = false;     // Parar na primeira falha

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("=== AUDITORIA COMPLETA DE INCLUDES - NUMEIA EA ===", LOG_LEVEL_INFO);
   AuditLog("Iniciando validação de todos os arquivos do projeto...", LOG_LEVEL_INFO);
   
   // Executar auditoria automática
   AuditAllIncludes();
   
   // Verificação adicional de estrutura
   ValidateProjectStructure();
   
   AuditLog("=== AUDITORIA CONCLUÍDA ===", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Função: ValidateProjectStructure                                 |
//+------------------------------------------------------------------+
void ValidateProjectStructure()
{
   AuditLog("=== VALIDAÇÃO DA ESTRUTURA DO PROJETO ===", LOG_LEVEL_INFO);
   
   string directories[] = {
      "Core",
      "Agents", 
      "Agents/PatternModels",
      "Auditor",
      "Config",
      "Utils",
      "Include/Analysis",
      "Include/DecisionEngine",
      "Include/ExecutionLogic",
      "Include/Intelligence",
      "Include/Integration",
      "Include/Modules",
      "Include/Tools",
      "Include/Types",
      "Include/Visuals"
   };
   
   int validDirs = 0;
   int invalidDirs = 0;
   
   for(int i = 0; i < ArraySize(directories); i++)
   {
      string dirPath = "Numeia\\" + directories[i];
      if(ValidateDirectory(dirPath))
      {
         validDirs++;
         if(SHOW_DETAILS)
            AuditLog("✓ Diretório válido: " + directories[i], LOG_LEVEL_DEBUG);
      }
      else
      {
         invalidDirs++;
         LogError("✗ Diretório INVALIDO: " + directories[i]);
         if(STOP_ON_ERROR)
            return;
      }
   }
   
   AuditLog("Diretórios válidos: " + IntegerToString(validDirs), LOG_LEVEL_INFO);
   AuditLog("Diretórios inválidos: " + IntegerToString(invalidDirs), LOG_LEVEL_ERROR);
}

//+------------------------------------------------------------------+
//| Função: ValidateDirectory                                        |
//+------------------------------------------------------------------+
bool ValidateDirectory(string dirPath)
{
   // Em MQL5, não há função direta para validar diretório
   // Vamos tentar abrir um arquivo de teste no diretório
   string testFile = dirPath + "\\test.tmp";
   int fileHandle = FileOpen(testFile, FILE_WRITE|FILE_TXT);
   
   if(fileHandle != INVALID_HANDLE)
   {
      FileClose(fileHandle);
      FileDelete(testFile);
      return true;
   }
   
   return false;
} 