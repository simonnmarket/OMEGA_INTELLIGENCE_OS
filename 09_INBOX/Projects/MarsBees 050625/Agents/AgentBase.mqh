//+------------------------------------------------------------------+
//| AgentBase.mqh - Framework Institucional para Agentes Quant       |
//| v7.1 - Sistema Multiagente com Aprendizado Adaptativo            |
//+------------------------------------------------------------------+

#include <Math\Alglib\alglib.mqh>
#include "..\Core\QuantumState.mqh"
#include "..\Math\QuantumMath.mqh"

class AgentBase {
protected:
   string m_name;
   double m_confidence;
   double m_nash_weight;
   double m_adaptive_learning_rate;
   double m_performance[3];
   double m_success_rate;
   int m_neural_layer_size;
   CMatrixDouble m_neural_weights;
   QuantumState m_state;
   QuantumOperator m_operator;

   void Log(string message) {
      Print("[AgentBase] ", m_name, ": ", message);
   }

   virtual void UpdateNeuralWeights(double error) {
      for(int i = 0; i < m_neural_layer_size; i++) {
         for(int j = 0; j < m_neural_layer_size; j++) {
            m_neural_weights[i][j] -= m_adaptive_learning_rate * error;
         }
      }
   }

public:
   AgentBase(string name, int neural_size = 10) : m_name(name),
                                                m_confidence(0.5),
                                                m_nash_weight(1.0),
                                                m_adaptive_learning_rate(0.01),
                                                m_neural_layer_size(neural_size) {
      ArrayInitialize(m_performance, 0);
      m_success_rate = 0.5;
      if(!m_neural_weights.Resize(neural_size, neural_size)) {
         Log("Erro: Falha ao alocar m_neural_weights");
      }
   }

   virtual ~AgentBase() {}

   virtual int Analyze(string symbol, ENUM_TIMEFRAMES timeframe = PERIOD_M1) {
      if(!m_state.Observe(symbol, timeframe, 0) || !m_operator.Observe(symbol, timeframe, 0)) {
         Log("Erro: Falha ao atualizar estado quântico para " + symbol);
         return 0;
      }

      double input[10];
      ArrayInitialize(input, 0);
      input[0] = iClose(symbol, timeframe, 0);
      input[1] = iATR(symbol, timeframe, 14); // Removido o quarto parâmetro
      input[2] = iMomentum(symbol, timeframe, 14, 0);

      double output = NeuralPredict(input);

      m_confidence = MathMin(1.0, MathMax(0.0,
                           m_state.GetQuantumCoherence() *
                           (1 - m_state.GetQuantumEntropy())));

      return (output > 0.66) ? 1 :
             (output < -0.66) ? -1 : 0;
   }

   virtual double NeuralPredict(double &input[]) {
      double sum = 0;
      for(int i = 0; i < m_neural_layer_size; i++) {
         for(int j = 0; j < MathMin(ArraySize(input), m_neural_layer_size); j++) {
            sum.1 * (reward > 0 ? 1 : 0);
      m_adaptive_learning_rate = 0.01 * (1 + MathSin(m_success_rate * M_PI));
      UpdateNeuralWeights(1 - reward);
      Log("Feedback recebido: " + DoubleToString(reward, 2));
   }

   string Name() const { return m_name; }
   double Confidence() const { return m_confidence * m_nash_weight; }
   double GetNashWeight() const { return m_nash_weight; }
   void SetNashWeight(double weight) { m_nash_weight = weight; }
   double GetSuccessRate() const { return m_success_rate; }

   virtual int DetectMarketRegime(string symbol) {
      double volatility = iATR(symbol, PERIOD_M1, 14); // Removido o quarto parâmetro
      if(volatility == 0) {
         Log("Erro: Falha ao obter ATR para " + symbol);
         return 3;
      }
      double momentum = iMomentum(symbol, PERIOD_M15, 14, 0);
      if(volatility < 0.5 && MathAbs(momentum) < 30)
         return 1; // Lateral
      else if(volatility > 1.0 && MathAbs(momentum) > 70)
         return         double range = iHigh(symbol, PERIOD_M1, 0) - iLow(symbol, PERIOD_M1, 0);
         double prev_range = iHigh(symbol, PERIOD_M1, i) - iLow(symbol, PERIOD_M1, i);
         if(prev_range == 0) continue;
         sum += MathLog(range / prev_range);
      }
      return sum / depth;
   }

   virtual double GetCorrelationWith(const AgentBase* other) const {
      return MathCos(m_success_rate - other.m_success_rate);
   }

   virtual AgentBase* Clone() const {
      AgentBase* clone = new AgentBase(m_name, m_neural_layer_size);
      clone.m_confidence = this.m_confidence;
      clone.m_nash_weight = this.m_nash_weight;
      return clone;
   }
};