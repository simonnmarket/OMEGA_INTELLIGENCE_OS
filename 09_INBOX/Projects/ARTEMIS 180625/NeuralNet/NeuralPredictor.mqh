#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict

#include "..\Core\TimeframeHierarchy.mqh"
#include "..\Core\VolatilityAnalysis.mqh"
#include "..\Neural\NeuralNetwork.mqh"
#include <Math\Stat\stat.mqh>
#include <Math\Alglib\alglib.mqh>

// Estrutura para métricas de performance
struct NeuralMetrics {
   double accuracy;
   double loss;
   double validation_loss;
   int epochs_trained;
};

class NeuralPredictor : public CObject {
private:
    TimeframeHierarchy* m_timeframe;
    VolatilityAnalysis* m_volatility;
    string m_symbol;
    ENUM_TIMEFRAMES m_tf;
    int m_input_size;
    int m_hidden_layers;
    int m_hidden_size;
    int m_output_size;
    double m_learning_rate;
    bool m_is_initialized;
    CNeuralNetwork* m_network;
    
    // Parâmetros da rede
    double m_weights_input_hidden[];
    double m_weights_hidden_output[];
    double m_bias_hidden[];
    double m_bias_output[];
    
    // Métricas
    NeuralMetrics m_metrics;
    
    // Parâmetros de treinamento
    int m_batch_size;
    int m_max_epochs;
    double m_regularization;
    double m_early_stopping_patience;

public:
    NeuralPredictor() {
        m_timeframe = NULL;
        m_volatility = NULL;
        m_symbol = NULL;
        m_tf = PERIOD_CURRENT;
        m_input_size = 10;
        m_hidden_layers = 1;
        m_hidden_size = 8;
        m_output_size = 1;
        m_learning_rate = 0.01;
        m_is_initialized = false;
        m_network = NULL;
        
        // Inicializar parâmetros de treinamento
        m_batch_size = 32;
        m_max_epochs = 100;
        m_regularization = 0.0001;
        m_early_stopping_patience = 10;
        
        // Inicializar pesos e bias
        InitializeWeights();
    }

    ~NeuralPredictor() {
        Release();
    }

    bool Initialize(string symbol, ENUM_TIMEFRAMES tf, int input_size, int hidden_layers, int hidden_size, int output_size, double learning_rate = 0.01) {
        if(m_is_initialized) {
            Print("NeuralPredictor já inicializado");
            return false;
        }
        m_symbol = symbol;
        m_tf = tf;
        m_input_size = input_size;
        m_hidden_layers = hidden_layers;
        m_hidden_size = hidden_size;
        m_output_size = output_size;
        m_learning_rate = learning_rate;

        m_timeframe = new TimeframeHierarchy();
        if(!m_timeframe.Initialize(symbol, tf)) {
            Print("Erro ao inicializar TimeframeHierarchy");
            delete m_timeframe;
            m_timeframe = NULL;
            return false;
        }
        m_volatility = new VolatilityAnalysis();
        if(!m_volatility.Initialize(symbol, tf)) {
            Print("Erro ao inicializar VolatilityAnalysis");
            m_timeframe.Release();
            delete m_timeframe;
            m_timeframe = NULL;
            delete m_volatility;
            m_volatility = NULL;
            return false;
        }
        m_network = new CNeuralNetwork(input_size, hidden_layers, hidden_size, output_size);
        m_network.SetLearningRate(learning_rate);
        m_is_initialized = true;
        return true;
    }

    void Release() {
        if(!m_is_initialized) return;
        if(m_timeframe != NULL) {
            m_timeframe.Release();
            delete m_timeframe;
            m_timeframe = NULL;
        }
        if(m_volatility != NULL) {
            m_volatility.Release();
            delete m_volatility;
            m_volatility = NULL;
        }
        if(m_network != NULL) {
            delete m_network;
            m_network = NULL;
        }
        m_is_initialized = false;
    }

    bool IsInitialized() const {
        return m_is_initialized;
    }

    // --- Feature Extraction ---
    bool LoadHistoricalFeatures(double &features[]) {
        double closes[];
        int copied = CopyClose(m_symbol, m_tf, 0, m_input_size + 1, closes);
        if(copied <= 1) return false;
        ArrayResize(features, m_input_size);
        for(int i=0; i<m_input_size; i++) {
            features[i] = (closes[i] - closes[i+1]) / closes[i+1]; // Retorno percentual
        }
        NormalizeArray(features);
        return true;
    }

    void NormalizeArray(double &arr[]) {
        double min_val = arr[0], max_val = arr[0];
        for(int i=1; i<ArraySize(arr); i++) {
            if(arr[i] < min_val) min_val = arr[i];
            if(arr[i] > max_val) max_val = arr[i];
        }
        double range = max_val - min_val + 1e-7;
        for(int i=0; i<ArraySize(arr); i++) {
            arr[i] = (arr[i] - min_val) / range;
        }
    }

    // --- Prediction ---
    double PredictSignal() {
        double features[];
        if(!LoadHistoricalFeatures(features)) return 0.5; // Neutro
        return m_network.Predict(features);
    }

