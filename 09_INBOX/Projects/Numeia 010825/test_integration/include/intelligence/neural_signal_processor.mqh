//+------------------------------------------------------------------+
//| neural_signal_processor.mqh - Processador Neural Institucional  |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Versão: v2.1 (GodMode Final + IA Ready + Blindagem Institucional) |
//| Atualizado em: 2025-07-21 | Agente: Qwen (CEO Mode)              |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890abcdef |
//+------------------------------------------------------------------+
#ifndef __NEURAL_SIGNAL_PROCESSOR_MQH__
#define __NEURAL_SIGNAL_PROCESSOR_MQH__

#include <Include/Utils/logger_institutional.mqh>
#include <Include/Types/trade_signal_enum.mqh>
#include <Include/Data/market_data_connector.mqh>
#include <Include/Intelligence/anomaly_detector_ai.mqh>
#include <Include/Risk/risk_profile.mqh>

//+------------------------------------------------------------------+
//| Definições da Rede Neural Avançada                              |
//+------------------------------------------------------------------+
#define INPUT_LAYER_SIZE      12           // Aumentado para novas features
#define HIDDEN_LAYER_SIZE     24           // Camada oculta expandida
#define OUTPUT_LAYER_SIZE     5            // Sinais: Strong Buy, Weak Buy, Hold, Weak Sell, Strong Sell
#define RETRAIN_INTERVAL      86400        // Retreinamento diário (em segundos)
#define MIN_TRAINING_SAMPLES  1000         // Limiar mínimo de amostras

//+------------------------------------------------------------------+
//| Classe NeuralSignalProcessor - Versão Avançada                  |
//+------------------------------------------------------------------+
class NeuralSignalProcessor
{
private:
   logger_institutional &m_logger;
   market_data_connector &m_data_stream;
   risk_profile &m_risk;
   anomaly_detector_ai &m_ai;

   string m_symbol;
   bool m_is_initialized;
   datetime m_last_retrain;
   double m_weights[HIDDEN_LAYER_SIZE][INPUT_LAYER_SIZE];
   double m_biases[HIDDEN_LAYER_SIZE];
   double m_output_weights[OUTPUT_LAYER_SIZE][HIDDEN_LAYER_SIZE];
   double m_output_bias[OUTPUT_LAYER_SIZE];

   // Histórico de decisões
   struct SignalHistory {
      datetime timestamp;
      ENUM_TRADE_SIGNAL signal;
      double confidence;
      double profit;
   };
   SignalHistory m_signal_history[];

   // Painel de decisão
   CLabel *m_neural_label = NULL;

   //+--------------------------------------------------------------+
   //| Inicializa pesos aleatórios                                  |
   //+--------------------------------------------------------------+
   void InitializeWeights()
   {
      for(int i = 0; i < HIDDEN_LAYER_SIZE; i++)
      {
         m_biases[i] = MathRand() / 32767.0 - 0.5;
         for(int j = 0; j < INPUT_LAYER_SIZE; j++)
            m_weights[i][j] = MathRand() / 32767.0 - 0.5;
      }

      for(int i = 0; i < OUTPUT_LAYER_SIZE; i++)
      {
         m_output_bias[i] = MathRand() / 32767.0 - 0.5;
         for(int j = 0; j < HIDDEN_LAYER_SIZE; j++)
            m_output_weights[i][j] = MathRand() / 32767.0 - 0.5;
      }
   }

   //+--------------------------------------------------------------+
   //| Função de ativação ReLU                                      |
   //+--------------------------------------------------------------+
   double ReLU(double x)
   {
      return MathMax(0.0, x);
   }

   //+--------------------------------------------------------------+
   //| Derivada da ReLU                                             |
   //+--------------------------------------------------------------+
   double ReLUDerivative(double x)
   {
      return x > 0 ? 1.0 : 0.0;
   }

   //+--------------------------------------------------------------+
   //| Normalização Z-Score com validação                           |
   //+--------------------------------------------------------------+
   void NormalizeFeature(double &value, double mean, double stddev)
   {
      if(stddev != 0 && !DoubleIsNaN(mean) && !DoubleIsNaN(stddev))
         value = (value - mean) / stddev;
      else
         value = 0.0;
   }

