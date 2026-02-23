# RELATÓRIO TÉCNICO: STATUS DE COMPONENTES DO SISTEMA
# Análise de Uso e Recomendações de Descontinuação

**Documento Oficial para:** CONSELHO EXECUTIVO & CEO  
**Versão:** 1.0 - Padrão Institucional  
**Data:** 17 de Novembro de 2025 (CET/Berlin)  
**Protocolo:** Prometheus v3.0.0 | TIER-0  
**Status Sistema:** ✅ **FASE 1.5 CONCLUÍDA - ANÁLISE DE COMPONENTES**

---

## 📋 SUMÁRIO EXECUTIVO

Este relatório analisa o status de uso de cada componente do sistema após a implementação do "Transplante de Cérebro Sistêmico" (Fase 1.5). O objetivo é identificar quais componentes estão em uso ativo, quais podem ser descontinuados e quais arquivos do processo antigo podem ser descartados.

**Resultado Principal:** Sistema novo (`prometheus_brain_v1.1.py`) opera independentemente, mas alguns componentes antigos ainda têm valor para gestão de risco e orquestração opcional.

---

## 🔍 ANÁLISE DETALHADA POR COMPONENTE

### 1. DOCKER APP

**Status:** ⚠️ **USO OPCIONAL - PODE SER MANTIDO OU DESCONTINUADO**

**Uso Atual:**
- **Airflow:** Docker Compose em `Orchestration/Airflow/docker/`
- **Serviços:** postgres, redis, airflow-scheduler, airflow-worker, airflow-apiserver
- **DAG Ativa:** `prometheus_mt5_executor` (orquestra sistema antigo)

**Dependência do Novo Sistema:**
- ❌ **NÃO NECESSÁRIO** para `prometheus_brain_v1.1.py`
- ✅ **OPCIONAL** para orquestração futura do novo cérebro

**Recomendação:**
- **Opção A (Recomendada):** **MANTER** para orquestração futura
  - Pode ser usado para orquestrar `prometheus_brain_v1.1.py` em produção
  - Útil para agendamento, retry automático, monitoramento
  - Já configurado e funcionando
  
- **Opção B:** **DESCONTINUAR** se preferir execução direta
  - `prometheus_brain_v1.1.py` pode rodar diretamente no Windows
  - Sem dependências externas
  - Mais simples, mas sem orquestração avançada

**Decisão Técnica:**
```
MANTER Docker/Airflow se:
- Planeja orquestração complexa (múltiplas estratégias)
- Precisa de agendamento flexível
- Quer retry automático e monitoramento avançado

DESCONTINUAR Docker/Airflow se:
- Prefere simplicidade
- Execução direta é suficiente
- Não precisa de orquestração complexa
```

**Arquivos Relacionados:**
- `Orchestration/Airflow/docker/docker-compose.yaml` ✅ Mantido
- `Orchestration/Airflow/Dags/prometheus_mt5_executor_dag.py` ⚠️ Pode ser adaptado para novo cérebro

---

### 2. POWERSHELL

**Status:** ✅ **EM USO ATIVO - MANTER**

**Uso Atual:**
- Scripts de inicialização e manutenção
- Scripts de configuração SSH
- Scripts de monitoramento
- Scripts de validação

**Dependência do Novo Sistema:**
- ✅ **NECESSÁRIO** para scripts de inicialização do novo cérebro
- ✅ **NECESSÁRIO** para scripts de manutenção Windows
- ✅ **NECESSÁRIO** para configuração e troubleshooting

**Scripts Ativos:**
```
Scripts/start_server_outbox.ps1          ⚠️ Sistema antigo (Numeia_v6_0)
Scripts/start_main_server.ps1             ⚠️ Sistema antigo (main_server.py)
Scripts/start_watchdog.ps1                ⚠️ Sistema antigo (watchdog)
Scripts/fix_ssh_final.ps1                 ✅ Útil (configuração SSH)
Scripts/create_ssh_user.ps1              ✅ Útil (configuração SSH)
Scripts/forcar_chave_rsa_limpa.ps1        ✅ Útil (configuração SSH)
```