    // --- Training ---
    bool Train(double &input[], double target) {
        if(!m_is_initialized) return false;
        double target_arr[1];
        target_arr[0] = target;
        m_network.Train(input, target_arr);
        return true;
    }

    // --- Batch Training ---
    bool TrainBatch(double &inputs[][], double &targets[][], int batch_size = 32) {
        if(!m_is_initialized) return false;
        m_network.TrainBatch(inputs, targets, batch_size);
        return true;
    }

    // --- Save/Load Weights ---
    bool SaveWeights(string filename) {
        if(!m_is_initialized) return false;
        m_network.Save(filename);
        return true;
    }
    bool LoadWeights(string filename) {
        if(!m_is_initialized) return false;
        m_network.Load(filename);
        return true;
    }

    // --- Quantum Parameters ---
    void SetQuantumParameters(double entanglement, double tunneling) {
        if(m_network != NULL) m_network.SetQuantumParameters(entanglement, tunneling);
    }
    double GetQuantumCoherence() const {
        if(m_network != NULL) return m_network.GetQuantumCoherence();
        return 0.0;
    }
    double GetQuantumEntropy() const {
        if(m_network != NULL) return m_network.GetQuantumEntropy();
        return 0.0;
    }
    void UpdateQuantumMetrics() {
        if(m_network != NULL) m_network.UpdateQuantumMetrics();
    }

    double PredictNextMove() {
        double inputs[];
        LoadHistoricalData(inputs);
        NormalizeArray(inputs);
        
        // Forward pass
        double hidden_layer[];
        double output_layer[];
        ForwardPass(inputs, hidden_layer, output_layer);
        
        return output_layer[0];
    }

    bool Train(int epochs = 100) {
        double training_data[];
        double training_labels[];
        LoadTrainingData(training_data, training_labels);
        
        double best_validation_loss = DBL_MAX;
        int patience_counter = 0;
        
        for(int epoch = 0; epoch < epochs; epoch++) {
            double epoch_loss = 0.0;
            
            // Batch training
            for(int batch = 0; batch < ArraySize(training_data) - m_batch_size; batch += m_batch_size) {
                double batch_loss = TrainBatch(training_data, training_labels, batch);
                epoch_loss += batch_loss;
            }
            
            // Validação
            double validation_loss = Validate(training_data, training_labels);
            
            // Early stopping
            if(validation_loss < best_validation_loss) {
                best_validation_loss = validation_loss;
                patience_counter = 0;
            } else {
                patience_counter++;
                if(patience_counter >= m_early_stopping_patience) {
                    Print("Early stopping at epoch ", epoch);
                    break;
                }
            }
            
            // Atualizar métricas
            m_metrics.loss = epoch_loss / (ArraySize(training_data) / m_batch_size);
            m_metrics.validation_loss = validation_loss;
            m_metrics.epochs_trained = epoch + 1;
            
            if(epoch % 10 == 0) {
                Print("Epoch ", epoch, " - Loss: ", m_metrics.loss, " - Validation Loss: ", m_metrics.validation_loss);
            }
        }
        
        return true;
    }

    NeuralMetrics GetMetrics() {
        return m_metrics;
    }

private:
    void InitializeWeights() {
        // Inicializar pesos com Xavier/Glorot
        double input_scale = MathSqrt(2.0 / m_input_size);
        double hidden_scale = MathSqrt(2.0 / m_hidden_size);
        
        ArrayResize(m_weights_input_hidden, m_input_size * m_hidden_size);
        ArrayResize(m_weights_hidden_output, m_hidden_size * m_output_size);
        ArrayResize(m_bias_hidden, m_hidden_size);
        ArrayResize(m_bias_output, m_output_size);
        
        for(int i = 0; i < ArraySize(m_weights_input_hidden); i++) {
            m_weights_input_hidden[i] = (MathRand() / 32767.0 * 2 - 1) * input_scale;
        }
        
        for(int i = 0; i < ArraySize(m_weights_hidden_output); i++) {
            m_weights_hidden_output[i] = (MathRand() / 32767.0 * 2 - 1) * hidden_scale;
        }
    }

    void ForwardPass(const double &inputs[], double &hidden_layer[], double &output_layer[]) {
        // Camada oculta
        ArrayResize(hidden_layer, m_hidden_size);
        for(int i = 0; i < m_hidden_size; i++) {
            double sum = m_bias_hidden[i];
            for(int j = 0; j < m_input_size; j++) {
                sum += inputs[j] * m_weights_input_hidden[j * m_hidden_size + i];
            }
            hidden_layer[i] = ReLU(sum);
        }
        
        // Camada de saída
        ArrayResize(output_layer, m_output_size);
        for(int i = 0; i < m_output_size; i++) {
            double sum = m_bias_output[i];
            for(int j = 0; j < m_hidden_size; j++) {
                sum += hidden_layer[j] * m_weights_hidden_output[j * m_output_size + i];
            }
            output_layer[i] = Tanh(sum);
        }
    }

