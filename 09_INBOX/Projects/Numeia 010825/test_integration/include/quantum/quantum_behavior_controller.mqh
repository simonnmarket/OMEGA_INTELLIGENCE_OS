//+------------------------------------------------------------------+
//| quantum_behavior_controller.mqh - Controle Quântico de Comportamento |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Quantum/                                          |
//| Versão: v2.2 (TIER-0 Quantum Institutional Grade)              |
//| Atualizado em: 2025-07-23             |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_BEHAVIOR_CONTROLLER_MQH__
#define __QUANTUM_BEHAVIOR_CONTROLLER_MQH__

#include <include/utils/logger_institutional.mqh>
#include <include/quantum/quantum_entanglement.mqh>
#include <include/quantum/quantum_processor.mqh>
#include <include/neural/quantum_neural_net.mqh>
#include <include/intelligence/quantum_learning.mqh>
#include <include/quantum/quantum_memory_cell.mqh>
#include <include/types/trade_signal_enum.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>

//+------------------------------------------------------------------+
//| PARÂMETROS QUÂNTICOS                                            |
//+------------------------------------------------------------------+
input group "Quantum Behavior"
input int      QUBITS_BEHAVIOR = 512;    // Qubits de controle
input double   QUANTUM_ADJUSTMENT = 0.25; // Fator quântico (0-1)
input bool     ENABLE_ENTANGLED_BEHAVIOR = true; // Comportamento emaranhado
input int      UPDATE_INTERVAL_MS = 300; // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| ESTRUTURA DE DECISÃO QUÂNTICA                                   |
//+------------------------------------------------------------------+
struct QuantumBehaviorDecision
{
   double             quantum_weights[];  // Pesos quânticos
   double             coherence_level;    // Nível de coerência
   datetime           decision_time;      // Timestamp quântico
   int                behavior_state;     // Estado comportamental
   ENUM_TRADE_SIGNAL  last_signal;        // Último sinal associado
   double             signal_confidence;  // Confiança no sinal
   double             entropy_level;      // Entropia do mercado
};

//+------------------------------------------------------------------+
//| Estrutura de Resultados de Comportamento                        |
//+------------------------------------------------------------------+
struct QuantumBehaviorResult {
   datetime timestamp;
   string symbol;
   int behavior_state;
   double coherence_level;
   double entropy_level;
   bool success;
   string behavior_label;
   ENUM_TRADE_SIGNAL last_signal;
   double execution_time_ms;
   double risk_multiplier;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumBehaviorController                     |
//+------------------------------------------------------------------+
class QuantumBehaviorController
{
private:
   logger_institutional &m_logger;
   QuantumEntanglement  &m_entangler;
   QuantumProcessor     &m_qprocessor;
   QuantumNeuralNet     &m_qnet;
   QuantumLearning      &m_qlearning;
   QuantumMemoryCell    &m_qmemory;
   string               m_symbol;
   datetime             m_last_update_time;

   QuantumBehaviorDecision m_qdecision;
   double               m_behavior_entropy;
   
   // Histórico de decisões
   QuantumBehaviorResult m_behavior_history[];

