//+------------------------------------------------------------------+
//| NeuralPredictor.mqh - Preditor Neural para Trading               |
//| Sistema de Trading Quântico - Artemis                            |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict

#include "NeuralNetwork.mqh"
#include "NeuralMetrics.mqh"
#include "..\Core\TimeframeHierarchy.mqh"
#include "..\Core\VolatilityAnalysis.mqh"
#include <Math\Stat\stat.mqh>
#include <Math\Alglib\alglib.mqh>
#include "..\\Utils\\CLogger.mqh"

class CNeuralPredictor : public CObject {
private:
    TimeframeHierarchy* m_timeframe;
    CVolatilityAnalysis* m_volatility;
    string m_symbol;
    ENUM_TIMEFRAMES m_tf;
    CNeuralNetwork* m_network;
    CNeuralMetrics* m_metrics;
    bool m_is_initialized;
    
    // Parâmetros de configuração
    int m_input_size;
    int m_hidden_layers;
    int m_hidden_size;
    int m_output_size;
    double m_learning_rate;
    
    CLogger* m_logger;
    double m_weights_ih[][];  // Pesos input->hidden
    double m_weights_ho[][];  // Pesos hidden->output
    double m_bias_h[];       // Bias da camada oculta
    double m_bias_o[];       // Bias da camada de saída
    datetime m_last_update_time;
    
    // Métodos privados
    bool InitializeNetwork();
    void LoadHistoricalFeatures(double &features[]);
    void NormalizeArray(double &arr[]);
    void UpdateMetrics();
    
public:
    CNeuralPredictor() {
        m_timeframe = NULL;
        m_volatility = NULL;
        m_network = NULL;
        m_metrics = NULL;
        m_is_initialized = false;
        
        // Valores padrão
        m_input_size = 10;
        m_hidden_layers = 2;
        m_hidden_size = 16;
        m_output_size = 1;
        m_learning_rate = 0.01;
    }
    
    ~CNeuralPredictor() {
        Release();
    }
    
    bool Initialize(string symbol, ENUM_TIMEFRAMES tf, 
                   int input_size = 10, int hidden_layers = 2,
                   int hidden_size = 16, int output_size = 1,
                   double learning_rate = 0.01) {
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
        
        // Inicializa componentes
        m_timeframe = new TimeframeHierarchy();
        if(!m_timeframe.Initialize(symbol, tf)) {
            Print("Erro ao inicializar TimeframeHierarchy");
            Release();
            return false;
        }
        
        m_volatility = new CVolatilityAnalysis();
        if(!m_volatility.Initialize(symbol, tf)) {
            Print("Erro ao inicializar VolatilityAnalysis");
            Release();
            return false;
        }
        
        m_metrics = new CNeuralMetrics();
        m_metrics.SetSymbol(symbol);
        m_metrics.SetTimeframe(tf);
        
        if(!InitializeNetwork()) {
            Print("Erro ao inicializar rede neural");
            Release();
            return false;
        }
        
        m_is_initialized = true;
        return true;
    }
    
    void Release() {
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
        
        if(m_metrics != NULL) {
            delete m_metrics;
            m_metrics = NULL;
        }
        
        m_is_initialized = false;
    }
    
    double PredictSignal() {
        if(!m_is_initialized) return 0.5;
        
        double features[];
        if(!LoadHistoricalFeatures(features)) return 0.5;
        
        double prediction = m_network.Predict(features);
        UpdateMetrics();
        
        return prediction;
    }
    
    bool Train(const double& inputs[], double target) {
        if(!m_is_initialized) return false;
        
        double target_arr[1];
        target_arr[0] = target;
        m_network.Train(inputs, target_arr);
        UpdateMetrics();
        
        return true;
    }
    
    bool TrainBatch(const double& inputs[][], const double& targets[][], int batch_size = 32) {
        if(!m_is_initialized) return false;
        
        m_network.TrainBatch(inputs, targets, batch_size);
        UpdateMetrics();
        
        return true;
    }
    
    bool SaveModel(string filename) {
        if(!m_is_initialized) return false;
        return m_network.Save(filename);
    }
    
    bool LoadModel(string filename) {
        if(!m_is_initialized) return false;
        return m_network.Load(filename);
    }
    
    void SetQuantumParameters(double entanglement, double tunneling) {
        if(m_network != NULL) {
            m_network.SetQuantumParameters(entanglement, tunneling);
        }
    }
    
    NeuralMetrics GetMetrics() const {
        if(m_metrics != NULL) {
            return m_metrics.GetMetrics();
        }
        NeuralMetrics empty;
        return empty;
    }
    
    string GetMetricsReport() const {
        if(m_metrics != NULL) {
            return m_metrics.GetReport();
        }
        return "Métricas não disponíveis";
    }
    
    bool IsInitialized() const {
        return m_is_initialized;
    }
};

// Implementação dos métodos privados
bool CNeuralPredictor::InitializeNetwork() {
    m_network = new CNeuralNetwork(m_input_size, m_hidden_layers, 
                                 m_hidden_size, m_output_size);
    m_network.SetLearningRate(m_learning_rate);
    return true;
}

void CNeuralPredictor::LoadHistoricalFeatures(double &features[]) {
    double closes[];
    int copied = CopyClose(m_symbol, m_tf, 0, m_input_size + 1, closes);
    if(copied <= 1) return;
    
    ArrayResize(features, m_input_size);
    for(int i=0; i<m_input_size; i++) {
        features[i] = (closes[i] - closes[i+1]) / closes[i+1];
    }
    NormalizeArray(features);
}

void CNeuralPredictor::NormalizeArray(double &arr[]) {
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

void CNeuralPredictor::UpdateMetrics() {
    if(m_metrics != NULL && m_network != NULL) {
        NeuralMetrics metrics = m_network.GetMetrics();
        m_metrics.UpdateMetrics(metrics);
    }
} 