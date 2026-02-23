//+------------------------------------------------------------------+
//|                                                    MarketSignal.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "3.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Trade\Trade.mqh>
#include <Arrays\ArrayDouble.mqh>
#include "..\Interfaces\IModule.mqh"

//------------------- INPUTS QUÂNTICOS ------------------------------
input double QuantumBullThreshold = 0.7;    // Limiar Bull Forte
input double QuantumBearThreshold = 0.7;    // Limiar Bear Forte
input int    QuantumMemoryDepth   = 10;      // Profundidade Memória Quântica

//------------------- INPUTS DE FILTROS ------------------------------
input int    TrendPeriod = 14;              // Período para Análise de Tendência
input double VolatilityThreshold = 0.5;    // Limiar de Volatilidade
input double VolumeThreshold = 1.5;         // Limiar de Volume
input int    CorrelationPeriod = 20;        // Período para Correlação
input double MinCorrelation = 0.6;          // Correlação Mínima

// Enumerações
enum ENUM_MARKET_SIGNAL
{
   SIGNAL_NONE,  // Sem sinal
   SIGNAL_BUY,   // Sinal de compra
   SIGNAL_SELL   // Sinal de venda
};

enum ENUM_QUANTUM_STATE
{
   QUANTUM_BULL_STRONG,    // Estado quântico fortemente bullish
   QUANTUM_BULL_NEUTRAL,   // Estado quântico moderadamente bullish
   QUANTUM_NEUTRAL,        // Estado quântico neutro
   QUANTUM_BEAR_NEUTRAL,   // Estado quântico moderadamente bearish
   QUANTUM_BEAR_STRONG     // Estado quântico fortemente bearish
};

// Classe principal de sinais de mercado
class CMarketSignal : public ISignalGenerator, public IDataProcessor
{
private:
   ENUM_MARKET_SIGNAL m_current_signal;
   ENUM_QUANTUM_STATE m_quantum_state;
   double m_signal_strength;
   double m_volume_ratio;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
   // Buffer de memória quântica
   ENUM_QUANTUM_STATE m_state_buffer[10];
   double m_strength_buffer[10];
   int m_buffer_index;

   // Novas variáveis para análise
   double m_trend_strength;
   double m_volatility;
   double m_correlation;
   datetime m_last_signal_time;
   int m_signal_count;
   double m_success_rate;
   
   // Memory buffers
   CArrayDouble m_quantum_memory;
   CArrayDouble m_signal_memory;
   
public:
   // Construtor
   CMarketSignal()
   {
      m_current_signal = SIGNAL_NONE;
      m_quantum_state = QUANTUM_NEUTRAL;
      m_signal_strength = 0.0;
      m_volume_ratio = 1.0;
      m_version = "3.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
      m_buffer_index = 0;
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_correlation = 0.0;
      m_last_signal_time = 0;
      m_signal_count = 0;
      m_success_rate = 0.0;
      ArrayInitialize(m_state_buffer, QUANTUM_NEUTRAL);
      ArrayInitialize(m_strength_buffer, 0.0);
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_current_signal = SIGNAL_NONE;
      m_quantum_state = QUANTUM_NEUTRAL;
      m_signal_strength = 0.0;
      m_volume_ratio = 1.0;
      m_status = "Initialized";
      m_is_initialized = true;
      m_buffer_index = 0;
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_correlation = 0.0;
      m_last_signal_time = 0;
      m_signal_count = 0;
      m_success_rate = 0.0;
      ArrayInitialize(m_state_buffer, QUANTUM_NEUTRAL);
      ArrayInitialize(m_strength_buffer, 0.0);
      
      LogSignalGeneration(SIGNAL_NONE, "Inicialização do módulo");
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
      ShowQuantumDashboard();
   }
   
   bool Validate() override
   {
      if(!m_is_initialized)
      {
         Print("Erro: Módulo não inicializado!");
         return false;
      }
      if(m_signal_strength < -1.0 || m_signal_strength > 1.0)
      {
         Print("Erro: Força do sinal fora do intervalo válido!");
         return false;
      }
      if(m_volume_ratio < 0.1 || m_volume_ratio > 10.0)
      {
         Print("Alerta: Razão de volume extrema: ", m_volume_ratio);
      }
      return true;
   }
   
