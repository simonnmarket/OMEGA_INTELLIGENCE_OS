//+------------------------------------------------------------------+
//| dependency_graph.mqh - Grafo de Dependências Quântico            |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Analysis/                                        |
//| Versão: v1.0 (TIER-0 Compliant)                               |
//| Atualizado em: 2025-07-24 | Agente: Qwen (CEO Mode)              |
//+------------------------------------------------------------------+
#ifndef __DEPENDENCY_GRAPH_MQH__
#define __DEPENDENCY_GRAPH_MQH__

#include <include/utils/logger_institutional.mqh>

//+------------------------------------------------------------------+
//| Estrutura de Dependência                                         |
//+------------------------------------------------------------------+
struct DependencyEdge {
   string from;
   string to;
   datetime timestamp;
   bool is_critical;
   double weight;
};

//+------------------------------------------------------------------+
//| Estrutura de Ciclo Detectado                                     |
//+------------------------------------------------------------------+
struct DetectedCycle {
   string cycle_path[];
   int cycle_length;
   bool is_critical;
   string description;
   datetime detected_time;
};

//+------------------------------------------------------------------+
//| Classe CDependencyGraph Melhorada                                |
//+------------------------------------------------------------------+
class CDependencyGraph
{
private:
   logger_institutional &m_logger;
   DependencyEdge m_edges[];
   DetectedCycle m_cycles[];
   int m_total_nodes;
   int m_total_edges;
   int m_critical_cycles;
   
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

