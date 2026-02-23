// MEMORY_ID: T0PP_COMPILE_GATE
// TIMESTAMP: 2025-08-17T00:00:00Z
// AUTHOR: Cursor_Omega
#property strict

#include <Trade/Trade.mqh>
#include <Genesis/Core/GenesisTier0Macros.mqh>
#include <Genesis/Templates/QuantumLearning_T0pp.mqh>
#include <Genesis/Templates/QuantumFinanceFramework_T0pp.mqh>

input bool UseAdvancedPipeline = true;

CTrade                       g_trade;
CQuantumLearning            *g_learn  = NULL;
CQuantumFinanceFramework    *g_qff    = NULL;

int OnInit()
  {
   GEN_LOG_INFO("CompileGate", "Initializing...");

   g_learn = new CQuantumLearning(NULL,NULL,NULL,NULL,NULL,_Symbol);
   if(g_learn!=NULL)
      g_learn.Initialize();

   g_qff = new CQuantumFinanceFramework(NULL);
   if(g_qff!=NULL)
      g_qff.Initialize();

   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   if(g_learn!=NULL){ delete g_learn; g_learn=NULL; }
   if(g_qff!=NULL){ delete g_qff; g_qff=NULL; }
   GEN_LOG_INFO("CompileGate", "Deinitialized.");
  }

void OnTick()
  {
   if(!UseAdvancedPipeline)
      return;

   if(g_learn!=NULL && g_learn.IsReady())
     {
      g_learn.Tick();
      // Example decision read
      QL_Signal s = g_learn.GetDecision();
      if(s==QL_SIGNAL_LONG || s==QL_SIGNAL_SHORT)
        {
         double rm = g_learn.GetRiskMultiplier();
         GEN_LOG_INFO("CompileGate", StringFormat("Decision=%d RiskX=%.2f", (int)s, rm));
        }
     }
  }


