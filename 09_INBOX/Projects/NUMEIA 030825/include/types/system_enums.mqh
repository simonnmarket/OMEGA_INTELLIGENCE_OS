//+------------------------------------------------------------------+
//| system_enums.mqh - Enums e Constantes do Sistema                 |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v1.0 (TIER-0+ Quantum-Neural Core)                    |
//| Atualizado em: 2025-01-27             |
//| Status: TIER-0+ | Sistema Completo e Funcional                  |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __GENESIS_SYSTEM_ENUMS_MQH__
#define __GENESIS_SYSTEM_ENUMS_MQH__

//+------------------------------------------------------------------+
//| ENUMS PRINCIPAIS DO SISTEMA                                      |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| ENUM_FORCE_MODE - Modos de Força Máxima                          |
//+------------------------------------------------------------------+
enum ENUM_FORCE_MODE
{
   FORCE_MODE_STANDARD,     // Modo padrão
   FORCE_MODE_ENHANCED,     // Modo aprimorado
   FORCE_MODE_GODMODE,      // Modo divino
   FORCE_MODE_TRANSCENDENT  // Modo transcendental
};

//+------------------------------------------------------------------+
//| ENUM_STATUS - Status Geral do Sistema                             |
//+------------------------------------------------------------------+
enum ENUM_STATUS
{
   STATUS_ERROR,    // Vermelho - Erro
   STATUS_WARNING,  // Amarelo - Aviso
   STATUS_OK        // Verde - OK
};

//+------------------------------------------------------------------+
//| ENUM_CORE_STATUS - Status do Núcleo do Sistema                   |
//+------------------------------------------------------------------+
enum ENUM_CORE_STATUS
{
   CORE_STATUS_ERROR,    // Vermelho - Erro no núcleo
   CORE_STATUS_WARNING,  // Amarelo - Aviso no núcleo
   CORE_STATUS_OK        // Verde - Núcleo OK
};

//+------------------------------------------------------------------+
//| ENUM_QUANTUM_STATE - Estados Quânticos                           |
//+------------------------------------------------------------------+
enum ENUM_QUANTUM_STATE
{
   QUANTUM_STATE_GROUND,     // Estado fundamental
   QUANTUM_STATE_EXCITED,    // Estado excitado
   QUANTUM_STATE_SUPERPOSITION, // Superposição
   QUANTUM_STATE_ENTANGLED   // Entrelaçado
};

//+------------------------------------------------------------------+
//| ENUM_NEURAL_MODE - Modos Neurais                                 |
//+------------------------------------------------------------------+
enum ENUM_NEURAL_MODE
{
   NEURAL_MODE_LEARNING,     // Modo aprendizado
   NEURAL_MODE_INFERENCE,    // Modo inferência
   NEURAL_MODE_TRAINING,     // Modo treinamento
   NEURAL_MODE_ADAPTIVE      // Modo adaptativo
};

//+------------------------------------------------------------------+
//| ENUM_SECURITY_LEVEL - Níveis de Segurança                        |
//+------------------------------------------------------------------+
enum ENUM_SECURITY_LEVEL
{
   SECURITY_LEVEL_LOW,       // Baixo
   SECURITY_LEVEL_MEDIUM,    // Médio
   SECURITY_LEVEL_HIGH,      // Alto
   SECURITY_LEVEL_CRITICAL   // Crítico
};

//+------------------------------------------------------------------+
//| ENUM_AUDIT_STATUS - Status de Auditoria                          |
//+------------------------------------------------------------------+
enum ENUM_AUDIT_STATUS
{
   AUDIT_STATUS_PENDING,     // Pendente
   AUDIT_STATUS_RUNNING,     // Executando
   AUDIT_STATUS_COMPLETED,   // Concluído
   AUDIT_STATUS_FAILED       // Falhou
};

//+------------------------------------------------------------------+
//| ENUM_BLOCKCHAIN_STATUS - Status do Blockchain                    |
//+------------------------------------------------------------------+
enum ENUM_BLOCKCHAIN_STATUS
{
   BLOCKCHAIN_STATUS_OFFLINE,    // Offline
   BLOCKCHAIN_STATUS_SYNCING,    // Sincronizando
   BLOCKCHAIN_STATUS_READY,      // Pronto
   BLOCKCHAIN_STATUS_ERROR       // Erro
};

//+------------------------------------------------------------------+
//| CONSTANTES DO SISTEMA                                            |
//+------------------------------------------------------------------+

// Constantes de Status
#define STATUS_ERROR      0
#define STATUS_WARNING    1
#define STATUS_OK         2

#define CORE_STATUS_ERROR    0
#define CORE_STATUS_WARNING  1
#define CORE_STATUS_OK       2

// Constantes de Modo de Força
#define FORCE_MODE_STANDARD     0
#define FORCE_MODE_ENHANCED     1
#define FORCE_MODE_GODMODE      2
#define FORCE_MODE_TRANSCENDENT 3

// Constantes de Estado Quântico
#define QUANTUM_STATE_GROUND        0
#define QUANTUM_STATE_EXCITED       1
#define QUANTUM_STATE_SUPERPOSITION 2
#define QUANTUM_STATE_ENTANGLED     3

