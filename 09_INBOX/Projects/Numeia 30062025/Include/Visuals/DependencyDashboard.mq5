//+------------------------------------------------------------------+
//|                                        DependencyDashboard.mq5   |
//|                    Painel de Dependências - EA Numeia           |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots   0

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include "../../Core/ModuleRegistry.mqh"

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
input bool   SHOW_DASHBOARD = true;       // Mostrar painel
input int    UPDATE_INTERVAL = 5;         // Intervalo de atualização (segundos)
input bool   SHOW_DEPENDENCIES = true;    // Mostrar dependências
input bool   SHOW_INTEGRATIONS = true;    // Mostrar integrações
input bool   SHOW_STATUS = true;          // Mostrar status
input color  BACKGROUND_COLOR = clrBlack; // Cor de fundo
input color  TEXT_COLOR = clrWhite;       // Cor do texto
input color  ERROR_COLOR = clrRed;        // Cor de erro
input color  WARNING_COLOR = clrOrange;   // Cor de aviso
input color  SUCCESS_COLOR = clrLime;     // Cor de sucesso

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
ModuleRegistry* g_dashboardRegistry = NULL;
datetime g_lastUpdate = 0;
string g_dashboardName = "DependencyDashboard";
int g_dashboardWidth = 400;
int g_dashboardHeight = 600;
int g_lineHeight = 20;
int g_currentLine = 0;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   AuditLog("[DependencyDashboard] Inicializando painel de dependências...", LOG_LEVEL_INFO);
   
   // Inicializar registry
   InitializeModuleRegistry();
   g_dashboardRegistry = GetModuleRegistry();
   
   // Registrar módulos se necessário
   if(!g_dashboardRegistry.ValidateIntegrity()) {
      RegisterDashboardModules();
   }
   
   // Criar painel
   if(SHOW_DASHBOARD) {
      CreateDashboard();
   }
   
   AuditLog("[DependencyDashboard] Painel inicializado com sucesso", LOG_LEVEL_INFO);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   AuditLog("[DependencyDashboard] Encerrando painel de dependências...", LOG_LEVEL_INFO);
   
   // Remover objetos do painel
   ObjectsDeleteAll(0, g_dashboardName);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   // Atualizar painel periodicamente
   datetime currentTime = TimeCurrent();
   if(currentTime - g_lastUpdate >= UPDATE_INTERVAL) {
      UpdateDashboard();
      g_lastUpdate = currentTime;
   }
   
   return(rates_total);
}

//+------------------------------------------------------------------+
//| Criação do Painel                                                |
//+------------------------------------------------------------------+
void CreateDashboard()
{
   AuditLog("[DependencyDashboard] Criando painel visual...", LOG_LEVEL_DEBUG);
   
   // Criar fundo do painel
   string bgName = g_dashboardName + "_Background";
   ObjectCreate(0, bgName, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, bgName, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, bgName, OBJPROP_YDISTANCE, 20);
   ObjectSetInteger(0, bgName, OBJPROP_XSIZE, g_dashboardWidth);
   ObjectSetInteger(0, bgName, OBJPROP_YSIZE, g_dashboardHeight);
   ObjectSetInteger(0, bgName, OBJPROP_BGCOLOR, BACKGROUND_COLOR);
   ObjectSetInteger(0, bgName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, bgName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, bgName, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, bgName, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, bgName, OBJPROP_BACK, false);
   ObjectSetInteger(0, bgName, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, bgName, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, bgName, OBJPROP_HIDDEN, true);
   ObjectSetInteger(0, bgName, OBJPROP_ZORDER, 0);
   
   // Criar título
   string titleName = g_dashboardName + "_Title";
   ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
   ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 30);
   ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 14);
   ObjectSetInteger(0, titleName, OBJPROP_COLOR, SUCCESS_COLOR);
   ObjectSetString(0, titleName, OBJPROP_TEXT, "🔗 DEPENDENCY DASHBOARD");
   ObjectSetString(0, titleName, OBJPROP_FONT, "Arial Bold");
   
   // Criar área de conteúdo
   CreateContentArea();
   
   AuditLog("[DependencyDashboard] Painel criado com sucesso", LOG_LEVEL_DEBUG);
}

//+------------------------------------------------------------------+
//| Criação da Área de Conteúdo                                     |
//+------------------------------------------------------------------+
void CreateContentArea()
{
   g_currentLine = 0;
   
   // Status geral
   if(SHOW_STATUS) {
      AddStatusSection();
   }
   
   // Dependências
   if(SHOW_DEPENDENCIES) {
      AddDependenciesSection();
   }
   
   // Integrações
   if(SHOW_INTEGRATIONS) {
      AddIntegrationsSection();
   }
   
   // Estatísticas
   AddStatisticsSection();
}

