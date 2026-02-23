//+------------------------------------------------------------------+
//|                                             CoreBrainManager.mqh |
//|               Sistema de Gerenciamento Central - EA Numeia       |
//+------------------------------------------------------------------+
#ifndef __CORE_BRAIN_MANAGER_MQH__
#define __CORE_BRAIN_MANAGER_MQH__

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>
#include <Arrays\ArrayObj.mqh>
#include "../Include/ExecutionLogic/TradeExecutor.mqh"
#include "../Include/ExecutionLogic/PositionManager.mqh"
#include "../Include/ExecutionLogic/DefenseOrchestrator.mqh"
#include "../Include/ExecutionLogic/ExecutionLoopController.mqh"
#include "../Include/Integration/SkyIntelBridge.mqh"
#include "../Auditor/AuditManager.mqh"
#include "../Utils/Log.mqh"
#include "../Scripts/QuantumAudit/AuditEntanglementBridge.mqh"

//+------------------------------------------------------------------+
//| Classe: CoreBrainManager                                         |
//+------------------------------------------------------------------+
class CoreBrainManager
{
private:
   TradeExecutor         m_tradeExecutor;
   PositionManager       m_positionManager;
   DefenseOrchestrator   m_defenseOrchestrator;
   ExecutionLoopController m_loopController;
   SkyIntelBridge        m_skyIntel;
   AuditManager          m_audit;
   
   // Sistema de Auditoria Quântica
   bool                  m_quantumAuditEnabled;
   datetime              m_lastAuditTime;
   int                   m_auditIntervalMinutes;

public:
                     CoreBrainManager() : m_quantumAuditEnabled(true), m_lastAuditTime(0), m_auditIntervalMinutes(30) {}
                    ~CoreBrainManager() {}

   bool              Init();
   void              OnTick();
   void              OnDeinit();
   
   // Métodos de Auditoria Quântica
   void              EnableQuantumAudit(bool enable) { m_quantumAuditEnabled = enable; }
   void              SetAuditInterval(int minutes) { m_auditIntervalMinutes = minutes; }
   void              RunQuantumAudit();
   bool              ShouldRunAudit();
   void              ProcessAuditResults();
};

//+------------------------------------------------------------------+
//| Funções de Classe                                                |
//+------------------------------------------------------------------+
bool CoreBrainManager::Init()
{
   AuditLog("[CoreBrainManager] Inicializando módulos principais...", LOG_LEVEL_INFO);
   bool ok=true;
   ok &= m_tradeExecutor.Init();
   ok &= m_positionManager.Init();
   ok &= m_defenseOrchestrator.Init();
   ok &= m_loopController.Init();
   ok &= m_skyIntel.Init();
   ok &= m_audit.Init();
   
   // Inicializar auditoria quântica se habilitada
   if(m_quantumAuditEnabled)
   {
      AuditLog("[CoreBrainManager] Sistema de auditoria quântica habilitado", LOG_LEVEL_INFO);
      RunQuantumAudit(); // Primeira auditoria
   }
   
   AuditLog("[CoreBrainManager] Inicialização concluída", LOG_LEVEL_INFO);
   return ok;
}

void CoreBrainManager::OnTick()
{
   m_loopController.ExecuteLoop(m_tradeExecutor, m_positionManager, m_defenseOrchestrator, m_skyIntel, m_audit);
   
   // Verificar se deve executar auditoria quântica
   if(m_quantumAuditEnabled && ShouldRunAudit())
   {
      RunQuantumAudit();
   }
}

void CoreBrainManager::OnDeinit()
{
   AuditLog("[CoreBrainManager] Encerrando módulos...", LOG_LEVEL_INFO);
   m_tradeExecutor.OnDeinit();
   m_positionManager.OnDeinit();
   m_defenseOrchestrator.OnDeinit();
   m_loopController.OnDeinit();
   m_skyIntel.OnDeinit();
   m_audit.OnDeinit();
   AuditLog("[CoreBrainManager] Encerramento concluído", LOG_LEVEL_INFO);
}

//+------------------------------------------------------------------+
//| Métodos de Auditoria Quântica                                   |
//+------------------------------------------------------------------+
void CoreBrainManager::RunQuantumAudit()
{
   AuditLog("[CoreBrainManager] Executando auditoria quântica...", LOG_LEVEL_INFO);
   
   // Executar auditoria através do bridge
   AuditEntanglementBridge::RunAuditFromCoreBrain();
   
   // Processar resultados
   ProcessAuditResults();
   
   m_lastAuditTime = TimeCurrent();
   AuditLog("[CoreBrainManager] Auditoria quântica concluída", LOG_LEVEL_INFO);
}

bool CoreBrainManager::ShouldRunAudit()
{
   if(m_lastAuditTime == 0)
      return true;
      
   datetime currentTime = TimeCurrent();
   int minutesSinceLastAudit = (int)((currentTime - m_lastAuditTime) / 60);
   
   return (minutesSinceLastAudit >= m_auditIntervalMinutes);
}

void CoreBrainManager::ProcessAuditResults()
{
   AuditLog("[CoreBrainManager] Processando resultados da auditoria...", LOG_LEVEL_DEBUG);
   
   // Aqui pode adicionar lógica para processar resultados específicos
   // Por exemplo, alertas, notificações, etc.
   
   // Verificar se há problemas críticos
   if(FileIsExist("entanglement_status.dat"))
   {
      int handle = FileOpen("entanglement_status.dat", FILE_READ | FILE_TXT | FILE_COMMON);
      if(handle != INVALID_HANDLE)
      {
         int failCount = 0;
         while(!FileIsEnding(handle))
         {
            string line = FileReadString(handle);
            if(StringFind(line, "FALHA") >= 0)
               failCount++;
         }
         FileClose(handle);
         
         if(failCount > 0)
         {
            LogWarning("[CoreBrainManager] " + IntegerToString(failCount) + " problemas detectados na auditoria");
         }
         else
         {
            AuditLog("[CoreBrainManager] Auditoria passou sem problemas", LOG_LEVEL_INFO);
         }
      }
   }
}

#endif // __CORE_BRAIN_MANAGER_MQH__ 