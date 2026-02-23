#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Configurações de Risco
#define SKYLER_MAX_RISK_PER_TRADE    0.02    // 2% do capital
#define SKYLER_MAX_DAILY_LOSS        0.05    // 5% do capital
#define SKYLER_LEVERAGE              500     // Alavancagem 500x

// Configurações de Indicadores
#define SKYLER_RSI_PERIOD            14      // Período do RSI
#define SKYLER_MACD_FAST_PERIOD      12      // Período rápido do MACD
#define SKYLER_MACD_SLOW_PERIOD      26      // Período lento do MACD
#define SKYLER_MACD_SIGNAL_PERIOD    9       // Período do sinal do MACD
#define SKYLER_BB_PERIOD             20      // Período das Bandas de Bollinger
#define SKYLER_BB_DEVIATION          2.0     // Desvio padrão das Bandas

// Configurações de Teste
#define SKYLER_INITIAL_CAPITAL       100.0   // Capital inicial (EUR)
#define SKYLER_MAX_POSITION_SIZE     0.02    // Tamanho máximo da posição (%)

// Configurações de Monitoramento
#define SKYLER_MIN_SUCCESS_RATE      0.55    // Taxa mínima de sucesso
#define SKYLER_MAX_DRAWDOWN          0.10    // Drawdown máximo permitido
#define SKYLER_MIN_PROFIT_FACTOR     1.50    // Fator de lucro mínimo
#define SKYLER_HEALTH_THRESHOLD      0.70    // Limiar de saúde do sistema

// Configurações de Escalonamento
#define SKYLER_MAX_RISK_PER_LEVEL    0.02    // Risco máximo por nível
#define SKYLER_MAX_TOTAL_RISK        0.10    // Risco total máximo
#define SKYLER_VOLUME_STEP           0.10    // Passo de volume
#define SKYLER_PRICE_STEP            0.001   // Passo de preço

// Configurações de Análise Pré-Operação
#define SKYLER_MIN_REWARD_RISK       1.50    // Razão mínima recompensa/risco
#define SKYLER_MAX_POTENTIAL_LOSS    0.02    // Perda potencial máxima
#define SKYLER_MAX_MARKET_EXPOSURE   0.50    // Exposição máxima ao mercado

// Configurações de Eventos Econômicos
#define SKYLER_LOW_IMPACT_FACTOR     0.50    // Fator de impacto baixo
#define SKYLER_MEDIUM_IMPACT_FACTOR  1.00    // Fator de impacto médio
#define SKYLER_HIGH_IMPACT_FACTOR    2.00    // Fator de impacto alto

// Configurações de Timeframes
#define SKYLER_TIMEFRAME_M1          1       // 1 minuto
#define SKYLER_TIMEFRAME_M5          5       // 5 minutos
#define SKYLER_TIMEFRAME_M15         15      // 15 minutos
#define SKYLER_TIMEFRAME_H1          60      // 1 hora
#define SKYLER_TIMEFRAME_H4          240     // 4 horas
#define SKYLER_TIMEFRAME_D1          1440    // 1 dia
#define SKYLER_TIMEFRAME_W1          10080   // 1 semana
#define SKYLER_TIMEFRAME_MN          43200   // 1 mês

// Configurações de Integração ICMarkets
#define SKYLER_ICM_MAX_ORDERS        200     // Número máximo de ordens
#define SKYLER_ICM_EURUSD_SPREAD     0.0     // Spread EURUSD (pips)
#define SKYLER_ICM_GBPUSD_SPREAD     0.1     // Spread GBPUSD (pips)
#define SKYLER_ICM_USDJPY_SPREAD     0.1     // Spread USDJPY (pips)
#define SKYLER_ICM_LONG_SWAP         -0.0023 // Swap para posição longa (%)
#define SKYLER_ICM_SHORT_SWAP        -0.0045 // Swap para posição short (%) 