**Recomendação:**
- ✅ **MANTER** PowerShell
- ✅ **CRIAR** novos scripts para `prometheus_brain_v1.1.py`:
  - `Scripts/start_prometheus_brain.ps1` (novo)
  - `Scripts/stop_prometheus_brain.ps1` (novo)
  - `Scripts/restart_prometheus_brain.ps1` (novo)

**Scripts que Podem ser Descontinuados:**
- `start_server_outbox.ps1` - Sistema antigo (Numeia_v6_0)
- `start_main_server.ps1` - Sistema antigo (main_server.py)
- `start_watchdog.ps1` - Sistema antigo (watchdog)
- `iniciar_servidor_file_based.ps1` - Sistema antigo
- `iniciar_servidor_com_validacao.ps1` - Sistema antigo

---

### 3. GIT BASH

**Status:** ⚠️ **USO OPCIONAL - PODE SER DESCONTINUADO**

**Uso Atual:**
- Scripts bash (`.sh`) para deploy e execução
- Comandos bash para desenvolvimento

**Dependência do Novo Sistema:**
- ❌ **NÃO NECESSÁRIO** para `prometheus_brain_v1.1.py`
- ⚠️ **OPCIONAL** para scripts de deploy (podem ser convertidos para PowerShell)

**Scripts Bash Encontrados:**
```
Scripts/deploy_forex.sh                  ⚠️ Pode ser convertido para PowerShell
Scripts/run_core_orchestrator.sh          ⚠️ Sistema antigo
Scripts/run_core_with_fallback.sh         ⚠️ Sistema antigo
Scripts/prometheus_mt5_cron.sh            ⚠️ Sistema antigo (cron)
```

**Recomendação:**
- ⚠️ **DESCONTINUAR** Git Bash se não for usado
- ✅ **MANTER** apenas se preferir scripts bash
- ✅ **CONVERTER** scripts importantes para PowerShell (padronização Windows)

**Decisão Técnica:**
```
DESCONTINUAR Git Bash se:
- Todos os scripts podem ser convertidos para PowerShell
- Prefere padronização Windows
- Não há necessidade de compatibilidade Linux

MANTER Git Bash se:
- Prefere scripts bash
- Planeja deploy em Linux no futuro
- Já tem scripts bash funcionais
```

---

### 4. UBUNTU (WSL2)

**Status:** ⚠️ **USO OPCIONAL - DEPENDE DO DOCKER/AIRFLOW**

**Uso Atual:**
- Ambiente para Docker/Airflow
- WSL2 necessário para Docker Desktop no Windows

**Dependência do Novo Sistema:**
- ❌ **NÃO NECESSÁRIO** se Docker/Airflow for descontinuado
- ✅ **NECESSÁRIO** se Docker/Airflow for mantido

**Recomendação:**
- **Se Docker/Airflow for MANTIDO:** ✅ **MANTER** Ubuntu/WSL2
- **Se Docker/Airflow for DESCONTINUADO:** ⚠️ **PODE SER DESCONTINUADO**

**Decisão Técnica:**
```
MANTER Ubuntu/WSL2 se:
- Docker/Airflow será mantido
- Planeja desenvolvimento Linux no futuro

DESCONTINUAR Ubuntu/WSL2 se:
- Docker/Airflow será descontinuado
- Todo desenvolvimento será Windows nativo
```

---

### 5. AIRFLOW

**Status:** ⚠️ **USO OPCIONAL - PODE SER MANTIDO OU DESCONTINUADO**

**Uso Atual:**
- **DAG Ativa:** `prometheus_mt5_executor`
  - Orquestra `prometheus_mt5_executor.py` (sistema antigo)
  - Schedule: `*/5 * * * *` (a cada 5 minutos)
  - Executa via SSH no Windows host