   void Cleanup() override
   {
      m_current_signal = SIGNAL_NONE;
      m_quantum_state = QUANTUM_NEUTRAL;
      m_signal_strength = 0.0;
      m_volume_ratio = 1.0;
      m_status = "Cleaned";
      m_is_initialized = false;
      m_buffer_index = 0;
      m_trend_strength = 0.0;
      m_volatility = 0.0;
      m_correlation = 0.0;
      m_last_signal_time = 0;
      m_signal_count = 0;
      m_success_rate = 0.0;
      ArrayInitialize(m_state_buffer, QUANTUM_NEUTRAL);
      ArrayInitialize(m_strength_buffer, 0.0);
      
      LogSignalGeneration(SIGNAL_NONE, "Limpeza do módulo");
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "MarketSignal"; }
   
   // Implementação de ISignalGenerator
   ENUM_MARKET_SIGNAL GenerateSignal() override
   {
      if(!m_is_initialized) return SIGNAL_NONE;
      
      ENUM_MARKET_SIGNAL signal = SIGNAL_NONE;
      
      if(m_quantum_state == QUANTUM_BULL_STRONG || m_quantum_state == QUANTUM_BULL_NEUTRAL)
         signal = SIGNAL_BUY;
      else if(m_quantum_state == QUANTUM_BEAR_STRONG || m_quantum_state == QUANTUM_BEAR_NEUTRAL)
         signal = SIGNAL_SELL;
         
      // Validar e confirmar sinal
      if(signal != SIGNAL_NONE)
      {
         if(!ValidateSignal(signal) || !ConfirmSignal(signal))
         {
            signal = SIGNAL_NONE;
            LogSignalGeneration(SIGNAL_NONE, "Sinal rejeitado após validação");
         }
         else
         {
            m_current_signal = signal;
            m_last_signal_time = TimeCurrent();
            m_signal_count++;
            LogSignalGeneration(signal, "Sinal gerado e confirmado");
         }
      }

      return signal;
   }
   
   double GetSignalStrength() const override { return m_signal_strength; }
   
   // Implementação de IDataProcessor
   bool ProcessData(const double &data[]) override
   {
      if(!m_is_initialized || ArraySize(data) < 2) return false;
      
      m_signal_strength = data[0];
      m_volume_ratio = data[1];
      
      // Atualizar métricas
      UpdateMetrics(data);
      
      return true;
   }
   
   bool GetProcessedData(double &data[]) override
   {
      if(!m_is_initialized) return false;
      
      ArrayResize(data, 5);
      data[0] = m_signal_strength;
      data[1] = m_volume_ratio;
      data[2] = m_trend_strength;
      data[3] = m_volatility;
      data[4] = m_correlation;
      
      return true;
   }
   
   // Métodos específicos do MarketSignal
   void UpdateSignal(const double &price[], const double &volume[], int period)
   {
      if(!m_is_initialized || ArraySize(price) < period || ArraySize(volume) < period) return;
      
      // Atualizar análises
      CalculateSignalStrength(price, volume, period);
      UpdateQuantumState();
      
      // Atualizar métricas
      m_trend_strength = CalculateTrendStrength(price, period);
      m_volatility = CalculateVolatility(price, period);
      m_correlation = CalculateCorrelation(price, volume, period);
      
      // Gerar sinal
      GenerateSignal();
   }
   
