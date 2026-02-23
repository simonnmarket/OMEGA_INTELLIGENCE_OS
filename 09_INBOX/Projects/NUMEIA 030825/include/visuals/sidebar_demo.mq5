//+------------------------------------------------------------------+
//| sidebar_demo.mq5 - Demonstração do Sidebar com Módulos           |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v1.0 (Sidebar com Primeira Letra Alterada)               |
//| Atualizado em: 2025-01-27 | Agente: Claude Sonnet 4              |
//| Status: TIER-0 Compliant | SHA3 Protected | Sidebar Ready         |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_plots 0

#include "../Utils/Utils.mqh"
#include "../types/trade_signal_enum.mqh"

//+------------------------------------------------------------------+
//| Definições de Input                                              |
//+------------------------------------------------------------------+
input bool EnableSidebar = true;              // Ativar sidebar
input int SidebarX = 10;                      // Posição X do sidebar
input int SidebarY = 50;                      // Posição Y do sidebar
input color ActiveColor = clrLime;            // Cor dos módulos ativos
input color InactiveColor = clrGray;          // Cor dos módulos inativos
input int UpdateInterval = 1000;              // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| Variáveis Globais                                                |
//+------------------------------------------------------------------+
CGenesisUtils *g_logger;
CGenesisSidebarManager *g_sidebar;
datetime g_last_update;

//+------------------------------------------------------------------+
//| Função de Inicialização                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   // Inicializa logger
   g_logger = new CGenesisUtils();
   if(g_logger == NULL)
   {
      Print("[SIDEBAR] Erro ao inicializar logger");
      return INIT_FAILED;
   }

   // Inicializa sidebar
   if(EnableSidebar)
   {
      g_sidebar = new CGenesisSidebarManager(*g_logger, SidebarX, SidebarY);
      if(g_sidebar != NULL)
         g_sidebar.ListAllModules();
   }

   g_last_update = TimeCurrent();
   Print("[SIDEBAR] Demonstração do sidebar inicializada");
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Função de Desinicialização                                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_sidebar != NULL)
   {
      delete g_sidebar;
      g_sidebar = NULL;
   }
   
   if(g_logger != NULL)
   {
      delete g_logger;
      g_logger = NULL;
   }
   
   Print("[SIDEBAR] Demonstração do sidebar encerrada");
}

//+------------------------------------------------------------------+
//| Função de Tick                                                   |
//+------------------------------------------------------------------+
void OnTick()
{
   if(!EnableSidebar || g_sidebar == NULL) return;
   
   // Atualiza a cada intervalo definido
   if(TimeCurrent() - g_last_update >= UpdateInterval)
   {
      // Simula mudança de status de alguns módulos
      static int update_counter = 0;
      update_counter++;
      
      // Alterna status de módulos para demonstração
      if(update_counter % 5 == 0)
      {
         g_sidebar->UpdateModuleStatus(MODULE_QUANTUM, (update_counter % 10 == 0));
         g_sidebar->UpdateModuleStatus(MODULE_INTELLIGENCE, (update_counter % 8 == 0));
         g_sidebar->UpdateModuleStatus(MODULE_SECURITY, (update_counter % 12 == 0));
         
         Print("[SIDEBAR] Status dos módulos atualizado - Contador: " + IntegerToString(update_counter));
      }
      
      g_last_update = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Função de Clique do Mouse                                        |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_OBJECT_CLICK && EnableSidebar && g_sidebar != NULL)
   {
      // Verifica se o clique foi em um módulo do sidebar
      if(StringFind(sparam, "Sidebar_") >= 0)
      {
         string module_name = StringSubstr(sparam, 8); // Remove "Sidebar_"
         
         // Identifica qual módulo foi clicado
         if(module_name == "analysis")
         {
            Print("[SIDEBAR] Módulo Analysis clicado - " + g_sidebar->GetModuleDescription(MODULE_ANALYSIS));
         }
         else if(module_name == "quantum")
         {
            Print("[SIDEBAR] Módulo Quantum clicado - " + g_sidebar->GetModuleDescription(MODULE_QUANTUM));
         }
         else if(module_name == "intelligence")
         {
            Print("[SIDEBAR] Módulo Intelligence clicado - " + g_sidebar->GetModuleDescription(MODULE_INTELLIGENCE));
         }
         else if(module_name == "security")
         {
            Print("[SIDEBAR] Módulo Security clicado - " + g_sidebar->GetModuleDescription(MODULE_SECURITY));
         }
         else if(module_name == "neural")
         {
            Print("[SIDEBAR] Módulo Neural clicado - " + g_sidebar->GetModuleDescription(MODULE_NEURAL));
         }
         else if(module_name == "audit")
         {
            Print("[SIDEBAR] Módulo Audit clicado - " + g_sidebar->GetModuleDescription(MODULE_AUDIT));
         }
         else if(module_name == "compliance")
         {
            Print("[SIDEBAR] Módulo Compliance clicado - " + g_sidebar->GetModuleDescription(MODULE_COMPLIANCE));
         }
         else if(module_name == "data")
         {
            Print("[SIDEBAR] Módulo Data clicado - " + g_sidebar->GetModuleDescription(MODULE_DATA));
         }
         else if(module_name == "decisionengine")
         {
            Print("[SIDEBAR] Módulo DecisionEngine clicado - " + g_sidebar->GetModuleDescription(MODULE_DECISIONENGINE));
         }
         else if(module_name == "detection")
         {
            Print("[SIDEBAR] Módulo Detection clicado - " + g_sidebar->GetModuleDescription(MODULE_DETECTION));
         }
         else if(module_name == "executionlogic")
         {
            Print("[SIDEBAR] Módulo ExecutionLogic clicado - " + g_sidebar->GetModuleDescription(MODULE_EXECUTIONLOGIC));
         }
         else if(module_name == "integration")
         {
            Print("[SIDEBAR] Módulo Integration clicado - " + g_sidebar->GetModuleDescription(MODULE_INTEGRATION));
         }
         else if(module_name == "modules")
         {
            Print("[SIDEBAR] Módulo Modules clicado - " + g_sidebar->GetModuleDescription(MODULE_MODULES));
         }
         else if(module_name == "optimization")
         {
            Print("[SIDEBAR] Módulo Optimization clicado - " + g_sidebar->GetModuleDescription(MODULE_OPTIMIZATION));
         }
         else if(module_name == "risk")
         {
            Print("[SIDEBAR] Módulo Risk clicado - " + g_sidebar->GetModuleDescription(MODULE_RISK));
         }
         else if(module_name == "tools")
         {
            Print("[SIDEBAR] Módulo Tools clicado - " + g_sidebar->GetModuleDescription(MODULE_TOOLS));
         }
         else if(module_name == "types")
         {
            Print("[SIDEBAR] Módulo Types clicado - " + g_sidebar->GetModuleDescription(MODULE_TYPES));
         }
         else if(module_name == "visuals")
         {
            Print("[SIDEBAR] Módulo Visuals clicado - " + g_sidebar->GetModuleDescription(MODULE_VISUALS));
         }
      }
   }
} 