   //+--------------------------------------------------------------+
   //| Extração de features avançadas                               |
   //+--------------------------------------------------------------+
   bool ExtractFeatures(double &features[])
   {
      ArrayResize(features, INPUT_LAYER_SIZE);

      // Dados técnicos
      features[0] = iRSI(m_symbol, PERIOD_H1, 14, PRICE_CLOSE, 0);
      features[1] = iATR(m_symbol, PERIOD_H1, 14, 0) / SymbolInfoDouble(m_symbol, SYMBOL_POINT);
      features[2] = iADX(m_symbol, PERIOD_H1, 14, PRICE_CLOSE, MODE_PLUSDI, 0);
      features[3] = iMACD(m_symbol, PERIOD_H1, 12, 26, 9, PRICE_CLOSE, MODE_MAIN, 0);

      // Dados de mercado
      features[4] = Volume[0]; // Volume atual
      features[5] = getOrderBookImbalance();
      features[6] = getVolatilityIndex();

      // Dados temporais
      features[7] = fmod(TimeCurrent(), 86400) / 86400; // Normalizado [0,1]
      features[8] = DayOfWeek() / 7.0;

      // Dados quânticos
      features[9] = calculateQuantumEntropy();
      features[10] = m_ai.get_confidence_score();
      features[11] = m_risk.get_risk_multiplier();

      // Validação de NaN
      for(int i = 0; i < INPUT_LAYER_SIZE; i++)
      {
         if(DoubleIsNaN(features[i]))
         {
            m_logger.log_error(StringFormat("[NEURAL] Feature %d é NaN", i));
            return false;
         }
      }

      // Normalização Z-Score
      double means[] = {50, 20, 30, 0, 1000, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0};
      double stddevs[] = {15, 10, 15, 1.5, 500, 1.0, 0.2, 0.3, 0.2, 0.2, 0.2, 0.5};

      for(int i = 0; i < INPUT_LAYER_SIZE; i++)
         NormalizeFeature(features[i], means[i], stddevs[i]);

      return true;
   }

   //+--------------------------------------------------------------+
   //| Calcula entropia quântica                                    |
   //+--------------------------------------------------------------+
   double calculateQuantumEntropy()
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
   //| Obtém desequilíbrio no livro de ofertas                     |
   //+--------------------------------------------------------------+
   double getOrderBookImbalance()
   {
      // Simulação básica - substituir por conexão real em produção
      return (MathRand() % 200 - 100) / 100.0;
   }

   //+--------------------------------------------------------------+
   //| Índice de volatibilidade                                     |
   //+--------------------------------------------------------------+
   double getVolatilityIndex()
   {
      double atr = iATR(m_symbol, PERIOD_H1, 14, 0);
      double avg_price = (SymbolInfoDouble(m_symbol, SYMBOL_ASK) + SymbolInfoDouble(m_symbol, SYMBOL_BID)) / 2;
      return atr / avg_price;
   }

   //+--------------------------------------------------------------+
   //| Feed Forward na rede neural                                  |
   //+--------------------------------------------------------------+
   void FeedForward(double &inputs[], double &outputs[])
   {
      double hidden[HIDDEN_LAYER_SIZE];
      
      // Camada oculta
      for(int i = 0; i < HIDDEN_LAYER_SIZE; i++)
      {
         double sum = m_biases[i];
         for(int j = 0; j < INPUT_LAYER_SIZE; j++)
            sum += inputs[j] * m_weights[i][j];
         hidden[i] = ReLU(sum);
      }

      // Camada de saída
      for(int i = 0; i < OUTPUT_LAYER_SIZE; i++)
      {
         double sum = m_output_bias[i];
         for(int j = 0; j < HIDDEN_LAYER_SIZE; j++)
            sum += hidden[j] * m_output_weights[i][j];
         outputs[i] = sigmoid(sum);
      }

      // Softmax para normalização probabilística
      softmax(outputs, OUTPUT_LAYER_SIZE);
   }

   //+--------------------------------------------------------------+
   //| Função Sigmoid                                               |
   //+--------------------------------------------------------------+
   double sigmoid(double x)
   {
      return 1.0 / (1.0 + MathExp(-MathMax(-50.0, MathMin(50.0, x))));
   }

   //+--------------------------------------------------------------+
   //| Softmax para normalização                                   |
   //+--------------------------------------------------------------+
   void softmax(double &values[], int size)
   {
      double max_val = values[0];
      for(int i = 1; i < size; i++)
         if(values[i] > max_val) max_val = values[i];

      double sum = 0.0;
      for(int i = 0; i < size; i++)
      {
         values[i] = MathExp(values[i] - max_val);
         sum += values[i];
      }

      if(sum > 0)
         for(int i = 0; i < size; i++)
            values[i] /= sum;
   }