   // Getters
   ENUM_MARKET_SIGNAL GetSignal() const { return m_current_signal; }
   ENUM_QUANTUM_STATE GetQuantumState() const { return m_quantum_state; }
   double GetVolumeRatio() const { return m_volume_ratio; }
   double GetTrendStrength() const { return m_trend_strength; }
   double GetVolatility() const { return m_volatility; }
   double GetCorrelation() const { return m_correlation; }
   double GetSuccessRate() const { return m_success_rate; }
   
private:
   void CalculateSignalStrength(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return;
      
      double current_volume = volume[0];
      double avg_volume = 0.0;
      
      for(int i = 1; i < period && i < ArraySize(volume); i++)
      {
         avg_volume += volume[i];
      }
      
      avg_volume /= (period - 1);
      m_volume_ratio = (avg_volume > 0.0) ? current_volume / avg_volume : 1.0;
      
      double price_change = price[0] - price[1];
      m_signal_strength = price_change * m_volume_ratio;

      // Normalização para [-1,1]
      if(m_signal_strength > 1.0) m_signal_strength = 1.0;
      if(m_signal_strength < -1.0) m_signal_strength = -1.0;
   }
   
   void UpdateQuantumState()
   {
      // Atualiza buffer circular de estados
      m_state_buffer[m_buffer_index] = m_quantum_state;
      m_strength_buffer[m_buffer_index] = m_signal_strength;
      m_buffer_index = (m_buffer_index + 1) % QuantumMemoryDepth;

      // Cálculo de tendência ponderada
      double weighted_sum = 0.0;
      double weight = 1.0;
      double total_weight = 0.0;
      int idx;
      for(int i = 0; i < QuantumMemoryDepth; i++)
      {
         idx = (m_buffer_index - 1 - i + QuantumMemoryDepth) % QuantumMemoryDepth;
         weighted_sum += m_strength_buffer[idx] * weight;
         total_weight += weight;
         weight *= 0.7; // Peso decrescente exponencial
      }
      double avg_strength = (total_weight > 0) ? weighted_sum / total_weight : m_signal_strength;

      // Transição de estado quântico dinâmica
      if(avg_strength > QuantumBullThreshold)
         m_quantum_state = QUANTUM_BULL_STRONG;
      else if(avg_strength > 0.2)
         m_quantum_state = QUANTUM_BULL_NEUTRAL;
      else if(avg_strength < QuantumBearThreshold)
         m_quantum_state = QUANTUM_BEAR_STRONG;
      else if(avg_strength < -0.2)
         m_quantum_state = QUANTUM_BEAR_NEUTRAL;
      else
         m_quantum_state = QUANTUM_NEUTRAL;
   }
   
   // Dashboard de monitoramento
   void ShowQuantumDashboard()
   {
      string dashboard =
         "=== GALEX Quantum Dashboard ===\n" +
         "Estado Atual: " + EnumToString(m_quantum_state) + "\n" +
         "Força do Sinal: " + DoubleToString(m_signal_strength, 2) + "\n" +
         "Razão de Volume: " + DoubleToString(m_volume_ratio, 2) + "\n" +
         "Força da Tendência: " + DoubleToString(m_trend_strength, 2) + "\n" +
         "Volatilidade: " + DoubleToString(m_volatility, 2) + "\n" +
         "Correlação: " + DoubleToString(m_correlation, 2) + "\n" +
         "Taxa de Sucesso: " + DoubleToString(m_success_rate, 2) + "%\n" +
         "Memória Quântica:\n";
      for(int i = 0; i < QuantumMemoryDepth; i++)
      {
         int idx = (m_buffer_index - 1 - i + QuantumMemoryDepth) % QuantumMemoryDepth;
         dashboard += "[" + IntegerToString(i) + "] " +
                      EnumToString(m_state_buffer[idx]) +
                      " (" + DoubleToString(m_strength_buffer[idx], 2) + ")\n";
      }
      Comment(dashboard);
   }
   
   // Novos métodos de análise
   double CalculateTrendStrength(const double &price[], int period)
   {
      if(ArraySize(price) < period) return 0.0;
      
      double sum = 0.0;
      for(int i = 0; i < period; i++)
         sum += price[i];
      
      double sma = sum / period;
      double trend = 0.0;
      
      for(int i = 0; i < period; i++)
         trend += (price[i] - sma) * (i - period/2);
      
      return trend / (period * period);
   }
   
