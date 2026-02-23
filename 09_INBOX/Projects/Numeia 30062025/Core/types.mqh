//+------------------------------------------------------------------+
//| Core/types.mqh                                                   |
//| Definicoes globais de tipos para o Nucleo Quantico               |
//| Sistema Operacional para Fundos de Investimentos Algoritmicos    |
//+------------------------------------------------------------------+

#ifndef __TYPES_MQH__
#define __TYPES_MQH__

//--- Enumeracao de sinais de defesa institucional
enum DefenseSignal
{
   DEFENSE_NONE      = 0,     // Sem sinal ativo
   DEFENSE_BUY_ZONE  = 1,     // Zona de compra protegida
   DEFENSE_SELL_ZONE = -1     // Zona de venda protegida
};

//--- Estrutura de status de defesa
struct DefenseStatus
{
   double         defenseLine;  // Nivel institucional tracado
   double         hurst;        // Indicador de Hurst (persistencia)
   double         liquidity;    // Proxy de liquidez/tick volume
   double         footprint;    // Valor visual/institucional marcado
   DefenseSignal  signal;       // Sinal classificado
};

//--- Tipos adicionais (exemplos para expansao)
enum TradeDirection
{
   DIRECTION_LONG  = 0,
   DIRECTION_SHORT = 1
};

enum OrderTypeQuantum
{
   ORDER_BID_QUANTUM   = 0,
   ORDER_ASK_QUANTUM   = 1,
   ORDER_HEDGE_QUANTUM = 2
};

//--- Enums do sistema original (mantidos para compatibilidade)
enum ModuleStatus
{
   MODULE_OK = 0,
   MODULE_WARNING = 1,
   MODULE_ERROR = 2
};

enum AgentType
{
   AGENT_TRADING = 0,
   AGENT_RISK = 1,
   AGENT_PATTERN = 2,
   AGENT_MARKET_ANALYSIS = 3
};

enum ENUM_SIGNAL_TYPE
{
   SIGNAL_NONE = 0,
   SIGNAL_SPIKE_LONG = 1,
   SIGNAL_SPIKE_SHORT = 2,
   SIGNAL_UNCERTAIN = 3
};

//--- Estruturas do sistema original
struct TaskResult
{
   bool success;              // True se a tarefa foi concluída com sucesso
   string message;            // Mensagem informativa ou de erro
   datetime timestamp;        // Timestamp da execução
};

struct ExecutionContext
{
   string current_symbol;     // Símbolo em execução
   ENUM_TIMEFRAMES tf;        // Timeframe em uso
   datetime current_time;     // Tempo atual
   double equity;             // Capital atual
   int active_trades;         // Quantidade de trades abertos
};

//--- Constantes criticas para o sistema
const int MAX_RETRY_COUNT           = 3;
const double RISK_FACTOR            = 0.02;      // 2% por trade
const double MIN_LIQUIDITY_THRESHOLD= 1000000;   // Volume minimo aceitavel
const int QUANTUM_HEARTBEAT_FREQ   = 500;       // ms

#endif // __TYPES_MQH__ 