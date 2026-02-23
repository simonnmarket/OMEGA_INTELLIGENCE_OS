//+------------------------------------------------------------------+
//| MomentumAgent.mqh - Agente Quântico de Momentum                  |
//| v9.0 - Sistema Adaptativo com Detecção de Aceleração             |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"
#include <Math\Alglib\alglib.mqh>

class MomentumAgent : public AgentBase {
private:
   int m_periods[3];            // Períodos múltiplos [Curto, Médio, Longo]
   double m_thresholds[3];       // Limiares dinâmicos [Compra, Neutro, Venda]
   double m_velocity[3];         // Velocidade do preço (1a derivada)
   double m_acceleration[3];     // Aceleração do preço (2a derivada)
   double m_jerk[3];             // Jerk do preço (3a derivada)
   
   // Calcula derivadas do preço
   void CalculateDerivatives(string symbol) {
      for(int i=0; i<3; i++) {
         double p0 = iClose(symbol, PERIOD_M1, 0);
         double p1 = iClose(symbol, PERIOD_M1, 1);
         double p2 = iClose(symbol, PERIOD_M1, 2);
         double p3 = iClose(symbol, PERIOD_M1, 3);
         
         m_velocity[i] = (p0 - p1) / (iATR(symbol, PERIOD_M1, m_periods[i], 0) + 1e-8);
         m_acceleration[i] = (p0 - 2*p1 + p2) / (iATR(symbol, PERIOD_M1, m_periods[i], 0) + 1e-8);
         m_jerk[i] = (p0 - 3*p1 + 3*p2 - p3) / (iATR(symbol, PERIOD_M1, m_periods[i], 0) + 1e-8);
      }
   }
   
   // Atualiza limiares dinamicamente
   void UpdateThresholds() {
      double volatility = iATR(_Symbol, PERIOD_M1, 14, 0);
      double momentum = iMomentum(_Symbol, PERIOD_M15, 14, 0);
      
      // Limiares adaptativos baseados em volatilidade e momentum
      m_thresholds[0] = 1.5 + volatility/3.0;  // Limiar de compra
      m_thresholds[1] = 0.3 * volatility;      // Banda neutra
      m_thresholds[2] = 1.5 + volatility/3.0;  // Limiar de venda
   }

   // Calcula força do momentum ponderada
   double CalculateMomentumStrength() {
      double strength = 0;
      double weights = 0;
      
      for(int i=0; i<3; i++) {
         double w = 1.0 / (m_periods[i] + 1);
         strength += (m_velocity[i] + m_acceleration[i]/2 + m_jerk[i]/3) * w;
         weights += w;
      }
      
      return strength / weights;
   }

public:
   MomentumAgent() : AgentBase("QuantumMomentumHunter") {
      m_periods[0] = 5;   // Curto prazo
      m_periods[1] = 14;  // Médio prazo (principal)
      m_periods[2] = 30;  // Longo prazo
      ArrayInitialize(m_thresholds, 0);
      ArrayInitialize(m_velocity, 0);
      ArrayInitialize(m_acceleration, 0);
      ArrayInitialize(m_jerk, 0);
   }

   // Análise quântica de momentum
   int Analyze(string symbol) override {
      // 1. Atualiza parâmetros dinâmicos
      UpdateThresholds();
      CalculateDerivatives(symbol);
      
      // 2. Cálculo do momentum multidimensional
      double momentum_strength = CalculateMomentumStrength();
      
      // 3. Detecção de regime de mercado
      int regime = DetectMarketRegime(symbol);
      double regime_factor = (regime == 2) ? 1.5 : (regime == 1) ? 0.5 : 1.0;
      
      // 4. Sinal com limiares adaptativos
      if(momentum_strength > m_thresholds[0] * regime_factor && 
         m_acceleration[0] > 0 && m_jerk[0] > 0) {
         m_confidence = MathMin(1.0, momentum_strength / 3.0);
         return 1;  // Sinal de compra forte
      }
      else if(momentum_strength < -m_thresholds[2] * regime_factor && 
              m_acceleration[0] < 0 && m_jerk[0] < 0) {
         m_confidence = MathMin(1.0, -momentum_strength / 3.0);
         return -1; // Sinal de venda forte
      }
      
      // 5. Verificar divergência quântica
      double quantum_div = m_operator.QuantumDivergence();
      if(MathAbs(momentum_strength) > 1.0 && quantum_div > 0.5) {
         m_confidence = MathMin(0.7, MathAbs(momentum_strength) / 2.0);
         return (momentum_strength > 0) ? 1 : -1; // Sinal fraco
      }
      
      m_confidence = 0.0;
      return 0;
   }

   // Retroalimentação especializada para momentum
   void Feedback(double reward) override {
      // Ajusta períodos baseado no desempenho
      if(reward > 0) {
         for(int i=0; i<3; i++) {
            m_periods[i] = (int)MathMax(3, m_periods[i] * (1 - m_adaptive_learning_rate/2));
         }
      } else {
         for(int i=0; i<3; i++) {
            m_periods[i] = (int)MathMin(50, m_periods[i] * (1 + m_adaptive_learning_rate/2));
         }
      }
      
      // Chama a implementação base
      AgentBase::Feedback(reward);
   }

   // Clone especializado
   MomentumAgent* Clone() const override {
      MomentumAgent* clone = new MomentumAgent();
      clone.m_periods = this.m_periods;
      clone.m_thresholds = this.m_thresholds;
      clone.m_velocity = this.m_velocity;
      clone.m_acceleration = this.m_acceleration;
      clone.m_jerk = this.m_jerk;
      clone.m_confidence = this.m_confidence;
      clone.m_nash_weight = this.m_nash_weight;
      return clone;
   }
};