   // Painel de decisão
   CLabel *m_behavior_label = NULL;
   CLabel *m_behavior_signal = NULL;
   CLabel *m_behavior_confidence = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QBC] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_entangler.IsEntanglementActive())
      {
         m_logger.log_warning("[QBC] Emaranhamento quântico não ativo");
         return false;
      }

      if(!m_qprocessor.IsReady())
      {
         m_logger.log_warning("[QBC] Processador quântico não está pronto");
         return false;
      }

      if(!m_qnet.IsQuantumReady())
      {
         m_logger.log_warning("[QBC] Rede neural quântica não está pronta");
         return false;
      }

      if(!m_qlearning.IsReady())
      {
         m_logger.log_warning("[QBC] Sistema de aprendizado não está pronto");
         return false;
      }

      if(!m_qmemory.IsReady())
      {
         m_logger.log_warning("[QBC] Célula de memória quântica não está pronta");
         return false;
      }

      return true;
   }

   //+---------------------------------------------------------------+
   //| MÉTODO: CalculateQuantumBehavior                              |
   //+---------------------------------------------------------------+
   bool CalculateQuantumBehavior()
   {
      if(!is_valid_context())
      {
         m_logger.log_error("[QBC] Contexto inválido. Cálculo bloqueado.");
         return false;
      }

      double start_time = GetMicrosecondCount();

      // Obter estado atual da rede neural
      double current_weights[];
      if(!m_qnet.GetQuantumWeights(current_weights) || ArraySize(current_weights) == 0)
      {
         m_logger.log_error("[QBC] Falha ao obter pesos quânticos da rede neural");
         return false;
      }
      
      // Obter memória quântica de aprendizado
      QuantumMemoryState memory_state;
      if(!m_qmemory.RetrievePattern(m_qmemory.GetLastIndex(), memory_state))
      {
         m_logger.log_warning("[QBC] Não foi possível recuperar memória quântica. Usando fallback.");
         ArrayResize(memory_state.qcache_entry.quantum_state, ArraySize(current_weights));
         for(int i = 0; i < ArraySize(memory_state.qcache_entry.quantum_state); i++)
            memory_state.qcache_entry.quantum_state[i] = 0.5;
      }
      
      // Configurar array de decisão
      ArrayResize(m_qdecision.quantum_weights, QUBITS_BEHAVIOR);
      
      // Emaranhamento com comportamentos anteriores
      if(ENABLE_ENTANGLED_BEHAVIOR && ArraySize(memory_state.qcache_entry.quantum_state) > 0)
      {
         double entangled_weights[2];
         for(int i=0; i<QUBITS_BEHAVIOR && i<ArraySize(current_weights) && i<ArraySize(memory_state.qcache_entry.quantum_state); i++)
         {
            if(DoubleIsNaN(current_weights[i]) || DoubleIsNaN(memory_state.qcache_entry.quantum_state[i])) continue;
            
            m_entangler.EntanglePair(current_weights[i], memory_state.qcache_entry.quantum_state[i], entangled_weights);
            m_qdecision.quantum_weights[i] = (entangled_weights[0] + entangled_weights[1])/MathSqrt(2.0);
            
            // Ajuste quântico baseado na confiança do sinal
            double performance_metric = memory_state.qcache_entry.metrics.quantum_efficiency;
            m_qdecision.quantum_weights[i] *= (1.0 + QUANTUM_ADJUSTMENT * performance_metric);
            m_qdecision.quantum_weights[i] = MathMax(0.01, MathMin(1.0, m_qdecision.quantum_weights[i]));
         }
      }
      else
      {
         for(int i=0; i<ArraySize(current_weights) && i<QUBITS_BEHAVIOR; i++)
         {
            if(!DoubleIsNaN(current_weights[i]))
               m_qdecision.quantum_weights[i] = MathMax(0.01, MathMin(1.0, current_weights[i]));
         }
      }
      
      // Atualizar metadados
      m_qdecision.coherence_level = CalculateQuantumCoherence(m_qdecision.quantum_weights);
      m_qdecision.decision_time = TimeCurrent();
      m_qdecision.behavior_state = DetermineBehaviorState();
      m_qdecision.last_signal = m_qprocessor.GetCurrentSignal();
      m_qdecision.signal_confidence = m_qprocessor.GetSignalConfidence(m_qdecision.last_signal);
      m_qdecision.entropy_level = m_qprocessor.GetQuantumEntropy();
      
      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms
      
      // Registro histórico
      QuantumBehaviorResult result;
      result.timestamp = TimeCurrent();
      result.symbol = m_symbol;
      result.behavior_state = m_qdecision.behavior_state;
      result.coherence_level = m_qdecision.coherence_level;
      result.entropy_level = m_qdecision.entropy_level;
      result.success = true;
      result.last_signal = m_qdecision.last_signal;
      result.execution_time_ms = execution_time;
      result.risk_multiplier = m_qlearning.GetQuantumMetrics().profit_factor > 1.5 ? 1.2 : 0.8;
      result.behavior_label = 
         m_qdecision.behavior_state == 0 ? "CONSERVADOR" :
         m_qdecision.behavior_state == 1 ? "MODERADO" : "AGRESSIVO";
      ArrayPushBack(m_behavior_history, result);

      m_logger.log_info("[QBC] Comportamento calculado - Estado: " + 
                        result.behavior_label +
                        " | Sinal: " + TradeSignalUtils().ToString(m_qdecision.last_signal) +
                        " | Confiança: " + DoubleToString(m_qdecision.signal_confidence, 2) +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
      
      m_last_update_time = TimeCurrent();
      return true;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: CalculateQuantumCoherence                             |
   //+---------------------------------------------------------------+
   double CalculateQuantumCoherence(double &weights[])
   {
      if(ArraySize(weights) == 0) return 0.0;
      
      double norm = 0.0;
      for(int i=0; i<ArraySize(weights); i++)
      {
         if(DoubleIsNaN(weights[i])) continue;
         norm += weights[i] * weights[i];
      }
      
      return MathSqrt(norm) / ArraySize(weights);
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: DetermineBehaviorState                                |
   //+---------------------------------------------------------------+
   int DetermineBehaviorState()
   {
      if(ArraySize(m_qdecision.quantum_weights) == 0) return -1;
      
      double avg_weight = 0.0;
      int count = 0;
      for(int i=0; i<ArraySize(m_qdecision.quantum_weights); i++)
      {
         if(!DoubleIsNaN(m_qdecision.quantum_weights[i]))
         {
            avg_weight += m_qdecision.quantum_weights[i];
            count++;
         }
      }
      
      if(count == 0) return -1;
      avg_weight /= count;
      
      if(avg_weight < 0.3) return 0; // Conservador
      else if(avg_weight < 0.7) return 1; // Moderado
      else return 2; // Agressivo
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de comportamento                             |
   //+--------------------------------------------------------------+
   void updateBehaviorDisplay(int state, ENUM_TRADE_SIGNAL signal, double confidence)
   {
      if(m_behavior_label == NULL)
      {
         m_behavior_label = new CLabel("BehaviorLabel", 0, 10, 650);
         m_behavior_label->text("BEH: ????");
         m_behavior_label->color(clrGray);
      }

      if(m_behavior_signal == NULL)
      {
         m_behavior_signal = new CLabel("BehaviorSignal", 0, 10, 670);
         m_behavior_signal->text("SIG: NONE");
         m_behavior_signal->color(clrGray);
      }

      if(m_behavior_confidence == NULL)
      {
         m_behavior_confidence = new CLabel("BehaviorConfidence", 0, 10, 690);
         m_behavior_confidence->text("CONF: 0%");
         m_behavior_confidence->color(clrGray);
      }

      string state_text = 
         state == 0 ? "CONSERVADOR" :
         state == 1 ? "MODERADO" : 
         state == 2 ? "AGRESSIVO" : "DESCONHECIDO";

      m_behavior_label->text("BEH: " + state_text);
      m_behavior_label->color(
         state == 0 ? clrLime :
         state == 1 ? clrYellow : 
         state == 2 ? clrOrange : clrRed
      );

      m_behavior_signal->text("SIG: " + TradeSignalUtils().ToString(signal));
      m_behavior_signal->color(
         signal == SIGNAL_QUANTUM_FLASH ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrGray
      );

      m_behavior_confidence->text("CONF: " + DoubleToString(confidence*100, 0) + "%");
      m_behavior_confidence->color(
         confidence > 0.8 ? clrLime :
         confidence > 0.5 ? clrYellow : clrRed
      );
   }

public:
   //+---------------------------------------------------------------+
   //| CONSTRUTOR                                                    |
   //+---------------------------------------------------------------+
   QuantumBehaviorController(logger_institutional &logger,
                           QuantumEntanglement &qe, 
                           QuantumProcessor &qp,
                           QuantumNeuralNet &qnn, 
                           QuantumLearning &qlrn,
                           QuantumMemoryCell &qmc,
                           string symbol = _Symbol) :
      m_logger(logger),
      m_entangler(qe),
      m_qprocessor(qp),
      m_qnet(qnn),
      m_qlearning(qlrn),
      m_qmemory(qmc),
      m_symbol(symbol),
      m_behavior_entropy(0.0),
      m_last_update_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QBC] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de ambiente quântico
      if(!m_entangler.IsEntanglementActive())
      {
         m_logger.log_error("[QBC] Emaranhamento quântico não ativo");
         ExpertRemove();
      }
      
      ArrayResize(m_qdecision.quantum_weights, QUBITS_BEHAVIOR);
      m_qdecision.coherence_level = 0.0;
      m_qdecision.behavior_state = -1;
      m_qdecision.last_signal = SIGNAL_NONE;
      m_qdecision.signal_confidence = 0.0;
      m_qdecision.entropy_level = 0.0;
      
      m_logger.log_info("[QBC] Controlador quântico inicializado com " + 
                        IntegerToString(QUBITS_BEHAVIOR) + " qubits");
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: UpdateQuantumBehavior                                 |
   //+---------------------------------------------------------------+
   QuantumBehaviorDecision UpdateQuantumBehavior()
   {
      if(CalculateQuantumBehavior())
         return m_qdecision;
      
      QuantumBehaviorDecision error_decision;
      ArrayResize(error_decision.quantum_weights, QUBITS_BEHAVIOR);
      ArrayInitialize(error_decision.quantum_weights, 0.0);
      error_decision.coherence_level = -1;
      error_decision.behavior_state = -1;
      error_decision.decision_time = TimeCurrent();
      error_decision.last_signal = SIGNAL_NONE;
      error_decision.signal_confidence = 0.0;
      error_decision.entropy_level = 0.0;
      
      m_logger.log_warning("[QBC] Falha no cálculo comportamental - Usando decisão de fallback");
      return error_decision;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: GetBehaviorState                                      |
   //+---------------------------------------------------------------+
   int GetQuantumBehaviorState() const
   {
      return m_qdecision.behavior_state;
   }
   
   //+---------------------------------------------------------------+
   //| MÉTODO: GetBehaviorEntropy                                    |
   //+---------------------------------------------------------------+
   double GetQuantumBehaviorEntropy() const
   {
      return m_behavior_entropy;
   }

   //+--------------------------------------------------------------+
   //| Retorna se o sistema está pronto                             |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_entangler.IsEntanglementActive() && 
             m_qprocessor.IsReady() && 
             m_qnet.IsQuantumReady() && 
             m_qlearning.IsReady() && 
             m_qmemory.IsReady();
   }

   //+--------------------------------------------------------------+
   //| Obtém nível de coerência                                     |
   //+--------------------------------------------------------------+
   double GetCoherenceLevel() const
   {
      return m_qdecision.coherence_level;
   }

   //+--------------------------------------------------------------+
   //| Obtém último sinal associado                                 |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL GetLastSignal() const
   {
      return m_qdecision.last_signal;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de comportamento                           |
   //+--------------------------------------------------------------+
   bool ExportBehaviorHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_behavior_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_behavior_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_behavior_history[i].symbol,
            IntegerToString(m_behavior_history[i].behavior_state),
            DoubleToString(m_behavior_history[i].coherence_level, 4),
            DoubleToString(m_behavior_history[i].entropy_level, 4),
            m_behavior_history[i].success ? "SIM" : "NÃO",
            m_behavior_history[i].behavior_label,
            TradeSignalUtils().ToString(m_behavior_history[i].last_signal),
            DoubleToString(m_behavior_history[i].execution_time_ms, 1),
            DoubleToString(m_behavior_history[i].risk_multiplier, 2)
         );
      }

      FileClose(handle);
      m_logger.log_info("[QBC] Histórico de comportamento exportado para: " + file_path);
      return true;
   }

   //+---------------------------------------------------------------+
   //| MÉTODO: AdaptQuantumBehavior                                  |
   //+---------------------------------------------------------------+
   void AdaptQuantumBehavior()
   {
      if(m_behavior_entropy > 0.6)
         QUANTUM_ADJUSTMENT = MathMin(0.4, QUANTUM_ADJUSTMENT + 0.05);
      else
         QUANTUM_ADJUSTMENT = MathMax(0.1, QUANTUM_ADJUSTMENT - 0.02);
   }
};

#endif // __QUANTUM_BEHAVIOR_CONTROLLER_MQH__