    double TrainBatch(const double &data[], const double &labels[], int start_idx) {
        double batch_loss = 0.0;
        double gradients_input_hidden[];
        double gradients_hidden_output[];
        double gradients_bias_hidden[];
        double gradients_bias_output[];
        
        ArrayResize(gradients_input_hidden, ArraySize(m_weights_input_hidden));
        ArrayResize(gradients_hidden_output, ArraySize(m_weights_hidden_output));
        ArrayResize(gradients_bias_hidden, m_hidden_size);
        ArrayResize(gradients_bias_output, m_output_size);
        
        // Zero gradients
        ArrayInitialize(gradients_input_hidden, 0.0);
        ArrayInitialize(gradients_hidden_output, 0.0);
        ArrayInitialize(gradients_bias_hidden, 0.0);
        ArrayInitialize(gradients_bias_output, 0.0);
        
        // Processar batch
        for(int i = 0; i < m_batch_size; i++) {
            int idx = start_idx + i;
            if(idx >= ArraySize(data)) break;
            
            double inputs[];
            ArrayCopy(inputs, data, 0, idx * m_input_size, m_input_size);
            
            double hidden_layer[];
            double output_layer[];
            ForwardPass(inputs, hidden_layer, output_layer);
            
            // Calcular loss
            double error = labels[idx] - output_layer[0];
            batch_loss += error * error;
            
            // Backpropagation
            double output_gradient = -2.0 * error * (1.0 - output_layer[0] * output_layer[0]); // Derivada do Tanh
            
            // Gradientes da camada de saída
            for(int j = 0; j < m_hidden_size; j++) {
                gradients_hidden_output[j] += output_gradient * hidden_layer[j];
            }
            gradients_bias_output[0] += output_gradient;
            
            // Gradientes da camada oculta
            for(int j = 0; j < m_hidden_size; j++) {
                double hidden_gradient = output_gradient * m_weights_hidden_output[j];
                if(hidden_layer[j] > 0) { // Derivada do ReLU
                    for(int k = 0; k < m_input_size; k++) {
                        gradients_input_hidden[k * m_hidden_size + j] += hidden_gradient * inputs[k];
                    }
                    gradients_bias_hidden[j] += hidden_gradient;
                }
            }
        }
        
        // Atualizar pesos com regularização
        for(int i = 0; i < ArraySize(m_weights_input_hidden); i++) {
            m_weights_input_hidden[i] -= m_learning_rate * (gradients_input_hidden[i] + m_regularization * m_weights_input_hidden[i]);
        }
        
        for(int i = 0; i < ArraySize(m_weights_hidden_output); i++) {
            m_weights_hidden_output[i] -= m_learning_rate * (gradients_hidden_output[i] + m_regularization * m_weights_hidden_output[i]);
        }
        
        for(int i = 0; i < m_hidden_size; i++) {
            m_bias_hidden[i] -= m_learning_rate * gradients_bias_hidden[i];
        }
        
        m_bias_output[0] -= m_learning_rate * gradients_bias_output[0];
        
        return batch_loss / m_batch_size;
    }

    double Validate(const double &data[], const double &labels[]) {
        double validation_loss = 0.0;
        int validation_size = (int)(ArraySize(data) * 0.2); // 20% para validação
        
        for(int i = ArraySize(data) - validation_size; i < ArraySize(data); i++) {
            double inputs[];
            ArrayCopy(inputs, data, 0, i * m_input_size, m_input_size);
            
            double hidden_layer[];
            double output_layer[];
            ForwardPass(inputs, hidden_layer, output_layer);
            
            double error = labels[i] - output_layer[0];
            validation_loss += error * error;
        }
        
        return validation_loss / validation_size;
    }

    void LoadHistoricalData(double &inputs[]) {
        double closes[];
        int copied = CopyClose(m_symbol, PERIOD_M1, 0, m_input_size + 1, closes);
        ArrayResize(inputs, m_input_size);
        for(int i=0; i<m_input_size; i++) {
            inputs[i] = (closes[i] - closes[i+1]) / closes[i+1];
        }
    }

    void LoadTrainingData(double &data[], double &labels[]) {
        double closes[];
        int copied = CopyClose(m_symbol, PERIOD_M1, 0, m_input_size * 1000, closes); // 1000 exemplos
        
        int num_samples = (copied - m_input_size);
        ArrayResize(data, num_samples * m_input_size);
        ArrayResize(labels, num_samples);
        
        for(int i = 0; i < num_samples; i++) {
            // Dados de entrada
            for(int j = 0; j < m_input_size; j++) {
                data[i * m_input_size + j] = (closes[i + j] - closes[i + j + 1]) / closes[i + j + 1];
            }
            
            // Labels (retorno futuro)
            labels[i] = (closes[i] - closes[i + m_input_size]) / closes[i + m_input_size];
        }
    }

    // Funções de ativação
    double ReLU(double x) {
        return MathMax(0, x);
    }
    
    double Tanh(double x) {
        return MathTanh(x);
    }
}; 