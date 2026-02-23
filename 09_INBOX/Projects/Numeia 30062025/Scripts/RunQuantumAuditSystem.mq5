//+------------------------------------------------------------------+
//|                                        RunQuantumAuditSystem.mq5  |
//|              Execução Automática do Sistema de Auditoria Quântica |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../Utils/Log.mqh"
#include "../Scripts/QuantumAudit/AuditEntanglementBridge.mqh"

input bool Run_Full_Audit = true;
input bool Run_Continuous_Mode = false;
input int Continuous_Interval_Seconds = 30;
input bool Show_Visual_Panel = true;
input bool Generate_Report = true;

//+------------------------------------------------------------------+
//| Função principal do script                                       |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("[RunQuantumAuditSystem] 🚀 INICIANDO SISTEMA DE AUDITORIA QUÂNTICA", LOG_LEVEL_INFO);
   AuditLog("=" * 60, LOG_LEVEL_INFO);
   
   // Executar auditoria completa
   if(Run_Full_Audit)
   {
      AuditLog("[RunQuantumAuditSystem] Executando auditoria completa...", LOG_LEVEL_INFO);
      
      AuditEntanglementBridge bridge;
      if(bridge.Init())
      {
         bridge.RunFullAudit();
         
         // Obter estatísticas
         int total, ok, fail, warn;
         bridge.GetAuditStatistics(total, ok, fail, warn);
         
         // Exibir resultados
         DisplayAuditResults(total, ok, fail, warn);
         
         // Gerar relatório se solicitado
         if(Generate_Report)
         {
            GenerateAuditReport(total, ok, fail, warn);
         }
         
         // Mostrar painel visual se solicitado
         if(Show_Visual_Panel)
         {
            ShowVisualPanel();
         }
      }
      else
      {
         LogError("Falha na inicialização do sistema de auditoria");
         return;
      }
   }
   
   // Modo contínuo
   if(Run_Continuous_Mode)
   {
      AuditLog("[RunQuantumAuditSystem] Modo contínuo ativado - intervalo: " + 
               IntegerToString(Continuous_Interval_Seconds) + " segundos", LOG_LEVEL_INFO);
      
      // Aqui seria implementado um loop contínuo
      // Por questões de segurança do MQL5, isso seria feito no EA principal
      AuditLog("Modo contínuo configurado - será executado pelo EA principal", LOG_LEVEL_INFO);
   }
   
   AuditLog("=" * 60, LOG_LEVEL_INFO);
   AuditLog("[RunQuantumAuditSystem] ✅ SISTEMA DE AUDITORIA QUÂNTICA CONCLUÍDO", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Exibir resultados da auditoria                                   |
//+------------------------------------------------------------------+
void DisplayAuditResults(int total, int ok, int fail, int warn)
{
   AuditLog("=== RESULTADOS DA AUDITORIA QUÂNTICA ===", LOG_LEVEL_INFO);
   AuditLog("📊 Total de módulos auditados: " + IntegerToString(total), LOG_LEVEL_INFO);
   AuditLog("✅ Módulos OK: " + IntegerToString(ok), LOG_LEVEL_INFO);
   AuditLog("❌ Módulos com FALHA: " + IntegerToString(fail), LOG_LEVEL_INFO);
   AuditLog("⚠️ Módulos com WARN: " + IntegerToString(warn), LOG_LEVEL_INFO);
   
   // Calcular percentuais
   if(total > 0)
   {
      double okPercent = (double)ok / total * 100.0;
      double failPercent = (double)fail / total * 100.0;
      double warnPercent = (double)warn / total * 100.0;
      
      AuditLog("📈 Percentuais:", LOG_LEVEL_INFO);
      AuditLog("   ✅ OK: " + DoubleToString(okPercent, 1) + "%", LOG_LEVEL_INFO);
      AuditLog("   ❌ FALHA: " + DoubleToString(failPercent, 1) + "%", LOG_LEVEL_INFO);
      AuditLog("   ⚠️ WARN: " + DoubleToString(warnPercent, 1) + "%", LOG_LEVEL_INFO);
   }
   
   // Status geral
   if(fail == 0 && warn == 0)
   {
      AuditLog("🎉 EXCELENTE! Todos os módulos estão funcionando perfeitamente!", LOG_LEVEL_INFO);
   }
   else if(fail == 0)
   {
      AuditLog("👍 BOM! Sistema funcionando com alguns avisos menores", LOG_LEVEL_INFO);
   }
   else
   {
      LogWarning("⚠️ ATENÇÃO! Problemas detectados no sistema");
   }
}

//+------------------------------------------------------------------+
//| Gerar relatório de auditoria                                     |
//+------------------------------------------------------------------+
void GenerateAuditReport(int total, int ok, int fail, int warn)
{
   AuditLog("[RunQuantumAuditSystem] Gerando relatório de auditoria...", LOG_LEVEL_INFO);
   
   string reportFileName = "quantum_audit_report_" + TimeToString(TimeCurrent(), TIME_DATE) + ".txt";
   
   int handle = FileOpen(reportFileName, FILE_WRITE | FILE_TXT | FILE_COMMON);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, "=== RELATÓRIO DE AUDITORIA QUÂNTICA NUMEIA ===");
      FileWrite(handle, "Data/Hora: " + TimeToString(TimeCurrent()));
      FileWrite(handle, "");
      FileWrite(handle, "RESUMO EXECUTIVO:");
      FileWrite(handle, "- Total de módulos auditados: " + IntegerToString(total));
      FileWrite(handle, "- Módulos OK: " + IntegerToString(ok));
      FileWrite(handle, "- Módulos com FALHA: " + IntegerToString(fail));
      FileWrite(handle, "- Módulos com WARN: " + IntegerToString(warn));
      FileWrite(handle, "");
      
      if(total > 0)
      {
         double okPercent = (double)ok / total * 100.0;
         double failPercent = (double)fail / total * 100.0;
         double warnPercent = (double)warn / total * 100.0;
         
         FileWrite(handle, "PERCENTUAIS:");
         FileWrite(handle, "- OK: " + DoubleToString(okPercent, 1) + "%");
         FileWrite(handle, "- FALHA: " + DoubleToString(failPercent, 1) + "%");
         FileWrite(handle, "- WARN: " + DoubleToString(warnPercent, 1) + "%");
         FileWrite(handle, "");
      }
      
      // Status de cada módulo
      if(FileIsExist("entanglement_status.dat"))
      {
         FileWrite(handle, "DETALHES POR MÓDULO:");
         int statusHandle = FileOpen("entanglement_status.dat", FILE_READ | FILE_TXT | FILE_COMMON);
         if(statusHandle != INVALID_HANDLE)
         {
            while(!FileIsEnding(statusHandle))
            {
               string line = FileReadString(statusHandle);
               if(StringLen(line) > 0)
               {
                  FileWrite(handle, "- " + line);
               }
            }
            FileClose(statusHandle);
         }
      }
      
      FileWrite(handle, "");
      FileWrite(handle, "RECOMENDAÇÕES:");
      if(fail == 0 && warn == 0)
      {
         FileWrite(handle, "- Sistema funcionando perfeitamente");
         FileWrite(handle, "- Manter monitoramento regular");
      }
      else if(fail == 0)
      {
         FileWrite(handle, "- Revisar módulos com WARN");
         FileWrite(handle, "- Considerar otimizações");
      }
      else
      {
         FileWrite(handle, "- CORRIGIR módulos com FALHA imediatamente");
         FileWrite(handle, "- Revisar dependências");
         FileWrite(handle, "- Verificar includes e paths");
      }
      
      FileClose(handle);
      AuditLog("Relatório gerado: " + reportFileName, LOG_LEVEL_INFO);
   }
   else
   {
      LogError("Erro ao gerar relatório: " + reportFileName);
   }
}

//+------------------------------------------------------------------+
//| Mostrar painel visual                                            |
//+------------------------------------------------------------------+
void ShowVisualPanel()
{
   AuditLog("[RunQuantumAuditSystem] Ativando painel visual...", LOG_LEVEL_INFO);
   
   // Aqui seria chamado o script do painel visual
   // Por questões de segurança do MQL5, isso seria feito manualmente
   AuditLog("Para visualizar o painel, execute: Scripts/QuantumAudit/AuditEntanglementPanel.mq5", LOG_LEVEL_INFO);
   AuditLog("Ou adicione o painel ao EA principal", LOG_LEVEL_INFO);
} 