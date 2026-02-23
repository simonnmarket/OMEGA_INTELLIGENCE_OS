//+------------------------------------------------------------------+
//|                                        TesteAuditoriaSimples.mq5  |
//|              Teste Direto da Auditoria Quântica                  |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Função principal do script                                       |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🚨 TESTE DIRETO DA AUDITORIA QUÂNTICA", LOG_LEVEL_INFO);
   AuditLog("=" * 50, LOG_LEVEL_INFO);
   
   // Teste 1: Verificar se os arquivos da auditoria existem
   AuditLog("Teste 1: Verificando arquivos da auditoria...", LOG_LEVEL_INFO);
   
   string auditFiles[] = {
      "Scripts/QuantumAudit/QuantumAuditEngine.mqh",
      "Scripts/QuantumAudit/QuantumEntanglementMap.mqh", 
      "Scripts/QuantumAudit/AuditEntanglementBridge.mqh",
      "Scripts/QuantumAudit/AuditEntanglementPanel.mq5"
   };
   
   bool allFilesExist = true;
   for(int i = 0; i < ArraySize(auditFiles); i++)
   {
      if(FileIsExist(auditFiles[i]))
      {
         AuditLog("✅ " + auditFiles[i] + " - EXISTE", LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ " + auditFiles[i] + " - NÃO EXISTE");
         allFilesExist = false;
      }
   }
   
   if(!allFilesExist)
   {
      LogError("FALHA: Arquivos da auditoria não encontrados!");
      return;
   }
   
   // Teste 2: Verificar se o CoreBrainManager pode incluir a auditoria
   AuditLog("Teste 2: Verificando integração com CoreBrainManager...", LOG_LEVEL_INFO);
   
   if(FileIsExist("Core/CoreBrainManager.mqh"))
   {
      AuditLog("✅ CoreBrainManager.mqh - EXISTE", LOG_LEVEL_INFO);
   }
   else
   {
      LogError("❌ CoreBrainManager.mqh - NÃO EXISTE");
      return;
   }
   
   // Teste 3: Tentar executar a auditoria diretamente
   AuditLog("Teste 3: Executando auditoria diretamente...", LOG_LEVEL_INFO);
   
   try
   {
      // Incluir e testar o bridge
      #include "../Scripts/QuantumAudit/AuditEntanglementBridge.mqh"
      
      AuditEntanglementBridge bridge;
      if(bridge.Init())
      {
         AuditLog("✅ Bridge inicializado com sucesso", LOG_LEVEL_INFO);
         
         bridge.RunFullAudit();
         AuditLog("✅ Auditoria executada", LOG_LEVEL_INFO);
         
         // Verificar se o arquivo de resultados foi criado
         if(FileIsExist("entanglement_status.dat"))
         {
            AuditLog("✅ Arquivo de resultados criado", LOG_LEVEL_INFO);
            
            // Ler e mostrar resultados
            int handle = FileOpen("entanglement_status.dat", FILE_READ | FILE_TXT | FILE_COMMON);
            if(handle != INVALID_HANDLE)
            {
               AuditLog("📊 RESULTADOS DA AUDITORIA:", LOG_LEVEL_INFO);
               while(!FileIsEnding(handle))
               {
                  string line = FileReadString(handle);
                  if(StringLen(line) > 0)
                  {
                     AuditLog("   " + line, LOG_LEVEL_INFO);
                  }
               }
               FileClose(handle);
            }
         }
         else
         {
            LogError("❌ Arquivo de resultados não foi criado");
         }
      }
      else
      {
         LogError("❌ Falha na inicialização do bridge");
      }
   }
   catch(...)
   {
      LogError("❌ ERRO durante execução da auditoria");
   }
   
   AuditLog("=" * 50, LOG_LEVEL_INFO);
   AuditLog("🎯 TESTE CONCLUÍDO", LOG_LEVEL_INFO);
} 