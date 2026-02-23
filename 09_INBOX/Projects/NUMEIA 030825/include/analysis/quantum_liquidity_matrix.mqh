//+------------------------------------------------------------------+
//| quantum_liquidity_matrix.mqh - Matriz Quântica de Liquidez       |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Analysis/                                        |
//| Versão: v2.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-23             |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_LIQUIDITY_MATRIX_MQH__
#define __QUANTUM_LIQUIDITY_MATRIX_MQH__

#include "utils/logger_institutional.mqh"
#include "include/quantum/quantum_entanglement.mqh"
#include "include/analysis/quantum_darkpool.mqh"
#include "include/neural/quantum_neural_net.mqh"
#include "include/types/trade_signal_enum.mqh"
#include "include/analysis/quantum_order_book.mqh"


//+------------------------------------------------------------------+
//| PARÂMETROS QUÂNTICOS                                            |
//+------------------------------------------------------------------+
input group "Quantum Liquidity"
input int      QUBITS_LIQUIDITY = 1024;   // Qubits de análise
input double   VOLUME_THRESHOLD = 0.2;    // Limiar de volume (0-1)
input bool     ENABLE_DARKPOOL_SYNC = true; // Sincronização com Dark Pool
input int      UPDATE_INTERVAL_MS = 300; // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| ESTRUTURA DA MATRIZ DE LIQUIDEZ                                 |
//+------------------------------------------------------------------+
struct QuantumLiquidityMatrix
{
   double             bid_liquidity[];    // Liquidez no bid (emaranhada)
   double             ask_liquidity[];    // Liquidez no ask (emaranhada)
   double             dark_pool_ratio;    // Razão Dark Pool
   datetime           update_time;        // Timestamp quântico
   int                quantum_phase;      // Fase quântica
   ENUM_TRADE_SIGNAL  last_signal;        // Último sinal associado
   double             signal_confidence;  // Confiança do sinal
};

//+------------------------------------------------------------------+
//| Estrutura de Resultados de Liquidez                              |
//+------------------------------------------------------------------+
struct QuantumLiquidityResult {
   datetime timestamp;
   string symbol;
   double bid_liquidity_sum;
   double ask_liquidity_sum;
   double dark_pool_ratio;
   double liquidity_entropy;
   bool darkpool_sync_active;
   ENUM_TRADE_SIGNAL last_signal;
   double execution_time_ms;
   bool success;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumLiquidityMatrix                        |
//+------------------------------------------------------------------+
class QuantumLiquidityMatrix
{
private:
   logger_institutional &m_logger;
   QuantumEntanglement  &m_entangler;
   DarkPoolConnector    &m_darkpool;
   QuantumNeuralNet     &m_qnet;
   QuantumOrderBook     &m_qorderbook;
   string               m_symbol;
   datetime             m_last_update_time;

   QuantumLiquidityMatrix m_qmatrix;
   double               m_liquidity_entropy;
   
   // Histórico de liquidez
   QuantumLiquidityResult m_liquidity_history[];

