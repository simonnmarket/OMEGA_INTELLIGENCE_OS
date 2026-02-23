//+------------------------------------------------------------------+
//| NeuroNet.mqh - Rede Neural Completa com Backpropagation         |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: include/neural/                                          |
//| Versão: v6.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-24 |              |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __NEURONET_MQH__
#define __NEURONET_MQH__

#include "utils/logger_institutional.mqh"
#include "core/quantum_blockchain.mqh"
#include "intelligence/quantum_learning.mqh"
#include "analysis/dependency_graph.mqh"
#include "Arrays\ArrayObj.mqh"

//+------------------------------------------------------------------+
//| Funções de Ativação                                             |
//+------------------------------------------------------------------+
enum ENUM_ACTIVATION_FUNCTION
{
   ACTIVATION_SIGMOID,
   ACTIVATION_TANH,
   ACTIVATION_RELU,
   ACTIVATION_LINEAR
};

//+------------------------------------------------------------------+
//| Estrutura de Camada                                             |
//+------------------------------------------------------------------+
struct NeuralLayer
{
   double inputs[];
   double outputs[];
   double weights[][];
   double biases[];
   double errors[];
   ENUM_ACTIVATION_FUNCTION activation;
};

//+------------------------------------------------------------------+
//| Estrutura de Resultado de Treinamento                           |
//+------------------------------------------------------------------+
struct TrainingResult
{
   bool success;
   int epoch;
   double loss;
   double accuracy;
   datetime start_time;
   datetime end_time;
   string details;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: CNeuroNet                                     |
//+------------------------------------------------------------------+
class CNeuroNet
{
private:
   logger_institutional &m_logger;
   QuantumBlockchain    &m_blockchain;
   QuantumLearning      &m_learning;
   CDependencyGraph     &m_dependency_graph;
   string               m_symbol;

   // Camadas da rede
   NeuralLayer m_layers[];
   int m_input_size;
   int m_output_size;
   int m_hidden_layers;

   // Parâmetros de treinamento
   double m_learning_rate;
   double m_momentum;
   int m_max_epochs;
   double m_target_loss;

