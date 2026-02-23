//+------------------------------------------------------------------+
//| ArtemisMarketField.mqh - Campo Vetorial Otimizado               |
//| Projeto Artemis - Versão Institucional                          |
//| Sistema híbrido quântico-relativístico otimizado                |
//+------------------------------------------------------------------+

#include "ArtemisQuantumState.mqh"
#include "ArtemisQuantumMath.mqh"

#ifndef ARTEMIS_MARKET_FIELD_MQH
#define ARTEMIS_MARKET_FIELD_MQH

//+------------------------------------------------------------------+
//| Enumerações para regimes de mercado                             |
//+------------------------------------------------------------------+
enum ARTEMIS_MARKET_REGIME {
   REGIME_TRENDING = 0,
   REGIME_SIDEWAYS = 1,
   REGIME_VOLATILE = 2,
   REGIME_UNKNOWN = 3
};

//+------------------------------------------------------------------+
//| Pool de objetos para otimização de memória                     |
//+------------------------------------------------------------------+
template<typename T>
class ArtemisObjectPool {
private:
   T* m_pool[100];
   bool m_available[100];
   int m_pool_size;
   int m_next_index;

public:
   ArtemisObjectPool() {
      m_pool_size = 100;
      m_next_index = 0;
      
      for(int i = 0; i < m_pool_size; i++) {
         m_pool[i] = new T();
         m_available[i] = true;
      }
   }
   
   ~ArtemisObjectPool() {
      for(int i = 0; i < m_pool_size; i++) {
         if(m_pool[i] != NULL) {
            delete m_pool[i];
         }
      }
   }
   
   T* Acquire() {
      for(int i = 0; i < m_pool_size; i++) {
         int index = (m_next_index + i) % m_pool_size;
         if(m_available[index]) {
            m_available[index] = false;
            m_next_index = (index + 1) % m_pool_size;
            return m_pool[index];
         }
      }
      
      // Pool esgotado - criar novo objeto (não ideal)
      ArtemisLogger::Log(LOG_WARN, "ObjectPool", "Pool exhausted, creating new object");
      return new T();
   }
   
   void Release(T* obj) {
      for(int i = 0; i < m_pool_size; i++) {
         if(m_pool[i] == obj) {
            m_available[i] = true;
            return;
         }
      }
      
      // Objeto não pertence ao pool - deletar
      delete obj;
   }
};

//+------------------------------------------------------------------+
//| Vetor de mercado otimizado                                      |
//+------------------------------------------------------------------+
class ArtemisMarketVector {
private:
   double m_magnitude;
   double m_direction;
   string m_status;
   double m_probabilities[3]; // [Tendência, Lateral, Volátil]
   
   // Campos quânticos otimizados
   double m_quantum_entropy;
   double m_relativistic_momentum;
   
   // Cache para status strings
   static string m_status_cache[20];
   static int m_status_count;
   
   // Otimização de strings com interning
   string InternString(string str) {
      for(int i = 0; i < m_status_count; i++) {
         if(m_status_cache[i] == str) {
            return m_status_cache[i];
         }
      }
      
      if(m_status_count < 20) {
         m_status_cache[m_status_count] = str;
         m_status_count++;
         return m_status_cache[m_status_count - 1];
      }
      
      return str; // Fallback se cache estiver cheio
   }
   
   void CalculateRegimeProbabilities(const ArtemisQuantumState& state) {
      double momentum = state.GetMomentum();
      double volatility = state.GetVolatility();
      double entropy = state.GetEntropy();
      
      // Algoritmo otimizado para cálculo de probabilidades
      if(volatility > ARTEMIS_EPSILON) {
         m_probabilities[0] = MathAbs(momentum) / volatility; // Tendência
         m_probabilities[1] = 1.0 / (1.0 + entropy * 10); // Lateral
         m_probabilities[2] = entropy; // Volátil
      } else {
         m_probabilities[0] = 0.0;
         m_probabilities[1] = 1.0;
         m_probabilities[2] = 0.0;
      }
      
      // Normalização eficiente
      double sum = m_probabilities[0] + m_probabilities[1] + m_probabilities[2];
      if(sum > ARTEMIS_EPSILON) {
         double inv_sum = 1.0 / sum;
         m_probabilities[0] *= inv_sum;
         m_probabilities[1] *= inv_sum;
         m_probabilities[2] *= inv_sum;
      }
   }

public:
   ArtemisMarketVector() {
      m_magnitude = 0.0;
      m_direction = 0.0;
      m_status = "→ Neutro";
      m_quantum_entropy = 0.0;
      m_relativistic_momentum = 0.0;
      
      ArrayInitialize(m_probabilities, 0.0);
   }
   