//+------------------------------------------------------------------+
//| Adicionar Seção de Status                                        |
//+------------------------------------------------------------------+
void AddStatusSection()
{
   AddSectionTitle("📊 STATUS GERAL");
   
   // Verificar integridade
   bool integrityOK = g_dashboardRegistry.ValidateIntegrity();
   color statusColor = integrityOK ? SUCCESS_COLOR : ERROR_COLOR;
   string statusText = integrityOK ? "✅ SISTEMA INTEGRO" : "❌ PROBLEMAS DETECTADOS";
   
   AddInfoLine("Integridade:", statusText, statusColor);
   AddInfoLine("Última verificação:", TimeToString(TimeCurrent()), TEXT_COLOR);
   AddInfoLine("", "", TEXT_COLOR); // Linha vazia
}

//+------------------------------------------------------------------+
//| Adicionar Seção de Dependências                                  |
//+------------------------------------------------------------------+
void AddDependenciesSection()
{
   AddSectionTitle("🔗 DEPENDÊNCIAS CRÍTICAS");
   
   // Lista de dependências críticas
   string criticalDeps[] = {
      "CoreBrainManager -> TradeExecutor",
      "CoreBrainManager -> PositionManager", 
      "CoreBrainManager -> DefenseOrchestrator",
      "CoreBrainManager -> ExecutionLoopController",
      "CoreBrainManager -> SkyIntelBridge",
      "CoreBrainManager -> AuditManager",
      "CoreBrainManager -> Log"
   };
   
   for(int i = 0; i < ArraySize(criticalDeps); i++) {
      AddInfoLine("• " + criticalDeps[i], "CRÍTICA", WARNING_COLOR);
   }
   
   AddInfoLine("", "", TEXT_COLOR); // Linha vazia
}

//+------------------------------------------------------------------+
//| Adicionar Seção de Integrações                                   |
//+------------------------------------------------------------------+
void AddIntegrationsSection()
{
   AddSectionTitle("🔄 INTEGRAÇÕES ATIVAS");
   
   // Lista de integrações
   string integrations[] = {
      "CoreBrainManager ↔ TradeExecutor",
      "CoreBrainManager ↔ PositionManager",
      "CoreBrainManager ↔ DefenseOrchestrator",
      "TradeExecutor ↔ TradingAgent",
      "PositionManager ↔ RiskAgent",
      "SignalValidator ↔ TradeExecutor"
   };
   
   for(int i = 0; i < ArraySize(integrations); i++) {
      AddInfoLine("• " + integrations[i], "ATIVA", SUCCESS_COLOR);
   }
   
   AddInfoLine("", "", TEXT_COLOR); // Linha vazia
}

//+------------------------------------------------------------------+
//| Adicionar Seção de Estatísticas                                  |
//+------------------------------------------------------------------+
void AddStatisticsSection()
{
   AddSectionTitle("📈 ESTATÍSTICAS");
   
   // Estatísticas simuladas
   AddInfoLine("Total de módulos:", "25", TEXT_COLOR);
   AddInfoLine("Dependências:", "18", TEXT_COLOR);
   AddInfoLine("Integrações:", "12", TEXT_COLOR);
   AddInfoLine("Módulos Core:", "5", TEXT_COLOR);
   AddInfoLine("Módulos Execution:", "8", TEXT_COLOR);
   AddInfoLine("Módulos Analysis:", "5", TEXT_COLOR);
   AddInfoLine("Módulos Agents:", "4", TEXT_COLOR);
   AddInfoLine("Módulos Utils:", "4", TEXT_COLOR);
}

//+------------------------------------------------------------------+
//| Adicionar Título de Seção                                        |
//+------------------------------------------------------------------+
void AddSectionTitle(string title)
{
   string titleName = g_dashboardName + "_Title_" + IntegerToString(g_currentLine);
   ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
   ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 60 + (g_currentLine * g_lineHeight));
   ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 12);
   ObjectSetInteger(0, titleName, OBJPROP_COLOR, SUCCESS_COLOR);
   ObjectSetString(0, titleName, OBJPROP_TEXT, title);
   ObjectSetString(0, titleName, OBJPROP_FONT, "Arial Bold");
   
   g_currentLine++;
}