**Dependência do Novo Sistema:**
- ❌ **NÃO NECESSÁRIO** para `prometheus_brain_v1.1.py` (roda diretamente)
- ✅ **OPCIONAL** para orquestração futura do novo cérebro

**Recomendação:**
- **Opção A (Recomendada):** **MANTER** e adaptar DAG para novo cérebro
  ```python
  # Nova DAG proposta: prometheus_brain_dag.py
  run_brain = SSHOperator(
      task_id="run_prometheus_brain",
      ssh_conn_id="prometheus_executor_host",
      command="python C:/Users/Lenovo/.cursor/SamsungGlobalMarket/Server/prometheus_brain_v1.1.py",
      cmd_timeout=10 * 60,
  )
  ```
  
- **Opção B:** **DESCONTINUAR** se preferir execução direta
  - `prometheus_brain_v1.1.py` roda como serviço Windows
  - Sem dependências externas
  - Mais simples

**Decisão Técnica:**
```
MANTER Airflow se:
- Precisa de orquestração complexa
- Quer agendamento flexível
- Precisa de retry automático
- Quer monitoramento centralizado

DESCONTINUAR Airflow se:
- Execução direta é suficiente
- Prefere simplicidade
- Não precisa de orquestração
```

**Arquivos Relacionados:**
- `Orchestration/Airflow/Dags/prometheus_mt5_executor_dag.py` ⚠️ Adaptar ou descontinuar
- `Orchestration/Airflow/docker/docker-compose.yaml` ⚠️ Manter se Airflow for mantido

---

### 6. OUTROS ARQUIVOS DO PROCESSO ANTIGO

#### 6.1 Arquivos de Servidor Antigo (PODEM SER DESCONTINUADOS)

**Localização:** `Server/`

**Arquivos Identificados:**
```
Server/Numeia_v6_0_Tactical_Server.py     ❌ Sistema antigo (Numeia)
Server/main_server.py                     ❌ Sistema antigo (Big Tech)
Server/trading_engine.py                  ❌ Sistema antigo (Big Tech)
Server/mt5_socket_service.py              ❌ Sistema antigo (Socket)
```

**Status:** ❌ **DESCONTINUADOS** - Substituídos por `prometheus_brain_v1.1.py`

**Recomendação:**
- ⚠️ **ARQUIVAR** (mover para `Server/archive/`) ao invés de deletar
- ✅ **MANTER** por 30 dias para referência
- ✅ **DELETAR** após validação completa do novo sistema

---

#### 6.2 Executor de Risco (MANTER - AINDA ÚTIL)

**Arquivo:** `Server/prometheus_mt5_executor.py`

**Status:** ✅ **MANTER - AINDA EM USO**

**Motivo:**
- Gerencia SL/TP de posições abertas pelo novo cérebro
- Kill-switch institucional
- Métricas Prometheus de risco
- **COMPLEMENTA** o novo cérebro (não substitui)

**Uso Futuro:**
```python
# Novo cérebro abre posições
prometheus_brain_v1.1.py → Abre trades

# Executor de risco gerencia posições abertas
prometheus_mt5_executor.py → Ajusta SL/TP, monitora kill-switch
```

**Recomendação:**
- ✅ **MANTER** e rodar em paralelo com novo cérebro
- ✅ **INTEGRAR** magic numbers para reconhecer posições do novo cérebro

---

#### 6.3 Scripts PowerShell Antigos (PODEM SER DESCONTINUADOS)

**Scripts Identificados:**
```
Scripts/start_server_outbox.ps1           ❌ Sistema antigo (Numeia_v6_0)
Scripts/start_main_server.ps1             ❌ Sistema antigo (main_server.py)
Scripts/start_watchdog.ps1                ❌ Sistema antigo (watchdog)
Scripts/iniciar_servidor_file_based.ps1   ❌ Sistema antigo
Scripts/iniciar_servidor_com_validacao.ps1 ❌ Sistema antigo
Scripts/executar_protocolo_completo.ps1   ❌ Sistema antigo
```

