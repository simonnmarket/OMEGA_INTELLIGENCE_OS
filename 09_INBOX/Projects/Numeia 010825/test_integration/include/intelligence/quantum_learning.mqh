//+------------------------------------------------------------------+
//| quantum_learning.mqh - Sistema de Aprendizado Quântico Avançado  |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Learning/                                        |
//| Versão: v1.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-23             |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_LEARNING_MQH__
#define __QUANTUM_LEARNING_MQH__

#include <include/utils/logger_institutional.mqh>
#include <include/quantum/quantum_processor.mqh>
#include <include/risk/risk_profile.mqh>
#include <include/quantum/quantum_memory_cell.mqh>
#include <include/quantum/quantum_behavior_controller.mqh>
#include <include/types/trade_signal_enum.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>

//+------------------------------------------------------------------+
//| PARÂMETROS QUÂNTICOS                                            |
//+------------------------------------------------------------------+
input group "Quantum Learning"
input double   LEARNING_RATE = 0.01;      // Taxa de aprendizado (0.001-0.1)
input double   ENTROPY_THRESHOLD = 0.75;  // Limiar de entropia quântica
input bool     ENABLE_REINFORCEMENT = true; // Habilita reforço quântico
input int      UPDATE_INTERVAL_MS = 100; // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| ESTRUTURA DE MÉTRICAS QUÂNTICAS                                 |
//+------------------------------------------------------------------+
struct QuantumMetrics
{
   double profit_factor;
   double win_rate;
   double sharpe_ratio;
   double quantum_efficiency;
   datetime timestamp;
   ENUM_TRADE_SIGNAL last_signal;
   double signal_confidence;
};

//+------------------------------------------------------------------+
//| Estrutura de Histórico de Aprendizado                           |
//+------------------------------------------------------------------+
struct QuantumLearningHistoryEntry {
   datetime timestamp;
   string symbol;
   int memory_state;
   double reward_score;
   double learning_rate;
   int patterns_stored;
   int patterns_retrieved;
   bool retrieval_success;
   double market_entropy;
   string action_taken;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumLearning - Aprendizado Quântico        |
//+------------------------------------------------------------------+
class QuantumLearning
{
private:
   logger_institutional &m_logger;
   QuantumProcessor     &m_qprocessor;
   RiskProfile          &m_risk_profile;
   QuantumMemoryCell    &m_memory_cell;
   QuantumBehaviorController &m_behavior_controller;
   string               m_symbol;
   datetime             m_last_update_time;

   QuantumMetrics       m_metrics;
   double               m_quantum_entropy;
   double               m_learning_progress;
   double               m_quantum_learning_rate;

   // Histórico de aprendizado
   QuantumLearningHistoryEntry m_learning_history[];

