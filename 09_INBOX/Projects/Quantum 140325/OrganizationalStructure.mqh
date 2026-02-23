#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Departamentos
enum Department {
    DEPT_RESEARCH,     // Research
    DEPT_DEVELOPMENT,  // Development
    DEPT_DATA,         // Data
    DEPT_QUANTUM       // Quantum
};

// Estrutura para membro da equipe
struct TeamMember {
    string name;           // Nome
    string role;           // Função
    string department;     // Departamento
    string leader;         // Líder
    string[] skills;       // Habilidades
    datetime joinDate;     // Data de entrada
};

// Classe para estrutura organizacional
class COrganizationalStructure {
private:
    // Estado
    bool m_isInitialized;
    TeamMember m_members[];
    int m_memberCount;
    
    // Métodos privados
    void InitializeResearchTeam() {
        // Dr. Ana Silva - Líder
        TeamMember leader;
        leader.name = "Dr. Ana Silva";
        leader.role = "Líder";
        leader.department = "Research";
        leader.leader = "";
        leader.joinDate = D'2024.01.01';
        ArrayResize(leader.skills, 2);
        leader.skills[0] = "Quantum Analysis";
        leader.skills[1] = "Data Science";
        AddMember(leader);
        
        // Membros da equipe
        string[] roles = {"Quantum Analyst", "Data Scientist"};
        for(int i = 0; i < 2; i++) {
            TeamMember member;
            member.name = "Membro " + IntegerToString(i + 1);
            member.role = roles[i];
            member.department = "Research";
            member.leader = leader.name;
            member.joinDate = D'2024.01.01';
            ArrayResize(member.skills, 1);
            member.skills[0] = roles[i];
            AddMember(member);
        }
    }
    
    void InitializeDevelopmentTeam() {
        // Carlos Mendes - Líder
        TeamMember leader;
        leader.name = "Carlos Mendes";
        leader.role = "Líder";
        leader.department = "Development";
        leader.leader = "";
        leader.joinDate = D'2024.01.01';
        ArrayResize(leader.skills, 2);
        leader.skills[0] = "Algorithm Engineering";
        leader.skills[1] = "ML Development";
        AddMember(leader);
        
        // Membros da equipe
        string[] roles = {"Algorithm Engineer", "ML Specialist"};
        for(int i = 0; i < 2; i++) {
            TeamMember member;
            member.name = "Membro " + IntegerToString(i + 1);
            member.role = roles[i];
            member.department = "Development";
            member.leader = leader.name;
            member.joinDate = D'2024.01.01';
            ArrayResize(member.skills, 1);
            member.skills[0] = roles[i];
            AddMember(member);
        }
    }
    
    void InitializeDataTeam() {
        // Beatriz Rocha - Líder
        TeamMember leader;
        leader.name = "Beatriz Rocha";
        leader.role = "Líder";
        leader.department = "Data";
        leader.leader = "";
        leader.joinDate = D'2024.01.01';
        ArrayResize(leader.skills, 2);
        leader.skills[0] = "Data Engineering";
        leader.skills[1] = "Quality Analysis";
        AddMember(leader);
        
        // Membros da equipe
        string[] roles = {"Data Engineer", "Quality Analyst"};
        for(int i = 0; i < 2; i++) {
            TeamMember member;
            member.name = "Membro " + IntegerToString(i + 1);
            member.role = roles[i];
            member.department = "Data";
            member.leader = leader.name;
            member.joinDate = D'2024.01.01';
            ArrayResize(member.skills, 1);
            member.skills[0] = roles[i];
            AddMember(member);
        }
    }
    
    void InitializeQuantumTeam() {
        // Dr. Pedro Albuquerque - Líder
        TeamMember leader;
        leader.name = "Dr. Pedro Albuquerque";
        leader.role = "Líder";
        leader.department = "Quantum";
        leader.leader = "";
        leader.joinDate = D'2024.01.01';
        ArrayResize(leader.skills, 2);
        leader.skills[0] = "Quantum Programming";
        leader.skills[1] = "Physics";
        AddMember(leader);
        
        // Membros da equipe
        string[] roles = {"Quantum Programmer", "Physics Specialist"};
        for(int i = 0; i < 2; i++) {
            TeamMember member;
            member.name = "Membro " + IntegerToString(i + 1);
            member.role = roles[i];
            member.department = "Quantum";
            member.leader = leader.name;
            member.joinDate = D'2024.01.01';
            ArrayResize(member.skills, 1);
            member.skills[0] = roles[i];
            AddMember(member);
        }
    }
    
public:
    // Construtor
    COrganizationalStructure() {
        m_isInitialized = false;
        m_memberCount = 0;
    }
    
    // Destrutor
    ~COrganizationalStructure() {
        ArrayFree(m_members);
    }
    
    // Inicialização
    bool Initialize() {
        if(m_isInitialized) return false;
        
        // Inicializar equipes
        InitializeResearchTeam();
        InitializeDevelopmentTeam();
        InitializeDataTeam();
        InitializeQuantumTeam();
        
        m_isInitialized = true;
        return true;
    }
    
    // Adicionar membro
    bool AddMember(const TeamMember& member) {
        if(!m_isInitialized) return false;
        
        int size = ArraySize(m_members);
        ArrayResize(m_members, size + 1);
        m_members[size] = member;
        m_memberCount++;
        
        return true;
    }
    
    // Remover membro
    bool RemoveMember(int index) {
        if(!m_isInitialized || index < 0 || index >= m_memberCount) return false;
        
        // Remover membro
        for(int i = index; i < m_memberCount - 1; i++) {
            m_members[i] = m_members[i + 1];
        }
        
        // Redimensionar array
        ArrayResize(m_members, m_memberCount - 1);
        m_memberCount--;
        
        return true;
    }
    
    // Obter membros por departamento
    TeamMember* GetMembersByDepartment(const string& department) {
        if(!m_isInitialized) return NULL;
        
        TeamMember* result[];
        int count = 0;
        
        for(int i = 0; i < m_memberCount; i++) {
            if(m_members[i].department == department) {
                ArrayResize(result, count + 1);
                result[count] = m_members[i];
                count++;
            }
        }
        
        return result;
    }
    
    // Obter líder de departamento
    TeamMember GetDepartmentLeader(const string& department) {
        if(!m_isInitialized) {
            TeamMember empty;
            return empty;
        }
        
        for(int i = 0; i < m_memberCount; i++) {
            if(m_members[i].department == department && m_members[i].leader == "") {
                return m_members[i];
            }
        }
        
        TeamMember empty;
        return empty;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    int GetMemberCount() const {
        return m_memberCount;
    }
    
    TeamMember* GetMembers() {
        return m_members;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Organizational Structure Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Member Count: ", m_memberCount);
        
        // Imprimir membros por departamento
        string[] departments = {"Research", "Development", "Data", "Quantum"};
        for(int i = 0; i < 4; i++) {
            TeamMember* members = GetMembersByDepartment(departments[i]);
            Print(departments[i], " Department:");
            Print("Leader: ", GetDepartmentLeader(departments[i]).name);
            Print("Member Count: ", ArraySize(members));
        }
    }
}; 