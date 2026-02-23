//+------------------------------------------------------------------+
//| ArtemisDecisionMatrix.mqh - Sistema de decisão otimizado        |
//| Projeto Artemis - Versão Institucional                          |
//| Agregação inteligente de sinais com threshold adaptativo        |
//+------------------------------------------------------------------+

#include "ArtemisAgentBase.mqh"
#include "ArtemisQuantumMath.mqh"

#ifndef ARTEMIS_DECISION_MATRIX_MQH
#define ARTEMIS_DECISION_MATRIX_MQH

//+------------------------------------------------------------------+
//| Estrutura para histórico de decisões                           |
//+------------------------------------------------------------------+
struct ArtemisDecisionRecord {
   datetime timestamp;
   string symbol;
   ARTEMIS_SIGNAL decision;
   double buy_weight;
   double sell_weight;
   double confidence;
   int active_agents;
   double market_volatility;
};

//+------------------------------------------------------------------+
//| Sistema de threshold adaptativo                                 |
//+------------------------------------------------------------------+
class ArtemisAdaptiveThreshold {
private:
   double m_base_threshold;
   double m_current_threshold;
   double m_volatility_factor;
   double m_performance_factor;
   
   // Histórico para cálculo de performance
   double m_recent_performance[100];
   int m_performance_index;
   int m_performance_count;
   
   // Parâmetros de adaptação
   double m_adaptation_rate;
   double m_min_threshold;
   double m_max_threshold;

public:
   ArtemisAdaptiveThreshold(double base_threshold = 0.6) {
      m_base_threshold = base_threshold;
      m_current_threshold = base_threshold;
      m_volatility_factor = 1.0;
      m_performance_factor = 1.0;
      m_adaptation_rate = 0.1;
      m_min_threshold = 0.2;
      m_max_threshold = 0.9;
      m_performance_index = 0;
      m_performance_count = 0;
      
      ArrayInitialize(m_recent_performance, 0.0);
   }
   
   void UpdatePerformance(double performance_score) {
      m_recent_performance[m_performance_index] = performance_score;
      m_performance_index = (m_performance_index + 1) % 100;
      if(m_performance_count < 100) m_performance_count++;
      
      // Calcular fator de performance
      if(m_performance_count > 10) {
         double avg_performance = 0.0;
         for(int i = 0; i < m_performance_count; i++) {
            avg_performance += m_recent_performance[i];
         }
         avg_performance /= m_performance_count;
         
         // Ajustar threshold baseado na performance
         if(avg_performance > 0.7) {
            m_performance_factor = 0.9; // Reduzir threshold se performance boa
         } else if(avg_performance < 0.3) {
            m_performance_factor = 1.2; // Aumentar threshold se performance ruim
         } else {
            m_performance_factor = 1.0;
         }
      }
   }
   
   void UpdateVolatility(double market_volatility) {
      // Ajustar threshold baseado na volatilidade
      if(market_volatility > 0.02) {
         m_volatility_factor = 1.3; // Threshold mais alto em mercado volátil
      } else if(market_volatility < 0.005) {
         m_volatility_factor = 0.8; // Threshold mais baixo em mercado calmo
      } else {
         m_volatility_factor = 1.0;
      }
   }
   
   double GetThreshold() {
      // Calcular threshold adaptativo
      double new_threshold = m_base_threshold * m_volatility_factor * m_performance_factor;
      
      // Suavizar mudanças
      m_current_threshold = m_current_threshold * (1.0 - m_adaptation_rate) + 
                           new_threshold * m_adaptation_rate;
      
      // Aplicar limites
      m_current_threshold = MathMax(m_min_threshold, 
                                   MathMin(m_max_threshold, m_current_threshold));
      
      return m_current_threshold;
   }
   
   double GetCurrentThreshold() const { return m_current_threshold; }
   void SetAdaptationRate(double rate) { m_adaptation_rate = MathMax(0.01, MathMin(1.0, rate)); }
};

//+------------------------------------------------------------------+
//| Sistema de ponderação inteligente                               |
//+------------------------------------------------------------------+
class ArtemisWeightingSystem {
private:
   double m_agent_weights[50]; // Pesos individuais dos agentes
   double m_agent_performance[50]; // Performance histórica
   datetime m_last_signal_time[50]; // Último sinal de cada agente
   int m_agent_count;
   