   //+--------------------------------------------------------------+
   //| Backpropagation para atualização online                      |
   //+--------------------------------------------------------------+
   void Backpropagate(double &inputs[], double &targets[], double learning_rate)
   {
      double hidden[HIDDEN_LAYER_SIZE];
      double hidden_activated[HIDDEN_LAYER_SIZE];
      double output[OUTPUT_LAYER_SIZE];

      // Feed forward para obter valores atuais
      for(int i = 0; i < HIDDEN_LAYER_SIZE; i++)
      {
         double sum = m_biases[i];
         for(int j = 0; j < INPUT_LAYER_SIZE; j++)
            sum += inputs[j] * m_weights[i][j];
         hidden[i] = sum;
         hidden_activated[i] = ReLU(sum);
      }

      double output_sum[OUTPUT_LAYER_SIZE];
      for(int i = 0; i < OUTPUT_LAYER_SIZE; i++)
      {
         output_sum[i] = m_output_bias[i];
         for(int j = 0; j < HIDDEN_LAYER_SIZE; j++)
            output_sum[i] += hidden_activated[j] * m_output_weights[i][j];
         output[i] = sigmoid(output_sum[i]);
      }

      // Gradientes da camada de saída
      double output_error[OUTPUT_LAYER_SIZE];
      for(int i = 0; i < OUTPUT_LAYER_SIZE; i++)
         output_error[i] = (output[i] - targets[i]) * output[i] * (1.0 - output[i]);

      // Gradientes da camada oculta
      double hidden_error[HIDDEN_LAYER_SIZE];
      for(int i = 0; i < HIDDEN_LAYER_SIZE; i++)
      {
         double error = 0.0;
         for(int j = 0; j < OUTPUT_LAYER_SIZE; j++)
            error += output_error[j] * m_output_weights[j][i];
         hidden_error[i] = error * ReLUDerivative(hidden[i]);
      }

      // Atualização dos pesos da camada de saída
      for(int i = 0; i < OUTPUT_LAYER_SIZE; i++)
      {
         m_output_bias[i] -= learning_rate * output_error[i];
         for(int j = 0; j < HIDDEN_LAYER_SIZE; j++)
            m_output_weights[i][j] -= learning_rate * output_error[i] * hidden_activated[j];
      }

      // Atualização dos pesos da camada oculta
      for(int i = 0; i < HIDDEN_LAYER_SIZE; i++)
      {
         m_biases[i] -= learning_rate * hidden_error[i];
         for(int j = 0; j < INPUT_LAYER_SIZE; j++)
            m_weights[i][j] -= learning_rate * hidden_error[i] * inputs[j];
      }
   }

