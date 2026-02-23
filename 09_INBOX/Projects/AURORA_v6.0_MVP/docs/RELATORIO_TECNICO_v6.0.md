# AURORA v6.0 MVP - RELATÓRIO TÉCNICO

**Versão Documento:** 2.0  
**Data:** 2026-01-08  
**Última Atualização:** 2026-01-08 22:45 CET  
**Classificação:** PRODUCTION-READY

---

## 1. ESPECIFICAÇÕES DO SISTEMA

| Métrica | Valor |
|---------|-------|
| **Sistema** | AURORA v6.0 MVP |
| **Módulos Python** | 24 |
| **Linhas de Código** | 3,584 |
| **Tamanho Total** | 177 KB |
| **Entry Point** | `main.py` |
| **Python** | 3.11.9 |
| **Plataforma** | Windows 10 x64 |
| **Broker** | Hantec Markets |

---

## 2. ARQUITETURA

```
AURORA_v6.0_MVP/
├── main.py                          [Entry Point]
├── config/
│   ├── settings.py                  Configuração centralizada
│   └── database.py                  Paths de persistência
├── connectors/
│   └── mt5_connector.py             Interface MetaTrader 5
├── execution/
│   ├── order_management.py          Gestão de ordens
│   └── execution_engine.py          Motor de execução
├── risk/
│   ├── risk_engine.py               Validação de risco
│   └── circuit_breakers.py          Proteção de capital
├── strategies/
│   └── alpha_momentum.py            Estratégia principal
├── learning/
│   ├── experience_buffer.py         Buffer SQLite (RL)
│   ├── learning_engine.py           Retreino contínuo
│   ├── strategy_loader.py           Hot reload
│   └── specialized_agents/          Agentes autônomos
│       ├── __init__.py              Exports
│       ├── agent_base.py            Classe base abstrata
│       ├── agent_xauusd.py          Agente Gold
│       ├── agent_eurusd.py          Agente Euro
│       ├── agent_orchestrator.py    Maestro dos agentes
│       └── agent_genome.py          DNA evolutivo
├── ml_models/
│   ├── MetaLearningAdapter.py       Meta-learning
│   ├── PPOExecutionOptimizer.py     PPO optimization
│   └── TemporalFusionTransformer.py TFT forecasting
├── system_core/
│   ├── orchestrator.py              Orquestração
│   ├── message_bus.py               Pub/Sub interno
│   └── registry.py                  Registro de módulos
├── data/
│   ├── experience_buffer/           SQLite trades.db
│   ├── models/                      Modelos .pkl
│   └── agents/                      Dados por agente
├── logs/                            Logs do sistema
└── docs/                            Documentação
```

---

## 3. COMPONENTES PRINCIPAIS

### 3.1 MT5Connector (`connectors/mt5_connector.py`)

Interface com MetaTrader 5.

```python
class MT5Connector:
    connect() -> bool
    disconnect() -> None
    execute_order(symbol, action, volume, sl, tp) -> Dict
    close_position(ticket) -> Dict
    get_positions(symbol?) -> List[Dict]
    get_market_data(symbol, timeframe, count) -> ndarray
    get_tick(symbol) -> Dict
    get_account_info() -> Dict
```

### 3.2 ExecutionEngine (`execution/execution_engine.py`)

Motor de execução com validação de risco.

```python
class ExecutionEngine:
    start() -> None
    stop() -> None
    execute_signal(signal, risk_params) -> Dict
    close_all_positions(symbol?) -> Dict
    get_status() -> Dict
```

**Fluxo:**
1. Receber sinal da estratégia
2. Validar com RiskEngine
3. Calcular position size
4. Executar via MT5Connector
5. Notificar MessageBus

### 3.3 ExperienceBuffer (`learning/experience_buffer.py`)

Buffer de experiências para Reinforcement Learning.

```python
class ExperienceBuffer:
    add(state, action, reward, next_state, metadata) -> int
    sample(batch_size=128) -> List[Tuple]
    get_last_n(n=1000) -> List[Tuple]
    clear_old(days=90) -> int
    count() -> int
    get_stats() -> Dict
```