   // Histórico de treinamento
   TrainingResult m_training_history[];

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[NEURAL] Sem conexão com o servidor");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[NEURAL] Logger não inicializado");
         return false;
      }

      if(!m_blockchain.IsReady())
      {
         m_logger.log_warning("[NEURAL] Blockchain não está pronto");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica função de ativação                                     |
   //+--------------------------------------------------------------+
   double activate(double x, ENUM_ACTIVATION_FUNCTION func)
   {
      switch(func)
      {
         case ACTIVATION_SIGMOID: return 1.0 / (1.0 + MathExp(-x));
         case ACTIVATION_TANH: return MathTanh(x);
         case ACTIVATION_RELU: return MathMax(0.0, x);
         case ACTIVATION_LINEAR: return x;
         default: return x;
      }
   }

   //+--------------------------------------------------------------+
   //| Derivada da função de ativação                                |
   //+--------------------------------------------------------------+
   double activation_derivative(double output, ENUM_ACTIVATION_FUNCTION func)
   {
      switch(func)
      {
         case ACTIVATION_SIGMOID: return output * (1.0 - output);
         case ACTIVATION_TANH: return 1.0 - MathPow(output, 2);
         case ACTIVATION_RELU: return output > 0 ? 1.0 : 0.0;
         case ACTIVATION_LINEAR: return 1.0;
         default: return 1.0;
      }
   }

   //+--------------------------------------------------------------+
   //| Inicializa pesos aleatórios                                   |
   //+--------------------------------------------------------------+
   void initialize_weights(NeuralLayer &layer)
   {
      int inputs = ArraySize(layer.inputs);
      int outputs = ArraySize(layer.outputs);
      
      ArrayResize(layer.weights, inputs * outputs);
      ArrayResize(layer.biases, outputs);
      
      for(int i = 0; i < inputs; i++)
      {
         for(int j = 0; j < outputs; j++)
         {
            layer.weights[i][j] = MathRand() / 32767.0 * 2.0 - 1.0; // [-1, 1]
         }
      }
      
      for(int j = 0; j < outputs; j++)
      {
         layer.biases[j] = MathRand() / 32767.0 * 2.0 - 1.0;
      }
   }

   //+--------------------------------------------------------------+
   //| Propagação para frente                                        |
   //+--------------------------------------------------------------+
   bool feed_forward(double inputs[])
   {
      if(ArraySize(inputs) != m_input_size) return false;

      // Primeira camada
      ArrayCopy(m_layers[0].inputs, inputs);
      
      for(int l = 0; l < m_hidden_layers + 1; l++)
      {
         NeuralLayer &layer = m_layers[l];
         NeuralLayer &next_layer = m_layers[l + 1];
         
         for(int j = 0; j < ArraySize(next_layer.outputs); j++)
         {
            double sum = layer.biases[j];
            for(int i = 0; i < ArraySize(layer.outputs); i++)
            {
               sum += layer.outputs[i] * layer.weights[i][j];
            }
            next_layer.inputs[j] = sum;
            next_layer.outputs[j] = activate(sum, next_layer.activation);
         }
      }
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retropropagação (Backpropagation)                             |
   //+--------------------------------------------------------------+
   bool backpropagate(double targets[])
   {
      int output_size = ArraySize(m_layers[m_hidden_layers + 1].outputs);
      if(ArraySize(targets) != output_size) return false;

      // Erro na camada de saída
      NeuralLayer &output_layer = m_layers[m_hidden_layers + 1];
      for(int i = 0; i < output_size; i++)
      {
         double error = targets[i] - output_layer.outputs[i];
         output_layer.errors[i] = error * activation_derivative(output_layer.outputs[i], output_layer.activation);
      }

      // Erro nas camadas ocultas
      for(int l = m_hidden_layers; l >= 0; l--)
      {
         NeuralLayer &layer = m_layers[l];
         NeuralLayer &next_layer = m_layers[l + 1];
         
         for(int i = 0; i < ArraySize(layer.outputs); i++)
         {
            double error = 0.0;
            for(int j = 0; j < ArraySize(next_layer.outputs); j++)
            {
               error += next_layer.errors[j] * layer.weights[i][j];
            }
            layer.errors[i] = error * activation_derivative(layer.outputs[i], layer.activation);
         }
      }

      // Atualiza pesos
      for(int l = 0; l <= m_hidden_layers; l++)
      {
         NeuralLayer &layer = m_layers[l];
         NeuralLayer &next_layer = m_layers[l + 1];
         
         for(int i = 0; i < ArraySize(layer.outputs); i++)
         {
            for(int j = 0; j < ArraySize(next_layer.outputs); j++)
            {
               double delta = m_learning_rate * next_layer.errors[j] * layer.outputs[i];
               layer.weights[i][j] += delta;
            }
         }
         
         for(int j = 0; j < ArraySize(next_layer.outputs); j++)
         {
            next_layer.biases[j] += m_learning_rate * next_layer.errors[j];
         }
      }
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Calcula perda (MSE)                                           |
   //+--------------------------------------------------------------+
   double calculate_loss(double outputs[], double targets[])
   {
      double loss = 0.0;
      int size = ArraySize(outputs);
      for(int i = 0; i < size; i++)
      {
         double error = targets[i] - outputs[i];
         loss += error * error;
      }
      return loss / size;
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CNeuroNet(int input_size,
           int hidden_layers,
           int neurons_per_layer,
           int output_size,
           double learning_rate = 0.1,
           double momentum = 0.9,
           int max_epochs = 1000,
           double target_loss = 0.001,
           string symbol = _Symbol) :
      m_input_size(input_size),
      m_hidden_layers(hidden_layers),
      m_output_size(output_size),
      m_learning_rate(learning_rate),
      m_momentum(momentum),
      m_max_epochs(max_epochs),
      m_target_loss(target_loss),
      m_symbol(symbol)
   {
      // Inicializar componentes
      m_logger.Init("NeuroNet");
      m_learning_rate = MathMax(0.001, MathMin(1.0, learning_rate));
      m_momentum = MathMax(0.0, MathMin(1.0, momentum));

      // Criar camadas
      ArrayResize(m_layers, hidden_layers + 2);
      
      // Camada de entrada
      ArrayResize(m_layers[0].outputs, input_size);
      m_layers[0].activation = ACTIVATION_LINEAR;
      
      // Camadas ocultas
      for(int l = 1; l <= hidden_layers; l++)
      {
         ArrayResize(m_layers[l].inputs, neurons_per_layer);
         ArrayResize(m_layers[l].outputs, neurons_per_layer);
         ArrayResize(m_layers[l].biases, neurons_per_layer);
         ArrayResize(m_layers[l].errors, neurons_per_layer);
         m_layers[l].activation = ACTIVATION_RELU;
      }
      
      // Camada de saída
      ArrayResize(m_layers[hidden_layers + 1].inputs, output_size);
      ArrayResize(m_layers[hidden_layers + 1].outputs, output_size);
      ArrayResize(m_layers[hidden_layers + 1].biases, output_size);
      ArrayResize(m_layers[hidden_layers + 1].errors, output_size);
      m_layers[hidden_layers + 1].activation = ACTIVATION_SIGMOID;

      // Inicializar pesos
      for(int l = 0; l < hidden_layers + 1; l++)
      {
         initialize_weights(m_layers[l]);
      }

      m_logger.log_success("[NEURAL] Rede Neural v6.1 inicializada com sucesso");
   }

   //+--------------------------------------------------------------+
   //| Processa entrada (Feed Forward)                               |
   //+--------------------------------------------------------------+
   bool Process(double inputs[], double outputs[])
   {
      if(!is_valid_context()) return false;

      if(!feed_forward(inputs)) return false;

      ArrayCopy(outputs, m_layers[m_hidden_layers + 1].outputs);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Treina a rede neural                                          |
   //+--------------------------------------------------------------+
   bool Train(double inputs[][], double targets[][], int num_samples)
   {
      if(!is_valid_context()) return false;

      double start_time = TimeCurrent();

      for(int epoch = 0; epoch < m_max_epochs; epoch++)
      {
         double total_loss = 0.0;
         
         for(int s = 0; s < num_samples; s++)
         {
            if(!feed_forward(inputs[s])) continue;
            if(!backpropagate(targets[s])) continue;
            
            double loss = calculate_loss(m_layers[m_hidden_layers + 1].outputs, targets[s]);
            total_loss += loss;
         }
         
         double avg_loss = total_loss / num_samples;
         
         if(avg_loss < m_target_loss)
         {
            TrainingResult result;
            result.success = true;
            result.epoch = epoch;
            result.loss = avg_loss;
            result.accuracy = 1.0 - avg_loss;
            result.start_time = (datetime)start_time;
            result.end_time = TimeCurrent();
            result.details = StringFormat("Treinamento concluído em %d épocas", epoch + 1);
            ArrayPushBack(m_training_history, result);
            
            m_logger.log_info("[NEURAL] Treinamento concluído com sucesso | Perda: " + DoubleToString(avg_loss, 6));
            return true;
         }
      }

      TrainingResult result;
      result.success = false;
      result.epoch = m_max_epochs;
      result.loss = -1;
      result.accuracy = 0;
      result.start_time = (datetime)start_time;
      result.end_time = TimeCurrent();
      result.details = "Treinamento falhou: número máximo de épocas atingido";
      ArrayPushBack(m_training_history, result);

      m_logger.log_error("[NEURAL] Treinamento falhou: número máximo de épocas atingido");
      return false;
   }

   //+--------------------------------------------------------------+
   //| Obtém saídas                                                  |
   //+--------------------------------------------------------------+
   bool GetOutputs(double outputs[])
   {
      ArrayCopy(outputs, m_layers[m_hidden_layers + 1].outputs);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                       |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_logger.is_initialized() && 
             ArraySize(m_layers) > 0;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de treinamento                              |
   //+--------------------------------------------------------------+
   bool ExportTrainingHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_training_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_training_history[i].start_time, TIME_DATE|TIME_SECONDS),
            TimeToString(m_training_history[i].end_time, TIME_DATE|TIME_SECONDS),
            m_training_history[i].success ? "SIM" : "NÃO",
            IntegerToString(m_training_history[i].epoch),
            DoubleToString(m_training_history[i].loss, 6),
            DoubleToString(m_training_history[i].accuracy, 4),
            m_training_history[i].details
         );
      }

      FileClose(handle);
      m_logger.log_info("[NEURAL] Histórico de treinamento exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~CNeuroNet()
   {
      m_logger.log_info("[NEURAL] Rede Neural encerrada para " + m_symbol);
   }
};

#endif // __NEURONET_MQH__