#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para tarefa
struct Task {
    string id;              // Identificador único
    string description;     // Descrição da tarefa
    int priority;          // Prioridade (1-5)
    double urgency;        // Urgência (0-1)
    double importance;     // Importância (0-1)
    datetime deadline;     // Prazo limite
    bool isCompleted;      // Status de conclusão
};

// Classe de Priorização de Tarefas
class CTaskPrioritization {
private:
    // Estado
    bool m_isInitialized;
    Task m_tasks[];
    
    // Métodos privados
    double CalculatePriorityScore(const Task& task) {
        // Fórmula de priorização: (Urgência * 0.6 + Importância * 0.4) * (1 - Tempo Restante)
        double timeRemaining = (double)(task.deadline - TimeCurrent()) / (24 * 60 * 60);
        double timeFactor = MathMax(0, 1 - timeRemaining);
        
        return (task.urgency * 0.6 + task.importance * 0.4) * timeFactor;
    }
    
    void SortTasks() {
        int size = ArraySize(m_tasks);
        for(int i = 0; i < size - 1; i++) {
            for(int j = 0; j < size - i - 1; j++) {
                double score1 = CalculatePriorityScore(m_tasks[j]);
                double score2 = CalculatePriorityScore(m_tasks[j + 1]);
                
                if(score1 < score2) {
                    Task temp = m_tasks[j];
                    m_tasks[j] = m_tasks[j + 1];
                    m_tasks[j + 1] = temp;
                }
            }
        }
    }
    
public:
    // Construtor
    CTaskPrioritization() {
        m_isInitialized = false;
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar tarefa
    bool AddTask(const string& id,
                 const string& description,
                 const double& urgency,
                 const double& importance,
                 const datetime& deadline) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_tasks);
        ArrayResize(m_tasks, size + 1);
        
        m_tasks[size].id = id;
        m_tasks[size].description = description;
        m_tasks[size].urgency = MathMin(1.0, MathMax(0.0, urgency));
        m_tasks[size].importance = MathMin(1.0, MathMax(0.0, importance));
        m_tasks[size].deadline = deadline;
        m_tasks[size].isCompleted = false;
        
        // Calcular prioridade baseada em urgência e importância
        m_tasks[size].priority = (int)((urgency * 0.6 + importance * 0.4) * 5) + 1;
        
        // Ordenar tarefas
        SortTasks();
        
        return true;
    }
    
    // Marcar tarefa como concluída
    bool CompleteTask(const string& id) {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < ArraySize(m_tasks); i++) {
            if(m_tasks[i].id == id) {
                m_tasks[i].isCompleted = true;
                return true;
            }
        }
        
        return false;
    }
    
    // Obter próxima tarefa pendente
    bool GetNextTask(Task& task) {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < ArraySize(m_tasks); i++) {
            if(!m_tasks[i].isCompleted) {
                task = m_tasks[i];
                return true;
            }
        }
        
        return false;
    }
    
    // Obter todas as tarefas pendentes
    void GetPendingTasks(Task& tasks[]) {
        ArrayFree(tasks);
        
        for(int i = 0; i < ArraySize(m_tasks); i++) {
            if(!m_tasks[i].isCompleted) {
                int size = ArraySize(tasks);
                ArrayResize(tasks, size + 1);
                tasks[size] = m_tasks[i];
            }
        }
    }
    
    // Obter todas as tarefas
    void GetAllTasks(Task& tasks[]) {
        ArrayFree(tasks);
        ArrayCopy(tasks, m_tasks);
    }
    
    // Verificar se há tarefas pendentes
    bool HasPendingTasks() const {
        if(!m_isInitialized) return false;
        
        for(int i = 0; i < ArraySize(m_tasks); i++) {
            if(!m_tasks[i].isCompleted) {
                return true;
            }
        }
        
        return false;
    }
    
    // Limpar tarefas concluídas
    void ClearCompletedTasks() {
        Task temp[];
        ArrayResize(temp, 0);
        
        for(int i = 0; i < ArraySize(m_tasks); i++) {
            if(!m_tasks[i].isCompleted) {
                int size = ArraySize(temp);
                ArrayResize(temp, size + 1);
                temp[size] = m_tasks[i];
            }
        }
        
        ArrayCopy(m_tasks, temp);
    }
    
    // Métodos de acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
}; 