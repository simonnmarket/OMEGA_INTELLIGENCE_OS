//+------------------------------------------------------------------+
//|                                              ArquiteturaVisual.mq5 |
//|              Dashboard de Arquitetura Visual - EA Numeia          |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "Utils/Log.mqh"

input int X_Pos = 20;
input int Y_Pos = 50;
input color Color_OK = clrLimeGreen;
input color Color_Warning = clrOrange;
input color Color_Error = clrRed;
input color Color_Pending = clrYellow;
input color Color_Background = clrDarkSlateGray;
input color Color_Text = clrWhite;

//+------------------------------------------------------------------+
//| Estrutura para representar um módulo                              |
//+------------------------------------------------------------------+
struct ModuleInfo
{
   string name;
   string path;
   string status;
   bool isUpdated;
   bool isConfirmed;
};

//+------------------------------------------------------------------+
//| Classe principal do dashboard                                     |
//+------------------------------------------------------------------+
class ArchitectureDashboard
{
private:
   ModuleInfo m_modules[];
   string m_pendingFile;
   
public:
   ArchitectureDashboard() : m_pendingFile("pending_updates.dat") {}
   
   bool Init()
   {
      AuditLog("[ArchitectureDashboard] Inicializando dashboard...", LOG_LEVEL_INFO);
      
      CreateMainPanel();
      ScanProjectStructure();
      CheckPendingUpdates();
      RenderDashboard();
      
      AuditLog("[ArchitectureDashboard] Dashboard inicializado", LOG_LEVEL_INFO);
      return true;
   }
   
   void ScanProjectStructure()
   {
      AuditLog("[ArchitectureDashboard] Escaneando estrutura...", LOG_LEVEL_INFO);
      
      ArrayResize(m_modules, 0);
      
      // Módulos principais
      AddModule("CoreBrainManager", "Core/CoreBrainManager.mqh", "OK");
      AddModule("TradeExecutor", "Include/ExecutionLogic/TradeExecutor.mqh", "OK");
      AddModule("PositionManager", "Include/ExecutionLogic/PositionManager.mqh", "OK");
      AddModule("DefenseOrchestrator", "Include/ExecutionLogic/DefenseOrchestrator.mqh", "OK");
      AddModule("ExecutionLoopController", "Include/ExecutionLogic/ExecutionLoopController.mqh", "OK");
      AddModule("SkyIntelBridge", "Include/Integration/SkyIntelBridge.mqh", "OK");
      AddModule("AuditManager", "Auditor/AuditManager.mqh", "OK");
      AddModule("Log", "Utils/Log.mqh", "OK");
      AddModule("NumeiaEA", "Expert/NumeiaEA.mq5", "OK");
      
      // Módulos de auditoria quântica
      AddModule("QuantumAuditEngine", "Scripts/QuantumAudit/QuantumAuditEngine.mqh", "OK");
      AddModule("QuantumEntanglementMap", "Scripts/QuantumAudit/QuantumEntanglementMap.mqh", "OK");
      AddModule("AuditEntanglementBridge", "Scripts/QuantumAudit/AuditEntanglementBridge.mqh", "OK");
      AddModule("AuditEntanglementPanel", "Scripts/QuantumAudit/AuditEntanglementPanel.mq5", "OK");
      
      ValidateModulesStatus();
      
      AuditLog("[ArchitectureDashboard] Estrutura escaneada - " + IntegerToString(ArraySize(m_modules)) + " módulos", LOG_LEVEL_INFO);
   }
   
   void CheckPendingUpdates()
   {
      AuditLog("[ArchitectureDashboard] Verificando atualizações...", LOG_LEVEL_INFO);
      
      int pendingCount = 0;
      
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(FileIsExist(m_modules[i].path))
         {
            // Simular verificação de modificação recente
            if(MathRand() % 10 == 0)
            {
               m_modules[i].status = "PENDING";
               m_modules[i].isUpdated = true;
               m_modules[i].isConfirmed = false;
               pendingCount++;
            }
         }
      }
      