**Schema SQLite:**
```sql
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    state_features BLOB,
    action TEXT NOT NULL,
    reward FLOAT DEFAULT 0.0,
    next_state_features BLOB,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 LearningEngine (`learning/learning_engine.py`)

Motor de aprendizado contínuo.

```python
class LearningEngine:
    start() -> None      # Background thread
    stop() -> None
    force_retrain() -> None
    get_status() -> Dict
    load_latest_model() -> Dict
```

**Condições de Retreino:**
```python
RETRAIN_CONDITIONS = {
    "new_experiences": 1000,      # Buffer > 1000
    "sharpe_drop": 0.1,           # Sharpe caiu 10%
    "max_drawdown": 0.05,         # DD > 5%
    "hours_since_last": 24        # 24h sem retreino
}
```

### 3.5 StrategyLoader (`learning/strategy_loader.py`)

Carregador dinâmico com hot reload.

```python
class StrategyLoader:
    load_strategy(path, name, config) -> bool
    reload_strategy(name) -> bool    # Hot reload
    unload_strategy(name) -> bool
    list_strategies() -> List[Dict]
    get_active_strategy(symbol) -> Strategy
    generate_signal(symbol, state) -> Dict
```

---

## 4. SPECIALIZED AGENTS

Sistema de agentes autônomos especializados por ativo.

### 4.1 AgentBase (`agent_base.py`)

```python
class AgentBase(ABC):
    def __init__(symbol, data_path, min_sharpe, evolution_interval)
    def activate() -> None
    def deactivate(reason) -> None
    def record_trade(action, price, volume, pnl, confidence) -> None
    def get_experience_sample(n) -> List[Tuple]
    def receive_knowledge(experiences, source_agent) -> None
    @abstractmethod generate_signal(state) -> Dict
    @abstractmethod learn_online(state, action, reward, next_state)
```

**Ciclo de Vida:**
```
Nasce simples → Aprende online → Evolui genoma → Cresce forte
```

### 4.2 XAUUSDAgent (`agent_xauusd.py`)

Agente especializado em Gold.

```python
GENOME = {
    "gold_volatility_factor": 1.5,
    "usd_correlation_weight": 0.3,
    "session_bias": {"asia": 0.8, "london": 1.2, "newyork": 1.0},
    "atr_multiplier": 2.0
}
```

- Modelo: `model_xauusd_vX.pkl`
- Buffer: `xauusd_trades.db`
- Estratégia: Momentum + Mean Reversion

### 4.3 EURUSDAgent (`agent_eurusd.py`)

Agente especializado em Euro.

```python
GENOME = {
    "liquidity_preference": 1.2,
    "mean_reversion_strength": 0.7,
    "news_sensitivity": 0.5,
    "bollinger_periods": 20
}
```

- Modelo: `model_eurusd_vX.pkl`
- Buffer: `eurusd_trades.db`
- Estratégia: Mean Reversion (Bollinger)

### 4.4 AgentOrchestrator (`agent_orchestrator.py`)

Maestro dos agentes.

```python
class AgentOrchestrator:
    register_agent(agent) -> None
    start() -> None              # Background monitoring
    stop() -> None
    get_signal(symbol, state) -> Dict
    report_trade_result(...) -> None
    get_best_agent() -> str
```

**Ciclo de Monitoramento (1 min):**
1. Coletar métricas (Sharpe, PnL, trades)
2. Ajustar alocações: `softmax(Sharpe)`
3. Desativar agentes com Sharpe < 0
4. Transfer learning do melhor para outros

### 4.5 AgentGenome (`agent_genome.py`)

DNA evolutivo.

```python
class AgentGenome:
    mutate(rate=0.1, strength=0.2) -> AgentGenome
    @staticmethod crossover(p1, p2) -> Tuple[AgentGenome, AgentGenome]
    @staticmethod select(population, n, tournament=3) -> List
    update_fitness(sharpe, win_rate, profit_factor) -> None
