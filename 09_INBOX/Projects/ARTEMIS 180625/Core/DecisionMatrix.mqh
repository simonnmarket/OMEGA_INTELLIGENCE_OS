//+------------------------------------------------------------------+
//| DecisionMatrix.mqh - Quantum Decision Matrix                     |
//+------------------------------------------------------------------+

class DecisionMatrix
{
private:
   double weights[];
   int matrix_size;
   
public:
   DecisionMatrix()
   {
      matrix_size = 3;  // Number of agents
      ArrayResize(weights, matrix_size);
      ArrayInitialize(weights, 1.0 / matrix_size);  // Equal weights initially
   }
   
   int Calculate(double &signals[], double quantum_state)
   {
      if(ArraySize(signals) != matrix_size) return 0;
      
      double decision = 0.0;
      
      // Combine agent signals with quantum state
      for(int i = 0; i < matrix_size; i++)
      {
         decision += signals[i] * weights[i];
      }
      
      // Apply quantum state influence
      decision *= (1.0 + quantum_state);
      
      // Normalize and convert to trading signal
      if(decision > 0.5) return 1;      // Buy signal
      if(decision < -0.5) return -1;    // Sell signal
      return 0;                         // No signal
   }
   
   void UpdateWeights(double &performance[])
   {
      if(ArraySize(performance) != matrix_size) return;
      
      double total_performance = 0.0;
      
      // Calculate total performance
      for(int i = 0; i < matrix_size; i++)
      {
         total_performance += MathAbs(performance[i]);
      }
      
      // Update weights based on performance
      if(total_performance > 0)
      {
         for(int i = 0; i < matrix_size; i++)
         {
            weights[i] = MathAbs(performance[i]) / total_performance;
         }
      }
   }
   
   double GetWeight(int index)
   {
      if(index >= 0 && index < matrix_size)
         return weights[index];
      return 0.0;
   }
}; 