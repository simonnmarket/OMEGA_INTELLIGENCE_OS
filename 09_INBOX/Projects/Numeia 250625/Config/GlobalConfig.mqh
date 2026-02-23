//+------------------------------------------------------------------+
//| GlobalConfig.mqh - Configurações Globais da EA Numeia           |
//| Projeto: EA Numeia - Config                                     |
//| Função: Centraliza configurações globais do sistema             |
//+------------------------------------------------------------------+
#ifndef __GLOBAL_CONFIG_MQH__
#define __GLOBAL_CONFIG_MQH__

// Configurações básicas
input string EA_NAME = "Numeia EA";
input int MAGIC_NUMBER = 12345;

// Configurações de logging
input bool ENABLE_LOGGING = true;
input bool ENABLE_AUDIT_LOG = true;

// Configurações de execução
input bool ENABLE_TRADING = true;
input bool ENABLE_RISK_MANAGEMENT = true;

// Configurações de timeframes
input ENUM_TIMEFRAMES DEFAULT_TIMEFRAME = PERIOD_M15;
input ENUM_TIMEFRAMES ANALYSIS_TIMEFRAME = PERIOD_H1;

// Configurações de símbolos
input string DEFAULT_SYMBOL = "EURUSD";

#endif // __GLOBAL_CONFIG_MQH__ 