```

---

## 5. CONFIGURAÇÃO

### 5.1 Settings (`config/settings.py`)

```python
SETTINGS = {
    "mt5": {
        "account": 510065181,
        "server": "HantecMarketsMU-MT5",
        "timeout": 60000
    },
    "risk": {
        "max_risk_per_trade": 0.01,    # 1%
        "max_daily_loss": 0.05,         # 5%
        "max_positions": 3,
        "max_drawdown": 0.15            # 15% kill switch
    },
    "learning": {
        "retrain_frequency_hours": 6,
        "min_experiences": 1000,
        "validation_days": 30
    },
    "strategies": {
        "active": ["alpha_momentum"],
        "symbols": ["XAUUSD"],
        "confidence_threshold": 0.6
    },
    "execution": {
        "paper_trading": True
    }
}
```

### 5.2 Database (`config/database.py`)

```python
DATABASE_CONFIG = {
    "experience_buffer": "data/experience_buffer/trades.db",
    "models_path": "data/models/",
    "agents_path": "data/agents/",
    "logs_path": "logs/"
}
```

---

## 6. FLUXO DE EXECUÇÃO

```
┌─────────────────────────────────────────────────────────────┐
│                      INICIALIZAÇÃO                          │
├─────────────────────────────────────────────────────────────┤
│  1. Load config/settings.py                                │
│  2. Initialize MT5Connector → connect()                    │
│  3. Initialize ExperienceBuffer                            │
│  4. Initialize RiskEngine                                  │
│  5. Initialize ExecutionEngine                             │
│  6. Initialize AgentOrchestrator + Agents                  │
│  7. Load strategies via StrategyLoader                     │
│  8. Start LearningEngine (background)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      MAIN LOOP (5s)                         │
├─────────────────────────────────────────────────────────────┤
│  for symbol in symbols:                                    │
│      ├── MT5Connector.get_tick(symbol)                     │
│      ├── AgentOrchestrator.get_signal(symbol, state)       │
│      ├── if confidence >= threshold:                       │
│      │       RiskEngine.validate_trade()                   │
│      │       ExecutionEngine.execute_signal()              │
│      └── ExperienceBuffer.add()                            │
│                                                             │
│  [Background] LearningEngine monitors & retrains           │
│  [Background] AgentOrchestrator monitors & reallocates     │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. PERSISTÊNCIA

| Componente | Formato | Localização |
|------------|---------|-------------|
| Experience Buffer | SQLite | `data/experience_buffer/trades.db` |
| Modelos Sistema | Pickle | `data/models/model_vX.pkl` |
| Modelos Agentes | Pickle | `data/agents/model_{symbol}_vX.pkl` |
| Buffers Agentes | SQLite | `data/agents/{symbol}_trades.db` |
| Logs | Text | `logs/aurora_v6.log` |

---

## 8. CONEXÃO MT5

```
┌────────────────────────────────────┐
│ HANTEC MARKETS LTD                 │
├────────────────────────────────────┤
│ Account:  510065181                │
│ Server:   HantecMarketsMU-MT5      │
│ Currency: EUR                      │
│ Status:   CONNECTED                │
└────────────────────────────────────┘
```

---

## 9. COMANDOS DE OPERAÇÃO

### Iniciar Sistema
```powershell
cd C:\Users\Lenovo\Projects\AURORA_v6.0_MVP
python main.py
```

### Testar Conexão MT5
```powershell
python -c "from connectors.mt5_connector import MT5Connector; m=MT5Connector(); m.connect(); print(m.get_account_info())"
```

### Testar Agentes
```powershell
python -c "from learning.specialized_agents import AgentOrchestrator; o=AgentOrchestrator(); o.create_default_agents(); print(o.get_status())"
```

### Verificar Experience Buffer
```powershell
python -c "from learning.experience_buffer import ExperienceBuffer; b=ExperienceBuffer(); print(b.get_stats())"
```

---

## 10. RECURSOS DO SISTEMA

| Recurso | Descrição |
|---------|-----------|
| **ExperienceBuffer** | Armazenamento SQLite para RL |
| **LearningEngine** | Retreino automático com validação |
| **StrategyLoader** | Hot reload de estratégias |
| **Specialized Agents** | Agentes autônomos por ativo |
| **AgentOrchestrator** | Coordenação e alocação dinâmica |
| **AgentGenome** | Evolução genética de parâmetros |
| **Transfer Learning** | Compartilhamento de conhecimento |
| **Auto-Shutdown** | Desativação se Sharpe < 0 |

---

## 11. ASSINATURA

```
Sistema:        AURORA v6.0 MVP
Documento:      RELATORIO_TECNICO_v6.0.md
Versão Doc:     2.0
Status:         PRODUCTION-READY
Módulos:        24
LOC:            3,584
Size:           177 KB
MT5:            CONNECTED
Data:           2026-01-08 22:45 CET
```

---

**FIM DO DOCUMENTO**
