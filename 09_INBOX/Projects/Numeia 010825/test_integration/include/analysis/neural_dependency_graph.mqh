//+------------------------------------------------------------------+
//| neural_dependency_graph.mqh - Grafo Neural de Dependências       |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: include/analysis/                                        |
//| Versão: v1.1 (TIER-0+)                                        |
//| Atualizado em: 2025-07-24               |
//| Status: TIER-0+ | 10K+/dia Ready                                |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __NEURAL_DEPENDENCY_GRAPH_MQH__
#define __NEURAL_DEPENDENCY_GRAPH_MQH__

#include <include/analysis/dependency_graph.mqh>
#include <NeuroNet.mqh>

//+------------------------------------------------------------------+
//| Grafo de Dependências com Previsão Neural                       |
//+------------------------------------------------------------------+
class CNeuralDependencyGraph : public CDependencyGraph
{
private:
   CNeuroNet *m_prediction_net;
   logger_institutional &m_logger;

   //+--------------------------------------------------------------+
   //| Prediz risco de inicialização                                 |
   //+--------------------------------------------------------------+
   bool PredictInitializationRisk(string node_path)
   {
      int node_idx = -1;
      for(int i=0; i<ArraySize(m_nodes); i++)
      {
         if(m_nodes[i].path == node_path)
         {
            node_idx = i;
            break;
         }
      }

      if(node_idx == -1) return true; // Alto risco se nó não existir

      double inputs[5] = {
         (double)m_nodes[node_idx].priority,
         (double)ArraySize(m_edges),
         (double)(m_nodes[node_idx].is_critical ? 1.0 : 0.0),
         (double)m_firewall.GetSecurityLevel(),
         (double)m_logger.GetErrorCount()
      };

      double output[1];
      m_prediction_net->FeedForward(inputs, output);

      return output[0] > 0.5;
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CNeuralDependencyGraph(logger_institutional &logger,
                        QuantumFirewall &firewall,
                        QuantumLearning &learning,
                        string project_root = "MQL5/") :
      CDependencyGraph(logger, firewall, learning, project_root),
      m_logger(logger)
   {
      m_prediction_net = new CNeuroNet(5, 10, 1);
      if(m_prediction_net == NULL)
      {
         m_logger.log_error("[NEURAL-GRAPH] Falha ao criar rede neural de previsão");
         ExpertRemove();
      }
      m_logger.log_info("[NEURAL-GRAPH] Grafo Neural de Dependências inicializado");
   }

   //+--------------------------------------------------------------+
   //| Valida dependências com previsão neural                       |
   //+--------------------------------------------------------------+
   bool ValidateDependencies(string node_path)
   {
      if(PredictInitializationRisk(node_path))
      {
         m_logger.log_warning("[NEURAL-GRAPH] Alto risco de falha previsto para: " + node_path);
      }

      return CDependencyGraph::ValidateNode(node_path);
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~CNeuralDependencyGraph()
   {
      if(m_prediction_net != NULL)
      {
         delete m_prediction_net;
         m_prediction_net = NULL;
      }
      m_logger.log_info("[NEURAL-GRAPH] Grafo Neural encerrado");
   }
};

#endif // __NEURAL_DEPENDENCY_GRAPH_MQH__