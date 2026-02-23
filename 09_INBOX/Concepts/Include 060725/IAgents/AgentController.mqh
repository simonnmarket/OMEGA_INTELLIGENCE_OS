// Include/IAgents/AgentController.mqh
// Controlador geral dos agentes IA por ativo
// Projeto: Lenovo Apollo11 Quantum EA Hybrid

#ifndef __AGENT_CONTROLLER_MQH__
#define __AGENT_CONTROLLER_MQH__
#include "IAgent_XAGUSD.mqh"

class AgentController
  {
private:
   IAgent_TEMPLATE *agents[];
   int total;

public:
   AgentController()
     {
      ArrayResize(agents, 1);
      agents[0] = new IAgent_XAGUSD();
      total = 1;
     }

   ~AgentController()
     {
      for(int i = 0; i < total; i++)
         if(CheckPointer(agents[i]) == POINTER_DYNAMIC)
            delete agents[i];
     }

   void UpdateAll()
     {
      for(int i = 0; i < total; i++)
         agents[i].UpdateState();
     }

   void OnTick()
     {
      for(int i = 0; i < total; i++)
         if(Symbol() == agents[i].Symbol())
            agents[i].ExecuteTrade();
     }
  };

#endif
