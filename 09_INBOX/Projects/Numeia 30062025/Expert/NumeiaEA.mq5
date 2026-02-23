//+------------------------------------------------------------------+
//|                                                      NumeiaEA.mq5 |
//|               Expert Advisor Principal - Projeto Numeia          |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Includes Principais                                              |
//+------------------------------------------------------------------+
#include "../Core/CoreBrainManager.mqh"

//+------------------------------------------------------------------+
//| Declaração de Instância do Gerenciador Central                  |
//+------------------------------------------------------------------+
CoreBrainManager brain;

//============================ EA SETTINGS =========================//
input bool EnableSkyIntel   = true;  // Ativar inteligência estratégica
input bool EnableDefense    = true;  // Ativar zona de defesa e break-even
input bool EnableAudit      = true;  // Ativar logs de auditoria
input bool EnableRiskFilter = true;  // Ativar análise de risco

//============================ INIT ================================//
int OnInit()
{
   if(!brain.Init())
   {
      Print("[NumeiaEA] Falha na inicialização do sistema central.");
      return(INIT_FAILED);
   }
   Print("[NumeiaEA] Sistema inicializado com sucesso.");
   return(INIT_SUCCEEDED);
}

//============================ DEINIT ==============================//
void OnDeinit(const int reason)
{
   brain.OnDeinit();
   Print("[NumeiaEA] Encerramento completo.");
}

//============================ MAIN LOOP ===========================//
void OnTick()
{
   brain.OnTick();
} 