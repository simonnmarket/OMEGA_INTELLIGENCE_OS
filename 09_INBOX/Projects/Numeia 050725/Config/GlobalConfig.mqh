//+------------------------------------------------------------------+
//|                     GlobalConfig.mqh                             |
//|     Configurações Globais da EA Numeia - Projeto Sky Lab        |
//+------------------------------------------------------------------+
#pragma once

//===========================
// Identificação do Sistema
//===========================
#define EA_NAME             "Numeia EA"
#define EA_VERSION          "1.0.0"
#define EA_AUTHOR           "Projeto Sky Lab"
#define EA_DEBUG_MODE       true       // Ativar logs de depuração
#define MAX_ACTIVE_ORDERS   20         // Número máximo de ordens simultâneas permitidas

//===========================
// Configurações de Operação
//===========================
#define MAGIC_NUMBER        20250618
#define SYMBOL              "EURUSD"
#define SLIPPAGE            3
#define ALLOWED_TIMEFRAMES  "M1,M5,M15,H1,H4,D1"

//===========================
// Controle de Execução
//===========================
#define ENABLE_SCALING              true     // Ativar escalonamento de lotes
#define MAX_SCALING_LOT            100.0     // Lote máximo escalado
#define INITIAL_SCALING_LOT        0.10      // Lote inicial no escalonamento
#define SCALING_MULTIPLIER         2.0       // Multiplicador de lote por etapa (ex: 0.10 → 0.20 → 0.40)

//===========================
// Concorrência Multi-Timeframe
//===========================
#define ENABLE_MTF_VALIDATION      true
#define REQUIRED_TIMEFRAME_MATCHES 4         // Número mínimo de timeframes que devem confirmar a tendência

//===========================
// Intervalos de Tempo
//===========================
#define ALLOWED_TRADING_HOURS_FROM  "08:00"
#define ALLOWED_TRADING_HOURS_TO    "22:00"

//===========================
// Segurança e Logs
//===========================
#define ENABLE_LOGGING             true
#define ENABLE_AUDIT_MODULE        true
#define LOG_LEVEL_DEBUG            1
#define LOG_LEVEL_WARNING          2
#define LOG_LEVEL_ERROR            3
#define CURRENT_LOG_LEVEL          LOG_LEVEL_DEBUG

//===========================
// Backtesting
//===========================
#define IS_BACKTEST_MODE           false

//===========================
// Indicadores e Estratégias
//===========================
#define ENABLE_PATTERN_RECOGNITION true
#define ENABLE_VOLUME_ANALYSIS     true
#define ENABLE_QUANTUM_MODE        false    // Modo especial para experimentação com modelos quânticos futuros

//===========================
// Placeholder para futura IA
//===========================
#define ENABLE_AI_AGENT_SUPPORT    true
#define AI_AGENT_THINKING_TIME_MS  500

//+------------------------------------------------------------------+
