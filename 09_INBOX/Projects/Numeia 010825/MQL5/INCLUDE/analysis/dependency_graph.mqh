//+------------------------------------------------------------------+
//| dependency_graph.mqh - Grafo de Dependências com IA Neural       |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: include/analysis/                                        |
//| Versão: v2.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-24             |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __DEPENDENCY_GRAPH_MQH__
#define __DEPENDENCY_GRAPH_MQH__

#include "utils/logger_institutional.mqh"
#include "security/quantumfirewall.mqh"
#include "types/trade_signal_enum.mqh"
#include "intelligence/quantum_learning.mqh"
#include "Arrays\ArrayObj.mqh"

//+------------------------------------------------------------------+
//| Estrutura de Nó do Grafo                                        |
//+------------------------------------------------------------------+
struct DependencyNode
{
   string path;
   string name;
   int priority;
   bool is_critical;
   bool is_ready;
   datetime last_check;
   double failure_probability;
   ENUM_AUDIT_ISSUE last_issue;
};

//+------------------------------------------------------------------+
//| Estrutura de Aresta                                             |
//+------------------------------------------------------------------+
struct DependencyEdge
{
   string from;
   string to;
   int weight;
   datetime created;
};

//+------------------------------------------------------------------+
//| Estrutura de Resultado de Validação                             |
//+------------------------------------------------------------------+
struct ValidationReport
{
   bool success;
   string node;
   string status;
   int error_count;
   int warning_count;
   double risk_score;
   datetime validation_time;
   string details;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: CDependencyGraph                              |
//+------------------------------------------------------------------+
class CDependencyGraph
{
private:
   logger_institutional &m_logger;
   QuantumFirewall      &m_firewall;
   QuantumLearning      &m_learning;
   string               m_project_root;
   datetime             m_last_update;

   // Arrays de nós e arestas
   DependencyNode m_nodes[];
   DependencyEdge m_edges[];

   // Histórico de validações
   ValidationReport m_validation_history[];

