# AURORA v6.0 MVP - TIER-0 INTEGRATED

> Sistema de Trading com Machine Learning e Compliance Institucional

## 🎯 Visão Geral

Sistema integrado que combina:
- **TIER-0 Core**: Orchestrator, Health, Auth, Circuit Breakers
- **v6.0 MVP**: Strategies, Learning, Specialized Agents
- **Compliance**: NIST SP 800-53, ISO 27001, SEC 15c3-5, MiFID II

## 📊 Status da Integração

✅ **FASE A CONCLUÍDA** - Sistema totalmente integrado  
- Data: 2026-01-11  
- Tempo: ~40 minutos  
- Backup: `BACKUP_PRE_INTEGRATION_20260111_223657`

## 🏗️ Arquitetura Integrada

```
AURORA_v6.0_MVP/
├── system_core/              # TIER-0 Orchestrator + Circuit Breakers
├── connectors/               # TIER-0 MT5 Connector
├── risk/                     # TIER-0 Risk Engine FSM
├── execution/                # TIER-0 Execution Engine
├── auth/                     # TIER-0 Authentication (JWT + API Keys)
├── health/                   # TIER-0 Health Monitor (5 levels)
├── utils/                    # TIER-0 Vault + Redlock
├── api/                      # TIER-0 REST API
├── strategies/               # Trading Strategies
├── learning/                 # ML & Learning Engine
│   ├── experience_buffer.py
│   ├── learning_engine.py
│   ├── strategy_loader.py
│   └── specialized_agents/   # PRÓXIMA FASE B
├── ml_models/                # ML Models
├── config/                   # Unified Configuration
├── data/                     # Data & Models
├── tests/                    # TIER-0 Tests (34+)
├── app.py                    # FastAPI Application
└── main.py                   # Entry Point
```

## 🚀 Quick Start

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar Servidor
```bash
python main.py
```

### 3. Acessar API
- **Base URL**: http://localhost:8081
- **Docs**: http://localhost:8081/docs
- **Health**: http://localhost:8081/health

## 📡 API Endpoints

### Core
- `GET /` - System info
- `GET /health` - Comprehensive health
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /metrics` - Prometheus metrics

### Trading
- `POST /api/v1/trade` - Execute trade
- `GET /api/v1/trade/{id}/status` - Trade status
- `GET /api/v1/risk/status` - Risk engine status
- `GET /api/v1/circuit-breakers` - CB status
- `GET /api/v1/account` - MT5 account info

## 🔒 Segurança TIER-0

- ✅ JWT + API Key authentication
- ✅ Rate limiting (100/IP, 1000/key)
- ✅ HashiCorp Vault integration
- ✅ Distributed locking (Redlock)
- ✅ Circuit breakers hierárquicos
- ✅ Audit trail completo
- ✅ Input validation (Pydantic)

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov

# Testes específicos
pytest tests/health/ -v
pytest tests/risk/ -v
pytest tests/integration/ -v
```

## 📈 Health Levels

1. **CRITICAL** - Sistema inoperante
2. **DEGRADED** - Funcionalidade limitada
3. **STABLE** - Operação normal
4. **OPTIMAL** - Performance máxima
5. **RESILIENT** - Tolerante a falhas

## 🔄 Componentes Integrados

### Novos (TIER-0)
- `utils/` - Vault client, Redlock manager
- `health/` - Health monitoring 5-level
- `auth/` - Authentication middleware
- `api/` - REST API endpoints
- `system_core/async_orchestrator.py`
- `connectors/mt5_connector_tier0.py`
- `risk/finite_state_risk_tier0.py`
- `execution/safe_execution_tier0.py`

### Mantidos (v6.0 MVP)
- `strategies/` - Trading strategies
- `learning/` - ML & learning engine
- `ml_models/` - ML models
- `data/` - Data storage

### Próximos (FASE B)
- `learning/specialized_agents/` - Agent framework

## 🎯 Próxima Fase: FASE B

Implementação dos **Specialized Agents**:
- Agent Base Framework
- XAUUSD Agent
- EURUSD Agent
- Agent Orchestrator
- Agent Genome & Evolution

## 📋 Changelog

### v6.0.0-TIER0 (2026-01-11)
- ✅ Integração completa TIER-0
- ✅ Sistema unificado
- ✅ Compliance institucional
- ✅ 34+ testes implementados
- ✅ Servidor FastAPI ativo

---

**Versão**: 6.0.0-TIER0  
**Status**: ✅ OPERACIONAL  
**Compliance**: NIST, ISO 27001, SEC, MiFID II