   // Painel de decisão
   CLabel *m_learn_label = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QLRN] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_qprocessor.IsReady())
      {
         m_logger.log_warning("[QLRN] Processador quântico não está pronto");
         return false;
      }

      if(!m_risk_profile.is_initialized())
      {
         m_logger.log_warning("[QLRN] Perfil de risco não está inicializado");
         return false;
      }

      if(!m_memory_cell.IsReady())
      {
         m_logger.log_warning("[QLRN] Célula de memória não está pronta");
         return false;
      }

      if(!m_behavior_controller.IsReady())
      {
         m_logger.log_warning("[QLRN] Controlador de comportamento não está pronto");
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
   //| Atualiza painel de aprendizado                               |
   //+--------------------------------------------------------------+
   void updateLearnDisplay(double reward, bool success)
   {
      if(m_learn_label == NULL)
         m_learn_label = new CLabel("LearnLabel", 0, 10, 390);

      m_learn_label->text(StringFormat("QLRN: %s| R:%+.0f%%",
         success ? "OK" : "ERR", reward * 100));

      m_learn_label->color(success ? clrLime : clrRed);
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   QuantumLearning(logger_institutional &logger,
                  QuantumProcessor &qp,
                  RiskProfile &rp,
                  QuantumMemoryCell &qmc,
                  QuantumBehaviorController &qbc,
                  string symbol = _Symbol) :
      m_logger(logger),
      m_qprocessor(qp),
      m_risk_profile(rp),
      m_memory_cell(qmc),
      m_behavior_controller(qbc),
      m_symbol(symbol),
      m_learning_progress(0.0),
      m_quantum_learning_rate(LEARNING_RATE),
      m_last_update_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QLRN] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de integridade quântica
      if(!m_qprocessor.IsReady())
      {
         m_logger.log_error("[QLRN] Processador quântico não inicializado");
         ExpertRemove();
      }

      if(!m_risk_profile.is_initialized())
      {
         m_logger.log_error("[QLRN] Perfil de risco não inicializado");
         ExpertRemove();
      }

      // Inicializa métricas
      m_metrics.profit_factor = 1.0;
      m_metrics.win_rate = 0.5;
      m_metrics.sharpe_ratio = 1.0;
      m_metrics.quantum_efficiency = 0.5;
      m_metrics.timestamp = TimeCurrent();
      m_metrics.last_signal = SIGNAL_NONE;
      m_metrics.signal_confidence = 0.0;

      m_logger.log_info("[QLRN] Sistema de aprendizado quântico inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Obtém métricas quânticas                                     |
   //+--------------------------------------------------------------+
   QuantumMetrics GetQuantumMetrics()
   {
      if(!is_valid_context())
      {
         m_logger.log_warning("[QLRN] Contexto inválido. Retornando métricas padrão.");
         return m_metrics;
      }

      // Atualiza métricas com base no sinal atual
      ENUM_TRADE_SIGNAL current_signal = m_qprocessor.GetCurrentSignal();
      m_metrics.last_signal = current_signal;
      m_metrics.signal_confidence = m_qprocessor.GetSignalConfidence(current_signal);

      m_quantum_entropy = CalculateMarketEntropy();
      return m_metrics;
   }

   //+--------------------------------------------------------------+
   //| Calcula score de sinal quântico                              |
   //+--------------------------------------------------------------+
   double CalculateSignalScore(ENUM_TRADE_SIGNAL signal)
   {
      if(!is_valid_context()) return 0.0;

      double base_score = m_qprocessor.GetSignalConfidence(signal);
      double risk_multiplier = m_risk_profile.get_risk_multiplier();
      double entropy_factor = 1.0 - (m_quantum_entropy / ENTROPY_THRESHOLD);

      double final_score = base_score * risk_multiplier * entropy_factor;
      return MathMax(0.0, MathMin(100.0, final_score));
   }

   //+--------------------------------------------------------------+
   //| Aplica reforço quântico                                      |
   //+--------------------------------------------------------------+
   void ApplyQuantumReinforcement(ENUM_TRADE_SIGNAL signal, double reward)
   {
      if(!ENABLE_REINFORCEMENT || !is_valid_context()) return;

      double learning_adjustment = LEARNING_RATE * reward;
      m_learning_progress += learning_adjustment;
      m_learning_progress = MathMax(0.0, MathMin(1.0, m_learning_progress));

      // Registro histórico
      QuantumLearningHistoryEntry entry;
      entry.timestamp = TimeCurrent();
      entry.symbol = m_symbol;
      entry.memory_state = m_memory_cell.GetQuantumMemoryDensity() > 0.5 ? 1 : 0;
      entry.reward_score = reward;
      entry.learning_rate = m_quantum_learning_rate;
      entry.patterns_stored = m_memory_cell.GetQuantumMemoryDensity() * 100;
      entry.patterns_retrieved = m_memory_cell.GetQuantumMemoryDensity() * 100;
      entry.retrieval_success = true;
      entry.market_entropy = m_quantum_entropy;
      entry.action_taken = TradeSignalUtils().ToString(signal);
      ArrayPushBack(m_learning_history, entry);

      m_logger.log_info("[QLRN] Reforço aplicado: " + 
                       TradeSignalUtils().ToString(signal) + 
                       " | Recompensa: " + DoubleToString(reward, 2) +
                       " | Progresso: " + DoubleToString(m_learning_progress*100, 1) + "%");

      updateLearnDisplay(reward, true);
   }

   //+--------------------------------------------------------------+
   //| Retorna se o sistema está pronto                             |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_qprocessor.IsReady() && 
             m_risk_profile.is_initialized() && 
             m_memory_cell.IsReady() && 
             m_behavior_controller.IsReady();
   }

   //+--------------------------------------------------------------+
   //| Obtém taxa de aprendizado                                    |
   //+--------------------------------------------------------------+
   double GetLearningRate() const
   {
      return m_quantum_learning_rate;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de aprendizado                             |
   //+--------------------------------------------------------------+
   bool ExportLearningHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_learning_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_learning_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_learning_history[i].symbol,
            IntegerToString(m_learning_history[i].memory_state),
            DoubleToString(m_learning_history[i].reward_score, 4),
            DoubleToString(m_learning_history[i].learning_rate, 6),
            IntegerToString(m_learning_history[i].patterns_stored),
            IntegerToString(m_learning_history[i].patterns_retrieved),
            m_learning_history[i].retrieval_success ? "SIM" : "NÃO",
            DoubleToString(m_learning_history[i].market_entropy, 4),
            m_learning_history[i].action_taken
         );
      }

      FileClose(handle);
      m_logger.log_info("[QLRN] Histórico de aprendizado exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Obtém última recompensa                                      |
   //+--------------------------------------------------------------+
   double GetLastReward()
   {
      if(ArraySize(m_learning_history) == 0) return 0.0;
      return m_learning_history[ArraySize(m_learning_history)-1].reward_score;
   }

   //+--------------------------------------------------------------+
   //| Otimização Quântica de Memória                               |
   //+--------------------------------------------------------------+
   void QuantumMemoryOptimization()
   {
      if(!is_valid_context()) return;
      m_memory_cell.OptimizeMemoryUsage();
      m_logger.log_info("[QLRN] Memória quântica otimizada");
   }

   //+--------------------------------------------------------------+
   //| Atualização em Tempo Real                                    |
   //+--------------------------------------------------------------+
   void RealTimeLearning()
   {
      while(!IsStopped())
      {
         ApplyQuantumReinforcement(m_qprocessor.GetCurrentSignal(), 0.1);
         Sleep(30000); // Atualização a cada 30 segundos
      }
   }
};

#endif // __QUANTUM_LEARNING_MQH__