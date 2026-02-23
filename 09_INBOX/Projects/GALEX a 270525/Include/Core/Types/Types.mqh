//+------------------------------------------------------------------+
//|                                                      Types.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Enums
enum ENUM_MARKET_SIGNAL
{
   SIGNAL_NONE = 0,    // Sem sinal
   SIGNAL_BUY = 1,     // Sinal de compra
   SIGNAL_SELL = 2     // Sinal de venda
};

enum ENUM_LOG_LEVEL
{
   LOG_LEVEL_DEBUG = 0,   // Debug
   LOG_LEVEL_INFO = 1,    // Informação
   LOG_LEVEL_WARNING = 2, // Aviso
   LOG_LEVEL_ERROR = 3    // Erro
};

enum ENUM_RISK_STRATEGY
{
   RISK_STRATEGY_FIXED = 0,      // Risco fixo
   RISK_STRATEGY_ATR = 1,        // Risco baseado em ATR
   RISK_STRATEGY_VOLATILITY = 2  // Risco baseado em volatilidade
};

enum ENUM_TRAILING_TYPE
{
   TRAILING_NONE = 0,     // Sem trailing
   TRAILING_FIXED = 1,    // Trailing fixo
   TRAILING_ATR = 2,      // Trailing baseado em ATR
   TRAILING_PERCENT = 3   // Trailing percentual
};

enum ENUM_BREAKEVEN_TYPE
{
   BREAKEVEN_NONE = 0,    // Sem break even
   BREAKEVEN_FIXED = 1,   // Break even fixo
   BREAKEVEN_ATR = 2,     // Break even baseado em ATR
   BREAKEVEN_PERCENT = 3  // Break even percentual
};

// Estruturas
struct MarketData
{
   double price;          // Preço atual
   double volume;         // Volume atual
   double bid;           // Preço de compra
   double ask;           // Preço de venda
   double spread;        // Spread atual
   datetime time;        // Horário atual
   int digits;           // Dígitos do ativo
   double point;         // Valor do ponto
   double tick_size;     // Tamanho do tick
   double tick_value;    // Valor do tick
   double min_lot;       // Lote mínimo
   double max_lot;       // Lote máximo
   double lot_step;      // Incremento do lote
};

struct TradeParameters
{
   double lot_size;      // Tamanho do lote
   double stop_loss;     // Stop Loss
   double take_profit;   // Take Profit
   int magic_number;     // Número mágico
   string comment;       // Comentário
   datetime expiration;  // Expiração
   color arrow_color;    // Cor da seta
};

struct RiskParameters
{
   double initial_lots;          // Lote inicial
   double max_lots;             // Lote máximo
   double risk_percent;         // Percentual de risco
   int stop_loss_points;        // Stop Loss em pontos
   int take_profit_points;      // Take Profit em pontos
   bool use_atr_stop_loss;      // Usar ATR para Stop Loss
   double atr_stop_loss_mult;   // Multiplicador do ATR para Stop Loss
   bool use_atr_take_profit;    // Usar ATR para Take Profit
   double atr_take_profit_mult; // Multiplicador do ATR para Take Profit
   bool use_trailing_stop;      // Usar Trailing Stop
   int trailing_stop;           // Trailing Stop em pontos
   int trailing_step;           // Trailing Step em pontos
   bool use_break_even;         // Usar Break Even
   int break_even_points;       // Pontos para ativar Break Even
   int break_even_profit;       // Pontos de lucro após Break Even
};

struct PhysicsParameters
{
   double gravitational_force;   // Força gravitacional
   double potential_energy;      // Energia potencial
   double kinetic_energy;        // Energia cinética
   double acceleration;          // Aceleração
   double velocity;             // Velocidade
   double drag_coefficient;     // Coeficiente de arrasto
   double exhaust_velocity;     // Velocidade de exaustão
   double mass;                 // Massa
   double thrust;              // Empuxo
   double fuel_consumption;     // Consumo de combustível
};

struct TrajectoryParameters
{
   double angle;               // Ângulo da trajetória
   double distance;            // Distância percorrida
   double height;             // Altura
   double time_of_flight;     // Tempo de voo
   double range;              // Alcance
   double apogee;             // Apogeu
   double perigee;            // Perigeu
   double eccentricity;       // Excentricidade
   double period;             // Período
   double inclination;        // Inclinação
};

struct MarketAnalysis
{
   double trend_strength;      // Força da tendência
   double momentum;            // Momentum
   double volatility;          // Volatilidade
   double volume_flow;         // Fluxo de volume
   double price_action;        // Ação do preço
   double support_level;       // Nível de suporte
   double resistance_level;    // Nível de resistência
   double pivot_point;         // Ponto pivô
   double fibonacci_level;     // Nível de Fibonacci
   double ichimoku_cloud;      // Nuvem de Ichimoku
};

struct InstitutionalActivity
{
   double volume_pulse;        // Pulso de volume
   double energy_flow;         // Fluxo de energia
   double cosmic_frequency;    // Frequência cósmica
   double neural_confidence;   // Confiança neural
   double volume_threshold;    // Limiar de volume
   double price_threshold;     // Limiar de preço
   int lookback_period;        // Período de análise
   bool is_active;            // Atividade detectada
   datetime last_update;       // Última atualização
   string activity_type;       // Tipo de atividade
}; 