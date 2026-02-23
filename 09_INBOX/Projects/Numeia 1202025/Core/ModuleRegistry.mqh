//+------------------------------------------------------------------+
//|                                             ModuleRegistry.mqh   |
//|               Sistema Central de Registro de Módulos - EA Numeia |
//| Função: Mapeamento automático de dependências e integrações      |
//+------------------------------------------------------------------+
#ifndef __MODULE_REGISTRY_MQH__
#define __MODULE_REGISTRY_MQH__

#include "../Utils/Log.mqh"
#include <Arrays\ArrayObj.mqh>
#include <Arrays\ArrayString.mqh>

//+------------------------------------------------------------------+
//| Estruturas de Dados                                              |
//+------------------------------------------------------------------+
struct ModuleInfo {
   string moduleName;           // Nome do módulo
   string filePath;             // Caminho do arquivo
   string moduleType;           // Tipo (Core, Agent, Analysis, etc.)
   datetime lastModified;       // Última modificação
   bool isActive;               // Status ativo/inativo
   string version;              // Versão do módulo
   string description;          // Descrição funcional
};

struct DependencyInfo {
   string sourceModule;         // Módulo que depende
   string targetModule;         // Módulo dependido
   string dependencyType;       // Tipo de dependência (include, class, function)
   bool isCritical;             // Dependência crítica
   string interface;            // Interface utilizada
};

struct IntegrationInfo {
   string moduleA;              // Primeiro módulo
   string moduleB;              // Segundo módulo
   string integrationType;      // Tipo de integração
   string dataFlow;             // Fluxo de dados
   bool bidirectional;          // Integração bidirecional
};

//+------------------------------------------------------------------+
//| Classe: ModuleRegistry                                           |
//+------------------------------------------------------------------+
class ModuleRegistry {
private:
   CArrayObj* m_modules;        // Lista de módulos
   CArrayObj* m_dependencies;   // Lista de dependências
   CArrayObj* m_integrations;   // Lista de integrações
   CArrayString* m_fileWatcher; // Monitor de arquivos
   bool m_autoSync;             // Sincronização automática
   datetime m_lastScan;         // Última verificação

public:
   ModuleRegistry() {
      m_modules = new CArrayObj();
      m_dependencies = new CArrayObj();
      m_integrations = new CArrayObj();
      m_fileWatcher = new CArrayString();
      m_autoSync = true;
      m_lastScan = 0;
   }

   ~ModuleRegistry() {
      delete m_modules;
      delete m_dependencies;
      delete m_integrations;
      delete m_fileWatcher;
   }

   //+------------------------------------------------------------------+
   //| Registro de Módulos                                              |
   //+------------------------------------------------------------------+
   bool RegisterModule(string moduleName, string filePath, string moduleType, string description = "") {
      AuditLog("[ModuleRegistry] Registrando módulo: " + moduleName);
      
      // Verificar se já existe
      if(FindModule(moduleName) != -1) {
         LogWarning("[ModuleRegistry] Módulo já registrado: " + moduleName);
         return false;
      }

      ModuleInfo* info = new ModuleInfo();
      info.moduleName = moduleName;
      info.filePath = filePath;
      info.moduleType = moduleType;
      info.lastModified = TimeCurrent();
      info.isActive = true;
      info.version = "1.0";
      info.description = description;

      m_modules.Add(info);
      
      AuditLog("[ModuleRegistry] Módulo registrado com sucesso: " + moduleName);
      return true;
   }

   //+------------------------------------------------------------------+
   //| Registro de Dependências                                         |
   //+------------------------------------------------------------------+
   bool RegisterDependency(string sourceModule, string targetModule, string dependencyType, bool isCritical = false) {
      AuditLog("[ModuleRegistry] Registrando dependência: " + sourceModule + " -> " + targetModule);
      
      DependencyInfo* dep = new DependencyInfo();
      dep.sourceModule = sourceModule;
      dep.targetModule = targetModule;
      dep.dependencyType = dependencyType;
      dep.isCritical = isCritical;
      dep.interface = "";

      m_dependencies.Add(dep);
      
      AuditLog("[ModuleRegistry] Dependência registrada: " + sourceModule + " -> " + targetModule);
      return true;
   }