   void Update(const ArtemisQuantumState& state) {
      // Cálculos otimizados
      m_quantum_entropy = state.GetEntropy();
      double momentum = state.GetMomentum();
      double volatility = state.GetVolatility();
      
      // Momento relativístico com validação
      if(volatility > ARTEMIS_EPSILON) {
         m_relativistic_momentum = momentum * (1.0 + volatility / 100.0);
      } else {
         m_relativistic_momentum = momentum;
      }
      
      // Magnitude normalizada
      m_magnitude = SafeDivide(MathAbs(m_relativistic_momentum), 
                              volatility + ARTEMIS_EPSILON, 0.0) * 
                   (1.0 + m_quantum_entropy);
      
      // Direção suavizada com tanh otimizada
      m_direction = ArtemisMatCache::FastTanh(m_relativistic_momentum * 100);
      
      CalculateRegimeProbabilities(state);
      
      // Sistema de classificação otimizado
      UpdateStatus();
   }
   
   void UpdateStatus() {
      string new_status;
      
      if(m_direction > 0.5) {
         if(m_magnitude > 2.0) {
            new_status = "↑↑ Fase de Aceleração";
         } else if(m_magnitude > 1.0) {
            new_status = "↑ Fase de Impulso";
         } else {
            new_status = "→ Fase de Acumulação";
         }
      } else if(m_direction < -0.5) {
         if(m_magnitude > 2.0) {
            new_status = "↓↓ Fase de Pânico";
         } else if(m_magnitude > 1.0) {
            new_status = "↓ Fase de Distribuição";
         } else {
            new_status = "→ Fase de Exaustão";
         }
      } else {
         if(m_probabilities[1] > 0.7) {
            new_status = "≡ Consolidação Forte";
         } else {
            new_status = "∼ Flutuação Caótica";
         }
      }
      
      m_status = InternString(new_status);
   }
   
   // Getters otimizados
   string GetStatus() const { return m_status; }
   double GetMagnitude() const { return m_magnitude; }
   double GetDirection() const { return m_direction; }
   double GetRegimeProbability(int regime) const {
      return (regime >= 0 && regime < 3) ? m_probabilities[regime] : 0.0;
   }
   double GetQuantumEntropy() const { return m_quantum_entropy; }
   double GetRelativisticMomentum() const { return m_relativistic_momentum; }
};

// Inicialização de variáveis estáticas
string ArtemisMarketVector::m_status_cache[20];
int ArtemisMarketVector::m_status_count = 0;

//+------------------------------------------------------------------+
//| Matriz de correlação incremental otimizada                     |
//+------------------------------------------------------------------+
class ArtemisCorrelationMatrix {
private:
   PearsonCorrelation m_correlations[10][10];
   double m_cached_values[10][10];
   datetime m_last_update[10][10];
   bool m_cache_valid[10][10];
   int m_matrix_size;
   
   static const int CACHE_TIMEOUT = 60; // 60 segundos

public:
   ArtemisCorrelationMatrix(int size = 10) {
      m_matrix_size = MathMin(size, 10);
      
      for(int i = 0; i < m_matrix_size; i++) {
         for(int j = 0; j < m_matrix_size; j++) {
            m_cached_values[i][j] = 0.0;
            m_last_update[i][j] = 0;
            m_cache_valid[i][j] = false;
         }
      }
   }
   
   void AddDataPoint(int asset1, int asset2, double value1, double value2) {
      if(asset1 >= 0 && asset1 < m_matrix_size && 
         asset2 >= 0 && asset2 < m_matrix_size) {
         
         m_correlations[asset1][asset2].AddPoint(value1, value2);
         m_cache_valid[asset1][asset2] = false;
         
         // Matriz simétrica
         if(asset1 != asset2) {
            m_correlations[asset2][asset1].AddPoint(value2, value1);
            m_cache_valid[asset2][asset1] = false;
         }
      }
   }
   
