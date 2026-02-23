# 🛡️ WATCHDOG DO SERVIDOR MT5 - SISTEMA 24/7

**Versão:** 1.0.0  
**Protocolo:** Omega TIER-0  
**Status:** OPERACIONAL

---

## 🎯 FUNCIONALIDADES

### ✅ Monitoramento Contínuo
- Verifica saúde do servidor a cada **10 segundos**
- Health check via conexão socket TCP/IP
- Detecção automática de falhas

### ✅ Auto-Restart Automático
- Reinicia servidor automaticamente em caso de falha
- Delay de 5 segundos entre parada e restart
- Máximo de 5 tentativas consecutivas (evita loop infinito)

### ✅ Preservação de Estado
- Salva estado em `watchdog_state.json`
- Preserva estatísticas de uptime, restarts, health checks
- Não perde progresso em caso de reinicialização

### ✅ Logging Institucional
- Logs em formato ISO 8601
- Arquivo: `logs/watchdog.log`
- Console output para monitoramento em tempo real

---

## 🚀 INSTRUÇÕES DE USO

### **Windows (PowerShell)**

```powershell
# 1. Navegar para o diretório do projeto
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket

# 2. Executar script de inicialização
.\start_watchdog.ps1
```

### **Linux/Mac**

```bash
# 1. Navegar para o diretório do projeto
cd ~/SamsungGlobalMarket

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Executar watchdog
python server_watchdog.py
```

---

## 📊 ESTRUTURA DE ARQUIVOS

```
SamsungGlobalMarket/
├── server_watchdog.py          # Script principal do watchdog
├── start_watchdog.ps1          # Script de inicialização (Windows)
├── simple_mt5_server.py        # Servidor MT5 monitorado
├── watchdog_state.json         # Estado persistido (gerado automaticamente)
└── logs/
    └── watchdog.log            # Logs do sistema
```

---

## 🔧 CONFIGURAÇÕES

O watchdog pode ser configurado editando o dicionário `WATCHDOG_CONFIG` em `server_watchdog.py`:

```python
WATCHDOG_CONFIG = {
    'server_script': 'simple_mt5_server.py',      # Script do servidor
    'host': '127.0.0.1',                          # Host do servidor
    'port': 5555,                                 # Porta do servidor
    'health_check_interval': 10,                  # Intervalo de health check (segundos)
    'restart_delay': 5,                           # Delay antes de reiniciar (segundos)
    'max_restart_attempts': 5,                    # Máximo de restarts consecutivos
    'state_file': 'watchdog_state.json',          # Arquivo de estado
    'logs_dir': 'logs'                            # Diretório de logs
}
```

---

## 📈 MONITORAMENTO

### **Status no Console**

O watchdog imprime status detalhado a cada 60 segundos:

```
======================================================================
[STATUS] Uptime: 3600s | Total: 7200s
[STATUS] Restarts: 1 | Health: 360 OK / 2 FAIL
[STATUS] Taxa de Sucesso: 99.45%
[STATUS] Servidor: RUNNING
======================================================================
```

### **Arquivo de Estado**

`watchdog_state.json` contém:
- `start_time`: Timestamp de início
- `restart_count`: Número de restarts
- `last_restart`: Timestamp do último restart
- `uptime_seconds`: Tempo de atividade atual
- `total_uptime_seconds`: Tempo total de atividade
- `health_checks_passed`: Health checks bem-sucedidos
- `health_checks_failed`: Health checks falhados

### **Logs**

`logs/watchdog.log` contém:
- Todas as operações do watchdog
- Health checks (sucesso/falha)
- Restarts automáticos
- Erros e warnings

---

## 🛡️ PROTEÇÕES IMPLEMENTADAS

### ✅ Evita Loop Infinito
- Limite de 5 restarts consecutivos
- Watchdog para se o limite for atingido
- Requer intervenção manual para reiniciar

### ✅ Shutdown Gracioso
- Ctrl+C para parar graciosamente
- Estado salvo automaticamente
- Servidor parado antes de encerrar

### ✅ Preservação de Estado
- Estado salvo a cada 30 segundos
- Estado carregado na inicialização
- Não perde estatísticas em reinicializações

---

## 🔍 TROUBLESHOOTING

### **Servidor não inicia**

1. Verificar se `simple_mt5_server.py` existe
2. Verificar se ambiente virtual está ativo
3. Verificar logs: `logs/watchdog.log`

### **Limite de restarts atingido**

1. Investigar causa da falha nos logs
2. Corrigir problema no servidor
3. Deletar `watchdog_state.json` (ou editar `restart_count`)
4. Reiniciar watchdog

### **Watchdog não detecta servidor**

1. Verificar se porta 5555 está livre
2. Verificar firewall/antivírus
3. Testar conexão manual: `telnet 127.0.0.1 5555`

---

## 📊 MÉTRICAS DE SUCESSO

O sistema é considerado **operacional** quando:

- ✅ Watchdog monitora sem interrupções
- ✅ Taxa de sucesso de health checks > 95%
- ✅ Restarts automáticos funcionam
- ✅ Estado é preservado entre reinicializações
- ✅ Logs são gerados corretamente

---

## 🚨 NOTAS IMPORTANTES

1. **Nunca execute múltiplos watchdogs simultaneamente**
2. **Sempre pare o watchdog antes de atualizar o servidor**
3. **Monitore os logs regularmente para detectar padrões de falha**
4. **Mantenha backups do `watchdog_state.json`**

---

## 🔄 INTEGRAÇÃO COM SISTEMA EXISTENTE

O watchdog é **100% compatível** com:
- ✅ `simple_mt5_server.py` (servidor atual)
- ✅ `MT5_Connector.py` (conector alternativo)
- ✅ Sistema de logging existente
- ✅ Protocolo Omega TIER-0

---

## 📞 SUPORTE

Em caso de problemas:
1. Verificar logs: `logs/watchdog.log`
2. Verificar estado: `watchdog_state.json`
3. Testar servidor manualmente: `python simple_mt5_server.py`

---

**Assinatura Técnica:**  
Sistema Prometheus v3.0.0 | Protocolo Omega TIER-0  
Timestamp: 2025-10-28T00:30:00Z | Agente_Omega

**Status:** PRODUCTION READY ✅

