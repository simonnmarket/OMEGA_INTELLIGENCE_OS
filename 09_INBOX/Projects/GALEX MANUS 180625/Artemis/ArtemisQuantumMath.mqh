//+------------------------------------------------------------------+
//| ArtemisQuantumMath.mqh - Biblioteca matemática otimizada         |
//| Projeto Artemis - Versão Institucional                          |
//| Implementa cálculos matemáticos otimizados para trading          |
//+------------------------------------------------------------------+

#ifndef ARTEMIS_QUANTUM_MATH_MQH
#define ARTEMIS_QUANTUM_MATH_MQH

//+------------------------------------------------------------------+
//| Constantes matemáticas otimizadas                               |
//+------------------------------------------------------------------+
#define ARTEMIS_PI          3.14159265358979323846
#define ARTEMIS_E           2.71828182845904523536
#define ARTEMIS_SQRT2       1.41421356237309504880
#define ARTEMIS_EPSILON     1e-15
#define ARTEMIS_MAX_DOUBLE  1.7976931348623157e+308

//+------------------------------------------------------------------+
//| Cache para funções matemáticas custosas                         |
//+------------------------------------------------------------------+
class ArtemisMatCache {
private:
   static double m_exp_cache[1000];
   static double m_tanh_cache[1000];
   static bool   m_cache_initialized;
   static double m_cache_min;
   static double m_cache_max;
   static double m_cache_step;
   
   static void InitializeCache() {
      if(m_cache_initialized) return;
      
      m_cache_min = -5.0;
      m_cache_max = 5.0;
      m_cache_step = (m_cache_max - m_cache_min) / 999.0;
      
      for(int i = 0; i < 1000; i++) {
         double x = m_cache_min + i * m_cache_step;
         m_exp_cache[i] = MathExp(x);
         m_tanh_cache[i] = MathTanh(x);
      }
      m_cache_initialized = true;
   }

public:
   // Exponencial otimizada com cache
   static double FastExp(double x) {
      InitializeCache();
      
      if(x < m_cache_min || x > m_cache_max) {
         return MathExp(x); // Fallback para valores fora do cache
      }
      
      double index_f = (x - m_cache_min) / m_cache_step;
      int index = (int)index_f;
      
      if(index >= 999) return m_exp_cache[999];
      if(index < 0) return m_exp_cache[0];
      
      // Interpolação linear para maior precisão
      double frac = index_f - index;
      return m_exp_cache[index] * (1.0 - frac) + m_exp_cache[index + 1] * frac;
   }
   
   // Tangente hiperbólica otimizada
   static double FastTanh(double x) {
      InitializeCache();
      
      if(x < m_cache_min) return -1.0;
      if(x > m_cache_max) return 1.0;
      
      double index_f = (x - m_cache_min) / m_cache_step;
      int index = (int)index_f;
      
      if(index >= 999) return m_tanh_cache[999];
      if(index < 0) return m_tanh_cache[0];
      
      double frac = index_f - index;
      return m_tanh_cache[index] * (1.0 - frac) + m_tanh_cache[index + 1] * frac;
   }
};

// Inicialização de variáveis estáticas
double ArtemisMatCache::m_exp_cache[1000];
double ArtemisMatCache::m_tanh_cache[1000];
bool ArtemisMatCache::m_cache_initialized = false;
double ArtemisMatCache::m_cache_min = 0;
double ArtemisMatCache::m_cache_max = 0;
double ArtemisMatCache::m_cache_step = 0;

//+------------------------------------------------------------------+
//| Funções matemáticas otimizadas                                  |
//+------------------------------------------------------------------+

// Validação segura para divisão
double SafeDivide(double numerator, double denominator, double default_value = 0.0) {
   if(MathAbs(denominator) < ARTEMIS_EPSILON) {
      return default_value;
   }
   return numerator / denominator;
}

// Normalização robusta
double SafeNormalize(double value, double min_val, double max_val) {
   if(MathAbs(max_val - min_val) < ARTEMIS_EPSILON) {
      return 0.5; // Valor neutro quando range é zero
   }
   
   double normalized = (value - min_val) / (max_val - min_val);
   return MathMax(0.0, MathMin(1.0, normalized));
}

// Função de onda quântica otimizada
double QuantumWaveFunction(double momentum, double volatility) {
   if(volatility < ARTEMIS_EPSILON) {
      return 0.0; // Estado indefinido com volatilidade zero
   }
   
   double ratio = momentum / volatility;
   double exp_arg = -ratio * ratio;
   
   // Usar cache para exponencial
   return ArtemisMatCache::FastExp(exp_arg);
}

// Probabilidade quântica
double QuantumProbability(double wave_function) {
   return wave_function * wave_function;
}

// Entropia quântica (implementação que estava faltando)
double QuantumEntropy(double probability) {
   if(probability <= ARTEMIS_EPSILON || probability >= (1.0 - ARTEMIS_EPSILON)) {
      return 0.0; // Entropia zero para estados puros
   }
   
   double log_p = MathLog(probability);
   double log_1_p = MathLog(1.0 - probability);
   
   return -(probability * log_p + (1.0 - probability) * log_1_p);
}

// Correlação de Pearson incremental
class PearsonCorrelation {
private:
   double m_sum_x;
   double m_sum_y;
   double m_sum_xx;
   double m_sum_yy;
   double m_sum_xy;
   int    m_count;
   
public:
   PearsonCorrelation() : m_sum_x(0), m_sum_y(0), m_sum_xx(0), 
                         m_sum_yy(0), m_sum_xy(0), m_count(0) {}
   
   void AddPoint(double x, double y) {
      m_sum_x += x;
      m_sum_y += y;
      m_sum_xx += x * x;
      m_sum_yy += y * y;
      m_sum_xy += x * y;
      m_count++;
   }
   
   double GetCorrelation() {
      if(m_count < 2) return 0.0;
      
      double n = (double)m_count;
      double numerator = n * m_sum_xy - m_sum_x * m_sum_y;
      double denom_x = n * m_sum_xx - m_sum_x * m_sum_x;
      double denom_y = n * m_sum_yy - m_sum_y * m_sum_y;
      
      return SafeDivide(numerator, MathSqrt(denom_x * denom_y), 0.0);
   }
   
   void Reset() {
      m_sum_x = m_sum_y = m_sum_xx = m_sum_yy = m_sum_xy = 0.0;
      m_count = 0;
   }
};

#endif // ARTEMIS_QUANTUM_MATH_MQH