   //+------------------------------------------------------------------+
   //| Registro de Integrações                                          |
   //+------------------------------------------------------------------+
   bool RegisterIntegration(string moduleA, string moduleB, string integrationType, string dataFlow = "", bool bidirectional = false) {
      AuditLog("[ModuleRegistry] Registrando integração: " + moduleA + " <-> " + moduleB);
      
      IntegrationInfo* integration = new IntegrationInfo();
      integration.moduleA = moduleA;
      integration.moduleB = moduleB;
      integration.integrationType = integrationType;
      integration.dataFlow = dataFlow;
      integration.bidirectional = bidirectional;

      m_integrations.Add(integration);
      
      AuditLog("[ModuleRegistry] Integração registrada: " + moduleA + " <-> " + moduleB);
      return true;
   }

   //+------------------------------------------------------------------+
   //| Verificação de Integridade                                       |
   //+------------------------------------------------------------------+
   bool ValidateIntegrity() {
      AuditLog("[ModuleRegistry] Iniciando validação de integridade...");
      
      int errors = 0;
      int warnings = 0;

      // Verificar dependências quebradas
      for(int i = 0; i < m_dependencies.Total(); i++) {
         DependencyInfo* dep = m_dependencies.At(i);
         if(FindModule(dep.targetModule) == -1) {
            LogError("[ModuleRegistry] DEPENDÊNCIA QUEBRADA: " + dep.sourceModule + " -> " + dep.targetModule);
            errors++;
         }
      }

      // Verificar módulos órfãos
      for(int i = 0; i < m_modules.Total(); i++) {
         ModuleInfo* module = m_modules.At(i);
         if(!HasDependencies(module.moduleName) && !HasIntegrations(module.moduleName)) {
            LogWarning("[ModuleRegistry] MÓDULO ÓRFÃO: " + module.moduleName);
            warnings++;
         }
      }

      // Verificar dependências circulares
      if(HasCircularDependencies()) {
         LogError("[ModuleRegistry] DEPENDÊNCIAS CIRCULARES DETECTADAS!");
         errors++;
      }

      AuditLog("[ModuleRegistry] Validação concluída - Erros: " + IntegerToString(errors) + ", Avisos: " + IntegerToString(warnings));
      return errors == 0;
   }

   //+------------------------------------------------------------------+
   //| Análise de Impacto                                               |
   //+------------------------------------------------------------------+
   void AnalyzeImpact(string moduleName) {
      AuditLog("[ModuleRegistry] Analisando impacto de mudanças em: " + moduleName);
      
      CArrayString* affectedModules = new CArrayString();
      CArrayString* criticalDependencies = new CArrayString();
      
      // Encontrar módulos afetados
      for(int i = 0; i < m_dependencies.Total(); i++) {
         DependencyInfo* dep = m_dependencies.At(i);
         if(dep.targetModule == moduleName) {
            affectedModules.Add(dep.sourceModule);
            if(dep.isCritical) {
               criticalDependencies.Add(dep.sourceModule);
            }
         }
      }

      // Relatório de impacto
      AuditLog("[ModuleRegistry] === RELATÓRIO DE IMPACTO ===");
      AuditLog("[ModuleRegistry] Módulo analisado: " + moduleName);
      AuditLog("[ModuleRegistry] Módulos afetados: " + IntegerToString(affectedModules.Total()));
      AuditLog("[ModuleRegistry] Dependências críticas: " + IntegerToString(criticalDependencies.Total()));

      for(int i = 0; i < affectedModules.Total(); i++) {
         string affected = affectedModules.At(i);
         bool isCritical = false;
         for(int j = 0; j < criticalDependencies.Total(); j++) {
            if(criticalDependencies.At(j) == affected) {
               isCritical = true;
               break;
            }
         }
         
         if(isCritical) {
            LogError("[ModuleRegistry] IMPACTO CRÍTICO: " + affected);
         } else {
            LogWarning("[ModuleRegistry] IMPACTO: " + affected);
         }
      }

      delete affectedModules;
      delete criticalDependencies;
   }

