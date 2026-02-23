// ============================================================================
// Expert: NumeiaEA.mq5
// Projeto: QuantumOmegaGodMode
// Função: EA de Teste com core_brain_manager
// Versão: v1.0
// Data: 2025-07-13
// ============================================================================

#include "../core/core_brain_manager.mqh"
#include "../include/decisionengine/decision_router.mqh"
#include "../include/executionlogic/trade_executor.mqh"
#include "../include/executionlogic/safe_mode_manager.mqh"
#include "../utils/logger_institutional.mqh"

logger_institutional g_logger;
decision_router      g_router(g_logger);
trade_executor       g_executor(g_logger);
safe_mode_manager    g_safety(g_logger);
core_brain_manager   g_core(g_router, g_executor, g_safety, g_logger);

int OnInit() {
   g_core.initialize();
   return(INIT_SUCCEEDED);
}

void OnTick() {
   g_core.on_tick();
}