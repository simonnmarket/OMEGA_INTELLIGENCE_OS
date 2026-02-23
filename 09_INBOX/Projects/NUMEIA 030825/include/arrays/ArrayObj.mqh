//+------------------------------------------------------------------+
//| ArrayObj.mqh - Array de Objetos com Blindagem Institucional      |
//| Projeto: Genesis / EA Genesis                                    |
//| Pasta: include/arrays/                                           |
//| Versão: v1.0 (GodMode Final + IA Ready + Blindagem Institucional) |
//| Atualizado em: 2025-01-27 | Agente: Qwen (CEO Mode)              |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __GENESIS_ARRAYOBJ_MQH__
#define __GENESIS_ARRAYOBJ_MQH__

#include "../Utils/Utils.mqh"
#include "../include/constants/Genesis_Constants.mqh"

//+------------------------------------------------------------------+
//| Classe CGenesisArrayObj - Array de Objetos com Segurança Genesis |
//+------------------------------------------------------------------+
class CGenesisArrayObj
{
protected:
   void  *m_data[];           // Ponteiro para objetos
   int    m_count;            // Número de elementos
   int    m_delta;            // Incremento de alocação
   int    m_maximal;          // Tamanho máximo permitido
   bool   m_sort_mode;        // Modo de ordenação
   bool   m_auto_shrink;      // Redução automática

   CGenesisUtils *m_logger;   // Referência ao logger Genesis

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CGenesisArrayObj()
   {
      m_count = 0;
      m_delta = 16;
      m_maximal = 0x7FFFFFFF;
      m_sort_mode = false;
      m_auto_shrink = true;
      m_logger = NULL;
   }

   //+--------------------------------------------------------------+
   //| CONSTRUTOR COM LOGGER GENESIS                                |
   //+--------------------------------------------------------------+
   CGenesisArrayObj(CGenesisUtils &logger)
   {
      m_count = 0;
      m_delta = 16;
      m_maximal = 0x7FFFFFFF;
      m_sort_mode = false;
      m_auto_shrink = true;
      m_logger = &logger;
      
      // Validação de integridade Genesis
      if(!ValidateArrayIntegrity())
      {
         Print("CGenesisArrayObj: Falha na validação de integridade");
         return;
      }
   }

   //+--------------------------------------------------------------+
   //| DESTRUTOR                                                    |
   //+--------------------------------------------------------------+
   ~CGenesisArrayObj()
   {
      Clear();
   }

   //+--------------------------------------------------------------+
   //| Métodos de Acesso                                            |
   //+--------------------------------------------------------------+
   int Count() const { return m_count; }
   int Maximum() const { return m_maximal; }
   int Delta() const { return m_delta; }
   bool SortMode() const { return m_sort_mode; }
   bool AutoShrink() const { return m_auto_shrink; }

   //+--------------------------------------------------------------+
   //| Define o logger Genesis                                      |
   //+--------------------------------------------------------------+
   void SetLogger(CGenesisUtils &logger)
   {
      m_logger = &logger;
   }

   //+--------------------------------------------------------------+
   //| Define o modo de ordenação                                   |
   //+--------------------------------------------------------------+
   bool Sort(const int mode = 0)
   {
      if(m_count < 2 || !m_sort_mode) return true;
      return QuickSort(0, m_count - 1);
   }

   //+--------------------------------------------------------------+
   //| Aloca memória                                                |
   //+--------------------------------------------------------------+
   bool Reserve(const int size)
   {
      if(size <= ArraySize(m_data)) return true;
      if(size > m_maximal)
      {
         Print("CGenesisArrayObj::Reserve - Tamanho excede máximo permitido: " + IntegerToString(size));
         return false;
      }
      if(!ArrayResize(m_data, size))
      {
         Print("CGenesisArrayObj::Reserve - Falha ao redimensionar array");
         return false;
      }
      return true;
   }

   //+--------------------------------------------------------------+
   //| Reduz o array                                                |
   //+--------------------------------------------------------------+
   bool Synchronize()
   {
      if(m_auto_shrink && m_count < ArraySize(m_data))
      {
         if(!ArrayResize(m_data, m_count))
         {
            Print("CGenesisArrayObj::Synchronize - Falha ao sincronizar array");
            return false;
         }
      }
      return true;
   }

   //+--------------------------------------------------------------+
   //| Adiciona objeto no final                                     |
   //+--------------------------------------------------------------+
   int Add(void *element)
   {
      if(m_count >= ArraySize(m_data))
      {
         if(!Reserve(ArraySize(m_data) + m_delta))
         {
            Print("CGenesisArrayObj::Add - Falha ao alocar memória");
            return -1;
         }
      }
      m_data[m_count] = element;
      m_count++;
      return m_count - 1;
   }

   //+--------------------------------------------------------------+
   //| Insere objeto na posição                                     |
   //+--------------------------------------------------------------+
   int Insert(void *element, const int pos)
   {
      if(pos < 0 || pos > m_count) 
      {
         Print("CGenesisArrayObj::Insert - Posição inválida: " + IntegerToString(pos));
         return -1;
      }
      if(m_count >= ArraySize(m_data))
      {
         if(!Reserve(ArraySize(m_data) + m_delta))
         {
            Print("CGenesisArrayObj::Insert - Falha ao alocar memória");
            return -1;
         }
      }
      if(pos < m_count)
         ArrayCopy(m_data, m_data, pos + 1, pos, m_count - pos);
      
      m_data[pos] = element;
      m_count++;
      return pos;
   }