      return true;
   }

   //+--------------------------------------------------------------+
   //| Encontra nó no grafo                                          |
   //+--------------------------------------------------------------+
   int FindNode(string node_name)
   {
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         if(m_edges[i].from == node_name || m_edges[i].to == node_name)
            return i;
      }
      return -1;
   }

   //+--------------------------------------------------------------+
   //| Verifica se existe caminho entre dois nós                     |
   //+--------------------------------------------------------------+
   bool HasPath(string from, string to, string &path[])
   {
      if(from == to) return true;
      
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         if(m_edges[i].from == from)
         {
            ArrayPushBack(path, m_edges[i].from);
            if(HasPath(m_edges[i].to, to, path))
            {
               ArrayPushBack(path, m_edges[i].to);
               return true;
            }
            ArrayResize(path, ArraySize(path) - 1);
         }
      }
      return false;
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                    |
   //+--------------------------------------------------------------+
   CDependencyGraph(logger_institutional &logger) : 
      m_logger(logger),
      m_total_nodes(0),
      m_total_edges(0),
      m_critical_cycles(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[GRAPH] Logger não inicializado");
         return;
      }

      m_logger.log_info("[GRAPH] Grafo de dependências inicializado");
   }

   //+--------------------------------------------------------------+
   //| Adiciona aresta ao grafo                                      |
   //+--------------------------------------------------------------+
   void AddEdge(string from, string to, bool is_critical = false, double weight = 1.0)
   {
      if(!is_valid_context()) return;

      DependencyEdge edge;
      edge.from = from;
      edge.to = to;
      edge.timestamp = TimeCurrent();
      edge.is_critical = is_critical;
      edge.weight = weight;

      ArrayPushBack(m_edges, edge);
      m_total_edges++;

      m_logger.log_debug(StringFormat("[GRAPH] Aresta adicionada: %s -> %s (Crítico: %s, Peso: %.2f)", 
                                     from, to, is_critical ? "SIM" : "NÃO", weight));
   }

   //+--------------------------------------------------------------+
   //| Detecta ciclos simples (2 nós)                                |
   //+--------------------------------------------------------------+
   bool FindSimpleCycles(string &cycles[])
   {
      if(!is_valid_context()) return false;

      bool found = false;
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         for(int j = 0; j < ArraySize(m_edges); j++)
         {
            if(i != j && m_edges[i].to == m_edges[j].from && m_edges[i].from == m_edges[j].to)
            {
               string cycle = m_edges[i].from + " <-> " + m_edges[i].to;
               ArrayPushBack(cycles, cycle);
               m_logger.log_error("[GRAPH] Ciclo simples detectado: " + cycle);
               found = true;
            }
         }
      }
      return found;
   }

   //+--------------------------------------------------------------+
   //| Detecta ciclos complexos (3+ nós)                             |
   //+--------------------------------------------------------------+
   bool FindComplexCycles(string &cycles[])
   {
      if(!is_valid_context()) return false;

      bool found = false;
      string visited[];
      string path[];

      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         ArrayInitialize(visited);
         ArrayInitialize(path);
         
         if(FindComplexCycleFromNode(m_edges[i].from, m_edges[i].from, visited, path, cycles))
         {
            found = true;
         }
      }
      return found;
   }

   //+--------------------------------------------------------------+
   //| Busca recursiva para ciclos complexos                         |
   //+--------------------------------------------------------------+
   bool FindComplexCycleFromNode(string start_node, string current_node, 
                                string &visited[], string &path[], string &cycles[])
   {
      // Verifica se já visitou este nó
      for(int i = 0; i < ArraySize(visited); i++)
      {
         if(visited[i] == current_node)
         {
            // Encontrou ciclo
            if(current_node == start_node && ArraySize(path) > 2)
            {
               string cycle_path = "";
               for(int j = 0; j < ArraySize(path); j++)
               {
                  cycle_path += path[j];
                  if(j < ArraySize(path) - 1) cycle_path += " -> ";
               }
               cycle_path += " -> " + start_node;
               
               ArrayPushBack(cycles, cycle_path);
               m_logger.log_error("[GRAPH] Ciclo complexo detectado: " + cycle_path);
               return true;
            }
            return false;
         }
      }

      // Marca como visitado
      ArrayPushBack(visited, current_node);
      ArrayPushBack(path, current_node);

      // Busca vizinhos
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         if(m_edges[i].from == current_node)
         {
            if(FindComplexCycleFromNode(start_node, m_edges[i].to, visited, path, cycles))
            {
               return true;
            }
         }
      }

      // Remove do caminho
      ArrayResize(path, ArraySize(path) - 1);
      return false;
   }

   //+--------------------------------------------------------------+
   //| Detecta todos os tipos de ciclos                              |
   //+--------------------------------------------------------------+
   bool FindAllCycles(string &cycles[])
   {
      if(!is_valid_context()) return false;

      bool found_simple = FindSimpleCycles(cycles);
      bool found_complex = FindComplexCycles(cycles);

      if(found_simple || found_complex)
      {
         m_logger.log_warning(StringFormat("[GRAPH] Total de ciclos detectados: %d", ArraySize(cycles)));
         return true;
      }

      return false;
   }

   //+--------------------------------------------------------------+
   //| Analisa profundidade das dependências                          |
   //+--------------------------------------------------------------+
   int GetMaxDepth(string node_name)
   {
      if(!is_valid_context()) return 0;

      int max_depth = 0;
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         if(m_edges[i].from == node_name)
         {
            int depth = GetMaxDepth(m_edges[i].to) + 1;
            if(depth > max_depth) max_depth = depth;
         }
      }
      return max_depth;
   }

   //+--------------------------------------------------------------+
   //| Calcula métricas do grafo                                     |
   //+--------------------------------------------------------------+
   void CalculateMetrics(int &total_nodes, int &total_edges, int &critical_edges, int &cycles_count)
   {
      if(!is_valid_context()) return;

      total_nodes = 0;
      total_edges = ArraySize(m_edges);
      critical_edges = 0;
      cycles_count = 0;

      // Conta nós únicos
      string unique_nodes[];
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         bool found_from = false, found_to = false;
         for(int j = 0; j < ArraySize(unique_nodes); j++)
         {
            if(unique_nodes[j] == m_edges[i].from) found_from = true;
            if(unique_nodes[j] == m_edges[i].to) found_to = true;
         }
         if(!found_from) ArrayPushBack(unique_nodes, m_edges[i].from);
         if(!found_to) ArrayPushBack(unique_nodes, m_edges[i].to);
         
         if(m_edges[i].is_critical) critical_edges++;
      }
      total_nodes = ArraySize(unique_nodes);

      // Conta ciclos
      string cycles[];
      FindAllCycles(cycles);
      cycles_count = ArraySize(cycles);

      m_logger.log_info(StringFormat("[GRAPH] Métricas: Nós=%d, Arestas=%d, Críticas=%d, Ciclos=%d", 
                                    total_nodes, total_edges, critical_edges, cycles_count));
   }

   //+--------------------------------------------------------------+
   //| Exporta grafo para análise                                    |
   //+--------------------------------------------------------------+
   bool ExportGraph(string file_path)
   {
      if(!is_valid_context()) return false;

      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      FileWrite(handle, "FROM", "TO", "CRITICAL", "WEIGHT", "TIMESTAMP");
      
      for(int i = 0; i < ArraySize(m_edges); i++)
      {
         FileWrite(handle,
            m_edges[i].from,
            m_edges[i].to,
            m_edges[i].is_critical ? "SIM" : "NÃO",
            DoubleToString(m_edges[i].weight, 2),
            TimeToString(m_edges[i].timestamp, TIME_DATE|TIME_SECONDS)
         );
      }

      FileClose(handle);
      m_logger.log_info("[GRAPH] Grafo exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                        |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_logger.is_initialized();
   }

   //+--------------------------------------------------------------+
   //| Obtém estatísticas do grafo                                   |
   //+--------------------------------------------------------------+
   void GetStatistics(int &nodes, int &edges, int &cycles)
   {
      CalculateMetrics(nodes, edges, edges, cycles);
   }
};

#endif // __DEPENDENCY_GRAPH_MQH__ 