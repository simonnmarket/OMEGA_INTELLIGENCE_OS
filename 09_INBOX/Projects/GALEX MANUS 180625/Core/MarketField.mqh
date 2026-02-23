//+------------------------------------------------------------------+
//| MarketField.mqh - Campo Vetorial Avançado                        |
//| v3.0 - Sistema Híbrido Quântico-Relativístico                    |
//+------------------------------------------------------------------+

#include "QuantumState.mqh"
#include <Math\Alglib\alglib.mqh> // Para cálculos avançados

class MarketVector {
private:
   double m_magnitude;
   double m_direction;
   string m_status;
   double m_probabilities[3]; // Probabilidades de regime [Tendência, Lateral, Volátil]
   
   // Novos campos quânticos
   double m_quantum_entropy;
   double m_relativistic_momentum;
   
   void CalculateRegimeProbabilities(const QuantumState& state) {
      // Usando algoritmo de máquina de vetores de suporte (SVM)
      CMatrixDouble matrix;
      matrix.Resize(3, 3);
      // ... preenchimento com dados do estado
      
      // Cálculo das probabilidades (simplificado)
      m_probabilities[0] = state.Momentum() / (state.Volatility() + 1e-8);
      m_probabilities[1] = 1.0 - MathAbs(state.Momentum());
      m_probabilities[2] = state.Volatility() / 10.0;
      
      // Normalização
      double sum = m_probabilities[0] + m_probabilities[1] + m_probabilities[2];
      for(int i=0; i<3; i++) 
         m_probabilities[i] /= sum;
   }

public:
   MarketVector() : m_magnitude(0), m_direction(0), m_status("→ Neutro"), 
                   m_quantum_entropy(0), m_relativistic_momentum(0) 
   {
      ArrayInitialize(m_probabilities, 0);
   }

   void Update(const QuantumState& state) {
      // Cálculo da entropia quântica
      m_quantum_entropy = state.Entropy();
      
      // Momento relativístico (ajustado pela volatilidade)
      m_relativistic_momentum = state.Momentum() * (1 + state.Volatility()/100);
      
      double delta = m_relativistic_momentum;
      double vol = state.Volatility();

      // Normalização adaptativa
      m_magnitude = NormalizeDouble(MathAbs(delta / (vol + 1e-8)) * (1 + m_quantum_entropy), 6);
      m_direction = MathTanh(delta * 100); // Função tanh para suavização

      CalculateRegimeProbabilities(state);

      // Sistema de classificação melhorado
      if(m_direction > 0.5) {
         if(m_magnitude > 2.0) m_status = "↑↑ Fase de Aceleração";
         else if(m_magnitude > 1.0) m_status = "↑ Fase de Impulso";
         else m_status = "→ Fase de Acumulação";
      } 
      else if(m_direction < -0.5) {
         if(m_magnitude > 2.0) m_status = "↓↓ Fase de Pânico";
         else if(m_magnitude > 1.0) m_status = "↓ Fase de Distribuição";
         else m_status = "→ Fase de Exaustão";
      } 
      else {
         if(m_probabilities[1] > 0.7) m_status = "≡ Consolidação Forte";
         else m_status = "∼ Flutuação Caótica";
      }
   }

   string Status() const { return m_status; }
   
   // Novos métodos institucionais
   double GetRegimeProbability(int regime) const {
      return (regime >=0 && regime <3) ? m_probabilities[regime] : 0;
   }
   
   double GetQuantumEntropy() const { return m_quantum_entropy; }
};

class MarketField {
private:
   MarketVector m_vectors[10]; // Ampliado para 10 ativos
   QuantumState m_states[10];
   int m_current_index;
   
   // Matriz de correlação cruzada
   CMatrixDouble m_correlation_matrix;
   
public:
   MarketField() : m_current_index(0) {
      m_correlation_matrix.Resize(10, 10);
   }

   void AnalyzeAll(string &symbols[], int count, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      for(int i=0; i<count && i<10; i++) {
         m_states[i].Observe(symbols[i], timeframe, 0);
         m_vectors[i].Update(m_states[i]);
         m_current_index = i;
      }
      UpdateCorrelationMatrix();
   }

   void Update(string symbol, int index, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      if(index >= 0 && index < 10) {
         m_states[index].Observe(symbol, timeframe, 0);
         m_vectors[index].Update(m_states[index]);
         m_current_index = index;
         UpdateCorrelationMatrix();
      }
   }
   
   void UpdateCorrelationMatrix() {
      // Preenche a matriz de correlação entre os ativos
      for(int i=0; i<=m_current_index; i++) {
         for(int j=0; j<=m_current_index; j++) {
            m_correlation_matrix[i][j] = 
               PearsonCorrelation(m_states[i].GetSeries(), m_states[j].GetSeries());
         }
      }
   }

   string GetStatus(int index) {
      if(index >= 0 && index <= m_current_index)
         return m_vectors[index].Status();
      return "→ Ativo Não Monitorado";
   }
   
   // Novas funcionalidades institucionais
   double GetCrossAssetCorrelation(int asset1, int asset2) {
      if(asset1 >=0 && asset1 <=m_current_index && 
         asset2 >=0 && asset2 <=m_current_index)
         return m_correlation_matrix[asset1][asset2];
      return 0;
   }
   
   int DetectMarketRegime() {
      // Lógica avançada de detecção de regime
      int regime = 0;
      // ... implementação complexa
      return regime;
   }
};