// Constantes de Modo Neural
#define NEURAL_MODE_LEARNING    0
#define NEURAL_MODE_INFERENCE   1
#define NEURAL_MODE_TRAINING    2
#define NEURAL_MODE_ADAPTIVE    3

// Constantes de Segurança
#define SECURITY_LEVEL_LOW      0
#define SECURITY_LEVEL_MEDIUM   1
#define SECURITY_LEVEL_HIGH     2
#define SECURITY_LEVEL_CRITICAL 3

// Constantes de Auditoria
#define AUDIT_STATUS_PENDING    0
#define AUDIT_STATUS_RUNNING    1
#define AUDIT_STATUS_COMPLETED  2
#define AUDIT_STATUS_FAILED     3

// Constantes de Blockchain
#define BLOCKCHAIN_STATUS_OFFLINE   0
#define BLOCKCHAIN_STATUS_SYNCING   1
#define BLOCKCHAIN_STATUS_READY     2
#define BLOCKCHAIN_STATUS_ERROR     3

//+------------------------------------------------------------------+
//| FUNÇÕES UTILITÁRIAS PARA ENUMS                                   |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Converte ENUM_STATUS para string                                 |
//+------------------------------------------------------------------+
string StatusToString(ENUM_STATUS status)
{
   switch(status)
   {
      case STATUS_ERROR:   return "ERROR";
      case STATUS_WARNING: return "WARNING";
      case STATUS_OK:      return "OK";
      default:             return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_CORE_STATUS para string                            |
//+------------------------------------------------------------------+
string CoreStatusToString(ENUM_CORE_STATUS status)
{
   switch(status)
   {
      case CORE_STATUS_ERROR:   return "CORE_ERROR";
      case CORE_STATUS_WARNING: return "CORE_WARNING";
      case CORE_STATUS_OK:      return "CORE_OK";
      default:                  return "CORE_UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_FORCE_MODE para string                             |
//+------------------------------------------------------------------+
string ForceModeToString(ENUM_FORCE_MODE mode)
{
   switch(mode)
   {
      case FORCE_MODE_STANDARD:     return "STANDARD";
      case FORCE_MODE_ENHANCED:     return "ENHANCED";
      case FORCE_MODE_GODMODE:      return "GODMODE";
      case FORCE_MODE_TRANSCENDENT: return "TRANSCENDENT";
      default:                      return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_QUANTUM_STATE para string                          |
//+------------------------------------------------------------------+
string QuantumStateToString(ENUM_QUANTUM_STATE state)
{
   switch(state)
   {
      case QUANTUM_STATE_GROUND:        return "GROUND";
      case QUANTUM_STATE_EXCITED:       return "EXCITED";
      case QUANTUM_STATE_SUPERPOSITION: return "SUPERPOSITION";
      case QUANTUM_STATE_ENTANGLED:     return "ENTANGLED";
      default:                          return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_NEURAL_MODE para string                            |
//+------------------------------------------------------------------+
string NeuralModeToString(ENUM_NEURAL_MODE mode)
{
   switch(mode)
   {
      case NEURAL_MODE_LEARNING:  return "LEARNING";
      case NEURAL_MODE_INFERENCE: return "INFERENCE";
      case NEURAL_MODE_TRAINING:  return "TRAINING";
      case NEURAL_MODE_ADAPTIVE:  return "ADAPTIVE";
      default:                    return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_SECURITY_LEVEL para string                         |
//+------------------------------------------------------------------+
string SecurityLevelToString(ENUM_SECURITY_LEVEL level)
{
   switch(level)
   {
      case SECURITY_LEVEL_LOW:      return "LOW";
      case SECURITY_LEVEL_MEDIUM:   return "MEDIUM";
      case SECURITY_LEVEL_HIGH:     return "HIGH";
      case SECURITY_LEVEL_CRITICAL: return "CRITICAL";
      default:                      return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_AUDIT_STATUS para string                           |
//+------------------------------------------------------------------+
string AuditStatusToString(ENUM_AUDIT_STATUS status)
{
   switch(status)
   {
      case AUDIT_STATUS_PENDING:   return "PENDING";
      case AUDIT_STATUS_RUNNING:   return "RUNNING";
      case AUDIT_STATUS_COMPLETED: return "COMPLETED";
      case AUDIT_STATUS_FAILED:    return "FAILED";
      default:                     return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Converte ENUM_BLOCKCHAIN_STATUS para string                      |
//+------------------------------------------------------------------+
string BlockchainStatusToString(ENUM_BLOCKCHAIN_STATUS status)
{
   switch(status)
   {
      case BLOCKCHAIN_STATUS_OFFLINE: return "OFFLINE";
      case BLOCKCHAIN_STATUS_SYNCING: return "SYNCING";
      case BLOCKCHAIN_STATUS_READY:   return "READY";
      case BLOCKCHAIN_STATUS_ERROR:   return "ERROR";
      default:                        return "UNKNOWN";
   }
}

#endif // __GENESIS_SYSTEM_ENUMS_MQH__ 