   double GetCorrelation(int asset1, int asset2) {
      if(asset1 < 0 || asset1 >= m_matrix_size || 
         asset2 < 0 || asset2 >= m_matrix_size) {
         return 0.0;
      }
      
      datetime current_time = TimeCurrent();
      
      // Verificar cache
      if(m_cache_valid[asset1][asset2] && 
         (current_time - m_last_update[asset1][asset2]) < CACHE_TIMEOUT) {
         return m_cached_values[asset1][asset2];
      }
      
      // Recalcular e cachear
      double correlation = m_correlations[asset1][asset2].GetCorrelation();
      m_cached_values[asset1][asset2] = correlation;
      m_last_update[asset1][asset2] = current_time;
      m_cache_valid[asset1][asset2] = true;
      
      return correlation;
   }
   
   void Reset() {
      for(int i = 0; i < m_matrix_size; i++) {
         for(int j = 0; j < m_matrix_size; j++) {
            m_correlations[i][j].Reset();
            m_cache_valid[i][j] = false;
         }
      }
   }
};

//+------------------------------------------------------------------+
//| Campo de mercado otimizado                                      |
//+------------------------------------------------------------------+
class ArtemisMarketField {
private:
   ArtemisMarketVector* m_vectors[10];
   ArtemisQuantumState* m_states[10];
   ArtemisCorrelationMatrix* m_correlation_matrix;
   ArtemisObjectPool<ArtemisMarketVector>* m_vector_pool;
   ArtemisObjectPool<ArtemisQuantumState>* m_state_pool;
   
   int m_current_count;
   int m_max_assets;
   datetime m_last_full_update;
   
   // Métricas de performance
   int m_update_count;
   double m_avg_update_time;

public:
   ArtemisMarketField(int max_assets = 10) {
      m_max_assets = MathMin(max_assets, 10);
      m_current_count = 0;
      m_last_full_update = 0;
      m_update_count = 0;
      m_avg_update_time = 0.0;
      
      // Inicializar pools
      m_vector_pool = new ArtemisObjectPool<ArtemisMarketVector>();
      m_state_pool = new ArtemisObjectPool<ArtemisQuantumState>();
      m_correlation_matrix = new ArtemisCorrelationMatrix(m_max_assets);
      
      // Inicializar arrays
      for(int i = 0; i < m_max_assets; i++) {
         m_vectors[i] = NULL;
         m_states[i] = NULL;
      }
      
      ArtemisLogger::Log(LOG_INFO, "MarketField", 
                        StringFormat("Field initialized for %d assets", m_max_assets));
   }
   
   ~ArtemisMarketField() {
      // Liberar objetos dos pools
      for(int i = 0; i < m_current_count; i++) {
         if(m_vectors[i] != NULL) {
            m_vector_pool.Release(m_vectors[i]);
         }
         if(m_states[i] != NULL) {
            m_state_pool.Release(m_states[i]);
         }
      }
      
      delete m_vector_pool;
      delete m_state_pool;
      delete m_correlation_matrix;
      
      ArtemisLogger::Log(LOG_INFO, "MarketField", "Field destroyed");
   }
   
   bool AnalyzeAll(string &symbols[], int count, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      if(count <= 0 || count > m_max_assets) {
         ArtemisLogger::Log(LOG_ERROR, "MarketField", "Invalid symbol count");
         return false;
      }
      
      datetime start_time = GetMicrosecondCount();
      
      // Redimensionar se necessário
      if(count != m_current_count) {
         ResizeField(count);
      }
      
      // Analisar cada ativo
      for(int i = 0; i < count; i++) {
         if(!UpdateAsset(i, symbols[i], timeframe)) {
            ArtemisLogger::Log(LOG_WARN, "MarketField", 
                              StringFormat("Failed to update asset %s", symbols[i]));
         }
      }
      
      // Atualizar correlações (otimizado)
      UpdateCorrelations();
      
      m_last_full_update = TimeCurrent();
      
      // Métricas de performance
      datetime end_time = GetMicrosecondCount();
      double update_time = (double)(end_time - start_time) / 1000.0; // ms
      m_avg_update_time = (m_avg_update_time * m_update_count + update_time) / (m_update_count + 1);
      m_update_count++;
      
      ArtemisLogger::Log(LOG_TRACE, "MarketField", 
                        StringFormat("Full analysis completed in %.2f ms", update_time));
      
      return true;
   }
   
