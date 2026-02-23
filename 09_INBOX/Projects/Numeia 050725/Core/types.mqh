//+------------------------------------------------------------------+
//|                        types.mqh                                 |
//|        Tipos e Estruturas Comuns da EA Numeia                    |
//+------------------------------------------------------------------+
#pragma once

// Enum de status de execução dos módulos
enum ModuleStatus {
   MODULE_OK = 0,
   MODULE_WARNING,
   MODULE_ERROR
};

// Enum de tipo de agente
enum AgentType {
   AGENT_TRADING,
   AGENT_RISK,
   AGENT_PATTERN,
   AGENT_MARKET_ANALYSIS
};

// Resultado padrão de uma tarefa executada por qualquer módulo
struct TaskResult {
   bool success;              // True se a tarefa foi concluída com sucesso
   string message;            // Mensagem informativa ou de erro
   datetime timestamp;        // Timestamp da execução
};

// Parâmetros gerais para orquestração
struct ExecutionContext {
   string current_symbol;     // Símbolo em execução
   ENUM_TIMEFRAMES tf;        // Timeframe em uso
   datetime current_time;     // Tempo atual
   double equity;             // Capital atual
   int active_trades;         // Quantidade de trades abertos
};