//+------------------------------------------------------------------+
//| Adicionar Linha de Informação                                    |
//+------------------------------------------------------------------+
void AddInfoLine(string label, string value, color textColor)
{
   string labelName = g_dashboardName + "_Label_" + IntegerToString(g_currentLine);
   string valueName = g_dashboardName + "_Value_" + IntegerToString(g_currentLine);
   
   // Label
   ObjectCreate(0, labelName, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, labelName, OBJPROP_XDISTANCE, 40);
   ObjectSetInteger(0, labelName, OBJPROP_YDISTANCE, 60 + (g_currentLine * g_lineHeight));
   ObjectSetInteger(0, labelName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, labelName, OBJPROP_FONTSIZE, 10);
   ObjectSetInteger(0, labelName, OBJPROP_COLOR, TEXT_COLOR);
   ObjectSetString(0, labelName, OBJPROP_TEXT, label);
   ObjectSetString(0, labelName, OBJPROP_FONT, "Arial");
   
   // Value
   ObjectCreate(0, valueName, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, valueName, OBJPROP_XDISTANCE, 250);
   ObjectSetInteger(0, valueName, OBJPROP_YDISTANCE, 60 + (g_currentLine * g_lineHeight));
   ObjectSetInteger(0, valueName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, valueName, OBJPROP_FONTSIZE, 10);
   ObjectSetInteger(0, valueName, OBJPROP_COLOR, textColor);
   ObjectSetString(0, valueName, OBJPROP_TEXT, value);
   ObjectSetString(0, valueName, OBJPROP_FONT, "Arial");
   
   g_currentLine++;
}

//+------------------------------------------------------------------+
//| Atualização do Painel                                            |
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   if(!SHOW_DASHBOARD) return;
   
   // Limpar conteúdo anterior
   ObjectsDeleteAll(0, g_dashboardName + "_Label_");
   ObjectsDeleteAll(0, g_dashboardName + "_Value_");
   ObjectsDeleteAll(0, g_dashboardName + "_Title_");
   
   // Recriar conteúdo
   CreateContentArea();
   
   // Atualizar timestamp
   string timeName = g_dashboardName + "_Time";
   if(ObjectFind(0, timeName) < 0) {
      ObjectCreate(0, timeName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, timeName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, timeName, OBJPROP_YDISTANCE, g_dashboardHeight + 25);
      ObjectSetInteger(0, timeName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, timeName, OBJPROP_FONTSIZE, 8);
      ObjectSetInteger(0, timeName, OBJPROP_COLOR, TEXT_COLOR);
      ObjectSetString(0, timeName, OBJPROP_FONT, "Arial");
   }
   ObjectSetString(0, timeName, OBJPROP_TEXT, "Última atualização: " + TimeToString(TimeCurrent()));
}

//+------------------------------------------------------------------+
//| Registro de Módulos para o Dashboard                             |
//+------------------------------------------------------------------+
void RegisterDashboardModules()
{
   AuditLog("[DependencyDashboard] Registrando módulos para o dashboard...", LOG_LEVEL_DEBUG);
   
   // Registrar módulos básicos
   g_dashboardRegistry.RegisterModule("CoreBrainManager", "../Core/CoreBrainManager.mqh", "Core", "Gerenciador central");
   g_dashboardRegistry.RegisterModule("TradeExecutor", "../Include/ExecutionLogic/TradeExecutor.mqh", "Execution", "Executor");
   g_dashboardRegistry.RegisterModule("PositionManager", "../Include/ExecutionLogic/PositionManager.mqh", "Execution", "Posições");
   g_dashboardRegistry.RegisterModule("DefenseOrchestrator", "../Include/ExecutionLogic/DefenseOrchestrator.mqh", "Execution", "Defesa");
   g_dashboardRegistry.RegisterModule("ExecutionLoopController", "../Include/ExecutionLogic/ExecutionLoopController.mqh", "Execution", "Loop");
   g_dashboardRegistry.RegisterModule("SkyIntelBridge", "../Include/Integration/SkyIntelBridge.mqh", "Integration", "SkyIntel");
   g_dashboardRegistry.RegisterModule("AuditManager", "../Auditor/AuditManager.mqh", "Auditor", "Auditoria");
   g_dashboardRegistry.RegisterModule("Log", "../Utils/Log.mqh", "Utils", "Logging");
   
   // Registrar dependências críticas
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "TradeExecutor", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "PositionManager", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "DefenseOrchestrator", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "ExecutionLoopController", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "SkyIntelBridge", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "AuditManager", "include", true);
   g_dashboardRegistry.RegisterDependency("CoreBrainManager", "Log", "include", true);
   
   AuditLog("[DependencyDashboard] Registro de módulos concluído", LOG_LEVEL_DEBUG);
} 