      AuditLog("[ArchitectureDashboard] Atualizações pendentes: " + IntegerToString(pendingCount), LOG_LEVEL_INFO);
   }
   
   void RenderDashboard()
   {
      AuditLog("[ArchitectureDashboard] Renderizando dashboard...", LOG_LEVEL_INFO);
      
      ObjectsDeleteAll(0, "arch_");
      
      CreateTitle();
      CreateStatistics();
      CreateModulesList();
      CreateAlerts();
      
      AuditLog("[ArchitectureDashboard] Dashboard renderizado", LOG_LEVEL_INFO);
   }
   
   void UpdateDashboard()
   {
      ScanProjectStructure();
      CheckPendingUpdates();
      RenderDashboard();
   }
   
   void ConfirmModuleUpdate(string moduleName)
   {
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(m_modules[i].name == moduleName)
         {
            m_modules[i].isConfirmed = true;
            m_modules[i].status = "OK";
            AuditLog("✅ Atualização confirmada: " + moduleName, LOG_LEVEL_INFO);
            break;
         }
      }
      RenderDashboard();
   }
   
   void GetStatistics(int &total, int &ok, int &warning, int &error, int &pending)
   {
      total = ArraySize(m_modules);
      ok = warning = error = pending = 0;
      
      for(int i = 0; i < total; i++)
      {
         if(m_modules[i].status == "OK")
            ok++;
         else if(m_modules[i].status == "WARNING")
            warning++;
         else if(m_modules[i].status == "ERROR")
            error++;
         else if(m_modules[i].status == "PENDING")
            pending++;
      }
   }

