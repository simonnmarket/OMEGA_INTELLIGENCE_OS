//+------------------------------------------------------------------+
//|                                           AuditEntanglementPanel.mq5 |
//|             Painel Visual de Emaranhamento da Auditoria Numeia     |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "../../Utils/Log.mqh"
#include <Graphics/ChartObjects/ChartObjectsTxtControls.mqh>

input int X_Pos = 20;
input int Y_Pos = 20;
input int Line_Height = 20;
input color Color_OK = clrLimeGreen;
input color Color_Fail = clrRed;
input color Color_Warn = clrOrange;
input ENUM_TIMEFRAMES tf = PERIOD_CURRENT;

string fileName = "entanglement_status.dat";

// Função para criar painel com estatísticas
void CreateStatisticsPanel(int ok_count, int fail_count, int total_modules)
{
   string stats_name = "stats_panel";
   string stats_text = StringFormat("Total: %d | OK: %d | FALHA: %d", 
                                   total_modules, ok_count, fail_count);
   
   if(ObjectCreate(0, stats_name, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, stats_name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, stats_name, OBJPROP_XDISTANCE, X_Pos);
      ObjectSetInteger(0, stats_name, OBJPROP_YDISTANCE, Y_Pos - 30);
      ObjectSetInteger(0, stats_name, OBJPROP_COLOR, clrLightBlue);
      ObjectSetInteger(0, stats_name, OBJPROP_FONTSIZE, 10);
      ObjectSetString(0, stats_name, OBJPROP_TEXT, stats_text);
   }
}

// Função para criar título do painel
void CreatePanelTitle()
{
   string title_name = "panel_title";
   string title_text = "Quantum Entanglement Audit Panel";
   
   if(ObjectCreate(0, title_name, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, title_name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, title_name, OBJPROP_XDISTANCE, X_Pos);
      ObjectSetInteger(0, title_name, OBJPROP_YDISTANCE, Y_Pos - 50);
      ObjectSetInteger(0, title_name, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, title_name, OBJPROP_FONTSIZE, 14);
      ObjectSetString(0, title_name, OBJPROP_TEXT, title_text);
   }
}

// Função para verificar integridade do arquivo
bool ValidateStatusFile()
{
   if(!FileIsExist(fileName))
   {
      LogWarning("Arquivo de status não encontrado: " + fileName);
      return false;
   }

   int handle = FileOpen(fileName, FILE_READ | FILE_TXT | FILE_COMMON);
   if(handle == INVALID_HANDLE)
   {
      LogError("Erro ao abrir arquivo para validação: " + fileName);
      return false;
   }

   int lineCount = 0;
   while(!FileIsEnding(handle))
   {
      string line = FileReadString(handle);
      if(StringLen(line) > 0)
         lineCount++;
   }
   FileClose(handle);
   
   AuditLog("Arquivo validado - " + IntegerToString(lineCount) + " linhas", LOG_LEVEL_DEBUG);
   return (lineCount > 0);
}

// Função para limpar painel
void ClearPanel()
{
   ObjectsDeleteAll(0, "ent_panel_");
   ObjectsDeleteAll(0, "stats_panel");
   ObjectsDeleteAll(0, "panel_title");
   AuditLog("Painel de auditoria limpo", LOG_LEVEL_DEBUG);
}

int OnInit()
{
   AuditLog("[AuditEntanglementPanel] Iniciando painel de auditoria...", LOG_LEVEL_INFO);
   
   // Validar arquivo antes de processar
   if(!ValidateStatusFile())
   {
      LogError("Arquivo de status inválido ou não encontrado");
      return(INIT_FAILED);
   }
   
   // Limpar painel anterior
   ClearPanel();
   
   // Criar título
   CreatePanelTitle();
   
   string moduleInfo;
   int lineIndex = 0;
   int ok_count = 0;
   int fail_count = 0;

   ResetLastError();
   int fileHandle = FileOpen(fileName, FILE_READ | FILE_TXT | FILE_COMMON);

   if(fileHandle == INVALID_HANDLE)
   {
      LogError("Falha ao abrir arquivo de status: " + fileName);
      return(INIT_FAILED);
   }

   while(!FileIsEnding(fileHandle))
   {
      moduleInfo = FileReadString(fileHandle);
      if(StringLen(moduleInfo) > 0)
      {
         // Melhorar detecção de status
         string status = "FALHA"; // Padrão
         if(StringFind(moduleInfo, "OK") >= 0)
            status = "OK";
         else if(StringFind(moduleInfo, "WARN") >= 0)
            status = "WARN";
         
         color statusColor = Color_Fail; // Padrão
         if(status == "OK")
            statusColor = Color_OK;
         else if(status == "WARN")
            statusColor = Color_Warn;

         // Contar por status
         if(status == "OK")
            ok_count++;
         else if(status == "WARN")
            fail_count++; // Contar como falha para estatísticas
         else
            fail_count++;

         string name = "status_label_" + (string)lineIndex;
         string fullText = "[Módulo] " + moduleInfo;

         if(!ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0))
         {
            LogError("Erro ao criar label: " + name);
            continue;
         }

         ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, name, OBJPROP_XDISTANCE, X_Pos);
         ObjectSetInteger(0, name, OBJPROP_YDISTANCE, Y_Pos + lineIndex * Line_Height);
         ObjectSetInteger(0, name, OBJPROP_COLOR, statusColor);
         ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 12);
         ObjectSetString(0, name, OBJPROP_TEXT, fullText);

         lineIndex++;
      }
   }

   FileClose(fileHandle);
   
   // Criar painel de estatísticas
   CreateStatisticsPanel(ok_count, fail_count, lineIndex);
   
   AuditLog("Painel de auditoria criado com sucesso - OK: " + IntegerToString(ok_count) + 
            ", FALHA: " + IntegerToString(fail_count) + 
            ", Total: " + IntegerToString(lineIndex), LOG_LEVEL_INFO);
   
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   ClearPanel();
   AuditLog("[AuditEntanglementPanel] Script encerrado", LOG_LEVEL_INFO);
} 