//+------------------------------------------------------------------+
//| sidebar_demo.mq5 - Demonstração do Sidebar com Módulos          |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v1.0                                                     |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_plots 0

#include <Genesis/Utils/Utils.mqh>
#include <Genesis/Core/TradeSignalEnum.mqh>

input bool EnableSidebar = true;
input int SidebarX = 10;
input int SidebarY = 50;
input color ActiveColor = clrLime;
input color InactiveColor = clrGray;
input int UpdateInterval = 1000;

datetime g_last_update;

int OnInit()
{ g_last_update = TimeCurrent(); Print("[SIDEBAR] Demonstração do sidebar inicializada"); return INIT_SUCCEEDED; }

void OnDeinit(const int reason)
{ Print("[SIDEBAR] Demonstração do sidebar encerrada"); }

void OnTick()
{ if(!EnableSidebar) return; if(TimeCurrent() - g_last_update >= UpdateInterval){ g_last_update = TimeCurrent(); Print("[SIDEBAR] Atualização de status de módulos"); } }

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
{
   return(rates_total);
}