**Status:** ❌ **DESCONTINUADOS** - Substituídos por novo sistema

**Recomendação:**
- ⚠️ **ARQUIVAR** (mover para `Scripts/archive/`)
- ✅ **MANTER** por 30 dias para referência
- ✅ **DELETAR** após validação completa

---

#### 6.4 Scripts Bash Antigos (PODEM SER DESCONTINUADOS)

**Scripts Identificados:**
```
Scripts/deploy_forex.sh                   ⚠️ Pode ser convertido ou descontinuado
Scripts/run_core_orchestrator.sh          ❌ Sistema antigo
Scripts/run_core_with_fallback.sh         ❌ Sistema antigo
Scripts/prometheus_mt5_cron.sh            ❌ Sistema antigo (cron)
```

**Status:** ❌ **DESCONTINUADOS** - Substituídos por novo sistema

**Recomendação:**
- ⚠️ **ARQUIVAR** (mover para `Scripts/archive/`)
- ✅ **MANTER** por 30 dias para referência
- ✅ **DELETAR** após validação completa

---

#### 6.5 Expert Advisor MQL5 (DESCONTINUAR)

**Arquivo:** `SamsungGlobalMarket_EA.mq5` (se existir)

**Status:** ❌ **DESCONTINUAR** conforme diretiva

**Motivo:**
- Substituído por `prometheus_brain_v1.1.py`
- Decisões agora em Python (auditável)
- Execução agora em Python (controlável)

**Recomendação:**
- ✅ **DESATIVAR** imediatamente no MT5 Terminal
- ⚠️ **ARQUIVAR** código MQL5 (não deletar, pode ser referência)
- ✅ **REMOVER** do MT5 Terminal

---

## 📊 TABELA RESUMO - STATUS DE COMPONENTES

| Componente | Status Atual | Uso no Novo Sistema | Recomendação | Ação Imediata |
|------------|-------------|---------------------|--------------|---------------|
| **Docker App** | ⚠️ Opcional | Não necessário | Manter ou descontinuar | Decisão estratégica |
| **PowerShell** | ✅ Ativo | Necessário | **MANTER** | Criar novos scripts |
| **Git Bash** | ⚠️ Opcional | Não necessário | Descontinuar | Converter scripts importantes |
| **Ubuntu/WSL2** | ⚠️ Opcional | Depende do Docker | Manter se Docker mantido | Decisão estratégica |
| **Airflow** | ⚠️ Opcional | Não necessário | Manter ou descontinuar | Adaptar DAG ou descontinuar |
| **prometheus_mt5_executor.py** | ✅ Ativo | **COMPLEMENTA** novo sistema | **MANTER** | Integrar magic numbers |
| **prometheus_brain_v1.1.py** | ✅ Ativo | **NOVO CÉREBRO** | **MANTER** | Sistema principal |

---

## 🎯 RECOMENDAÇÕES ESTRATÉGICAS

### Cenário A: Manter Orquestração (Recomendado para Produção)

**Componentes Mantidos:**
- ✅ Docker App
- ✅ Ubuntu/WSL2
- ✅ Airflow (adaptar DAG para novo cérebro)
- ✅ PowerShell
- ✅ `prometheus_mt5_executor.py` (gestão de risco)

**Vantagens:**
- Orquestração avançada
- Retry automático
- Monitoramento centralizado
- Agendamento flexível

**Desvantagens:**
- Maior complexidade
- Mais recursos (Docker, WSL2)
- Mais pontos de falha

---

### Cenário B: Execução Direta (Recomendado para Simplicidade)

