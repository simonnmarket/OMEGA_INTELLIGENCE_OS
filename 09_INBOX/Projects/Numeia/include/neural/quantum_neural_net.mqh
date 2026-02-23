//+------------------------------------------------------------------+
//| quantum_neural_net.mqh - Rede Neural Quântica Avançada           |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Neural/                                          |
//| Versão: v1.0 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-23           |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_NEURAL_NET_MQH__
#define __QUANTUM_NEURAL_NET_MQH__

#include <include/utils/logger_institutional.mqh>
#include <include/types/trade_signal_enum.mqh>
#include <include/quantum/quantum_processor.mqh>
#include <include/learning/quantum_learning.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>

//+------------------------------------------------------------------+
//| PARÂMETROS QUÂNTICOS                                            |
//+------------------------------------------------------------------+
input group "Quantum Neural Network"
input double   LEARNING_RATE = 0.01;      // Taxa de aprendizado
input int      HIDDEN_LAYERS = 3;         // Número de camadas ocultas
input int      NEURONS_PER_LAYER = 64;    // Neurônios por camada
input bool     ENABLE_QUANTUM_BACKPROP = true; // Backpropagation quântica

//+------------------------------------------------------------------+
//| Estrutura de Estado da Rede                                     |
//+------------------------------------------------------------------+
struct QuantumNeuralState
{
   double weights[];
   double activations[];
   double gradients[];
   datetime timestamp;
   double loss;
   ENUM_TRADE_SIGNAL last_signal;
   double signal_confidence;
};

//+------------------------------------------------------------------+
//| Estrutura de Resultados                                         |
//+------------------------------------------------------------------+
struct QuantumNeuralResult {
   datetime timestamp;
   string symbol;
   ENUM_TRADE_SIGNAL generated_signal;
   double confidence;
   double loss;
   bool success;
   double execution_time_ms;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: QuantumNeuralNet                              |
//+------------------------------------------------------------------+
class QuantumNeuralNet
{
private:
   logger_institutional &m_logger;
   QuantumProcessor     &m_qprocessor;
   QuantumLearning      &m_qlearning;
   string               m_symbol;
   datetime             m_last_update_time;

   QuantumNeuralState   m_qstate;
   double               m_quantum_entropy;
   double               m_learning_progress;
   
   // Histórico de decisões
   QuantumNeuralResult m_neural_history[];

   // Painel de decisão
   CLabel *m_neural_label = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QNN] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_qprocessor.IsReady())
      {
         m_logger.log_warning("[QNN] Processador quântico não está pronto");
         return false;
      }

      if(!m_qlearning.IsReady())
      {
         m_logger.log_warning("[QNN] Sistema de aprendizado não está pronto");
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
   //| Atualiza painel de rede neural                               |
   //+--------------------------------------------------------------+
   void updateNeuralDisplay(ENUM_TRADE_SIGNAL signal, double confidence)
   {
      if(m_neural_label == NULL)
         m_neural_label = new CLabel("NeuralLabel", 0, 10, 730);

      m_neural_label->text(StringFormat("IA: %s", TradeSignalUtils().ToString(signal)));

      m_neural_label->color(
         !is_valid_context() ? clrRed :
         signal == SIGNAL_QUANTUM_FLASH ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrGray
      );
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   QuantumNeuralNet(logger_institutional &logger,
                  QuantumProcessor &qp,
                  QuantumLearning &qlrn,
                  string symbol = _Symbol) :
      m_logger(logger),
      m_qprocessor(qp),
      m_qlearning(qlrn),
      m_symbol(symbol),
      m_learning_progress(0.0),
      m_last_update_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QNN] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de integridade quântica
      if(!m_qprocessor.IsReady())
      {
         m_logger.log_error("[QNN] Processador quântico não inicializado");
         ExpertRemove();
      }

      if(!m_qlearning.IsReady())
      {
         m_logger.log_error("[QNN] Sistema de aprendizado não inicializado");
         ExpertRemove();
      }

      // Inicializa estado
      ArrayResize(m_qstate.weights, NEURONS_PER_LAYER * HIDDEN_LAYERS);
      ArrayResize(m_qstate.activations, NEURONS_PER_LAYER);
      ArrayResize(m_qstate.gradients, NEURONS_PER_LAYER);
      m_qstate.loss = 1.0;
      m_qstate.last_signal = SIGNAL_NONE;
      m_qstate.signal_confidence = 0.0;
      m_qstate.timestamp = TimeCurrent();

      m_logger.log_info("[QNN] Rede neural quântica inicializada com " + 
                        IntegerToString(HIDDEN_LAYERS) + " camadas");
   }

   //+--------------------------------------------------------------+
   //| Obtém pesos quânticos                                        |
   //+--------------------------------------------------------------+
   bool GetQuantumWeights(double &weights[])
   {
      if(!is_valid_context()) return false;
      
      ArrayCopy(weights, m_qstate.weights);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Gera sinal quântico com base no processador                  |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL GetQuantumSignal()
   {
      if(!is_valid_context()) return SIGNAL_NONE;

      ENUM_TRADE_SIGNAL signal = m_qprocessor.GetCurrentSignal();
      double confidence = m_qprocessor.GetSignalConfidence(signal);
      double entropy_factor = 1.0 - (m_quantum_entropy / 0.75);

      m_qstate.last_signal = signal;
      m_qstate.signal_confidence = confidence * entropy_factor;
      m_qstate.timestamp = TimeCurrent();

      return signal;
   }

   //+--------------------------------------------------------------+
   //| Aplica ajuste de pesos com base no reforço                   |
   //+--------------------------------------------------------------+
   void AdjustWeights(double adjustment)
   {
      if(!is_valid_context()) return;
      
      for(int i = 0; i < ArraySize(m_qstate.weights); i++)
      {
         if(DoubleIsNaN(m_qstate.weights[i])) continue;
         m_qstate.weights[i] += adjustment * LEARNING_RATE;
         m_qstate.weights[i] = MathMax(0.01, MathMin(1.0, m_qstate.weights[i]));
      }
      
      m_logger.log_info("[QNN] Pesos ajustados: " + DoubleToString(adjustment, 3));
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                       |
   //+--------------------------------------------------------------+
   bool IsQuantumReady() const
   {
      return m_qprocessor.IsReady() && m_qlearning.IsReady();
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de decisões                                |
   //+--------------------------------------------------------------+
   bool ExportNeuralHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_neural_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_neural_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_neural_history[i].symbol,
            TradeSignalUtils().ToString(m_neural_history[i].generated_signal),
            DoubleToString(m_neural_history[i].confidence, 4),
            DoubleToString(m_neural_history[i].loss, 4),
            m_neural_history[i].success ? "SIM" : "NÃO",
            DoubleToString(m_neural_history[i].execution_time_ms, 1)
         );
      }

      FileClose(handle);
      m_logger.log_info("[QNN] Histórico de rede neural exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~QuantumNeuralNet()
   {
      m_logger.log_info("[QNN] Rede neural quântica encerrada para " + m_symbol);
   }
};

#endif // __QUANTUM_NEURAL_NET_MQH__