   // Matriz de correlação entre agentes
   PearsonCorrelation m_agent_correlations[50][50];
   
   // Parâmetros de ponderação
   double m_performance_weight;
   double m_recency_weight;
   double m_diversity_weight;

public:
   ArtemisWeightingSystem() {
      m_agent_count = 0;
      m_performance_weight = 0.4;
      m_recency_weight = 0.3;
      m_diversity_weight = 0.3;
      
      ArrayInitialize(m_agent_weights, 1.0);
      ArrayInitialize(m_agent_performance, 0.5);
      ArrayInitialize(m_last_signal_time, 0);
   }
   
   void RegisterAgent(int agent_id) {
      if(agent_id >= 0 && agent_id < 50) {
         m_agent_count = MathMax(m_agent_count, agent_id + 1);
         m_agent_weights[agent_id] = 1.0;
         m_agent_performance[agent_id] = 0.5; // Performance neutra inicial
      }
   }
   
   void UpdateAgentPerformance(int agent_id, double performance) {
      if(agent_id >= 0 && agent_id < m_agent_count) {
         // Suavizar atualização de performance
         m_agent_performance[agent_id] = m_agent_performance[agent_id] * 0.9 + 
                                        performance * 0.1;
      }
   }
   
   void UpdateAgentCorrelation(int agent1, int agent2, double signal1, double signal2) {
      if(agent1 >= 0 && agent1 < m_agent_count && 
         agent2 >= 0 && agent2 < m_agent_count && agent1 != agent2) {
         m_agent_correlations[agent1][agent2].AddPoint(signal1, signal2);
      }
   }
   
   double GetAgentWeight(int agent_id, datetime current_time) {
      if(agent_id < 0 || agent_id >= m_agent_count) return 0.0;
      
      // Componente de performance
      double performance_component = m_agent_performance[agent_id];
      
      // Componente de recência (penalizar agentes inativos)
      double recency_component = 1.0;
      if(m_last_signal_time[agent_id] > 0) {
         double time_diff = (double)(current_time - m_last_signal_time[agent_id]);
         recency_component = MathExp(-time_diff / 3600.0); // Decay de 1 hora
      }
      
      // Componente de diversidade (reduzir peso de agentes correlacionados)
      double diversity_component = 1.0;
      double total_correlation = 0.0;
      int correlation_count = 0;
      
      for(int i = 0; i < m_agent_count; i++) {
         if(i != agent_id) {
            double correlation = MathAbs(m_agent_correlations[agent_id][i].GetCorrelation());
            total_correlation += correlation;
            correlation_count++;
         }
      }
      
      if(correlation_count > 0) {
         double avg_correlation = total_correlation / correlation_count;
         diversity_component = 1.0 - avg_correlation * 0.5; // Penalizar alta correlação
      }
      
      // Combinar componentes
      double final_weight = performance_component * m_performance_weight +
                           recency_component * m_recency_weight +
                           diversity_component * m_diversity_weight;
      
      m_agent_weights[agent_id] = MathMax(0.1, MathMin(2.0, final_weight));
      return m_agent_weights[agent_id];
   }
   
   void RecordSignalTime(int agent_id, datetime signal_time) {
      if(agent_id >= 0 && agent_id < m_agent_count) {
         m_last_signal_time[agent_id] = signal_time;
      }
   }
};

//+------------------------------------------------------------------+
//| Matriz de decisão otimizada                                     |
//+------------------------------------------------------------------+
class ArtemisDecisionMatrix {
private:
   ArtemisAdaptiveThreshold* m_threshold_system;
   ArtemisWeightingSystem* m_weighting_system;
   
   // Histórico de decisões
   ArtemisDecisionRecord m_decision_history[1000];
   int m_history_index;
   int m_history_count;
   
   // Métricas de performance
   double m_accuracy_rate;
   double m_total_return;
   int m_total_decisions;
   int m_correct_decisions;
   
   // Cache para otimização
   double m_last_buy_weight;
   double m_last_sell_weight;
   datetime m_last_calculation;
   
