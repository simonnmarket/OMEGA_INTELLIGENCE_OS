//+------------------------------------------------------------------+
//|                                           EXECUTAR_ARQUITETURA.mq5 |
//|                    Script para Executar Arquitetura Visual         |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include "Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Função principal                                                  |
//+------------------------------------------------------------------+
void OnStart()
{
   AuditLog("🚀 INICIANDO EXECUÇÃO DO SISTEMA DE ARQUITETURA VISUAL", LOG_LEVEL_INFO);
   
   // Mostrar localização dos arquivos
   string currentPath = TerminalInfoString(TERMINAL_DATA_PATH);
   string scriptPath = currentPath + "\\MQL5\\Scripts\\Numeia\\ArquiteturaVisual.mq5";
   
   AuditLog("📁 Localização do arquivo: " + scriptPath, LOG_LEVEL_INFO);
   AuditLog("💡 Para executar: MetaTrader 5 > Navegador > Scripts > Numeia > ArquiteturaVisual", LOG_LEVEL_INFO);
   
   // Criar painel de instruções
   CreateInstructionsPanel();
   
   // Verificar se o arquivo existe
   if(FileIsExist("ArquiteturaVisual.mq5"))
   {
      AuditLog("✅ Arquivo ArquiteturaVisual.mq5 encontrado!", LOG_LEVEL_INFO);
      AuditLog("🎯 Execute o arquivo ArquiteturaVisual.mq5 no MetaTrader 5", LOG_LEVEL_INFO);
   }
   else
   {
      LogError("❌ Arquivo ArquiteturaVisual.mq5 não encontrado!");
      AuditLog("🔍 Verifique se o arquivo está na pasta correta", LOG_LEVEL_ERROR);
   }
   
   // Verificar dependências
   CheckDependencies();
   
   AuditLog("📋 INSTRUÇÕES DE EXECUÇÃO:", LOG_LEVEL_INFO);
   AuditLog("1. Abra o MetaTrader 5", LOG_LEVEL_INFO);
   AuditLog("2. Vá para Navegador > Scripts", LOG_LEVEL_INFO);
   AuditLog("3. Encontre a pasta 'Numeia'", LOG_LEVEL_INFO);
   AuditLog("4. Clique duas vezes em 'ArquiteturaVisual'", LOG_LEVEL_INFO);
   AuditLog("5. Visualize o painel no gráfico", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Criar painel de instruções                                        |
//+------------------------------------------------------------------+
void CreateInstructionsPanel()
{
   // Painel principal
   string panelName = "exec_instructions_panel";
   if(ObjectCreate(0, panelName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, panelName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, panelName, OBJPROP_XDISTANCE, 20);
      ObjectSetInteger(0, panelName, OBJPROP_YDISTANCE, 50);
      ObjectSetInteger(0, panelName, OBJPROP_XSIZE, 500);
      ObjectSetInteger(0, panelName, OBJPROP_YSIZE, 300);
      ObjectSetInteger(0, panelName, OBJPROP_BGCOLOR, clrDarkBlue);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_COLOR, clrWhite);
      ObjectSetInteger(0, panelName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, panelName, OBJPROP_BACK, false);
   }
   
   // Título
   string titleName = "exec_title";
   if(ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 60);
      ObjectSetInteger(0, titleName, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 16);
      ObjectSetString(0, titleName, OBJPROP_TEXT, "🚀 COMO EXECUTAR ARQUITETURA VISUAL");
   }
   
   // Instrução 1
   string inst1 = "exec_inst1";
   if(ObjectCreate(0, inst1, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, inst1, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, inst1, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, inst1, OBJPROP_YDISTANCE, 90);
      ObjectSetInteger(0, inst1, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, inst1, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, inst1, OBJPROP_TEXT, "1️⃣ Abra o MetaTrader 5");
   }
   
   // Instrução 2
   string inst2 = "exec_inst2";
   if(ObjectCreate(0, inst2, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, inst2, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, inst2, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, inst2, OBJPROP_YDISTANCE, 110);
      ObjectSetInteger(0, inst2, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, inst2, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, inst2, OBJPROP_TEXT, "2️⃣ Vá para Navegador > Scripts");
   }
   
   // Instrução 3
   string inst3 = "exec_inst3";
   if(ObjectCreate(0, inst3, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, inst3, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, inst3, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, inst3, OBJPROP_YDISTANCE, 130);
      ObjectSetInteger(0, inst3, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, inst3, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, inst3, OBJPROP_TEXT, "3️⃣ Encontre a pasta 'Numeia'");
   }
   
   // Instrução 4
   string inst4 = "exec_inst4";
   if(ObjectCreate(0, inst4, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, inst4, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, inst4, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, inst4, OBJPROP_YDISTANCE, 150);
      ObjectSetInteger(0, inst4, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, inst4, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, inst4, OBJPROP_TEXT, "4️⃣ Clique duas vezes em 'ArquiteturaVisual'");
   }
   
   // Instrução 5
   string inst5 = "exec_inst5";
   if(ObjectCreate(0, inst5, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, inst5, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, inst5, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, inst5, OBJPROP_YDISTANCE, 170);
      ObjectSetInteger(0, inst5, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, inst5, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, inst5, OBJPROP_TEXT, "5️⃣ Visualize o painel no gráfico");
   }
   
   // Status
   string status = "exec_status";
   if(ObjectCreate(0, status, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, status, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, status, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, status, OBJPROP_YDISTANCE, 200);
      ObjectSetInteger(0, status, OBJPROP_COLOR, clrLimeGreen);
      ObjectSetInteger(0, status, OBJPROP_FONTSIZE, 12);
      ObjectSetString(0, status, OBJPROP_TEXT, "✅ Sistema pronto para execução!");
   }
   
   // Caminho do arquivo
   string filepath = "exec_filepath";
   if(ObjectCreate(0, filepath, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, filepath, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, filepath, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, filepath, OBJPROP_YDISTANCE, 230);
      ObjectSetInteger(0, filepath, OBJPROP_COLOR, clrWhite);
      ObjectSetInteger(0, filepath, OBJPROP_FONTSIZE, 10);
      ObjectSetString(0, filepath, OBJPROP_TEXT, "📁 Arquivo: ArquiteturaVisual.mq5");
   }
}

//+------------------------------------------------------------------+
//| Verificar dependências                                            |
//+------------------------------------------------------------------+
void CheckDependencies()
{
   AuditLog("🔍 Verificando dependências...", LOG_LEVEL_INFO);
   
   string deps[] = {
      "Utils/Log.mqh",
      "Core/CoreBrainManager.mqh",
      "Include/ExecutionLogic/TradeExecutor.mqh",
      "Auditor/AuditManager.mqh"
   };
   
   int found = 0;
   for(int i = 0; i < ArraySize(deps); i++)
   {
      if(FileIsExist(deps[i]))
      {
         found++;
         AuditLog("✅ " + deps[i], LOG_LEVEL_INFO);
      }
      else
      {
         LogError("❌ " + deps[i]);
      }
   }
   
   AuditLog("📊 Dependências: " + IntegerToString(found) + "/" + IntegerToString(ArraySize(deps)), LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Função de limpeza                                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, "exec_");
   AuditLog("🧹 Instruções de execução encerradas", LOG_LEVEL_INFO);
} 