   double CalculateVolatility(const double &price[], int period)
   {
      if(ArraySize(price) < period) return 0.0;
      
      double sum = 0.0;
      double sum_squared = 0.0;
      
      for(int i = 0; i < period; i++)
      {
         sum += price[i];
         sum_squared += price[i] * price[i];
      }
      
      double mean = sum / period;
      double variance = (sum_squared / period) - (mean * mean);
      
      return MathSqrt(variance);
   }
   
   double CalculateCorrelation(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < period || ArraySize(volume) < period) return 0.0;
      
      double sum_price = 0.0;
      double sum_volume = 0.0;
      double sum_price_volume = 0.0;
      double sum_price_squared = 0.0;
      double sum_volume_squared = 0.0;
      
      for(int i = 0; i < period; i++)
      {
         sum_price += price[i];
         sum_volume += volume[i];
         sum_price_volume += price[i] * volume[i];
         sum_price_squared += price[i] * price[i];
         sum_volume_squared += volume[i] * volume[i];
      }
      
      double numerator = period * sum_price_volume - sum_price * sum_volume;
      double denominator = MathSqrt((period * sum_price_squared - sum_price * sum_price) *
                                  (period * sum_volume_squared - sum_volume * sum_volume));
      
      return (denominator != 0.0) ? numerator / denominator : 0.0;
   }
   
   // Validação de sinais
   bool ValidateSignal(const ENUM_MARKET_SIGNAL signal)
   {
      // Verificar tendência
      if(!IsTrendValid())
      {
         LogSignalGeneration(signal, "Tendência inválida");
         return false;
      }
      
      // Verificar volatilidade
      if(!IsVolatilityAcceptable())
      {
         LogSignalGeneration(signal, "Volatilidade muito alta");
         return false;
      }
      
      // Verificar volume
      if(!IsVolumeValid())
      {
         LogSignalGeneration(signal, "Volume insuficiente");
         return false;
      }
      
      // Verificar correlação
      if(!IsCorrelationValid())
      {
         LogSignalGeneration(signal, "Correlação muito baixa");
         return false;
      }
      
      return true;
   }
   
   bool IsTrendValid()
   {
      return MathAbs(m_trend_strength) > 0.1;
   }
   
   bool IsVolatilityAcceptable()
   {
      return m_volatility < VolatilityThreshold;
   }
   
   bool IsVolumeValid()
   {
      return m_volume_ratio > VolumeThreshold;
   }
   
   bool IsCorrelationValid()
   {
      return MathAbs(m_correlation) > MinCorrelation;
   }
   
   // Sistema de confirmação
   bool ConfirmSignal(const ENUM_MARKET_SIGNAL signal)
   {
      // Verificar tempo desde último sinal
      if(TimeCurrent() - m_last_signal_time < PeriodSeconds(PERIOD_M15))
      {
         LogSignalGeneration(signal, "Tempo insuficiente desde último sinal");
         return false;
      }
      
      // Verificar taxa de sucesso
      if(m_signal_count > 10 && m_success_rate < 50.0)
      {
         LogSignalGeneration(signal, "Taxa de sucesso muito baixa");
         return false;
      }
      
      return true;
   }
   
   // Logging detalhado
   void LogSignalGeneration(const ENUM_MARKET_SIGNAL signal, const string message)
   {
      string log = StringFormat(
         "GALEX Signal [%s] - %s\n" +
         "Força: %.2f, Volume: %.2f\n" +
         "Tendência: %.2f, Volatilidade: %.2f\n" +
         "Correlação: %.2f, Estado: %s",
         EnumToString(signal),
         message,
         m_signal_strength,
         m_volume_ratio,
         m_trend_strength,
         m_volatility,
         m_correlation,
         EnumToString(m_quantum_state)
      );
      
      Print(log);
   }
   
   // Atualização de métricas
   void UpdateMetrics(const double &data[])
   {
      // Atualizar taxa de sucesso
      if(m_signal_count > 0)
      {
         double success = 0.0;
         for(int i = 0; i < m_signal_count; i++)
         {
            if(data[i] > 0) success++;
         }
         m_success_rate = (success / m_signal_count) * 100.0;
      }
   }
}; 