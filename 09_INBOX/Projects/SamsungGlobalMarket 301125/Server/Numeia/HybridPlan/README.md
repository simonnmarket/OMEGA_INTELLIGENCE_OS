# Projeto Numeia - Plano Híbrido ΩΔ

**Versão:** 2025-11-20 23:50 UTC  
**Autor:** CEO-Cientista-Chefe  
**Status:** ✅ Implementação Completa

---

## 📋 Descrição

Sistema de execução híbrido que alterna entre modo **paralelo** (emergência) e **serial** (padrão) baseado em configuração e monitoramento automático de latência/falha.

---

## 🏗️ Arquitetura Modular

```
Server/Numeia/HybridPlan/
├── __init__.py                  # Módulo principal
├── connection_pool.py           # MT5ConnectionPool (Singleton)
├── capital_manager.py           # CapitalManager (Gestão de Risco)
├── monitoring.py                # ExecutionMonitor (Monitoramento)
├── parallel_executor.py         # ParallelExecutor (Modo Paralelo)
├── serial_executor.py           # SerialExecutor (Modo Serial)
├── execution_controller.py      # ExecutionController (Controlador)
├── numeia_hybrid_executor.py    # Main Executor
└── README.md                    # Este arquivo
```

---

## 🔧 Componentes

### 1. MT5ConnectionPool
- **Função:** Singleton pool de conexões MT5
- **Thread-safe:** Sim (locks + queue)
- **Métodos:** `acquire()`, `release()`, `shutdown()`

### 2. CapitalManager
- **Função:** Gestão adaptativa de risco em portfólio
- **Features:**
  - Cálculo de tamanho de posição baseado em risco
  - Verificação de margem disponível
  - Monitoramento de exposição total
  - Limites de risco por trade e portfólio

### 3. ExecutionMonitor
- **Função:** Monitoramento de latência e taxa de falha
- **Features:**
  - Detecção de latência alta contínua (>500ms)
  - Detecção de taxa de falha alta (>5%)
  - Rollback automático para modo serial
  - Recuperação automática após cooldown

### 4. ParallelExecutor
- **Função:** Execução paralela de ordens
- **Features:**
  - ThreadPoolExecutor com connection pool
  - Queue thread-safe para tarefas
  - Monitoramento de latência por ordem
  - Logging JSON estruturado

### 5. SerialExecutor
- **Função:** Execução serial de ordens
- **Features:**
  - Usa TradingExecutor existente
  - Execução sequencial uma por vez
  - Integração com monitoramento

### 6. ExecutionController
- **Função:** Controlador principal
- **Features:**
  - Escolhe entre modo paralelo/serial
  - Integra com CircuitBreaker existente
  - Gerencia componentes

---

## ⚙️ Configuração (config.json)

```json
{
  "EXECUTION_CYCLE_SECONDS": 300,
  "EMERGENCY_MODE_ENABLED": false,
  "MAX_PARALLEL_WORKERS": 10,
  "LATENCY_THRESHOLD_MS": 500,
  "FAILURE_RATE_THRESHOLD": 0.05,
  "ROLLBACK_ENABLED": true,
  "MONITORING_WINDOW_SECONDS": 300,
  "FAILURE_WINDOW_SECONDS": 600
}
```

### Variáveis

- **EXECUTION_CYCLE_SECONDS:** Tempo entre execuções (segundos)
- **EMERGENCY_MODE_ENABLED:** Ativa execução paralela (bool)
- **MAX_PARALLEL_WORKERS:** Máximo de threads paralelas
- **LATENCY_THRESHOLD_MS:** Threshold de latência para rollback (ms)
- **FAILURE_RATE_THRESHOLD:** Taxa de falha para rollback (0.05 = 5%)
- **ROLLBACK_ENABLED:** Habilita rollback automático (bool)
- **MONITORING_WINDOW_SECONDS:** Janela de monitoramento de latência (s)
- **FAILURE_WINDOW_SECONDS:** Janela de monitoramento de falha (s)

---

## 🚀 Uso

### Execução Básica

```bash
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\HybridPlan\numeia_hybrid_executor.py
```

### Modo Serial (Padrão)

```json
{
  "EMERGENCY_MODE_ENABLED": false
}
```

- Executa ordens sequencialmente
- Usa TradingExecutor existente
- Mais seguro e estável

### Modo Paralelo (Emergência)

```json
{
  "EMERGENCY_MODE_ENABLED": true,
  "MAX_PARALLEL_WORKERS": 10
}
```

- Executa múltiplas ordens em paralelo
- Usa connection pool e ThreadPoolExecutor
- Rollback automático se problemas detectados

---

## 📊 Monitoramento

### Logs Estruturados (JSON)

Todos os logs incluem:
- `timestamp`: ISO 8601
- `order_id`: ID único da ordem
- `latency_ms`: Latência em milissegundos
- `symbol`: Símbolo negociado
- `volume`: Volume negociado
- `status`: SUCCESS/FAILED/QUEUED
- `mode`: parallel/serial

### Status do Sistema

```python
controller = ExecutionController(config)
status = controller.get_status()
```

Retorna:
- `current_mode`: Modo atual (parallel/serial)
- `monitor`: Estatísticas de monitoramento
- `portfolio`: Status do portfólio
- `rollback_triggered`: Se rollback foi acionado

---

## 🔄 Rollback Automático

O sistema aciona rollback automático se:

1. **Latência Alta Contínua:**
   - Média > threshold (500ms)
   - Taxa de latência alta > 50%
   - Por 5 minutos consecutivos

2. **Taxa de Falha Alta:**
   - Taxa de falha > threshold (5%)
   - Por 10 minutos consecutivos

Após rollback:
- Sistema reverte para modo serial
- Aguarda período de cooldown (1 hora)
- Verifica recuperação antes de retentar paralelo

---

## 🛡️ Integração com Sistema Existente

O Plano Híbrido integra com:
- **CircuitBreaker:** Valida sinais antes de executar
- **SignalGenerator:** Gera sinais de trading
- **TradingExecutor:** Usado no modo serial
- **SystemConfig:** Configurações compartilhadas

---

## 📈 Próximos Passos

### Extensões Recomendadas

1. **ML para Ajuste Dinâmico:**
   - Ajuste automático de SL, TP, volume
   - Baseado em performance histórica

2. **Observabilidade:**
   - OpenTelemetry + Prometheus + Grafana
   - Dashboards em tempo real

3. **Deploy Containerizado:**
   - Kubernetes + Docker
   - Infra IaC via Terraform
   - CI/CD automatizado

4. **Backtest Robusto:**
   - Monte Carlo
   - Simulações estocásticas

5. **NLP para Inteligência de Mercado:**
   - Análise de sentimentos
   - Notícias e eventos

---

## ✅ Status da Implementação

- ✅ Estrutura modular criada
- ✅ MT5ConnectionPool implementado
- ✅ CapitalManager implementado
- ✅ ExecutionMonitor implementado
- ✅ ParallelExecutor implementado
- ✅ SerialExecutor implementado
- ✅ ExecutionController implementado
- ✅ Main executor implementado
- ✅ Config.json atualizado
- ✅ Integração com sistema existente

---

**Última Atualização:** 20 de Novembro de 2025, 23:50 UTC  
**Versão:** 1.0.0

