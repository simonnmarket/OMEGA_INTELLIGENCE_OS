//+------------------------------------------------------------------+
//| Include/Types/DefenseTypes.mqh                                   |
//| Tipos e estruturas para Sinais de Defesa Institucional           |
//| Padrão: Numeia EA – Núcleo Quântico                              |
//+------------------------------------------------------------------+
#ifndef __TYPES_DEFENSE_TYPES_MQH__
#define __TYPES_DEFENSE_TYPES_MQH__

//--- Enum institucional para status de sinal
enum DefenseSignal
{
   DEFENSE_NONE      = 0,
   DEFENSE_BUY_ZONE  = 1,
   DEFENSE_SELL_ZONE = -1
};

//--- Estrutura que representa o estado atual de defesa do mercado
struct DefenseStatus
{
   double         defenseLine;  // Nível institucional traçado
   double         hurst;        // Indicador de ciclo/ruído
   double         liquidity;    // Proxy de liquidez/tick volume
   double         footprint;    // Valor visual ou institucional marcado
   DefenseSignal  signal;       // Sinal classificado
};

#endif // __TYPES_DEFENSE_TYPES_MQH__
