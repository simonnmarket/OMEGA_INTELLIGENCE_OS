//+------------------------------------------------------------------+
//| CoreBrainManager.mqh - Núcleo de Controle da EA Numeia          |
//+------------------------------------------------------------------+
#ifndef __CORE_BRAIN_MANAGER_MQH__
#define __CORE_BRAIN_MANAGER_MQH__

#include "ExecutionOrchestrator.mqh"
#include "ModuleRegistry.mqh"
#include "AuditInterface.mqh"
#include "../Config/GlobalConfig.mqh"
#include "../Utils/Log.mqh"

// Classe central do sistema, responsável por orquestrar os módulos
class CoreBrainManager {
private:
   ExecutionOrchestrator orchestrator;
   ModuleRegistry registry;
   AuditInterface audit;

public:
   // Inicializa o cérebro e todos os módulos registrados
   void Initialize() {
      Log("Inicializando CoreBrainManager...");
      registry.RegisterModules();               // Registro de módulos essenciais
      orchestrator.DefineExecutionFlow();       // Define fluxo de execução
      audit.Initialize();                       // Inicializa conexão com auditoria
      Log("CoreBrainManager inicializado com sucesso.");
   }

   // Executa o ciclo principal da EA
   void Run() {
      Log("CoreBrainManager executando ciclo principal...");
      if (!registry.ValidateModules()) {
         Log("Erro: Módulos inválidos ou não registrados!", LOG_LEVEL_ERROR);
         return;
      }

      orchestrator.ExecuteModules();            // Dispara execução dos módulos
      audit.ValidateCompliance();               // Auditoria e conformidade
   }
};

#endif // __CORE_BRAIN_MANAGER_MQH__
