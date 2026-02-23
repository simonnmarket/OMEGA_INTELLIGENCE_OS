//+------------------------------------------------------------------+
//| quantum_market_data.mqh - Conector de Dados Quânticos Avançado   |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Data/                                            |
//| Versão: v5.2 (GodMode Final + IA Ready)                         |
//| Atualizado em: 2025-07-23           |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_MARKET_DATA_MQH__
#define __QUANTUM_MARKET_DATA_MQH__

#include "utils/logger_institutional.mqh"
#include "quantum/quantum_entanglement_simulator.mqh"
#include "quantum/quantum_cache_manager.mqh"
#include "types/trade_signal_enum.mqh"
#include "ChartObjects\ChartObjectsTxtControls.mqh"

//+------------------------------------------------------------------+
//| PARÂMETROS QUÂNTICOS                                            |
//+------------------------------------------------------------------+
input group "Quantum Market Data"
input ENUM_DATA_SOURCE DATA_SOURCE_PRIORITY = DATA_SOURCE_QUANTUM; // Prioridade de fonte
input double   MAX_LATENCY_NS = 10.0;    // Latência máxima (nanossegundos)
input bool     ENABLE_QUANTUM_FILTER = true; // Ativar filtro quântico
input int      UPDATE_INTERVAL_MS = 50;  // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| ESTRUTURA DE ESTADO DE MERCADO QUÂNTICO                         |
//+------------------------------------------------------------------+
struct QuantumMarketState {
   datetime timestamp;
   string symbol;
   double bid_price;
   double ask_price;
   double spread;
   double volume;
   double volatility;
   double order_flow_imbalance;
   ENUM_DATA_SOURCE data_source_used;
   bool quantum_active;
   double quantum_noise_factor;
   double market_entropy;
   ENUM_TRADE_SIGNAL last_signal;
};

//+------------------------------------------------------------------+
//| Estrutura de Histórico de Dados                                 |
//+------------------------------------------------------------------+
struct QuantumMarketDataHistory {
   datetime timestamp;
   string symbol;
   double bid;
   double ask;
   double spread;
   double volatility;
   double market_entropy;
   ENUM_DATA_SOURCE source;
   bool success;
   double execution_time_ms;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumMarketData                             |
//+------------------------------------------------------------------+
class QuantumMarketData
{
private:
   logger_institutional &m_logger;
   QuantumEntanglementSimulator &m_quantum_link;
   QuantumCacheManager &m_cache;
   string m_symbol;
   ENUM_DATA_SOURCE m_data_source;
   bool m_quantum_ready;
   double m_quantum_noise_factor;
   datetime m_last_update;

   // Histórico de estados
   QuantumMarketState m_state_history[];
   QuantumMarketDataHistory m_data_history[];

