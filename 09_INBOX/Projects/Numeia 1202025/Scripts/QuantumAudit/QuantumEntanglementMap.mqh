//+------------------------------------------------------------------+
//|                                    QuantumEntanglementMap.mqh     |
//|         Módulo de Mapeamento Quântico de Emaranhamento - Auditoria     |
//+------------------------------------------------------------------+
#ifndef QUANTUM_ENTANGLEMENT_MAP_MQH
#define QUANTUM_ENTANGLEMENT_MAP_MQH

#include "../../Utils/Log.mqh"
#include <Arrays\ArrayString.mqh>
#include <Arrays\ArrayInt.mqh>
#include <Arrays\ArrayDouble.mqh>

// Representação de ligação entre dois módulos
struct EntanglementLink
{
   string ModuleA;
   string ModuleB;
   double Strength; // de 0.0 a 1.0
   string Justification;
};

// Mapeador de emaranhamento quântico entre arquivos do projeto
class QuantumEntanglementMap
{
private:
   CArrayString m_Modules;
   EntanglementLink m_Links[]; // Array simples em vez de CArrayObj

public:
   bool Init()
   {
      m_Modules.Clear();
      ArrayResize(m_Links, 0);
      AuditLog("[QuantumEntanglementMap] Módulo iniciado com sucesso.", LOG_LEVEL_INFO);
      return true;
   }

   void RegisterModule(const string &name)
   {
      if(m_Modules.Search(name) == -1)
      {
         m_Modules.Add(name);
         AuditLog("Módulo registrado: " + name, LOG_LEVEL_DEBUG);
      }
   }

   void CreateLink(const string &modA, const string &modB, double strength, const string justification)
   {
      int size = ArraySize(m_Links);
      ArrayResize(m_Links, size + 1);
      
      m_Links[size].ModuleA = modA;
      m_Links[size].ModuleB = modB;
      m_Links[size].Strength = strength;
      m_Links[size].Justification = justification;
      
      AuditLog("Link criado: " + modA + " <--> " + modB + 
               " (" + DoubleToString(strength, 2) + ") [" + justification + "]", LOG_LEVEL_DEBUG);
   }

   int LinksTotal()
   {
      return ArraySize(m_Links);
   }