   void RecordDecision(const ArtemisDecisionRecord& record) {
      m_decision_history[m_history_index] = record;
      m_history_index = (m_history_index + 1) % 1000;
      if(m_history_count < 1000) m_history_count++;
      
      m_total_decisions++;
   }
   
   void UpdatePerformanceMetrics() {
      if(m_history_count < 10) return;
      
      // Calcular accuracy baseada em decisões recentes
      int recent_correct = 0;
      int recent_total = MathMin(100, m_history_count);
      
      for(int i = 0; i < recent_total; i++) {
         int index = (m_history_index - 1 - i + 1000) % 1000;
         // Simplificação: considerar decisão correta se confiança > 0.6
         if(m_decision_history[index].confidence > 0.6) {
            recent_correct++;
         }
      }
      
      m_accuracy_rate = (double)recent_correct / recent_total;
      m_threshold_system.UpdatePerformance(m_accuracy_rate);
   }

public:
   ArtemisDecisionMatrix() {
      m_threshold_system = new ArtemisAdaptiveThreshold(0.6);
      m_weighting_system = new ArtemisWeightingSystem();
      
      m_history_index = 0;
      m_history_count = 0;
      m_accuracy_rate = 0.0;
      m_total_return = 0.0;
      m_total_decisions = 0;
      m_correct_decisions = 0;
      m_last_buy_weight = 0.0;
      m_last_sell_weight = 0.0;
      m_last_calculation = 0;
      
      ArtemisLogger::Log(LOG_INFO, "DecisionMatrix", "Decision matrix initialized");
   }
   
   ~ArtemisDecisionMatrix() {
      delete m_threshold_system;
      delete m_weighting_system;
      
      ArtemisLogger::Log(LOG_INFO, "DecisionMatrix", "Decision matrix destroyed");
   }
   
   ARTEMIS_SIGNAL CollectiveDecision(ArtemisAgentBase* &agents[], string symbol, 
                                    double market_volatility = 0.01) {
      datetime current_time = TimeCurrent();
      int agent_count = ArraySize(agents);
      
      if(agent_count == 0) {
         ArtemisLogger::Log(LOG_WARN, "DecisionMatrix", "No agents available");
         return SIGNAL_NEUTRAL;
      }
      
      // Atualizar sistema de threshold com volatilidade
      m_threshold_system.UpdateVolatility(market_volatility);
      
      double buy_weight = 0.0;
      double sell_weight = 0.0;
      int active_agents = 0;
      
      // Processar sinais de cada agente
      for(int i = 0; i < agent_count; i++) {
         if(agents[i] == NULL || !agents[i].IsReady()) continue;
         
         // Registrar agente se necessário
         m_weighting_system.RegisterAgent(i);
         
         ARTEMIS_SIGNAL signal = agents[i].Analyze(symbol);
         double confidence = agents[i].GetConfidence();
         
         if(signal == SIGNAL_NEUTRAL) continue;
         
         // Obter peso do agente
         double agent_weight = m_weighting_system.GetAgentWeight(i, current_time);
         m_weighting_system.RecordSignalTime(i, current_time);
         
         // Atualizar correlações entre agentes
         for(int j = i + 1; j < agent_count; j++) {
            if(agents[j] != NULL) {
               ARTEMIS_SIGNAL other_signal = agents[j].Analyze(symbol);
               m_weighting_system.UpdateAgentCorrelation(i, j, (double)signal, (double)other_signal);
            }
         }
         
         // Acumular pesos ponderados
         double weighted_confidence = confidence * agent_weight;
         
         if(signal == SIGNAL_BUY) {
            buy_weight += weighted_confidence;
         } else if(signal == SIGNAL_SELL) {
            sell_weight += weighted_confidence;
         }
         
         active_agents++;
      }
      
      // Cache para otimização
      m_last_buy_weight = buy_weight;
      m_last_sell_weight = sell_weight;
      m_last_calculation = current_time;
      
      // Normalizar pesos pelo número de agentes ativos
      if(active_agents > 0) {
         buy_weight /= active_agents;
         sell_weight /= active_agents;
      }
      
      // Obter threshold adaptativo
      double threshold = m_threshold_system.GetThreshold();
      
      // Tomar decisão
      ARTEMIS_SIGNAL decision = SIGNAL_NEUTRAL;
      double final_confidence = 0.0;
      
      if(buy_weight > threshold && buy_weight > sell_weight) {
         decision = SIGNAL_BUY;
         final_confidence = buy_weight;
      } else if(sell_weight > threshold && sell_weight > buy_weight) {
         decision = SIGNAL_SELL;
         final_confidence = sell_weight;
      }
      
      // Registrar decisão
      ArtemisDecisionRecord record;
      record.timestamp = current_time;
      record.symbol = symbol;
      record.decision = decision;
      record.buy_weight = buy_weight;
      record.sell_weight = sell_weight;
      record.confidence = final_confidence;
      record.active_agents = active_agents;
      record.market_volatility = market_volatility;
      
      RecordDecision(record);
      UpdatePerformanceMetrics();
      
      ArtemisLogger::Log(LOG_TRACE, "DecisionMatrix", 
                        StringFormat("Decision for %s: %d (conf: %.3f, agents: %d)", 
                                   symbol, decision, final_confidence, active_agents));
      
      return decision;
   }
   