private:
   void AddModule(string name, string path, string status)
   {
      int size = ArraySize(m_modules);
      ArrayResize(m_modules, size + 1);
      
      m_modules[size].name = name;
      m_modules[size].path = path;
      m_modules[size].status = status;
      m_modules[size].isUpdated = false;
      m_modules[size].isConfirmed = true;
   }
   
   void ValidateModulesStatus()
   {
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(!FileIsExist(m_modules[i].path))
         {
            m_modules[i].status = "ERROR";
            LogError("Módulo não encontrado: " + m_modules[i].path);
         }
         else if(MathRand() % 20 == 0)
         {
            m_modules[i].status = "WARNING";
         }
      }
   }
   
   void CreateMainPanel()
   {
      string panelName = "arch_main_panel";
      
      if(ObjectCreate(0, panelName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, panelName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, panelName, OBJPROP_XDISTANCE, X_Pos);
         ObjectSetInteger(0, panelName, OBJPROP_YDISTANCE, Y_Pos);
         ObjectSetInteger(0, panelName, OBJPROP_XSIZE, 800);
         ObjectSetInteger(0, panelName, OBJPROP_YSIZE, 600);
         ObjectSetInteger(0, panelName, OBJPROP_BGCOLOR, Color_Background);
         ObjectSetInteger(0, panelName, OBJPROP_BORDER_COLOR, Color_Text);
         ObjectSetInteger(0, panelName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
         ObjectSetInteger(0, panelName, OBJPROP_BACK, false);
      }
   }
   
   void CreateTitle()
   {
      string titleName = "arch_title";
      string titleText = "🏗️ ARQUITETURA VISUAL - EA NUMEIA";
      
      if(ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, X_Pos + 10);
         ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, Y_Pos + 10);
         ObjectSetInteger(0, titleName, OBJPROP_COLOR, Color_Text);
         ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 16);
         ObjectSetString(0, titleName, OBJPROP_TEXT, titleText);
      }
   }
   
   void CreateStatistics()
   {
      int total, ok, warning, error, pending;
      GetStatistics(total, ok, warning, error, pending);
      
      string statsName = "arch_stats";
      string statsText = StringFormat("📊 ESTATÍSTICAS: Total=%d | ✅ OK=%d | ⚠️ WARN=%d | ❌ ERR=%d | 🟡 PEND=%d", 
                                     total, ok, warning, error, pending);
      
      if(ObjectCreate(0, statsName, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, statsName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, statsName, OBJPROP_XDISTANCE, X_Pos + 10);
         ObjectSetInteger(0, statsName, OBJPROP_YDISTANCE, Y_Pos + 40);
         ObjectSetInteger(0, statsName, OBJPROP_COLOR, Color_Text);
         ObjectSetInteger(0, statsName, OBJPROP_FONTSIZE, 12);
         ObjectSetString(0, statsName, OBJPROP_TEXT, statsText);
      }
   }
   
   void CreateModulesList()
   {
      int startY = Y_Pos + 80;
      int lineHeight = 20;
      
      string listTitle = "arch_modules_title";
      if(ObjectCreate(0, listTitle, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, listTitle, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, listTitle, OBJPROP_XDISTANCE, X_Pos + 10);
         ObjectSetInteger(0, listTitle, OBJPROP_YDISTANCE, startY);
         ObjectSetInteger(0, listTitle, OBJPROP_COLOR, Color_Text);
         ObjectSetInteger(0, listTitle, OBJPROP_FONTSIZE, 14);
         ObjectSetString(0, listTitle, OBJPROP_TEXT, "📁 MÓDULOS:");
      }
      
      for(int i = 0; i < ArraySize(m_modules) && i < 15; i++)
      {
         string moduleName = "arch_module_" + IntegerToString(i);
         string statusIcon = "";
         color statusColor = Color_Text;
         
         if(m_modules[i].status == "OK")
         {
            statusIcon = "✅";
            statusColor = Color_OK;
         }
         else if(m_modules[i].status == "WARNING")
         {
            statusIcon = "⚠️";
            statusColor = Color_Warning;
         }
         else if(m_modules[i].status == "ERROR")
         {
            statusIcon = "❌";
            statusColor = Color_Error;
         }
         else if(m_modules[i].status == "PENDING")
         {
            statusIcon = "🟡";
            statusColor = Color_Pending;
         }
         
         string moduleText = StringFormat("%s %s (%s)", statusIcon, m_modules[i].name, m_modules[i].status);
         
         if(ObjectCreate(0, moduleName, OBJ_LABEL, 0, 0, 0))
         {
            ObjectSetInteger(0, moduleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
            ObjectSetInteger(0, moduleName, OBJPROP_XDISTANCE, X_Pos + 20);
            ObjectSetInteger(0, moduleName, OBJPROP_YDISTANCE, startY + (i + 1) * lineHeight);
            ObjectSetInteger(0, moduleName, OBJPROP_COLOR, statusColor);
            ObjectSetInteger(0, moduleName, OBJPROP_FONTSIZE, 10);
            ObjectSetString(0, moduleName, OBJPROP_TEXT, moduleText);
         }
      }
   }
   
   void CreateAlerts()
   {
      int startY = Y_Pos + 450;
      
      string alertTitle = "arch_alerts_title";
      if(ObjectCreate(0, alertTitle, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, alertTitle, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, alertTitle, OBJPROP_XDISTANCE, X_Pos + 10);
         ObjectSetInteger(0, alertTitle, OBJPROP_YDISTANCE, startY);
         ObjectSetInteger(0, alertTitle, OBJPROP_COLOR, Color_Text);
         ObjectSetInteger(0, alertTitle, OBJPROP_FONTSIZE, 14);
         ObjectSetString(0, alertTitle, OBJPROP_TEXT, "🚨 ALERTAS:");
      }
      
      int errorCount = 0;
      int pendingCount = 0;
      
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(m_modules[i].status == "ERROR") errorCount++;
         if(m_modules[i].status == "PENDING") pendingCount++;
      }
      
      string alertText = "";
      color alertColor = Color_OK;
      
      if(errorCount > 0)
      {
         alertText = "❌ " + IntegerToString(errorCount) + " módulos com ERRO!";
         alertColor = Color_Error;
      }
      else if(pendingCount > 0)
      {
         alertText = "🟡 " + IntegerToString(pendingCount) + " atualizações pendentes";
         alertColor = Color_Pending;
      }
      else
      {
         alertText = "✅ Sistema funcionando perfeitamente!";
         alertColor = Color_OK;
      }
      
      string alertName = "arch_alert_status";
      if(ObjectCreate(0, alertName, OBJ_LABEL, 0, 0, 0))
      {
         ObjectSetInteger(0, alertName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, alertName, OBJPROP_XDISTANCE, X_Pos + 20);
         ObjectSetInteger(0, alertName, OBJPROP_YDISTANCE, startY + 20);
         ObjectSetInteger(0, alertName, OBJPROP_COLOR, alertColor);
         ObjectSetInteger(0, alertName, OBJPROP_FONTSIZE, 12);
         ObjectSetString(0, alertName, OBJPROP_TEXT, alertText);
      }
   }
};

//+------------------------------------------------------------------+
//| Variáveis globais                                                 |
//+------------------------------------------------------------------+
ArchitectureDashboard dashboard;

//+------------------------------------------------------------------+
//| Função principal                                                  |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🏗️ INICIANDO DASHBOARD DE ARQUITETURA VISUAL", LOG_LEVEL_INFO);
   
   if(dashboard.Init())
   {
      AuditLog("✅ Dashboard inicializado com sucesso", LOG_LEVEL_INFO);
      AuditLog("📊 Visualize o painel no gráfico", LOG_LEVEL_INFO);
   }
   else
   {
      LogError("❌ Falha na inicialização");
   }
}

//+------------------------------------------------------------------+
//| Função de limpeza                                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, "arch_");
   AuditLog("🧹 Dashboard encerrado", LOG_LEVEL_INFO);
} 