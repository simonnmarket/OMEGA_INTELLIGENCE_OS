//+------------------------------------------------------------------+
//| MeanReversionAgent.mqh - Agente Quântico de Reversão à Média     |
//| v8.0 - Sistema Adaptativo com Detecção de Regimes                |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"
#include <Math\Alglib\alglib.mqh>

class MeanReversionAgent : public AgentBase {
private:
   int m_periods[3];            // Períodos múltiplos [Curto, Médio, Longo]
   double m_thresholds[3];       // Limiares dinâmicos [Compra, Neutro, Venda]
   double m_half_life;           // Meia-vida da reversão
   double m_z_score_history[];   // Histórico de Z-scores
   
   // Calcula meia-vida da reversão
   void CalculateHalfLife(string symbol) {
      double sum = 0;
      double sum2 = 0;
      int count = 100; // Janela de análise
      
      for(int i=0; i<count; i++) {
         double price = iClose(symbol, PERIOD_M1, i);
         double ma = iMA(symbol, PERIOD_M1, m_periods[1], 0, MODE_SMA, PRICE_CLOSE, i);
         double z = (price - ma) / (iATR(symbol, PERIOD_M1, m_periods[1], i) + 1e-8);
         
         ArrayResize(m_z_score_history, count);
         m_z_score_history[i] = z;
         
         sum += z;
         sum2 += z*z;
      }
      
      double variance = (sum2 - sum*sum/count)/(count-1);
      m_half_life = MathLog(2) / (variance + 1e-8);
   }
   
   // Atualiza limiares dinamicamente
   void UpdateThresholds() {
      double volatility = iATR(_Symbol, PERIOD_M1, 14, 0);
      double momentum = iMomentum(_Symbol, PERIOD_M15, 14, 0);
      
      // Limiares adaptativos baseados em volatilidade e momentum
      m_thresholds[0] = -1.8 - volatility/2.0;  // Limiar de compra
      m_thresholds[1] = 0.5 * volatility;       // Banda neutra
      m_thresholds[2] = 1.8 + volatility/2.0;   // Limiar de venda
   }

public:
   MeanReversionAgent() : AgentBase("QuantumMeanReversionBot") {
      m_periods[0] = 5;   // Curto prazo
      m_periods[1] = 20;  // Médio prazo (principal)
      m_periods[2] = 50;  // Longo prazo
      ArrayInitialize(m_thresholds, 0);
      m_half_life = 1.0;
      ArrayResize(m_z_score_history, 0);
   }

   // Análise quântica de reversão
   int Analyze(string symbol) override {
      // 1. Atualiza parâmetros dinâmicos
      UpdateThresholds();
      CalculateHalfLife(symbol);
      
      // 2. Cálculo do Z-score multidimensional
      double z_scores[3];
      for(int i=0; i<3; i++) {
         double price = iClose(symbol, PERIOD_M1, 0);
         double ma = iMA(symbol, PERIOD_M1, m_periods[i], 0, MODE_SMA, PRICE_CLOSE, 0);
         double atr = iATR(symbol, PERIOD_M1, m_periods[i], 0);
         z_scores[i] = (price - ma) / (atr + 1e-8);
      }
      
      // 3. Ponderar Z-scores pela meia-vida
      double weighted_z = 0;
      double weights = 0;
      for(int i=0; i<3; i++) {
         double w = MathExp(-m_half_life / m_periods[i]);
         weighted_z += z_scores[i] * w;
         weights += w;
      }
      weighted_z /= weights;
      
      // 4. Detecção de regime de mercado
      int regime = DetectMarketRegime(symbol);
      double regime_factor = (regime == 1) ? 1.5 : (regime == 2) ? 0.7 : 1.0;
      
      // 5. Sinal com limiares adaptativos
      if(weighted_z < m_thresholds[0] * regime_factor) {
         m_confidence = MathMin(1.0, MathAbs(weighted_z) / 3.0);
         return 1;  // Sinal de compra forte
      }
      else if(weighted_z > m_thresholds[2] * regime_factor) {
         m_confidence = MathMin(1.0, MathAbs(weighted_z) / 3.0);
         return -1; // Sinal de venda forte
      }
      
      // 6. Verificar divergência quântica
      double quantum_div = m_operator.QuantumDivergence();
      if(MathAbs(weighted_z) > 1.0 && quantum_div > 0.5) {
         m_confidence = MathMin(0.7, MathAbs(weighted_z) / 2.0);
         return (weighted_z < 0) ? 1 : -1; // Sinal fraco
      }
      
      m_confidence = 0.0;
      return 0;
   }

   // Retroalimentação especializada para reversão
   void Feedback(double reward) override {
      // Ajusta períodos baseado no desempenho
      if(reward > 0) {
         for(int i=0; i<3; i++) {
            m_periods[i] = (int)MathMax(5, m_periods[i] * (1 - m_adaptive_learning_rate));
         }
      } else {
         for(int i=0; i<3; i++) {
            m_periods[i] = (int)MathMin(100, m_periods[i] * (1 + m_adaptive_learning_rate));
         }
      }
      
      // Chama a implementação base
      AgentBase::Feedback(reward);
   }

   // Clone especializado
   MeanReversionAgent* Clone() const override {
      MeanReversionAgent* clone = new MeanReversionAgent();
      clone.m_periods = this.m_periods;
      clone.m_thresholds = this.m_thresholds;
      clone.m_half_life = this.m_half_life;
      clone.m_z_score_history = this.m_z_score_history;
      clone.m_confidence = this.m_confidence;
      clone.m_nash_weight = this.m_nash_weight;
      return clone;
   }
};