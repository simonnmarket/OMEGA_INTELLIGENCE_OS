//+------------------------------------------------------------------+
//|                                    TesteTypesSimples.mq5          |
//|         Teste Simples do types.mqh                               |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

#include "Core/types.mqh"

//+------------------------------------------------------------------+
//| Função principal do script                                        |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("🚀 TESTE SIMPLES DO TYPES.MQH");
   Print("================================");
   
   // Teste 1: Enums
   ModuleStatus status = MODULE_OK;
   AgentType agent = AGENT_TRADING;
   ENUM_SIGNAL_TYPE signal = SIGNAL_NONE;
   DefenseSignal defense = DEFENSE_NONE;
   
   Print("✓ Enums funcionando:");
   Print("  - ModuleStatus: " + IntegerToString(status));
   Print("  - AgentType: " + IntegerToString(agent));
   Print("  - ENUM_SIGNAL_TYPE: " + IntegerToString(signal));
   Print("  - DefenseSignal: " + IntegerToString(defense));
   
   // Teste 2: Estruturas
   TaskResult result;
   result.success = true;
   result.message = "Teste OK";
   result.timestamp = TimeCurrent();
   
   ExecutionContext context;
   context.current_symbol = "EURUSD";
   context.tf = PERIOD_M5;
   context.current_time = TimeCurrent();
   context.equity = 10000.0;
   context.active_trades = 0;
   
   DefenseStatus defenseStatus;
   defenseStatus.defenseLine = 1.1000;
   defenseStatus.hurst = 0.5;
   defenseStatus.liquidity = 1000.0;
   defenseStatus.footprint = 1.1005;
   defenseStatus.signal = DEFENSE_NONE;
   
   Print("✓ Estruturas funcionando:");
   Print("  - TaskResult: " + result.message);
   Print("  - ExecutionContext: " + context.current_symbol);
   Print("  - DefenseStatus: " + DoubleToString(defenseStatus.defenseLine, 4));
   
   // Teste 3: Constantes
   Print("✓ Constantes funcionando:");
   Print("  - MAX_RETRY_COUNT: " + IntegerToString(MAX_RETRY_COUNT));
   Print("  - RISK_FACTOR: " + DoubleToString(RISK_FACTOR, 3));
   Print("  - MIN_LIQUIDITY_THRESHOLD: " + DoubleToString(MIN_LIQUIDITY_THRESHOLD, 0));
   Print("  - QUANTUM_HEARTBEAT_FREQ: " + IntegerToString(QUANTUM_HEARTBEAT_FREQ));
   
   Print("🎉 TESTE CONCLUÍDO COM SUCESSO!");
   Print("✅ types.mqh está funcionando corretamente!");
   
   // Criar objeto visual
   string objName = "teste_types_result";
   ObjectCreate(0, objName, OBJ_LABEL, 0, 0, 0);
   ObjectSetString(0, objName, OBJPROP_TEXT, "✅ TYPES OK!");
   ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, 20);
   ObjectSetInteger(0, objName, OBJPROP_COLOR, clrLime);
   ObjectSetInteger(0, objName, OBJPROP_FONTSIZE, 14);
   
   ChartRedraw();
} 