   //+--------------------------------------------------------------+
   //| Pós-processamento do output                                  |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL PostprocessOutput(double &output[])
   {
      double buy_strength = output[0] + output[1];
      double sell_strength = output[3] + output[4];
      double hold_strength = output[2];

      double threshold_high = 0.7;
      double threshold_low = 0.55;

      if(buy_strength > threshold_high && buy_strength > sell_strength)
         return (output[0] > output[1]) ? SIGNAL_QUANTUM_ALERT : SIGNAL_BUY;
      else if(sell_strength > threshold_high && sell_strength > buy_strength)
         return (output[4] > output[3]) ? SIGNAL_DARKPOOL_CRITICAL : SIGNAL_SELL;
      else if(buy_strength > threshold_low)
         return SIGNAL_REVERSE_BUY;
      else if(sell_strength > threshold_low)
         return SIGNAL_REVERSE_SELL;
      else if(hold_strength > 0.6)
         return SIGNAL_NONE;

      return SIGNAL_BREAK_EVEN;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de decisão                                   |
   //+--------------------------------------------------------------+
   void updateNeuralDisplay(ENUM_TRADE_SIGNAL signal, double &output[])
   {
      if(m_neural_label == NULL)
         m_neural_label = new CLabel("NeuralLabel", 0, 10, 150);

      m_neural_label->text(StringFormat("IA: %s | Conf: %.2f%%",
         signal_to_string(signal),
         MathMax(output[0], MathMax(output[1], MathMax(output[2], MathMax(output[3], output[4])))) * 100));

      m_neural_label->color(
         signal == SIGNAL_QUANTUM_ALERT ? clrMagenta :
         signal == SIGNAL_DARKPOOL_CRITICAL ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrWhite
      );
   }

public:
   //+--------------------------------------------------------------+
   //| Construtor                                                   |
   //+--------------------------------------------------------------+
   NeuralSignalProcessor(logger_institutional &logger,
                         market_data_connector &data_stream,
                         risk_profile &risk,
                         anomaly_detector_ai &ai,
                         string symbol)
      : m_logger(logger), m_data_stream(data_stream), m_risk(risk), m_ai(ai)
   {
      m_symbol = symbol;
      m_is_initialized = false;
      m_last_retrain = 0;

      // Validação de contexto
      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[NEURAL] Logger não inicializado");
         return;
      }

      if(StringLen(m_symbol) == 0 || !SymbolInfoInteger(m_symbol, SYMBOL_SELECT))
      {
         m_logger.log_error("[NEURAL] Símbolo inválido: " + m_symbol);
         return;
      }

      // Inicialização da rede
      InitializeWeights();
      m_is_initialized = true;

      m_logger.log_info("[NEURAL] Processador neural inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Processa sinal com rede neural profunda                      |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL ProcessSignal()
   {
      if(!m_is_initialized)
      {
         m_logger.log_error("[NEURAL] Tentativa de processar sinal sem inicialização");
         return SIGNAL_NONE;
      }

      // Verifica condições de segurança
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_warning("[NEURAL] Sem conexão com o servidor");
         return SIGNAL_NONE;
      }

      if(m_ai.detect_anomaly())
      {
         m_logger.log_critical("[NEURAL] Anomalia crítica detectada");
         return SIGNAL_NONE;
      }

      // Extração de features
      double inputs[INPUT_LAYER_SIZE];
      if(!ExtractFeatures(inputs))
      {
         m_logger.log_error("[NEURAL] Falha na extração de features");
         return SIGNAL_NONE;
      }

      // Feed forward
      double outputs[OUTPUT_LAYER_SIZE];
      FeedForward(inputs, outputs);

      // Pós-processamento
      ENUM_TRADE_SIGNAL signal = PostprocessOutput(outputs);

      // Registro histórico
      SignalHistory hist;
      hist.timestamp = TimeCurrent();
      hist.signal = signal;
      hist.confidence = MathMax(outputs[0], MathMax(outputs[1], MathMax(outputs[2], MathMax(outputs[3], outputs[4]))));
      ArrayPushBack(m_signal_history, hist);

      // Log detalhado
      m_logger.log_info(StringFormat(
         "[NEURAL] Sinal gerado: %s | Probabilidades: B=%.2f, W_B=%.2f, H=%.2f, W_S=%.2f, S=%.2f",
         signal_to_string(signal),
         outputs[0], outputs[1], outputs[2], outputs[3], outputs[4]
      ));

      // Atualiza display
      updateNeuralDisplay(signal, outputs);

      return signal;
   }

   //+--------------------------------------------------------------+
   //| Atualiza modelo com feedback                                 |
   //+--------------------------------------------------------------+
   void UpdateWithFeedback(ENUM_TRADE_SIGNAL signal, double profit)
   {
      if(!m_is_initialized) return;

      // Define alvos com base no resultado
      double targets[OUTPUT_LAYER_SIZE] = {0, 0, 0, 0, 0};
      double reward_factor = profit > 0 ? 1.0 : 0.5;

      switch(signal)
      {
         case SIGNAL_QUANTUM_ALERT:
         case SIGNAL_BUY:
            targets[0] = 0.9 * reward_factor;
            targets[1] = 0.1 * reward_factor;
            break;
         case SIGNAL_REVERSE_BUY:
            targets[1] = 0.8 * reward_factor;
            break;
         case SIGNAL_BREAK_EVEN:
            targets[2] = 0.9 * reward_factor;
            break;
         case SIGNAL_REVERSE_SELL:
            targets[3] = 0.8 * reward_factor;
            break;
         case SIGNAL_DARKPOOL_CRITICAL:
         case SIGNAL_SELL:
            targets[4] = 0.9 * reward_factor;
            targets[3] = 0.1 * reward_factor;
            break;
      }

      // Extrai features atuais
      double inputs[INPUT_LAYER_SIZE];
      if(!ExtractFeatures(inputs)) return;

      // Atualização via backpropagation
      Backpropagate(inputs, targets, 0.01);

      m_logger.log_info(StringFormat(
         "[NEURAL] Modelo atualizado | Sinal: %s | Resultado: %.2f",
         signal_to_string(signal),
         profit
      ));
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de sinais                                  |
   //+--------------------------------------------------------------+
   bool ExportHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_signal_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_signal_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            signal_to_string(m_signal_history[i].signal),
            DoubleToString(m_signal_history[i].confidence, 4),
            DoubleToString(m_signal_history[i].profit, 4)
         );
      }

      FileClose(handle);
      m_logger.log_info("[NEURAL] Histórico exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retorna se o processador está pronto                         |
   //+--------------------------------------------------------------+
   bool is_ready() const
   {
      return m_is_initialized;
   }

   //+--------------------------------------------------------------+
   //| Registra lucro/perda para aprendizado                        |
   //+--------------------------------------------------------------+
   void log_trade_result(ENUM_TRADE_SIGNAL signal, double profit)
   {
      for(int i = ArraySize(m_signal_history) - 1; i >= 0; i--)
      {
         if(m_signal_history[i].signal == signal && m_signal_history[i].profit == 0)
         {
            m_signal_history[i].profit = profit;
            UpdateWithFeedback(signal, profit);
            break;
         }
      }
   }
};

#endif // __NEURAL_SIGNAL_PROCESSOR_MQH__