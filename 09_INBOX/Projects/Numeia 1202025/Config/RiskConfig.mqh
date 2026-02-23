//+------------------------------------------------------------------+
//|                      RiskConfig.mqh                              |
//|        Configurações de risco da EA Numeia                      |
//+------------------------------------------------------------------+
#ifndef __RISK_CONFIG_MQH__
#define __RISK_CONFIG_MQH__

// Limite máximo de risco por operação (em % do saldo da conta)
input double MAX_RISK_PERCENT = 2.0;

// Limite diário de perda (em % do saldo inicial do dia)
input double DAILY_LOSS_LIMIT_PERCENT = 5.0;

// Limite diário de lucro (pode ser usado para stop gain)
input double DAILY_PROFIT_TARGET_PERCENT = 10.0;

// Número máximo de trades por dia
input int MAX_TRADES_PER_DAY = 10;

// Fator de alavancagem permitido
input double LEVERAGE_FACTOR = 5.0;

// Habilitar controle de risco adaptativo com base na volatilidade
input bool ENABLE_VOLATILITY_BASED_RISK = true;

// Habilitar escalonamento de ordens baseado em fluxo direcional
input bool ENABLE_ORDER_SCALING = true;

// Lotes mínimos e máximos permitidos
input double MIN_LOT_SIZE = 0.1;
input double MAX_LOT_SIZE = 100.0;

// Tamanho inicial do lote para escalonamento
input double INITIAL_SCALING_LOT = 0.1;

// Fator de crescimento para lotes escalonados (exponencial ou linear)
input double SCALING_FACTOR = 2.0;
input bool USE_EXPONENTIAL_SCALING = true;

// Delay mínimo entre ordens consecutivas (em segundos)
input int ORDER_DELAY_SECONDS = 60;

#endif // __RISK_CONFIG_MQH__ 