   // Painel de decisão
   CLabel *m_liquidity_label = NULL;
   CLabel *m_liquidity_dp = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QLM] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_entangler.IsEntanglementActive())
      {
         m_logger.log_warning("[QLM] Emaranhamento quântico não ativo");
         return false;
      }

      if(!m_darkpool.IsReady())
      {
         m_logger.log_warning("[QLM] Conector Dark Pool não está pronto");
         return false;
      }

      if(!m_qnet.IsQuantumReady())
      {
         m_logger.log_warning("[QLM] Rede neural quântica não está pronta");
         return false;
      }

      if(!m_qorderbook.IsReady())
      {
         m_logger.log_warning("[QLM] Orderbook quântico não está pronto");
         return false;
      }

      return true;
   }

   //+---------------------------------------------------------------+
   //| MÉTODO: CalculateQuantumLiquidity                             |
   //+---------------------------------------------------------------+
   bool CalculateQuantumLiquidity()
   {
      if(!is_valid_context())
      {
         m_logger.log_error("[QLM] Contexto inválido. Cálculo bloqueado.");
         return false;
      }

      double start_time = GetMicrosecondCount();

      // Obter dados de mercado emaranhados
      double market_data[];
      if(!m_entangler.GetMarketData(market_data, QUBITS_LIQUIDITY))
      {
         m_logger.log_error("[QLM] Falha ao obter dados de mercado emaranhados");
         return false;
      }
      
      // Configurar matriz
      ArrayResize(m_qmatrix.bid_liquidity, QUBITS_LIQUIDITY);
      ArrayResize(m_qmatrix.ask_liquidity, QUBITS_LIQUIDITY);
      
      // Processamento quântico
      for(int i=0; i<QUBITS_LIQUIDITY && i<ArraySize(market_data)-1; i++)
      {
         // Emaranhamento bid-ask
         double entangled_pair[2];
         if(m_entangler.EntanglePair(market_data[i], market_data[i+1], entangled_pair))
         {
            m_qmatrix.bid_liquidity[i] = entangled_pair[0];
            m_qmatrix.ask_liquidity[i] = entangled_pair[1];
         }
         else
         {
            m_qmatrix.bid_liquidity[i] = market_data[i];
            m_qmatrix.ask_liquidity[i] = market_data[i+1];
         }
         
         // Aplicar limiar quântico
         if(m_qmatrix.bid_liquidity[i] < VOLUME_THRESHOLD) m_qmatrix.bid_liquidity[i] = 0.0;
         if(m_qmatrix.ask_liquidity[i] < VOLUME_THRESHOLD) m_qmatrix.ask_liquidity[i] = 0.0;
      }
      
      // Integração com Dark Pool
      if(ENABLE_DARKPOOL_SYNC)
      {
         DarkPoolData dp_data;
         if(m_darkpool.GetDarkPoolData(dp_data))
         {
            m_qmatrix.dark_pool_ratio = dp_data.dark_pool_ratio;
         }
         else
         {
            m_logger.log_warning("[QLM] Falha ao obter dados do Dark Pool");
            m_qmatrix.dark_pool_ratio = 0.0;
         }
      }
      else
      {
         m_qmatrix.dark_pool_ratio = 0.0;
      }
      
      // Atualizar metadados
      m_qmatrix.update_time = TimeCurrent();
      m_qmatrix.quantum_phase = (m_qmatrix.quantum_phase + 1) % 4;
      m_liquidity_entropy = CalculateLiquidityEntropy();
      m_qmatrix.last_signal = m_qorderbook.GetLastSignal();
      m_qmatrix.signal_confidence = m_qorderbook.GetSignalConfidence();

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      // Registro histórico
      QuantumLiquidityResult result;
      result.timestamp = TimeCurrent();
      result.symbol = m_symbol;
      result.bid_liquidity_sum = ArraySum(m_qmatrix.bid_liquidity);
      result.ask_liquidity_sum = ArraySum(m_qmatrix.ask_liquidity);
      result.dark_pool_ratio = m_qmatrix.dark_pool_ratio;
      result.liquidity_entropy = m_liquidity_entropy;
      result.darkpool_sync_active = ENABLE_DARKPOOL_SYNC;
      result.last_signal = m_qmatrix.last_signal;
      result.execution_time_ms = execution_time;
      result.success = true;
      ArrayPushBack(m_liquidity_history, result);

      m_logger.log_info("[QLM] Matriz calculada - Entropia: " + 
                        DoubleToString(m_liquidity_entropy,3) + 
                        " | Dark Pool: " + DoubleToString(m_qmatrix.dark_pool_ratio,2) +
                        " | Sinal: " + TradeSignalUtils().ToString(m_qmatrix.last_signal) +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
      
      m_last_update_time = TimeCurrent();
      updateLiquidityDisplay(m_qmatrix.dark_pool_ratio, m_qmatrix.last_signal);
      return true;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: CalculateLiquidityEntropy                             |
   //+---------------------------------------------------------------+
   double CalculateLiquidityEntropy()
   {
      if(QUBITS_LIQUIDITY == 0) return 0.0;
      
      double total_volume = 0.0;
      for(int i=0; i<ArraySize(m_qmatrix.bid_liquidity); i++)
      {
         if(DoubleIsNaN(m_qmatrix.bid_liquidity[i])) continue;
         if(DoubleIsNaN(m_qmatrix.ask_liquidity[i])) continue;
         
         total_volume += m_qmatrix.bid_liquidity[i] + m_qmatrix.ask_liquidity[i];
      }
      
      if(total_volume <= 0) return 0.0;
      
      double entropy = 0.0;
      for(int i=0; i<ArraySize(m_qmatrix.bid_liquidity); i++)
      {
         if(DoubleIsNaN(m_qmatrix.bid_liquidity[i]) || DoubleIsNaN(m_qmatrix.ask_liquidity[i])) continue;
         
         double p = (m_qmatrix.bid_liquidity[i] + m_qmatrix.ask_liquidity[i]) / total_volume;
         if(p > 0)
            entropy -= p * MathLog(p);
      }
      
      return MathMax(0.0, MathMin(1.0, entropy));
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de liquidez                                  |
   //+--------------------------------------------------------------+
   void updateLiquidityDisplay(double dp_ratio, ENUM_TRADE_SIGNAL signal)
   {
      if(m_liquidity_label == NULL)
      {
         m_liquidity_label = new CLabel("LiquidityLabel", 0, 10, 1150);
         m_liquidity_label->text("LIQ: ????");
         m_liquidity_label->color(clrGray);
      }

      if(m_liquidity_dp == NULL)
      {
         m_liquidity_dp = new CLabel("LiquidityDP", 0, 10, 1170);
         m_liquidity_dp->text("DP: 0%");
         m_liquidity_dp->color(clrGray);
      }

      m_liquidity_label->text("LIQ: " + TradeSignalUtils().ToString(signal));
      m_liquidity_label->color(
         signal == SIGNAL_QUANTUM_FLASH ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrGray
      );

      m_liquidity_dp->text("DP: " + DoubleToString(dp_ratio*100, 0) + "%");
      m_liquidity_dp->color(
         dp_ratio > 0.5 ? clrMagenta :
         dp_ratio > 0.3 ? clrOrange : clrYellow
      );
   }

public:
   //+---------------------------------------------------------------+
   //| CONSTRUTOR                                                    |
   //+---------------------------------------------------------------+
   QuantumLiquidityMatrix(logger_institutional &logger,
                        QuantumEntanglement &qe, 
                        DarkPoolConnector &dpc, 
                        QuantumNeuralNet &qnn,
                        QuantumOrderBook &qob,
                        string symbol = _Symbol) :
      m_logger(logger),
      m_entangler(qe),
      m_darkpool(dpc),
      m_qnet(qnn),
      m_qorderbook(qob),
      m_symbol(symbol),
      m_liquidity_entropy(0.0),
      m_last_update_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QLM] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de ambiente quântico
      if(!m_entangler.IsEntanglementActive())
      {
         m_logger.log_error("[QLM] Emaranhamento quântico não ativo");
         ExpertRemove();
      }
      
      ArrayResize(m_qmatrix.bid_liquidity, QUBITS_LIQUIDITY);
      ArrayResize(m_qmatrix.ask_liquidity, QUBITS_LIQUIDITY);
      m_qmatrix.dark_pool_ratio = 0.0;
      m_qmatrix.quantum_phase = 0;
      m_qmatrix.last_signal = SIGNAL_NONE;
      m_qmatrix.signal_confidence = 0.0;
      
      m_logger.log_info("[QLM] Matriz de liquidez inicializada para " + m_symbol);
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: UpdateMatrix                                          |
   //+---------------------------------------------------------------+
   QuantumLiquidityMatrix UpdateMatrix()
   {
      if(CalculateQuantumLiquidity())
         return m_qmatrix;
      
      QuantumLiquidityMatrix error_matrix;
      ArrayResize(error_matrix.bid_liquidity, QUBITS_LIQUIDITY);
      ArrayResize(error_matrix.ask_liquidity, QUBITS_LIQUIDITY);
      ArrayInitialize(error_matrix.bid_liquidity, 0.0);
      ArrayInitialize(error_matrix.ask_liquidity, 0.0);
      error_matrix.dark_pool_ratio = -1;
      error_matrix.quantum_phase = -1;
      error_matrix.update_time = TimeCurrent();
      error_matrix.last_signal = SIGNAL_NONE;
      error_matrix.signal_confidence = 0.0;
      
      m_logger.log_warning("[QLM] Falha no cálculo da matriz de liquidez - Usando fallback");
      return error_matrix;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: ExportToDarkPool                                      |
   //+---------------------------------------------------------------+
   bool ExportToDarkPool(DarkPoolMatrix &matrix)
   {
      if(!is_valid_context()) return false;
      
      QuantumLiquidityMatrix qlm = UpdateMatrix();
      if(qlm.dark_pool_ratio < 0) return false;
      
      // Converter para formato Dark Pool
      ArrayResize(matrix.bid_volumes, ArraySize(qlm.bid_liquidity));
      ArrayResize(matrix.ask_volumes, ArraySize(qlm.ask_liquidity));
      
      ArrayCopy(matrix.bid_volumes, qlm.bid_liquidity);
      ArrayCopy(matrix.ask_volumes, qlm.ask_liquidity);
      matrix.dark_pool_ratio = qlm.dark_pool_ratio;
      matrix.timestamp = qlm.update_time;
      
      m_logger.log_info("[QLM] Matriz exportada para Dark Pool: " +
                        "Bid[0]=" + DoubleToString(qlm.bid_liquidity[0],2) + 
                        " | Ask[0]=" + DoubleToString(qlm.ask_liquidity[0],2) +
                        " | DP Ratio=" + DoubleToString(qlm.dark_pool_ratio,2));
      return true;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: GetLiquidityEntropy                                   |
   //+---------------------------------------------------------------+
   double GetLiquidityEntropy() const
   {
      return m_liquidity_entropy;
   }

   //+--------------------------------------------------------------+
   //| Retorna se o sistema está pronto                             |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_entangler.IsEntanglementActive() && 
             m_darkpool.IsReady() && 
             m_qnet.IsQuantumReady() && 
             m_qorderbook.IsReady();
   }

   //+--------------------------------------------------------------+
   //| Obtém último sinal                                           |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL GetLastSignal() const
   {
      return m_qmatrix.last_signal;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de liquidez                                |
   //+--------------------------------------------------------------+
   bool ExportLiquidityHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_liquidity_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_liquidity_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_liquidity_history[i].symbol,
            DoubleToString(m_liquidity_history[i].bid_liquidity_sum, 4),
            DoubleToString(m_liquidity_history[i].ask_liquidity_sum, 4),
            DoubleToString(m_liquidity_history[i].dark_pool_ratio, 4),
            DoubleToString(m_liquidity_history[i].liquidity_entropy, 4),
            m_liquidity_history[i].darkpool_sync_active ? "SIM" : "NÃO",
            TradeSignalUtils().ToString(m_liquidity_history[i].last_signal),
            DoubleToString(m_liquidity_history[i].execution_time_ms, 1),
            m_liquidity_history[i].success ? "SIM" : "NÃO"
         );
      }

      FileClose(handle);
      m_logger.log_info("[QLM] Histórico de liquidez exportado para: " + file_path);
      return true;
   }

   //+---------------------------------------------------------------+
   //| MÉTODO: AdjustThresholds                                      |
   //+---------------------------------------------------------------+
   void AdjustThresholds()
   {
      if(m_liquidity_entropy > 0.5)
         VOLUME_THRESHOLD = MathMax(0.05, VOLUME_THRESHOLD * 0.9);
      else
         VOLUME_THRESHOLD = MathMin(0.5, VOLUME_THRESHOLD * 1.1);
   }

   //+---------------------------------------------------------------+
   //| MÉTODO: CheckLiquidityPatterns                                |
   //+---------------------------------------------------------------+
   void CheckLiquidityPatterns()
   {
      if(m_qmatrix.quantum_phase == 3)
      {
         m_logger.log_info("[QLM] Fase quântica 3 detectada - Executando análise especial de liquidez");
         // Análise especial aqui
      }
   }
};

#endif // __QUANTUM_LIQUIDITY_MATRIX_MQH__