#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para tarefa
struct Task {
    string   id;
    string   name;
    string   description;
    datetime startTime;
    datetime endTime;
    int      priority;
    bool     isCompleted;
    string   status;
    string   assignedTo;
    string   dependencies[];
};

// Estrutura para recurso
struct Resource {
    string   id;
    string   name;
    string   type;
    double   capacity;
    double   used;
    bool     isAvailable;
    datetime nextAvailable;
};

// Estrutura para plano
struct Plan {
    string   id;
    string   name;
    datetime created;
    datetime updated;
    Task     tasks[];
    Resource resources[];
};

//+------------------------------------------------------------------+
//| Classe PlannerAgent                                               |
//+------------------------------------------------------------------+
class CPlannerAgent {
private:
    // Componentes principais
    CQuantumCore*   m_core;
    Plan            m_currentPlan;
    Task            m_taskQueue[];
    Resource        m_resources[];
    
    // Estado do agente
    bool            m_isActive;
    datetime        m_lastUpdate;
    int             m_maxTasks;
    int             m_maxResources;
    
    // Métodos privados
    bool            ValidateTask(const Task &task);
    bool            ValidateResource(const Resource &resource);
    bool            CheckDependencies(const Task &task);
    void            UpdateTaskStatus(Task &task);
    void            OptimizeResources();
    void            ReorderTaskQueue();
    string          GenerateUniqueId();
    
public:
                    CPlannerAgent();
                   ~CPlannerAgent();
    
    // Métodos principais
    bool            Initialize(CQuantumCore* core);
    bool            Start();
    void            Stop();
    
    // Métodos de planejamento
    bool            CreatePlan(string name);
    bool            AddTask(const Task &task);
    bool            AddResource(const Resource &resource);
    bool            UpdateTask(const Task &task);
    bool            UpdateResource(const Resource &resource);
    bool            RemoveTask(string id);
    bool            RemoveResource(string id);
    
    // Métodos de execução
    bool            ExecuteNextTask();
    bool            AssignTask(string taskId, string resourceId);
    bool            CompleteTask(string id);
    
    // Métodos de consulta
    Task            GetTask(string id);
    Resource        GetResource(string id);
    Task           *GetPendingTasks();
    Resource       *GetAvailableResources();
    