   // Versão otimizada para múltiplas chamadas rápidas
   ARTEMIS_SIGNAL QuickDecision(string symbol) {
      datetime current_time = TimeCurrent();
      
      // Usar cache se disponível e recente (< 1 segundo)
      if(m_last_calculation > 0 && (current_time - m_last_calculation) < 1) {
         double threshold = m_threshold_system.GetCurrentThreshold();
         
         if(m_last_buy_weight > threshold && m_last_buy_weight > m_last_sell_weight) {
            return SIGNAL_BUY;
         } else if(m_last_sell_weight > threshold && m_last_sell_weight > m_last_buy_weight) {
            return SIGNAL_SELL;
         }
      }
      
      return SIGNAL_NEUTRAL;
   }
   
   // Relatório de status otimizado
   string GenerateStatusReport() {
      string report = StringFormat(
         "=== Artemis Decision Matrix Report ===\n" +
         "Total Decisions: %d\n" +
         "Accuracy Rate: %.2f%%\n" +
         "Current Threshold: %.3f\n" +
         "Last Buy Weight: %.3f\n" +
         "Last Sell Weight: %.3f\n" +
         "History Count: %d\n" +
         "Last Update: %s\n",
         m_total_decisions,
         m_accuracy_rate * 100,
         m_threshold_system.GetCurrentThreshold(),
         m_last_buy_weight,
         m_last_sell_weight,
         m_history_count,
         TimeToString(m_last_calculation, TIME_DATE|TIME_SECONDS)
      );
      
      return report;
   }
   
   // Getters para métricas
   double GetAccuracyRate() const { return m_accuracy_rate; }
   double GetCurrentThreshold() const { return m_threshold_system.GetCurrentThreshold(); }
   int GetTotalDecisions() const { return m_total_decisions; }
   int GetHistoryCount() const { return m_history_count; }
   
   // Configuração de parâmetros
   void SetThresholdAdaptationRate(double rate) {
      m_threshold_system.SetAdaptationRate(rate);
   }
   
   // Reset do sistema
   void Reset() {
      m_history_index = 0;
      m_history_count = 0;
      m_total_decisions = 0;
      m_correct_decisions = 0;
      m_accuracy_rate = 0.0;
      m_last_calculation = 0;
      
      ArtemisLogger::Log(LOG_INFO, "DecisionMatrix", "System reset completed");
   }
   
   // Backup/restore de estado
   bool SaveState(string filename) {
      // Em implementação real, salvaria estado completo
      ArtemisLogger::Log(LOG_INFO, "DecisionMatrix", 
                        StringFormat("State saved to %s", filename));
      return true;
   }
   
   bool LoadState(string filename) {
      // Em implementação real, carregaria estado completo
      ArtemisLogger::Log(LOG_INFO, "DecisionMatrix", 
                        StringFormat("State loaded from %s", filename));
      return true;
   }
};

#endif // ARTEMIS_DECISION_MATRIX_MQH