   //+------------------------------------------------------------------+
   //| Geração de Relatórios                                            |
   //+------------------------------------------------------------------+
   void GenerateDependencyReport() {
      AuditLog("[ModuleRegistry] === RELATÓRIO DE DEPENDÊNCIAS ===");
      
      // Estatísticas gerais
      AuditLog("[ModuleRegistry] Total de módulos: " + IntegerToString(m_modules.Total()));
      AuditLog("[ModuleRegistry] Total de dependências: " + IntegerToString(m_dependencies.Total()));
      AuditLog("[ModuleRegistry] Total de integrações: " + IntegerToString(m_integrations.Total()));

      // Módulos por tipo
      int coreModules = 0, agentModules = 0, analysisModules = 0, executionModules = 0;
      
      for(int i = 0; i < m_modules.Total(); i++) {
         ModuleInfo* module = m_modules.At(i);
         if(module.moduleType == "Core") coreModules++;
         else if(module.moduleType == "Agent") agentModules++;
         else if(module.moduleType == "Analysis") analysisModules++;
         else if(module.moduleType == "Execution") executionModules++;
      }

      AuditLog("[ModuleRegistry] Módulos Core: " + IntegerToString(coreModules));
      AuditLog("[ModuleRegistry] Módulos Agent: " + IntegerToString(agentModules));
      AuditLog("[ModuleRegistry] Módulos Analysis: " + IntegerToString(analysisModules));
      AuditLog("[ModuleRegistry] Módulos Execution: " + IntegerToString(executionModules));

      // Dependências críticas
      AuditLog("[ModuleRegistry] === DEPENDÊNCIAS CRÍTICAS ===");
      for(int i = 0; i < m_dependencies.Total(); i++) {
         DependencyInfo* dep = m_dependencies.At(i);
         if(dep.isCritical) {
            AuditLog("[ModuleRegistry] CRÍTICA: " + dep.sourceModule + " -> " + dep.targetModule);
         }
      }
   }

   //+------------------------------------------------------------------+
   //| Sincronização Automática                                         |
   //+------------------------------------------------------------------+
   void AutoSync() {
      if(!m_autoSync) return;
      
      datetime currentTime = TimeCurrent();
      if(currentTime - m_lastScan < 60) return; // Verificar a cada minuto
      
      AuditLog("[ModuleRegistry] Executando sincronização automática...");
      
      // Verificar mudanças nos arquivos
      for(int i = 0; i < m_modules.Total(); i++) {
         ModuleInfo* module = m_modules.At(i);
         datetime fileTime = GetFileModificationTime(module.filePath);
         
         if(fileTime > module.lastModified) {
            AuditLog("[ModuleRegistry] Mudança detectada em: " + module.moduleName);
            module.lastModified = fileTime;
            AnalyzeImpact(module.moduleName);
         }
      }
      
      m_lastScan = currentTime;
      ValidateIntegrity();
   }

   //+------------------------------------------------------------------+
   //| Funções Auxiliares                                               |
   //+------------------------------------------------------------------+
private:
   int FindModule(string moduleName) {
      for(int i = 0; i < m_modules.Total(); i++) {
         ModuleInfo* module = m_modules.At(i);
         if(module.moduleName == moduleName) return i;
      }
      return -1;
   }

   bool HasDependencies(string moduleName) {
      for(int i = 0; i < m_dependencies.Total(); i++) {
         DependencyInfo* dep = m_dependencies.At(i);
         if(dep.sourceModule == moduleName || dep.targetModule == moduleName) return true;
      }
      return false;
   }

   bool HasIntegrations(string moduleName) {
      for(int i = 0; i < m_integrations.Total(); i++) {
         IntegrationInfo* integration = m_integrations.At(i);
         if(integration.moduleA == moduleName || integration.moduleB == moduleName) return true;
      }
      return false;
   }

   bool HasCircularDependencies() {
      // Implementação simplificada - verificar dependências circulares básicas
      for(int i = 0; i < m_dependencies.Total(); i++) {
         DependencyInfo* dep1 = m_dependencies.At(i);
         for(int j = 0; j < m_dependencies.Total(); j++) {
            DependencyInfo* dep2 = m_dependencies.At(j);
            if(dep1.sourceModule == dep2.targetModule && dep1.targetModule == dep2.sourceModule) {
               return true;
            }
         }
      }
      return false;
   }

   datetime GetFileModificationTime(string filePath) {
      // Em MQL5, não há função direta para isso
      // Retornar tempo atual como aproximação
      return TimeCurrent();
   }
};

//+------------------------------------------------------------------+
//| Instância Global do Registry                                       |
//+------------------------------------------------------------------+
ModuleRegistry* g_moduleRegistry = NULL;

//+------------------------------------------------------------------+
//| Funções Globais de Acesso                                          |
//+------------------------------------------------------------------+
void InitializeModuleRegistry() {
   if(g_moduleRegistry == NULL) {
      g_moduleRegistry = new ModuleRegistry();
      AuditLog("[ModuleRegistry] Sistema de registro inicializado");
   }
}

ModuleRegistry* GetModuleRegistry() {
   if(g_moduleRegistry == NULL) {
      InitializeModuleRegistry();
   }
   return g_moduleRegistry;
}

void CleanupModuleRegistry() {
   if(g_moduleRegistry != NULL) {
      delete g_moduleRegistry;
      g_moduleRegistry = NULL;
      AuditLog("[ModuleRegistry] Sistema de registro encerrado");
   }
}

#endif // __MODULE_REGISTRY_MQH__ 