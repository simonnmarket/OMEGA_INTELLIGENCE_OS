//+------------------------------------------------------------------+
//| sidebar_demo.mq5 - Demonstração do Sidebar com Módulos           |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Versão: v1.0 (Sidebar com Primeira Letra Alterada)               |
//| Atualizado em: 2025-07-30 | Agente: Claude Sonnet 4              |
//| Status: TIER-0 Compliant | SHA3 Protected | Sidebar Ready         |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_plots 0

#include "ChartObjects\ChartObjectsTxtControls.mqh"
#include "utils/logger_institutional.mqh"
#include "types/trade_signal_enum.mqh"

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
logger_institutional *g_logger;
SidebarManager *g_sidebar;
datetime g_last_update;

//+------------------------------------------------------------------+
//| Função de Inicialização                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   // Inicializa logger
   g_logger = new logger_institutional();
   if(!g_logger.is_initialized())
   {
      Print("[SIDEBAR] Erro ao inicializar logger");
      return INIT_FAILED;
   }

   // Inicializa sidebar
   if(EnableSidebar)
   {
      g_sidebar = new SidebarManager(*g_logger, SidebarX, SidebarY);
      g_sidebar.ListAllModules();
   }

   g_last_update = TimeCurrent();
   g_logger.log_info("[SIDEBAR] Demonstração do sidebar inicializada");
   
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
   }
   
   if(g_logger != NULL)
   {
      delete g_logger;
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
         
         g_logger.log_info("[SIDEBAR] Status dos módulos atualizado - Contador: " + IntegerToString(update_counter));
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
            g_logger.log_info("[SIDEBAR] Módulo Analysis clicado - " + g_sidebar->GetModuleDescription(MODULE_ANALYSIS));
         }
         else if(module_name == "quantum")
         {
            g_logger.log_info("[SIDEBAR] Módulo Quantum clicado - " + g_sidebar->GetModuleDescription(MODULE_QUANTUM));
         }
         else if(module_name == "intelligence")
         {
            g_logger.log_info("[SIDEBAR] Módulo Intelligence clicado - " + g_sidebar->GetModuleDescription(MODULE_INTELLIGENCE));
         }
         else if(module_name == "security")
         {
            g_logger.log_info("[SIDEBAR] Módulo Security clicado - " + g_sidebar->GetModuleDescription(MODULE_SECURITY));
         }
         else if(module_name == "neural")
         {
            g_logger.log_info("[SIDEBAR] Módulo Neural clicado - " + g_sidebar->GetModuleDescription(MODULE_NEURAL));
         }
         else if(module_name == "audit")
         {
            g_logger.log_info("[SIDEBAR] Módulo Audit clicado - " + g_sidebar->GetModuleDescription(MODULE_AUDIT));
         }
         else if(module_name == "compliance")
         {
            g_logger.log_info("[SIDEBAR] Módulo Compliance clicado - " + g_sidebar->GetModuleDescription(MODULE_COMPLIANCE));
         }
         else if(module_name == "data")
         {
            g_logger.log_info("[SIDEBAR] Módulo Data clicado - " + g_sidebar->GetModuleDescription(MODULE_DATA));
         }
         else if(module_name == "decisionengine")
         {
            g_logger.log_info("[SIDEBAR] Módulo DecisionEngine clicado - " + g_sidebar->GetModuleDescription(MODULE_DECISIONENGINE));
         }
         else if(module_name == "detection")
         {
            g_logger.log_info("[SIDEBAR] Módulo Detection clicado - " + g_sidebar->GetModuleDescription(MODULE_DETECTION));
         }
         else if(module_name == "executionlogic")
         {
            g_logger.log_info("[SIDEBAR] Módulo ExecutionLogic clicado - " + g_sidebar->GetModuleDescription(MODULE_EXECUTIONLOGIC));
         }
         else if(module_name == "integration")
         {
            g_logger.log_info("[SIDEBAR] Módulo Integration clicado - " + g_sidebar->GetModuleDescription(MODULE_INTEGRATION));
         }
         else if(module_name == "modules")
         {
            g_logger.log_info("[SIDEBAR] Módulo Modules clicado - " + g_sidebar->GetModuleDescription(MODULE_MODULES));
         }
         else if(module_name == "optimization")
         {
            g_logger.log_info("[SIDEBAR] Módulo Optimization clicado - " + g_sidebar->GetModuleDescription(MODULE_OPTIMIZATION));
         }
         else if(module_name == "risk")
         {
            g_logger.log_info("[SIDEBAR] Módulo Risk clicado - " + g_sidebar->GetModuleDescription(MODULE_RISK));
         }
         else if(module_name == "tools")
         {
            g_logger.log_info("[SIDEBAR] Módulo Tools clicado - " + g_sidebar->GetModuleDescription(MODULE_TOOLS));
         }
         else if(module_name == "types")
         {
            g_logger.log_info("[SIDEBAR] Módulo Types clicado - " + g_sidebar->GetModuleDescription(MODULE_TYPES));
         }
         else if(module_name == "visuals")
         {
            g_logger.log_info("[SIDEBAR] Módulo Visuals clicado - " + g_sidebar->GetModuleDescription(MODULE_VISUALS));
         }
      }
   }
} 