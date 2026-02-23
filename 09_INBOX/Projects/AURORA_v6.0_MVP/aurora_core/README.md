# AURORA CORE TIER-0

> Sistema de Trading Institucional com Compliance de Nível Financeiro

## 🎯 Visão Geral

AURORA CORE TIER-0 é um sistema de trading automatizado projetado com compliance institucional, seguindo os padrões:

- **NIST SP 800-53** - Controles de segurança
- **ISO 27001** - Segurança da informação
- **SEC 15c3-5** - Controle de risco de acesso ao mercado
- **MiFID II** - Regulamentação de trading algorítmico

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    AURORA CORE TIER-0                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  FastAPI    │  │  Health     │  │  Prometheus         │ │
│  │  :8081      │  │  Monitor    │  │  Metrics            │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │            │
│  ┌──────┴────────────────┴─────────────────────┴──────────┐│
│  │              Async Orchestrator                         ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               ││
│  │  │ MT5 CB   │ │ Risk CB  │ │ Exec CB  │               ││
│  │  └──────────┘ └──────────┘ └──────────┘               ││
│  └────────────────────────────────────────────────────────┘│
│         │                │                     │            │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────────┴─────────┐ │
│  │ MT5         │  │ Risk        │  │ Execution          │ │
│  │ Connector   │  │ Engine      │  │ Engine             │ │
│  └─────────────┘  └─────────────┘  └────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  HashiCorp  │  │  Redis      │  │  Auth               │ │
│  │  Vault      │  │  Cluster    │  │  Middleware         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Requisitos

- Python 3.11+
- Docker & Docker Compose
- Redis (ou Docker)

### Instalação

```bash
# 1. Instalar dependências
cd aurora_core
pip install -r requirements.core.txt

# 2. Copiar template de ambiente
copy .env.core.template .env.core

# 3. Iniciar servidor (modo demo)
python scripts/start_server.py
```

### Com Docker

```bash
# Build e start
docker-compose -f docker-compose.core.yml up -d

# Verificar status
docker-compose -f docker-compose.core.yml ps

# Logs
docker-compose -f docker-compose.core.yml logs -f aurora-core
```

## 📡 API Endpoints

### Health & Status
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Info do sistema |
| `/health` | GET | Health check completo |
| `/health/live` | GET | Liveness probe |
| `/health/ready` | GET | Readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Trading
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/trade` | POST | Executar trade |
| `/api/v1/trade/{id}/status` | GET | Status do trade |
| `/api/v1/risk/status` | GET | Status do risk engine |
| `/api/v1/circuit-breakers` | GET | Status dos circuit breakers |

### Exemplo de Trade

```bash
curl -X POST http://localhost:8081/api/v1/trade \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo_key_aurora_2025" \
  -d '{
    "symbol": "EURUSD",
    "operation": "BUY",
    "volume": 0.01,
    "idempotency_key": "trade_001"
  }'
```

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=src --cov-report=html

# Testes específicos
pytest tests/health/ -v
pytest tests/risk/ -v
```

## 🔒 Segurança

### Features
- ✅ JWT + API Key authentication
- ✅ Rate limiting (100/IP, 1000/key)
- ✅ Distributed locking (Redlock)
- ✅ Circuit breakers
- ✅ Audit trail completo
- ✅ Secrets via HashiCorp Vault

### Health Matrix (5 níveis)
1. **CRITICAL** - Sistema inoperante
2. **DEGRADED** - Funcionalidade limitada
3. **STABLE** - Operação normal
4. **OPTIMAL** - Performance máxima
5. **RESILIENT** - Tolerante a falhas

## 📊 Monitoramento

### Prometheus Metrics
- `aurora_health_level` - Nível de saúde geral
- `aurora_component_health` - Saúde por componente
- `circuit_breaker_state` - Estado dos circuit breakers
- `circuit_breaker_failures` - Contagem de falhas

### Alertas Configurados
- Circuit Breaker Open
- Vault Unavailable
- Redis Cluster Degraded
- High Latency
- Risk Engine Halted

## 📁 Estrutura do Projeto

```
aurora_core/
├── src/
│   ├── api/                 # FastAPI endpoints
│   ├── auth/                # JWT, API keys, rate limiting
│   ├── connectors/          # MT5 connector
│   ├── core/                # Orchestrator, circuit breakers
│   ├── execution/           # Trade execution
│   ├── health/              # Health monitoring
│   ├── risk/                # Risk engine FSM
│   └── utils/               # Vault, Redlock
├── tests/                   # Pytest tests
├── config/                  # Configurations
├── monitoring/              # Prometheus configs
├── scripts/                 # Utility scripts
├── vault/                   # Vault policies
├── docker-compose.core.yml
├── Dockerfile.core
└── requirements.core.txt
```

## 📝 Licença

Proprietário - AURORA Trading System

---

**Versão**: 2.0.0 TIER-0  
**Data**: 2026-01-11  
**Compliance**: NIST, ISO 27001, SEC, MiFID II