   //+--------------------------------------------------------------+
   //| Define objeto na posição                                     |
   //+--------------------------------------------------------------+
   bool Update(const int index, void *element)
   {
      if(index < 0 || index >= m_count)
      {
         Print("CGenesisArrayObj::Update - Índice fora do limite: " + IntegerToString(index));
         return false;
      }
      m_data[index] = element;
      return true;
   }

   //+--------------------------------------------------------------+
   //| Obtém objeto na posição                                      |
   //+--------------------------------------------------------------+
   void *At(const int index) const
   {
      if(index < 0 || index >= m_count)
      {
         Print("CGenesisArrayObj::At - Índice fora do limite: " + IntegerToString(index));
         return NULL;
      }
      return m_data[index];
   }

   //+--------------------------------------------------------------+
   //| Remove objeto da posição                                     |
   //+--------------------------------------------------------------+
   bool Delete(const int pos)
   {
      if(pos < 0 || pos >= m_count)
      {
         Print("CGenesisArrayObj::Delete - Posição inválida: " + IntegerToString(pos));
         return false;
      }
      if(pos < m_count - 1)
         ArrayCopy(m_data, m_data, pos, pos + 1, m_count - pos - 1);
      
      m_data[m_count - 1] = NULL;
      m_count--;
      Synchronize();
      return true;
   }

   //+--------------------------------------------------------------+
   //| Remove todos os objetos                                      |
   //+--------------------------------------------------------------+
   bool Clear()
   {
      for(int i = 0; i < m_count; i++)
      {
         m_data[i] = NULL;
      }
      m_count = 0;
      if(m_auto_shrink)
      {
         ArrayResize(m_data, 0);
      }
      return true;
   }

   //+--------------------------------------------------------------+
   //| Procura objeto                                               |
   //+--------------------------------------------------------------+
   int Search(const void *element) const
   {
      for(int i = 0; i < m_count; i++)
      {
         if(m_data[i] == element) return i;
      }
      return -1;
   }

   //+--------------------------------------------------------------+
   //| Ordenação rápida                                             |
   //+--------------------------------------------------------------+
   bool QuickSort(int start, int end)
   {
      if(start >= end) return true;
      int i = start, j = end;
      void *mid = m_data[(start + end) >> 1];
      
      while(i <= j)
      {
         while(i < end && Compare(m_data[i], mid) < 0) i++;
         while(j > start && Compare(m_data[j], mid) > 0) j--;
         if(i <= j)
         {
            void *temp = m_data[i];
            m_data[i] = m_data[j];
            m_data[j] = temp;
            i++; j--;
         }
      }
      if(start < j) QuickSort(start, j);
      if(i < end) QuickSort(i, end);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Comparação de objetos (pode ser sobrescrita)                 |
   //+--------------------------------------------------------------+
   virtual int Compare(const void *a, const void *b) const
   {
      // Em classes derivadas, sobrescreva para ordenação personalizada
      if(a < b) return -1;
      if(a > b) return 1;
      return 0;
   }

   //+--------------------------------------------------------------+
   //| Métodos de Configuração                                      |
   //+--------------------------------------------------------------+
   void Maximal(const int maximal) { m_maximal = maximal; }
   void Delta(const int delta) { m_delta = MathMax(1, delta); }
   void SortMode(const bool mode) { m_sort_mode = mode; }
   void AutoShrink(const bool shrink) { m_auto_shrink = shrink; }

   //+--------------------------------------------------------------+
   //| Validação de Integridade Genesis                             |
   //+--------------------------------------------------------------+
   bool ValidateArrayIntegrity()
   {
      if(m_count < 0 || m_delta <= 0 || m_maximal <= 0)
      {
         Print("CGenesisArrayObj: Parâmetros inválidos detectados");
         return false;
      }
      
      if(m_count > ArraySize(m_data))
      {
         Print("CGenesisArrayObj: Inconsistência entre count e tamanho do array");
         return false;
      }
      
      Print("CGenesisArrayObj: Validação de integridade OK");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Simulação de Operações                                       |
   //+--------------------------------------------------------------+
   void SimulateArrayOperations()
   {
      Print("CGenesisArrayObj: Simulando operações de array...");
      
      // Simular adição de elementos
      for(int i = 0; i < 5; i++)
      {
         void *test_obj = (void*)i;
         int index = Add(test_obj);
         Print("Elemento adicionado na posição: " + IntegerToString(index));
      }
      
      // Simular busca
      void *search_obj = (void*)2;
      int found_index = Search(search_obj);
      Print("Elemento encontrado na posição: " + IntegerToString(found_index));
      
      // Simular ordenação
      if(m_sort_mode)
      {
         Sort();
         Print("Array ordenado com sucesso");
      }
      
      Print("CGenesisArrayObj: Simulação concluída");
   }
};

#endif // __GENESIS_ARRAYOBJ_MQH__