   bool Update(string symbol, int index, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      if(index < 0 || index >= m_current_count) {
         ArtemisLogger::Log(LOG_ERROR, "MarketField", "Invalid asset index");
         return false;
      }
      
      return UpdateAsset(index, symbol, timeframe);
   }
   
private:
   void ResizeField(int new_count) {
      // Liberar objetos não utilizados
      for(int i = new_count; i < m_current_count; i++) {
         if(m_vectors[i] != NULL) {
            m_vector_pool.Release(m_vectors[i]);
            m_vectors[i] = NULL;
         }
         if(m_states[i] != NULL) {
            m_state_pool.Release(m_states[i]);
            m_states[i] = NULL;
         }
      }
      
      // Alocar novos objetos se necessário
      for(int i = m_current_count; i < new_count; i++) {
         m_vectors[i] = m_vector_pool.Acquire();
         m_states[i] = m_state_pool.Acquire();
      }
      
      m_current_count = new_count;
   }
   
   bool UpdateAsset(int index, string symbol, ENUM_TIMEFRAMES timeframe) {
      if(m_states[index] == NULL || m_vectors[index] == NULL) {
         return false;
      }
      
      if(!m_states[index].Observe(symbol, timeframe, 0)) {
         return false;
      }
      
      m_vectors[index].Update(m_states[index]);
      return true;
   }
   
   void UpdateCorrelations() {
      // Atualização otimizada - apenas para ativos ativos
      for(int i = 0; i < m_current_count; i++) {
         for(int j = i + 1; j < m_current_count; j++) {
            if(m_states[i] != NULL && m_states[j] != NULL) {
               double price_i = m_states[i].GetPrice();
               double price_j = m_states[j].GetPrice();
               
               m_correlation_matrix.AddDataPoint(i, j, price_i, price_j);
            }
         }
      }
   }

public:
   // Getters otimizados
   string GetStatus(int index) {
      if(index >= 0 && index < m_current_count && m_vectors[index] != NULL) {
         return m_vectors[index].GetStatus();
      }
      return "→ Ativo Não Monitorado";
   }
   
   double GetCrossAssetCorrelation(int asset1, int asset2) {
      return m_correlation_matrix.GetCorrelation(asset1, asset2);
   }
   
   ARTEMIS_MARKET_REGIME DetectMarketRegime() {
      if(m_current_count == 0) return REGIME_UNKNOWN;
      
      double trend_prob = 0.0;
      double sideways_prob = 0.0;
      double volatile_prob = 0.0;
      
      // Agregar probabilidades de todos os ativos
      for(int i = 0; i < m_current_count; i++) {
         if(m_vectors[i] != NULL) {
            trend_prob += m_vectors[i].GetRegimeProbability(0);
            sideways_prob += m_vectors[i].GetRegimeProbability(1);
            volatile_prob += m_vectors[i].GetRegimeProbability(2);
         }
      }
      
      // Normalizar
      double total = trend_prob + sideways_prob + volatile_prob;
      if(total > ARTEMIS_EPSILON) {
         trend_prob /= total;
         sideways_prob /= total;
         volatile_prob /= total;
      }
      
      // Determinar regime dominante
      if(trend_prob > sideways_prob && trend_prob > volatile_prob) {
         return REGIME_TRENDING;
      } else if(sideways_prob > volatile_prob) {
         return REGIME_SIDEWAYS;
      } else {
         return REGIME_VOLATILE;
      }
   }
   
   // Métricas de performance
   double GetAverageUpdateTime() const { return m_avg_update_time; }
   int GetUpdateCount() const { return m_update_count; }
   int GetCurrentAssetCount() const { return m_current_count; }
   
   // Método para obter relatório de status
   string GetStatusReport() {
      string report = StringFormat(
         "Market Field Status:\n" +
         "Assets: %d/%d\n" +
         "Updates: %d\n" +
         "Avg Update Time: %.2f ms\n" +
         "Market Regime: %d\n" +
         "Last Update: %s\n",
         m_current_count, m_max_assets,
         m_update_count,
         m_avg_update_time,
         DetectMarketRegime(),
         TimeToString(m_last_full_update, TIME_DATE|TIME_SECONDS)
      );
      
      return report;
   }
};

#endif // ARTEMIS_MARKET_FIELD_MQH

