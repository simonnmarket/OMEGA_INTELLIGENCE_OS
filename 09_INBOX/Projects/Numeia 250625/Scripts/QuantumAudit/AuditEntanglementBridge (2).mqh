//+------------------------------------------------------------------+
//|                AuditEntanglementBridge.mqh                      |
//|  Ponte entre QuantumAuditEngine e Painel Visual de Auditoria    |
//+------------------------------------------------------------------+
#ifndef AUDIT_ENTANGLEMENT_BRIDGE_MQH
#define AUDIT_ENTANGLEMENT_BRIDGE_MQH

#include "../../Utils/Log.mqh"
#include <Files\FileTxt.mqh>
#include "QuantumAuditEngine.mqh"
#include "QuantumEntanglementMap.mqh"

// Classe responsável por gerenciar auditoria e exportar resultados para o painel visual
class AuditEntanglementBridge
{
private:
   QuantumAuditEngine auditEngine;
   QuantumEntanglementMap entanglementMap;
   string resultFileName;

public:
   // Construtor
   AuditEntanglementBridge() : resultFileName("entanglement_status.dat") 
   {
      AuditLog("[AuditEntanglementBridge] Bridge inicializado", LOG_LEVEL_INFO);
   }

   // Inicialização geral
   bool Init()
   {
      AuditLog("[AuditEntanglementBridge] Inicializando...", LOG_LEVEL_INFO);
      
      bool engineOK = auditEngine.Init();
      bool mapOK = entanglementMap.Init();
      
      if(!engineOK || !mapOK)
      {
         LogError("Falha na inicialização do bridge");
         return false;
      }
      
      // Configurar mapa de emaranhamento com links padrão
      SetupDefaultEntanglementMap();
      
      AuditLog("Bridge inicializado com sucesso", LOG_LEVEL_INFO);
      return true;
   }