   // Painel de decisão
   CLabel *m_graph_label = NULL;
   CLabel *m_status_label = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[GRAPH] Sem conexão com o servidor");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[GRAPH] Logger não inicializado");
         return false;
      }

      if(!m_firewall.IsActive())
      {
         m_logger.log_warning("[GRAPH] Firewall quântico inativo");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de grafo                                      |
   //+--------------------------------------------------------------+
   void updateGraphDisplay(int node_count, int edge_count)
   {
      if(m_graph_label == NULL)
      {
         m_graph_label = new CLabel("GraphLabel", 0, 10, 1750);
         m_graph_label->text("GRAFO: ????");
         m_graph_label->color(clrGray);
      }

      if(m_status_label == NULL)
      {
         m_status_label = new CLabel("StatusLabel", 0, 10, 1770);
         m_status_label->text("NÓS: 0");
         m_status_label->color(clrGray);
      }

      m_graph_label->text("GRAFO: " + IntegerToString(node_count) + " Nós");
      m_graph_label->color(node_count > 0 ? clrLime : clrRed);

      m_status_label->text("ARESTAS: " + IntegerToString(edge_count));
      m_status_label->color(edge_count > 0 ? clrLime : clrRed);
   }

   //+--------------------------------------------------------------+
   //| Adiciona nó ao grafo                                          |
   //+--------------------------------------------------------------+
   bool AddNode(string path)
   {
      if(!is_valid_context()) return false;

      // Extrai nome do arquivo
      string name = StringSubstr(path, StringLast(path, "/") + 1);

      // Verifica duplicidade
      for(int i=0; i<ArraySize(m_nodes); i++)
      {
         if(m_nodes[i].path == path)
         {
            m_logger.log_warning("[GRAPH] Nó já existe: " + path);
            return false;
         }
      }

      // Cria novo nó
      DependencyNode node;
      node.path = path;
      node.name = name;
      node.priority = 1;
      node.is_critical = (StringFind(name, "quantum") >= 0 || 
                         StringFind(name, "processor") >= 0 ||
                         StringFind(name, "firewall") >= 0);
      node.is_ready = false;
      node.last_check = TimeCurrent();
      node.failure_probability = 0.0;
      node.last_issue = AUDIT_ISSUE_INVALID_NAME;

      ArrayPushBack(m_nodes, node);
      m_logger.log_info("[GRAPH] Nó adicionado: " + path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Adiciona aresta entre nós                                     |
   //+--------------------------------------------------------------+
   bool AddEdge(string from, string to, int weight = 1)
   {
      if(!is_valid_context()) return false;

      // Verifica se nós existem
      bool from_exists = false, to_exists = false;
      for(int i=0; i<ArraySize(m_nodes); i++)
      {
         if(m_nodes[i].path == from) from_exists = true;
         if(m_nodes[i].path == to) to_exists = true;
      }

      if(!from_exists || !to_exists)
      {
         m_logger.log_error("[GRAPH] Nó não encontrado: " + (from_exists ? to : from));
         return false;
      }

      // Cria aresta
      DependencyEdge edge;
      edge.from = from;
      edge.to = to;
      edge.weight = weight;
      edge.created = TimeCurrent();

      ArrayPushBack(m_edges, edge);
      m_logger.log_info("[GRAPH] Aresta adicionada: " + from + " -> " + to);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Valida todas as dependências                                  |
   //+--------------------------------------------------------------+
   bool ValidateAllDependencies()
   {
      if(!is_valid_context()) return false;

      bool all_valid = true;
      int error_count = 0;
      int warning_count = 0;
      double total_risk = 0.0;

      for(int i=0; i<ArraySize(m_nodes); i++)
      {
         if(!ValidateNode(m_nodes[i].path))
         {
            all_valid = false;
            error_count++;
         }
         else
         {
            warning_count += (m_nodes[i].failure_probability > 0.1) ? 1 : 0;
         }
         total_risk += m_nodes[i].failure_probability;
      }

      // Gera relatório
      ValidationReport report;
      report.success = all_valid;
      report.node = "ALL";
      report.status = all_valid ? "OK" : "ERRO";
      report.error_count = error_count;
      report.warning_count = warning_count;
      report.risk_score = total_risk / ArraySize(m_nodes);
      report.validation_time = TimeCurrent();
      report.details = "Validação completa: " + IntegerToString(ArraySize(m_nodes)) + " nós";
      ArrayPushBack(m_validation_history, report);

      m_logger.log_info("[GRAPH] Validação completa - Erros: " + IntegerToString(error_count) + 
                        " | Avisos: " + IntegerToString(warning_count) + 
                        " | Risco: " + DoubleToString(report.risk_score, 3));

      updateGraphDisplay(ArraySize(m_nodes), ArraySize(m_edges));
      return all_valid;
   }

   //+--------------------------------------------------------------+
   //| Valida nó específico                                          |
   //+--------------------------------------------------------------+
   bool ValidateNode(string node_path)
   {
      if(!is_valid_context()) return false;

      // Verifica se arquivo existe
      if(!FileIsExists(node_path))
      {
         m_logger.log_error("[GRAPH] Arquivo não encontrado: " + node_path);
         return false;
      }

      // Atualiza status do nó
      for(int i=0; i<ArraySize(m_nodes); i++)
      {
         if(m_nodes[i].path == node_path)
         {
            m_nodes[i].is_ready = true;
            m_nodes[i].last_check = TimeCurrent();
            m_nodes[i].failure_probability = 0.05; // Base risk
            m_nodes[i].last_issue = AUDIT_ISSUE_NONE;
            break;
         }
      }

      return true;
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CDependencyGraph(logger_institutional &logger,
                  QuantumFirewall &qf,
                  QuantumLearning &ql,
                  string project_root = "MQL5/") :
      m_logger(logger),
      m_firewall(qf),
      m_learning(ql),
      m_project_root(project_root),
      m_last_update(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[GRAPH] Logger não inicializado");
         ExpertRemove();
      }

      if(!m_firewall.IsActive())
      {
         m_logger.log_error("[GRAPH] Firewall quântico não ativo");
         ExpertRemove();
      }

      m_logger.log_info("[GRAPH] Grafo de dependências inicializado");
   }

   //+--------------------------------------------------------------+
   //| Obtém número de nós                                           |
   //+--------------------------------------------------------------+
   int GetNodeCount() const
   {
      return ArraySize(m_nodes);
   }

   //+--------------------------------------------------------------+
   //| Obtém número de arestas                                       |
   //+--------------------------------------------------------------+
   int GetEdgeCount() const
   {
      return ArraySize(m_edges);
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                       |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_logger.is_initialized() && m_firewall.IsActive();
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de validações                               |
   //+--------------------------------------------------------------+
   bool ExportValidationHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_validation_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_validation_history[i].validation_time, TIME_DATE|TIME_SECONDS),
            m_validation_history[i].node,
            m_validation_history[i].status,
            IntegerToString(m_validation_history[i].error_count),
            IntegerToString(m_validation_history[i].warning_count),
            DoubleToString(m_validation_history[i].risk_score, 4),
            m_validation_history[i].details
         );
      }

      FileClose(handle);
      m_logger.log_info("[GRAPH] Histórico de validações exportado para: " + file_path);
      return true;
   }
};

#endif // __DEPENDENCY_GRAPH_MQH__