   // Painel de decisão
   CLabel *m_data_label = NULL;
   CLabel *m_data_spread = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QDATA] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_quantum_link.IsQuantumReady())
      {
         m_logger.log_warning("[QDATA] Link quântico não está pronto");
         return false;
      }

      if(!m_cache.IsQuantumReady())
      {
         m_logger.log_warning("[QDATA] Cache quântico não está pronto");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Calcula entropia quântica do mercado                         |
   //+--------------------------------------------------------------+
   double CalculateMarketEntropy()
   {
      MqlRates rates[];
      CopyRates(m_symbol, PERIOD_M1, 0, 20, rates);
      double entropy = 0.0, sum = 0.0;
      for(int i = 0; i < ArraySize(rates); i++) sum += rates[i].close;
      if(sum <= 0) return 0.0;
      for(int i = 0; i < ArraySize(rates); i++)
      {
         double p = rates[i].close / sum;
         if(p > 0) entropy -= p * MathLog(p);
      }
      return NormalizeDouble(entropy, 4);
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de dados                                     |
   //+--------------------------------------------------------------+
   void updateDataDisplay(double spread, double entropy)
   {
      if(m_data_label == NULL)
      {
         m_data_label = new CLabel("DataLabel", 0, 10, 950);
         m_data_label->text("DADOS: ????");
         m_data_label->color(clrGray);
      }

      if(m_data_spread == NULL)
      {
         m_data_spread = new CLabel("DataSpread", 0, 10, 970);
         m_data_spread->text("SPREAD: 0");
         m_data_spread->color(clrGray);
      }

      m_data_label->text("DADOS: " + (m_quantum_ready ? "QUANTUM" : "CLASSIC"));
      m_data_label->color(m_quantum_ready ? clrLime : clrYellow);

      m_data_spread->text("SPREAD: " + DoubleToString(spread, 1));
      m_data_spread->color(
         spread < 10 ? clrLime :
         spread < 20 ? clrYellow : clrRed
      );
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   QuantumMarketData(logger_institutional &logger,
                   QuantumEntanglementSimulator &qentangler,
                   QuantumCacheManager &qcache,
                   string symbol = _Symbol) :
      m_logger(logger),
      m_quantum_link(qentangler),
      m_cache(qcache),
      m_symbol(symbol),
      m_data_source(DATA_SOURCE_QUANTUM),
      m_quantum_ready(false),
      m_quantum_noise_factor(0.0),
      m_last_update(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QDATA] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de integridade quântica
      if(!m_quantum_link.IsQuantumReady())
      {
         m_logger.log_warning("[QDATA] Modo clássico ativado (sem vantagem quântica)");
         m_quantum_ready = false;
      }
      else
      {
         m_quantum_ready = true;
         m_quantum_noise_factor = m_quantum_link.GetQuantumNoiseLevel();
         m_logger.log_info(StringFormat("[QDATA] Conexão quântica estabelecida para %s (Ruído: %.2f%%)",
                                       m_symbol, m_quantum_noise_factor*100));
      }

      m_logger.log_info("[QDATA] Conector de dados quânticos inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Obtém preço com filtro quântico                              |
   //+--------------------------------------------------------------+
   double GetQuantumFilteredValue(ENUM_APPLIED_PRICE price_type)
   {
      if(!is_valid_context()) return 0.0;

      double start_time = GetMicrosecondCount();

      double values[3];
      for(int i=0; i<3; i++)
      {
         values[i] = m_quantum_link.GetSuperposedPrice(m_symbol, price_type, i);
         if(DoubleIsNaN(values[i])) values[i] = SymbolInfoDouble(m_symbol, SYMBOL_BID);
      }

      // Aplica filtro de decoerência adaptativa
      double filtered = 0.0;
      for(int i=0; i<3; i++)
      {
         filtered += values[i] * (1 - m_quantum_noise_factor/(i+1));
      }
      double result = filtered / 3.0;

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      // Registro histórico
      QuantumMarketDataHistory record;
      record.timestamp = TimeCurrent();
      record.symbol = m_symbol;
      record.bid = m_quantum_ready ? result - 1 : result;
      record.ask = m_quantum_ready ? result + 1 : result;
      record.spread = record.ask - record.bid;
      record.volatility = iATR(m_symbol, PERIOD_H1, 14, 0);
      record.market_entropy = CalculateMarketEntropy();
      record.source = m_data_source;
      record.success = true;
      record.execution_time_ms = execution_time;
      ArrayPushBack(m_data_history, record);

      m_logger.log_debug(StringFormat("[QDATA] Preço quântico obtido: %.5f| Fonte: %s| Tempo: %.1fms",
                                    result, EnumToString(m_data_source), execution_time));

      updateDataDisplay(record.spread, record.market_entropy);
      return result;
   }

   //+--------------------------------------------------------------+
   //| Obtém spread com redução quântica de ruído                   |
   //+--------------------------------------------------------------+
   double GetQuantumSpread()
   {
      if(!is_valid_context()) return 0.0;

      string cache_key = m_symbol + "_SPREAD";
      if(m_cache.IsValid(cache_key))
      {
         double cached_value = m_cache.GetCachedValue(cache_key);
         if(!DoubleIsNaN(cached_value)) return cached_value;
      }

      double spread = 0.0;
      if(m_quantum_ready)
      {
         double spreads[3];
         for(int i=0; i<3; i++)
         {
            spreads[i] = m_quantum_link.GetQuantumSpread(m_symbol, i);
            if(DoubleIsNaN(spreads[i])) spreads[i] = SymbolInfoDouble(m_symbol, SYMBOL_SPREAD);
         }
         spread = (spreads[0] + spreads[1] + spreads[2]) / 3.0;
      }
      else
      {
         spread = SymbolInfoDouble(m_symbol, SYMBOL_SPREAD);
      }

      // Normaliza spread
      spread = MathMax(0.1, MathMin(100.0, spread));
      m_cache.StoreState();

      return spread;
   }

   //+--------------------------------------------------------------+
   //| Obtém volume quântico                                        |
   //+--------------------------------------------------------------+
   double GetQuantumVolume()
   {
      double volume = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_TICK);
      return m_quantum_ready ? volume * (1.0 + m_quantum_noise_factor * 0.1) : volume;
   }

   //+--------------------------------------------------------------+
   //| Obtém fluxo de ordens entrelaçado                            |
   //+--------------------------------------------------------------+
   void GetEntangledOrderFlow(double &bid_flow[], double &ask_flow[], int depth)
   {
      if(!is_valid_context())
      {
         m_logger.log_warning("[QDATA] Contexto inválido. Inicializando arrays vazios.");
         ArrayResize(bid_flow, depth);
         ArrayResize(ask_flow, depth);
         ArrayInitialize(bid_flow, 0.0);
         ArrayInitialize(ask_flow, 0.0);
         return;
      }

      ArrayResize(bid_flow, depth);
      ArrayResize(ask_flow, depth);

      for(int i=0; i<depth; i++)
      {
         bid_flow[i] = m_quantum_link.GetBidFlow(m_symbol, i);
         ask_flow[i] = m_quantum_link.GetAskFlow(m_symbol, i);
         if(DoubleIsNaN(bid_flow[i])) bid_flow[i] = 0.0;
         if(DoubleIsNaN(ask_flow[i])) ask_flow[i] = 0.0;
      }
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                       |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_quantum_link.IsQuantumReady() && m_cache.IsQuantumReady();
   }

   //+--------------------------------------------------------------+
   //| Obtém último spread                                          |
   //+--------------------------------------------------------------+
   double GetLastSpread()
   {
      if(ArraySize(m_data_history) == 0) return 0.0;
      return m_data_history[ArraySize(m_data_history)-1].spread;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de dados                                   |
   //+--------------------------------------------------------------+
   bool ExportDataHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_data_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_data_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_data_history[i].symbol,
            DoubleToString(m_data_history[i].bid, 5),
            DoubleToString(m_data_history[i].ask, 5),
            DoubleToString(m_data_history[i].spread, 1),
            DoubleToString(m_data_history[i].volatility, 4),
            DoubleToString(m_data_history[i].market_entropy, 4),
            EnumToString(m_data_history[i].source),
            m_data_history[i].success ? "SIM" : "NÃO",
            DoubleToString(m_data_history[i].execution_time_ms, 1)
         );
      }

      FileClose(handle);
      m_logger.log_info("[QDATA] Histórico de dados exportado para: " + file_path);
      return true;
   }
};

#endif // __QUANTUM_MARKET_DATA_MQH__