   void PrintAllLinks()
   {
      AuditLog("[QuantumEntanglementMap] Lista de emaranhamentos registrados:", LOG_LEVEL_INFO);
      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         AuditLog("- " + m_Links[i].ModuleA + " <--> " + m_Links[i].ModuleB + 
                  " | Força: " + DoubleToString(m_Links[i].Strength, 2) + 
                  " | Motivo: " + m_Links[i].Justification, LOG_LEVEL_DEBUG);
      }
   }

   // Validar link de um módulo
   bool ValidateLink(const string &moduleName)
   {
      AuditLog("Validando link para módulo: " + moduleName, LOG_LEVEL_DEBUG);
      
      // Verificar se o módulo existe
      if(!FileIsExist(moduleName))
      {
         LogWarning("Módulo não encontrado: " + moduleName);
         return false;
      }

      // Verificar se há links para este módulo
      bool hasLinks = false;
      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         if(m_Links[i].ModuleA == moduleName || m_Links[i].ModuleB == moduleName)
         {
            hasLinks = true;
            break;
         }
      }

      if(!hasLinks)
      {
         LogWarning("Módulo sem links de emaranhamento: " + moduleName);
         return false;
      }

      AuditLog("Link validado com sucesso: " + moduleName, LOG_LEVEL_DEBUG);
      return true;
   }

   // Analisar padrões de emaranhamento
   void AnalyzeEntanglementPatterns()
   {
      AuditLog("[QuantumEntanglementMap] Analisando padrões de emaranhamento...", LOG_LEVEL_INFO);
      
      int totalLinks = ArraySize(m_Links);
      int strongLinks = 0;
      int weakLinks = 0;
      double totalStrength = 0.0;
      
      for(int i = 0; i < totalLinks; i++)
      {
         totalStrength += m_Links[i].Strength;
         
         if(m_Links[i].Strength > 0.7)
            strongLinks++;
         else if(m_Links[i].Strength < 0.3)
            weakLinks++;
      }
      
      double avgStrength = (totalLinks > 0) ? totalStrength / totalLinks : 0.0;
      
      AuditLog("Análise de padrões - Total: " + IntegerToString(totalLinks) + 
               ", Fortes: " + IntegerToString(strongLinks) + 
               ", Fracas: " + IntegerToString(weakLinks) + 
               ", Média: " + DoubleToString(avgStrength, 3), LOG_LEVEL_INFO);
   }

   // Detectar módulos críticos (altamente emaranhados)
   void DetectCriticalModules(string &criticalModules[])
   {
      ArrayResize(criticalModules, 0);
      
      // Contar conexões por módulo usando arrays simples
      string allModules[];
      int connectionCounts[];
      double totalStrengths[];
      
      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         // Processar módulo A
         int indexA = -1;
         for(int j = 0; j < ArraySize(allModules); j++)
         {
            if(allModules[j] == m_Links[i].ModuleA)
            {
               indexA = j;
               break;
            }
         }
         
         if(indexA == -1)
         {
            int newSize = ArraySize(allModules) + 1;
            ArrayResize(allModules, newSize);
            ArrayResize(connectionCounts, newSize);
            ArrayResize(totalStrengths, newSize);
            
            allModules[newSize - 1] = m_Links[i].ModuleA;
            connectionCounts[newSize - 1] = 1;
            totalStrengths[newSize - 1] = m_Links[i].Strength;
         }
         else
         {
            connectionCounts[indexA]++;
            totalStrengths[indexA] += m_Links[i].Strength;
         }
         
         // Processar módulo B
         int indexB = -1;
         for(int j = 0; j < ArraySize(allModules); j++)
         {
            if(allModules[j] == m_Links[i].ModuleB)
            {
               indexB = j;
               break;
            }
         }
         
         if(indexB == -1)
         {
            int newSize = ArraySize(allModules) + 1;
            ArrayResize(allModules, newSize);
            ArrayResize(connectionCounts, newSize);
            ArrayResize(totalStrengths, newSize);
            
            allModules[newSize - 1] = m_Links[i].ModuleB;
            connectionCounts[newSize - 1] = 1;
            totalStrengths[newSize - 1] = m_Links[i].Strength;
         }
         else
         {
            connectionCounts[indexB]++;
            totalStrengths[indexB] += m_Links[i].Strength;
         }
      }
      
      // Identificar módulos críticos
      for(int i = 0; i < ArraySize(allModules); i++)
      {
         int connections = connectionCounts[i];
         double avgStrength = totalStrengths[i] / connections;
         
         if(connections > 3 || avgStrength > 0.8) // Thresholds configuráveis
         {
            int newSize = ArraySize(criticalModules) + 1;
            ArrayResize(criticalModules, newSize);
            criticalModules[newSize - 1] = allModules[i] + " (Conexões: " + 
                                          IntegerToString(connections) + ", Força média: " + 
                                          DoubleToString(avgStrength, 2) + ")";
         }
      }
      
      AuditLog("Módulos críticos detectados: " + IntegerToString(ArraySize(criticalModules)), LOG_LEVEL_INFO);
   }

   // Verificar integridade do mapa
   bool ValidateMapIntegrity()
   {
      AuditLog("[QuantumEntanglementMap] Validando integridade do mapa...", LOG_LEVEL_INFO);
      
      int validLinks = 0;
      int invalidLinks = 0;
      
      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         if(m_Links[i].ModuleA == "" || m_Links[i].ModuleB == "" || 
            m_Links[i].Justification == "" || m_Links[i].Strength < 0.0 || m_Links[i].Strength > 1.0)
         {
            LogError("Link inválido detectado: " + m_Links[i].ModuleA + " <-> " + m_Links[i].ModuleB);
            invalidLinks++;
         }
         else
         {
            validLinks++;
         }
      }
      
      bool isValid = (invalidLinks == 0);
      AuditLog("Validação concluída - Válidos: " + IntegerToString(validLinks) + 
               ", Inválidos: " + IntegerToString(invalidLinks), LOG_LEVEL_INFO);
      
      return isValid;
   }

   // Obter estatísticas completas
   void GetMapStatistics(int &totalLinks, int &uniqueModules, double &avgStrength, string &strongestLink)
   {
      totalLinks = ArraySize(m_Links);
      uniqueModules = m_Modules.Total();
      
      double totalStrength = 0.0;
      double maxStrength = 0.0;
      strongestLink = "";
      
      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         totalStrength += m_Links[i].Strength;
         
         if(m_Links[i].Strength > maxStrength)
         {
            maxStrength = m_Links[i].Strength;
            strongestLink = m_Links[i].ModuleA + " <-> " + m_Links[i].ModuleB + 
                           " (" + DoubleToString(m_Links[i].Strength, 2) + ")";
         }
      }
      
      avgStrength = (totalLinks > 0) ? totalStrength / totalLinks : 0.0;
      
      AuditLog("Estatísticas do mapa - Links: " + IntegerToString(totalLinks) + 
               ", Módulos únicos: " + IntegerToString(uniqueModules) + 
               ", Força média: " + DoubleToString(avgStrength, 3) + 
               ", Mais forte: " + strongestLink, LOG_LEVEL_INFO);
   }

   // Carregar mapa de arquivo
   bool LoadFromFile(const string &fileName)
   {
      AuditLog("Carregando mapa de arquivo: " + fileName, LOG_LEVEL_INFO);
      
      if(!FileIsExist(fileName))
      {
         LogWarning("Arquivo de mapa não encontrado: " + fileName);
         return false;
      }

      int handle = FileOpen(fileName, FILE_READ | FILE_TXT | FILE_ANSI);
      if(handle == INVALID_HANDLE)
      {
         LogError("Erro ao abrir arquivo de mapa: " + fileName);
         return false;
      }

      ArrayResize(m_Links, 0);
      m_Modules.Clear();

      while(!FileIsEnding(handle))
      {
         string line = FileReadString(handle);
         if(StringLen(line) > 0)
         {
            string parts[];
            StringSplit(line, ',', parts);
            if(ArraySize(parts) >= 4)
            {
               string modA = parts[0];
               string modB = parts[1];
               double strength = StringToDouble(parts[2]);
               string justification = parts[3];
               
               CreateLink(modA, modB, strength, justification);
               RegisterModule(modA);
               RegisterModule(modB);
            }
         }
      }
      
      FileClose(handle);
      AuditLog("Mapa carregado com sucesso - " + IntegerToString(ArraySize(m_Links)) + " links", LOG_LEVEL_INFO);
      return true;
   }

   // Salvar mapa em arquivo
   bool SaveToFile(const string &fileName)
   {
      AuditLog("Salvando mapa em arquivo: " + fileName, LOG_LEVEL_INFO);
      
      int handle = FileOpen(fileName, FILE_WRITE | FILE_TXT | FILE_ANSI);
      if(handle == INVALID_HANDLE)
      {
         LogError("Erro ao criar arquivo de mapa: " + fileName);
         return false;
      }

      for(int i = 0; i < ArraySize(m_Links); i++)
      {
         string line = m_Links[i].ModuleA + "," + m_Links[i].ModuleB + "," + 
                      DoubleToString(m_Links[i].Strength, 3) + "," + m_Links[i].Justification;
         FileWrite(handle, line);
      }
      
      FileClose(handle);
      AuditLog("Mapa salvo com sucesso - " + IntegerToString(ArraySize(m_Links)) + " links", LOG_LEVEL_INFO);
      return true;
   }

   // Destrutor para limpeza
   ~QuantumEntanglementMap()
   {
      ArrayResize(m_Links, 0);
      m_Modules.Clear();
   }
};

#endif // QUANTUM_ENTANGLEMENT_MAP_MQH 