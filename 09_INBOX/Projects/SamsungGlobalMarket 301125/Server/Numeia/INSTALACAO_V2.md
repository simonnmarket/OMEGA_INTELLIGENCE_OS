# GUIA DE INSTALAÇÃO - NUMEIA V2.0

**Data:** 21 de Novembro de 2025  
**Status:** ✅ Pronto para Instalação

---

## 📋 Pré-requisitos

### Python
- **Versão:** Python 3.7+
- **Verificar:** `python --version`

### MetaTrader 5
- **Terminal:** MetaTrader 5 Terminal instalado
- **Status:** Terminal aberto e logado na conta demo

---

## 🔧 Instalação de Dependências

### Opção 1: Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv_numeia

# Ativar ambiente virtual
# Windows PowerShell:
venv_numeia\Scripts\activate
# Windows CMD:
venv_numeia\Scripts\activate.bat
# Linux/macOS:
source venv_numeia/bin/activate

# Instalar dependências
pip install MetaTrader5 pydantic prometheus_client requests numpy pandas
```

### Opção 2: Instalação Direta

```bash
pip install MetaTrader5 pydantic prometheus_client requests numpy pandas
```

### Verificar Instalação

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\verificar_dependencias_v2.py
```

---

## ⚙️ Configuração

### 1. Verificar config.json

**Arquivo:** `config.json` (raiz do projeto)

**Estrutura mínima necessária:**
```json
{
  "EMERGENCY_MODE_ENABLED": false,
  "MAX_PARALLEL_WORKERS": 10,
  "EXECUTION_CYCLE_SECONDS": 15,
  "MAX_LATENCY_MS_P95": 300,
  "MAX_FAILURE_RATE": 0.03,
  "ROLLBACK_WINDOW_SECONDS": 600,
  "NOTIFICATION_WEBHOOK_URL": null,
  "TRADING_SYMBOLS": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"],
  "RISK_PARAMETERS": {
    "max_position_size_pct": 0.02,
    "kelly_fraction": 0.25,
    "max_drawdown_pct": 0.10,
    "max_daily_loss_pct": 0.05
  },
  "MONITORING": {
    "prometheus_port": 8000,
    "health_check_interval": 30,
    "order_timeout_seconds": 10
  }
}
```

### 2. Verificar MT5 Terminal

- ✅ Terminal MT5 **aberto**
- ✅ Conta demo **logada**
- ✅ Símbolos disponíveis no Market Watch

---

## 🚀 Execução

### Passo 1: Parar Sistema Anterior (Se Rodando)

```powershell
# Parar qualquer processo Python anterior
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Passo 2: Executar Numeia V2.0

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\numeia_executor_v2.py
```

### Passo 3: Verificar Execução

- ✅ Verificar logs no console
- ✅ Verificar arquivo `numeia_execution.jsonl`
- ✅ Verificar métricas Prometheus (se modo paralelo ativado): `http://localhost:8000/metrics`

---

## 📊 Comportamento Esperado

### Modo Serial (EMERGENCY_MODE_ENABLED: false)

**O que acontece:**
1. Sistema carrega configuração
2. Valida configuração com Pydantic
3. Log: `{"event":"serial_mode_activated"}`
4. Sistema **retorna imediatamente** (não executa)

**Nota:** Modo serial ainda não implementado neste arquivo. Sistema foca em modo paralelo.

### Modo Paralelo (EMERGENCY_MODE_ENABLED: true)

**O que acontece:**
1. Sistema carrega configuração
2. Inicia servidor Prometheus (porta 8000)
3. Inicializa connection pool com health checks
4. Gera sinais para símbolos em TRADING_SYMBOLS
5. Executa ordens em paralelo
6. Monitora latência e taxa de falha
7. Aciona rollback se necessário

---

## 🔍 Verificação de Logs

### Logs JSON (numeia_execution.jsonl)

```powershell
# Ver últimos logs
Get-Content numeia_execution.jsonl -Tail 20

# Monitorar logs em tempo real
Get-Content numeia_execution.jsonl -Wait -Tail 10
```

### Métricas Prometheus

**URL:** `http://localhost:8000/metrics` (apenas se modo paralelo ativado)

**Verificar no navegador ou:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/metrics
```

---

## ⚠️ Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pydantic'"

**Solução:**
```bash
pip install pydantic
```

### Erro: "Configuration file not found: config.json"

**Solução:**
- Verificar que está executando do diretório raiz do projeto
- Verificar que `config.json` existe

### Erro: "MT5 initialize failed"

**Solução:**
- Verificar que MetaTrader 5 Terminal está aberto
- Verificar que está logado na conta demo
- Tentar reiniciar terminal MT5

### Erro: "ValidationError" ao carregar config.json

**Solução:**
- Verificar estrutura do `config.json`
- Verificar que todos os campos obrigatórios estão presentes
- Validar tipos de dados (listas, dicionários, etc.)

---

## ✅ Checklist de Instalação

- [ ] Python 3.7+ instalado
- [ ] Ambiente virtual criado (opcional mas recomendado)
- [ ] Dependências instaladas (MetaTrader5, pydantic, prometheus_client, etc.)
- [ ] Dependências verificadas (`verificar_dependencias_v2.py`)
- [ ] `config.json` atualizado com estrutura completa
- [ ] MT5 Terminal aberto e logado
- [ ] Sistema anterior parado (se rodando)
- [ ] Pronto para executar `numeia_executor_v2.py`

---

**Última Atualização:** 21 de Novembro de 2025, 03:00 UTC  
**Status:** ✅ Pronto para Instalação e Execução