    // Getters
    bool            IsActive() const { return m_isActive; }
    Plan            GetCurrentPlan() const { return m_currentPlan; }
    int             GetTaskCount() const { return ArraySize(m_taskQueue); }
    int             GetResourceCount() const { return ArraySize(m_resources); }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CPlannerAgent::CPlannerAgent() {
    m_core = NULL;
    m_isActive = false;
    m_lastUpdate = 0;
    m_maxTasks = 100;
    m_maxResources = 50;
    
    ArrayResize(m_taskQueue, 0);
    ArrayResize(m_resources, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CPlannerAgent::~CPlannerAgent() {
    Stop();
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CPlannerAgent::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicia o agente                                                    |
//+------------------------------------------------------------------+
bool CPlannerAgent::Start() {
    if(!m_core) return false;
    
    m_isActive = true;
    m_lastUpdate = TimeCurrent();
    
    // Cria plano inicial
    CreatePlan("Default Plan");
    
    return true;
}

//+------------------------------------------------------------------+
//| Para o agente                                                      |
//+------------------------------------------------------------------+
void CPlannerAgent::Stop() {
    if(!m_isActive) return;
    
    // Completa tarefas pendentes
    for(int i = ArraySize(m_taskQueue) - 1; i >= 0; i--) {
        if(!m_taskQueue[i].isCompleted) {
            m_taskQueue[i].status = "Cancelled";
        }
    }
    
    m_isActive = false;
}

//+------------------------------------------------------------------+
//| Cria plano                                                        |
//+------------------------------------------------------------------+
bool CPlannerAgent::CreatePlan(string name) {
    if(!m_isActive) return false;
    
    m_currentPlan.id = GenerateUniqueId();
    m_currentPlan.name = name;
    m_currentPlan.created = TimeCurrent();
    m_currentPlan.updated = TimeCurrent();
    
    ArrayResize(m_currentPlan.tasks, 0);
    ArrayResize(m_currentPlan.resources, 0);
    
    return true;
}

//+------------------------------------------------------------------+
//| Adiciona tarefa                                                    |
//+------------------------------------------------------------------+
bool CPlannerAgent::AddTask(const Task &task) {
    if(!m_isActive || !ValidateTask(task)) return false;
    
    // Verifica limite de tarefas
    if(ArraySize(m_taskQueue) >= m_maxTasks) {
        Print("Maximum number of tasks reached");
        return false;
    }
    
    // Adiciona tarefa à fila
    int size = ArraySize(m_taskQueue);
    ArrayResize(m_taskQueue, size + 1);
    m_taskQueue[size] = task;
    
    // Adiciona ao plano atual
    size = ArraySize(m_currentPlan.tasks);
    ArrayResize(m_currentPlan.tasks, size + 1);
    m_currentPlan.tasks[size] = task;
    
    // Reordena fila
    ReorderTaskQueue();
    
    m_currentPlan.updated = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Adiciona recurso                                                   |
//+------------------------------------------------------------------+
bool CPlannerAgent::AddResource(const Resource &resource) {
    if(!m_isActive || !ValidateResource(resource)) return false;
    
    // Verifica limite de recursos
    if(ArraySize(m_resources) >= m_maxResources) {
        Print("Maximum number of resources reached");
        return false;
    }
    
    // Adiciona recurso
    int size = ArraySize(m_resources);
    ArrayResize(m_resources, size + 1);
    m_resources[size] = resource;
    
    // Adiciona ao plano atual
    size = ArraySize(m_currentPlan.resources);
    ArrayResize(m_currentPlan.resources, size + 1);
    m_currentPlan.resources[size] = resource;
    
    m_currentPlan.updated = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza tarefa                                                   |
//+------------------------------------------------------------------+
bool CPlannerAgent::UpdateTask(const Task &task) {
    if(!m_isActive || !ValidateTask(task)) return false;
    
    // Atualiza na fila
    for(int i = 0; i < ArraySize(m_taskQueue); i++) {
        if(m_taskQueue[i].id == task.id) {
            m_taskQueue[i] = task;
            break;
        }
    }
    
    // Atualiza no plano
    for(int i = 0; i < ArraySize(m_currentPlan.tasks); i++) {
        if(m_currentPlan.tasks[i].id == task.id) {
            m_currentPlan.tasks[i] = task;
            break;
        }
    }
    
    m_currentPlan.updated = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza recurso                                                  |
//+------------------------------------------------------------------+
bool CPlannerAgent::UpdateResource(const Resource &resource) {
    if(!m_isActive || !ValidateResource(resource)) return false;
    
    // Atualiza na lista
    for(int i = 0; i < ArraySize(m_resources); i++) {
        if(m_resources[i].id == resource.id) {
            m_resources[i] = resource;
            break;
        }
    }
    
    // Atualiza no plano
    for(int i = 0; i < ArraySize(m_currentPlan.resources); i++) {
        if(m_currentPlan.resources[i].id == resource.id) {
            m_currentPlan.resources[i] = resource;
            break;
        }
    }
    
    m_currentPlan.updated = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Remove tarefa                                                      |
//+------------------------------------------------------------------+
bool CPlannerAgent::RemoveTask(string id) {
    if(!m_isActive) return false;
    
    bool found = false;
    
    // Remove da fila
    for(int i = 0; i < ArraySize(m_taskQueue); i++) {
        if(m_taskQueue[i].id == id) {
            for(int j = i; j < ArraySize(m_taskQueue) - 1; j++) {
                m_taskQueue[j] = m_taskQueue[j + 1];
            }
            ArrayResize(m_taskQueue, ArraySize(m_taskQueue) - 1);
            found = true;
            break;
        }
    }
    
    // Remove do plano
    for(int i = 0; i < ArraySize(m_currentPlan.tasks); i++) {
        if(m_currentPlan.tasks[i].id == id) {
            for(int j = i; j < ArraySize(m_currentPlan.tasks) - 1; j++) {
                m_currentPlan.tasks[j] = m_currentPlan.tasks[j + 1];
            }
            ArrayResize(m_currentPlan.tasks, ArraySize(m_currentPlan.tasks) - 1);
            found = true;
            break;
        }
    }
    
    if(found) {
        m_currentPlan.updated = TimeCurrent();
    }
    
    return found;
}

//+------------------------------------------------------------------+
//| Remove recurso                                                     |
//+------------------------------------------------------------------+
bool CPlannerAgent::RemoveResource(string id) {
    if(!m_isActive) return false;
    
    bool found = false;
    
    // Remove da lista
    for(int i = 0; i < ArraySize(m_resources); i++) {
        if(m_resources[i].id == id) {
            for(int j = i; j < ArraySize(m_resources) - 1; j++) {
                m_resources[j] = m_resources[j + 1];
            }
            ArrayResize(m_resources, ArraySize(m_resources) - 1);
            found = true;
            break;
        }
    }
    
    // Remove do plano
    for(int i = 0; i < ArraySize(m_currentPlan.resources); i++) {
        if(m_currentPlan.resources[i].id == id) {
            for(int j = i; j < ArraySize(m_currentPlan.resources) - 1; j++) {
                m_currentPlan.resources[j] = m_currentPlan.resources[j + 1];
            }
            ArrayResize(m_currentPlan.resources, ArraySize(m_currentPlan.resources) - 1);
            found = true;
            break;
        }
    }
    
    if(found) {
        m_currentPlan.updated = TimeCurrent();
    }
    
    return found;
}

//+------------------------------------------------------------------+
//| Executa próxima tarefa                                            |
//+------------------------------------------------------------------+
bool CPlannerAgent::ExecuteNextTask() {
    if(!m_isActive || ArraySize(m_taskQueue) == 0) return false;
    
    // Obtém próxima tarefa
    Task task = m_taskQueue[0];
    
    // Verifica dependências
    if(!CheckDependencies(task)) {
        return false;
    }
    
    // Verifica recursos
    Resource *availableResources = GetAvailableResources();
    if(ArraySize(availableResources) == 0) {
        return false;
    }
    
    // Executa tarefa
    task.status = "Running";
    UpdateTask(task);
    
    return true;
}

//+------------------------------------------------------------------+
//| Atribui tarefa                                                    |
//+------------------------------------------------------------------+
bool CPlannerAgent::AssignTask(string taskId, string resourceId) {
    if(!m_isActive) return false;
    
    Task task = GetTask(taskId);
    Resource resource = GetResource(resourceId);
    
    if(task.id == "" || resource.id == "") return false;
    
    // Verifica disponibilidade do recurso
    if(!resource.isAvailable) return false;
    
    // Atribui tarefa
    task.assignedTo = resourceId;
    task.status = "Assigned";
    
    // Atualiza recurso
    resource.isAvailable = false;
    resource.used += 1;
    
    UpdateTask(task);
    UpdateResource(resource);
    
    return true;
}

//+------------------------------------------------------------------+
//| Completa tarefa                                                    |
//+------------------------------------------------------------------+
bool CPlannerAgent::CompleteTask(string id) {
    if(!m_isActive) return false;
    
    Task task = GetTask(id);
    if(task.id == "") return false;
    
    // Atualiza status
    task.isCompleted = true;
    task.status = "Completed";
    task.endTime = TimeCurrent();
    
    // Libera recurso
    if(task.assignedTo != "") {
        Resource resource = GetResource(task.assignedTo);
        if(resource.id != "") {
            resource.isAvailable = true;
            resource.used -= 1;
            UpdateResource(resource);
        }
    }
    
    UpdateTask(task);
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém tarefa                                                      |
//+------------------------------------------------------------------+
Task CPlannerAgent::GetTask(string id) {
    Task empty;
    ZeroMemory(empty);
    
    for(int i = 0; i < ArraySize(m_taskQueue); i++) {
        if(m_taskQueue[i].id == id) {
            return m_taskQueue[i];
        }
    }
    
    return empty;
}

//+------------------------------------------------------------------+
//| Obtém recurso                                                     |
//+------------------------------------------------------------------+
Resource CPlannerAgent::GetResource(string id) {
    Resource empty;
    ZeroMemory(empty);
    
    for(int i = 0; i < ArraySize(m_resources); i++) {
        if(m_resources[i].id == id) {
            return m_resources[i];
        }
    }
    
    return empty;
}

//+------------------------------------------------------------------+
//| Obtém tarefas pendentes                                           |
//+------------------------------------------------------------------+
Task *CPlannerAgent::GetPendingTasks() {
    static Task pendingTasks[];
    ArrayResize(pendingTasks, 0);
    
    for(int i = 0; i < ArraySize(m_taskQueue); i++) {
        if(!m_taskQueue[i].isCompleted) {
            int size = ArraySize(pendingTasks);
            ArrayResize(pendingTasks, size + 1);
            pendingTasks[size] = m_taskQueue[i];
        }
    }
    
    return pendingTasks;
}

//+------------------------------------------------------------------+
//| Obtém recursos disponíveis                                        |
//+------------------------------------------------------------------+
Resource *CPlannerAgent::GetAvailableResources() {
    static Resource availableResources[];
    ArrayResize(availableResources, 0);
    
    for(int i = 0; i < ArraySize(m_resources); i++) {
        if(m_resources[i].isAvailable) {
            int size = ArraySize(availableResources);
            ArrayResize(availableResources, size + 1);
            availableResources[size] = m_resources[i];
        }
    }
    
    return availableResources;
}

//+------------------------------------------------------------------+
//| Valida tarefa                                                     |
//+------------------------------------------------------------------+
bool CPlannerAgent::ValidateTask(const Task &task) {
    if(task.id == "" || task.name == "") return false;
    if(task.startTime <= 0) return false;
    if(task.priority < 0) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida recurso                                                    |
//+------------------------------------------------------------------+
bool CPlannerAgent::ValidateResource(const Resource &resource) {
    if(resource.id == "" || resource.name == "") return false;
    if(resource.capacity <= 0) return false;
    if(resource.used < 0) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Verifica dependências                                             |
//+------------------------------------------------------------------+
bool CPlannerAgent::CheckDependencies(const Task &task) {
    for(int i = 0; i < ArraySize(task.dependencies); i++) {
        Task dependency = GetTask(task.dependencies[i]);
        if(dependency.id != "" && !dependency.isCompleted) {
            return false;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza status da tarefa                                         |
//+------------------------------------------------------------------+
void CPlannerAgent::UpdateTaskStatus(Task &task) {
    if(task.isCompleted) {
        task.status = "Completed";
    }
    else if(task.assignedTo != "") {
        task.status = "Assigned";
    }
    else if(CheckDependencies(task)) {
        task.status = "Ready";
    }
    else {
        task.status = "Pending";
    }
}

//+------------------------------------------------------------------+
//| Otimiza recursos                                                  |
//+------------------------------------------------------------------+
void CPlannerAgent::OptimizeResources() {
    // Libera recursos não utilizados
    for(int i = 0; i < ArraySize(m_resources); i++) {
        if(!m_resources[i].isAvailable && m_resources[i].used == 0) {
            m_resources[i].isAvailable = true;
            m_resources[i].nextAvailable = TimeCurrent();
        }
    }
    
    // Redistribui recursos
    Task *pendingTasks = GetPendingTasks();
    Resource *availableResources = GetAvailableResources();
    
    for(int i = 0; i < ArraySize(pendingTasks); i++) {
        if(pendingTasks[i].assignedTo == "" && ArraySize(availableResources) > 0) {
            AssignTask(pendingTasks[i].id, availableResources[0].id);
        }
    }
}

//+------------------------------------------------------------------+
//| Reordena fila de tarefas                                         |
//+------------------------------------------------------------------+
void CPlannerAgent::ReorderTaskQueue() {
    // Ordena por prioridade e tempo de início
    for(int i = 0; i < ArraySize(m_taskQueue) - 1; i++) {
        for(int j = i + 1; j < ArraySize(m_taskQueue); j++) {
            if(m_taskQueue[i].priority < m_taskQueue[j].priority ||
               (m_taskQueue[i].priority == m_taskQueue[j].priority &&
                m_taskQueue[i].startTime > m_taskQueue[j].startTime)) {
                Task temp = m_taskQueue[i];
                m_taskQueue[i] = m_taskQueue[j];
                m_taskQueue[j] = temp;
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Gera ID único                                                     |
//+------------------------------------------------------------------+
string CPlannerAgent::GenerateUniqueId() {
    return IntegerToString(GetTickCount()) + "_" + IntegerToString(MathRand());
} 