   // Executa auditoria completa e exporta resultados
   void RunFullAudit()
   {
      AuditLog("[AuditEntanglementBridge] Executando auditoria completa...", LOG_LEVEL_INFO);
      
      // Lista de módulos que REALMENTE existem
      string modules[] = {
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

      ResetFile();
      
      int totalModules = ArraySize(modules);
      int successCount = 0;
      int failCount = 0;

      for(int i = 0; i < totalModules; i++)
      {
         string module = modules[i];
         AuditLog("Auditando módulo: " + module, LOG_LEVEL_DEBUG);
         
         // Verificar se o arquivo existe antes de auditar
         if(!FileIsExist(module))
         {
            LogError("Módulo não encontrado: " + module);
            ExportStatus(module, "FALHA");
            failCount++;
            continue;
         }
         
         bool linkValid = entanglementMap.ValidateLink(module);
         auditEngine.AnalyzeFile(module);
         
         string status = linkValid ? "OK" : "WARN";
         ExportStatus(module, status);
         
         if(linkValid)
            successCount++;
         else
            failCount++;
      }
      
      AuditLog("Auditoria completa concluída - Sucessos: " + IntegerToString(successCount) + 
               ", Falhas: " + IntegerToString(failCount), LOG_LEVEL_INFO);
   }

   // Executar auditoria com módulos customizados
   void RunCustomAudit(const string &customModules[])
   {
      AuditLog("[AuditEntanglementBridge] Executando auditoria customizada...", LOG_LEVEL_INFO);
      
      ResetFile();
      
      int totalModules = ArraySize(customModules);
      for(int i = 0; i < totalModules; i++)
      {
         string module = customModules[i];
         bool linkValid = entanglementMap.ValidateLink(module);
         auditEngine.AnalyzeFile(module);
         string status = linkValid ? "OK" : "FALHA";
         ExportStatus(module, status);
      }
      
      AuditLog("Auditoria customizada concluída para " + IntegerToString(totalModules) + " módulos", LOG_LEVEL_INFO);
   }

   // Verificar integridade dos resultados
   bool ValidateResults()
   {
      if(!FileIsExist(resultFileName))
      {
         LogWarning("Arquivo de resultados não encontrado: " + resultFileName);
         return false;
      }

      int handle = FileOpen(resultFileName, FILE_READ | FILE_TXT | FILE_ANSI);
      if(handle == INVALID_HANDLE)
      {
         LogError("Erro ao abrir arquivo de resultados: " + resultFileName);
         return false;
      }

      int lineCount = 0;
      int validLines = 0;
      
      while(!FileIsEnding(handle))
      {
         string line = FileReadString(handle);
         if(StringLen(line) > 0)
         {
            lineCount++;
            string parts[];
            StringSplit(line, ',', parts);
            if(ArraySize(parts) >= 2)
            {
               string status = parts[1];
               if(status == "OK" || status == "FALHA" || status == "WARN")
                  validLines++;
            }
         }
      }
      FileClose(handle);
      
      bool isValid = (validLines == lineCount);
      AuditLog("Validação de resultados - Total: " + IntegerToString(lineCount) + 
               ", Válidos: " + IntegerToString(validLines), LOG_LEVEL_DEBUG);
      
      return isValid;
   }

   // Obter estatísticas dos resultados
   void GetAuditStatistics(int &totalModules, int &okCount, int &failCount, int &warnCount)
   {
      totalModules = okCount = failCount = warnCount = 0;
      
      if(!FileIsExist(resultFileName))
         return;

      int handle = FileOpen(resultFileName, FILE_READ | FILE_TXT | FILE_ANSI);
      if(handle == INVALID_HANDLE)
         return;

      while(!FileIsEnding(handle))
      {
         string line = FileReadString(handle);
         if(StringLen(line) > 0)
         {
            string parts[];
            StringSplit(line, ',', parts);
            if(ArraySize(parts) >= 2)
            {
               totalModules++;
               string status = parts[1];
               
               if(status == "OK")
                  okCount++;
               else if(status == "FALHA")
                  failCount++;
               else if(status == "WARN")
                  warnCount++;
            }
         }
      }
      FileClose(handle);
      
      AuditLog("Estatísticas da auditoria - Total: " + IntegerToString(totalModules) + 
               ", OK: " + IntegerToString(okCount) + 
               ", FALHA: " + IntegerToString(failCount) + 
               ", WARN: " + IntegerToString(warnCount), LOG_LEVEL_INFO);
   }

   // Backup dos resultados
   void BackupResults()
   {
      if(!FileIsExist(resultFileName))
         return;

      string backupFile = resultFileName + ".backup";
      FileCopy(resultFileName, FILE_COMMON, backupFile, FILE_COMMON);
      AuditLog("Backup dos resultados criado: " + backupFile, LOG_LEVEL_INFO);
   }

   // Limpar resultados
   void ClearResults()
   {
      ResetFile();
      AuditLog("Resultados limpos", LOG_LEVEL_INFO);
   }

   // Método para ser chamado pelo CoreBrainManager
   static void RunAuditFromCoreBrain()
   {
      AuditLog("[AuditEntanglementBridge] Ativado pelo CoreBrainManager", LOG_LEVEL_INFO);
      
      AuditEntanglementBridge bridge;
      if(bridge.Init())
      {
         bridge.RunFullAudit();
         bridge.ValidateResults();
      }
   }

   // Método para auditoria automática com alertas
   static void RunAutomaticAuditWithAlerts()
   {
      AuditLog("[AuditEntanglementBridge] Executando auditoria automática com alertas...", LOG_LEVEL_INFO);
      
      AuditEntanglementBridge bridge;
      if(bridge.Init())
      {
         bridge.RunFullAudit();
         
         int total, ok, fail, warn;
         bridge.GetAuditStatistics(total, ok, fail, warn);
         
         if(fail > 0)
         {
            LogError("Problemas críticos detectados na auditoria automática!");
            // Aqui pode chamar o painel visual ou enviar alertas
         }
         else if(warn > 0)
         {
            LogWarning("Avisos detectados na auditoria automática");
         }
         else
         {
            AuditLog("Auditoria automática concluída com sucesso", LOG_LEVEL_INFO);
         }
      }
   }

private:
   // Configurar mapa de emaranhamento padrão
   void SetupDefaultEntanglementMap()
   {
      AuditLog("Configurando mapa de emaranhamento padrão...", LOG_LEVEL_DEBUG);
      
      // Registrar módulos principais que REALMENTE existem
      entanglementMap.RegisterModule("Core/CoreBrainManager.mqh");
      entanglementMap.RegisterModule("Include/ExecutionLogic/TradeExecutor.mqh");
      entanglementMap.RegisterModule("Include/ExecutionLogic/PositionManager.mqh");
      entanglementMap.RegisterModule("Include/ExecutionLogic/DefenseOrchestrator.mqh");
      entanglementMap.RegisterModule("Include/ExecutionLogic/ExecutionLoopController.mqh");
      entanglementMap.RegisterModule("Include/Integration/SkyIntelBridge.mqh");
      entanglementMap.RegisterModule("Auditor/AuditManager.mqh");
      entanglementMap.RegisterModule("Utils/Log.mqh");
      entanglementMap.RegisterModule("Expert/NumeiaEA.mq5");
      
      // Criar links de emaranhamento entre módulos que existem
      entanglementMap.CreateLink("Core/CoreBrainManager.mqh", "Include/ExecutionLogic/TradeExecutor.mqh", 0.8, "Integração de execução");
      entanglementMap.CreateLink("Core/CoreBrainManager.mqh", "Include/ExecutionLogic/DefenseOrchestrator.mqh", 0.7, "Integração de defesa");
      entanglementMap.CreateLink("Core/CoreBrainManager.mqh", "Include/Integration/SkyIntelBridge.mqh", 0.6, "Integração de inteligência");
      entanglementMap.CreateLink("Include/ExecutionLogic/TradeExecutor.mqh", "Include/ExecutionLogic/DefenseOrchestrator.mqh", 0.5, "Coordenação de execução");
      entanglementMap.CreateLink("Core/CoreBrainManager.mqh", "Auditor/AuditManager.mqh", 0.4, "Integração de auditoria");
      
      AuditLog("Mapa de emaranhamento padrão configurado", LOG_LEVEL_DEBUG);
   }

   // Reseta o arquivo de saída
   void ResetFile()
   {
      int handle = FileOpen(resultFileName, FILE_WRITE | FILE_TXT | FILE_ANSI);
      if(handle != INVALID_HANDLE)
      {
         FileClose(handle);
         AuditLog("Arquivo de resultados resetado", LOG_LEVEL_DEBUG);
      }
      else
      {
         LogError("Erro ao resetar arquivo de resultados: " + resultFileName);
      }
   }

   // Exporta o status de um módulo auditado
   void ExportStatus(string module, string status)
   {
      int handle = FileOpen(resultFileName, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI);
      if(handle != INVALID_HANDLE)
      {
         FileSeek(handle, 0, SEEK_END);
         string line = module + "," + status + "," + TimeToString(TimeCurrent());
         FileWrite(handle, line);
         FileClose(handle);
         
         AuditLog("Status exportado: " + module + " -> " + status, LOG_LEVEL_DEBUG);
      }
      else
      {
         LogError("Erro ao exportar status para: " + module);
      }
   }
};

#endif // AUDIT_ENTANGLEMENT_BRIDGE_MQH 