**Componentes Mantidos:**
- ✅ PowerShell
- ✅ `prometheus_mt5_executor.py` (gestão de risco)
- ❌ Docker App (descontinuar)
- ❌ Ubuntu/WSL2 (descontinuar)
- ❌ Airflow (descontinuar)
- ❌ Git Bash (descontinuar)

**Vantagens:**
- Simplicidade máxima
- Menos recursos
- Menos pontos de falha
- Execução direta

**Desvantagens:**
- Sem orquestração avançada
- Sem retry automático
- Monitoramento manual

---

## 📋 PLANO DE AÇÃO RECOMENDADO

### Fase 1: Decisão Estratégica (Imediato)

1. **Decidir:** Manter ou descontinuar Docker/Airflow
2. **Decidir:** Manter ou descontinuar Git Bash
3. **Decidir:** Manter ou descontinuar Ubuntu/WSL2

### Fase 2: Limpeza de Arquivos Antigos (Após Decisão)

1. **Arquivar** servidores antigos:
   ```
   Server/archive/
   ├── Numeia_v6_0_Tactical_Server.py
   ├── main_server.py
   ├── trading_engine.py
   └── mt5_socket_service.py
   ```

2. **Arquivar** scripts antigos:
   ```
   Scripts/archive/
   ├── start_server_outbox.ps1
   ├── start_main_server.ps1
   ├── start_watchdog.ps1
   └── ...
   ```

3. **Criar** novos scripts para novo sistema:
   ```
   Scripts/
   ├── start_prometheus_brain.ps1 (NOVO)
   ├── stop_prometheus_brain.ps1 (NOVO)
   └── restart_prometheus_brain.ps1 (NOVO)
   ```

### Fase 3: Integração (Se Airflow Mantido)

1. **Adaptar** DAG para novo cérebro:
   ```
   Orchestration/Airflow/Dags/prometheus_brain_dag.py (NOVO)
   ```

2. **Descontinuar** DAG antiga:
   ```
   Orchestration/Airflow/Dags/prometheus_mt5_executor_dag.py (ARQUIVAR)
   ```

---

## ✅ CHECKLIST DE DECISÃO

### Componentes Críticos (Manter)
- [x] **PowerShell** - Necessário para scripts Windows
- [x] **prometheus_brain_v1.1.py** - Novo cérebro (sistema principal)
- [x] **prometheus_mt5_executor.py** - Gestão de risco (complementa)

### Componentes Opcionais (Decisão Estratégica)
- [ ] **Docker App** - Manter ou descontinuar?
- [ ] **Airflow** - Manter ou descontinuar?
- [ ] **Ubuntu/WSL2** - Manter ou descontinuar?
- [ ] **Git Bash** - Manter ou descontinuar?

### Arquivos Antigos (Arquivar/Deletar)
- [ ] **Servidores antigos** - Arquivar em `Server/archive/`
- [ ] **Scripts antigos** - Arquivar em `Scripts/archive/`
- [ ] **EA MQL5** - Desativar no MT5 Terminal

---

## 📝 CONCLUSÃO

**Componentes Essenciais (Manter):**
1. ✅ **PowerShell** - Necessário
2. ✅ **prometheus_brain_v1.1.py** - Sistema principal
3. ✅ **prometheus_mt5_executor.py** - Gestão de risco

**Componentes Opcionais (Decisão Estratégica):**
1. ⚠️ **Docker/Airflow** - Manter se precisar de orquestração
2. ⚠️ **Ubuntu/WSL2** - Manter se Docker for mantido
3. ⚠️ **Git Bash** - Descontinuar (padronizar PowerShell)

**Arquivos Antigos:**
- ⚠️ **Arquivar** servidores e scripts antigos
- ⚠️ **Desativar** EA MQL5 no MT5 Terminal

**Próximo Passo:** Decisão estratégica sobre orquestração (Cenário A ou B).

---

**Assinatura:**  
Sistema Prometheus v3.0 | Análise de Componentes | TIER-0  
Data: 17 de Novembro de 2025 (CET/Berlin)

