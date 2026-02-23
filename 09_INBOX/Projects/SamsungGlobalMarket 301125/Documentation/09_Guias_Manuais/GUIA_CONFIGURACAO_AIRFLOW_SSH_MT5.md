# Guia de Configuração: Airflow SSH + Executor MT5

**Data:** 2025-11-13 (CET/Berlin)  
**Status:** Operacional  
**Próximo Passo:** Configurar conexão SSH no Airflow UI

---

## 📋 Pré-requisitos Verificados

- ✅ OpenSSH Server instalado e rodando (`sshd` service Running)
- ✅ Firewall configurado (porta 22/TCP aberta)
- ✅ Script `Server/prometheus_mt5_executor.py` existente
- ✅ Airflow rodando via Docker Compose

---

## 🔧 Configuração no Airflow UI

### 1. Criar Conexão SSH (`prometheus_executor_host`)

1. Acesse o Airflow UI: `http://localhost:8080`
2. Login: `airflow` / `airflow` (padrão)
3. Vá em **Admin → Connections**
4. Clique em **+** (adicionar nova conexão)
5. Preencha:

   **Connection Id:** `prometheus_executor_host`  
   **Connection Type:** `SSH`  
   **Host:** `host.docker.internal` (para Docker Desktop) ou IP do Windows host (ex: `192.168.x.x`)  
   **Schema/Port:** `22`  
   **Login:** `<SEU_USUARIO_WINDOWS>` (ex: `Lenovo`)  
   **Password:** `<SUA_SENHA_WINDOWS>` (ou use chave SSH)  
   **Extra:** (opcional) `{"key_file": "/path/to/private_key"}` (se usar chave SSH)

6. Clique em **Save**

---

### 2. Criar Conexão HTTP (`prometheus_localhost`)

1. Em **Admin → Connections**, clique em **+**
2. Preencha:

   **Connection Id:** `prometheus_localhost`  
   **Connection Type:** `HTTP`  
   **Host:** `host.docker.internal` (ou IP do Windows host)  
   **Schema/Port:** `63000`  
   **Login:** (vazio)  
   **Password:** (vazio)

3. Clique em **Save**

---

### 3. Definir Variável de Ambiente no Worker Airflow

No terminal WSL/Linux onde o Airflow está rodando:

```bash
cd /mnt/c/Users/Lenovo/.cursor/SamsungGlobalMarket/Orchestration/Airflow/docker

# Adicione ao arquivo .env (ou crie se não existir)
echo "PROMETHEUS_MT5_EXECUTOR_COMMAND=python \"C:/Users/Lenovo/.cursor/SamsungGlobalMarket/Server/prometheus_mt5_executor.py\"" >> .env

# Reinicie os containers para aplicar
docker compose -f docker-compose.yaml down
docker compose -f docker-compose.yaml up -d
```

**Nota:** Ajuste o caminho do script conforme sua instalação real.

---

### 4. Verificar Caminho do Script no Windows

No PowerShell (Windows):

```powershell
Test-Path "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\prometheus_mt5_executor.py"
```

Se retornar `True`, o caminho está correto.  
Se retornar `False`, ajuste o caminho no `.env` acima.

---

## ✅ Teste Manual (Antes da DAG)

### Teste SSH do Docker para Windows

No terminal WSL onde o Airflow está rodando:

```bash
# Teste conexão SSH a partir do container
docker compose -f docker-compose.yaml exec airflow-worker ssh -o StrictHostKeyChecking=no SEU_USUARIO@host.docker.internal "echo 'SSH funcionando!'"
```

**Ou via PowerShell (Windows):**

```powershell
# Teste conexão SSH local
ssh SEU_USUARIO@127.0.0.1 "echo 'SSH funcionando!'"
```

### Teste Execução do Script

No PowerShell (Windows):

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\prometheus_mt5_executor.py
```

**Aguardar:** Deve iniciar o servidor de métricas na porta `63000` e ficar rodando.  
**Verificar:** `http://localhost:63000/metrics` deve retornar métricas Prometheus.

---

## 🚀 Ativar DAG no Airflow

1. Acesse o Airflow UI: `http://localhost:8080`
2. Vá em **DAGs**
3. Procure por `prometheus_mt5_executor`
4. Ative o toggle no lado esquerdo
5. Clique em **Trigger DAG** para testar manualmente

**Monitorar:** Vá em **Graph View** e acompanhe a execução das tasks:
- `run_mt5_executor` (SSHOperator)
- `check_prometheus_metrics` (HttpOperator)

---

## 📊 Verificar Métricas Prometheus

Após a execução da DAG:

1. Abra: `http://localhost:63000/metrics`
2. Procure por:
   - `fx_balance`
   - `fx_equity`
   - `fx_open_positions`
   - `fx_open_orders`
   - `fx_sl_tp_fails`
   - `fx_killswitch_activations`
   - `fx_cooldown_status`

Se aparecerem, o executor está funcionando! ✅

---

## 🔍 Troubleshooting

### Erro: "Connection refused" ao fazer SSH

**Causa:** SSH não está acessível a partir do container Docker.

**Solução:**
```bash
# No Windows, verifique se o serviço está rodando
Get-Service sshd

# Verifique firewall
Get-NetFirewallRule -DisplayName "SSH Server inbound"

# Teste localmente
ssh SEU_USUARIO@127.0.0.1
```

### Erro: "Command not found: python"

**Causa:** Python não está no PATH do usuário Windows via SSH.

**Solução:** Use caminho completo:
```bash
# No .env do Airflow, ajuste:
PROMETHEUS_MT5_EXECUTOR_COMMAND="C:/Python311/python.exe \"C:/Users/Lenovo/.cursor/SamsungGlobalMarket/Server/prometheus_mt5_executor.py\""
```

### Erro: "MT5 initialize failed"

**Causa:** MetaTrader 5 não está aberto e logado no Windows.

**Solução:**
1. Abra o MetaTrader 5
2. Faça login na conta demo/real
3. Certifique-se de que o terminal está conectado ao broker

### Erro: "Port 63000 already in use"

**Causa:** Executor já está rodando em outro processo.

**Solução:**
```powershell
# No PowerShell (Windows)
Get-Process | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force
# Ou encontre o PID específico
netstat -ano | findstr :63000
taskkill /PID <PID> /F
```

---

## 📝 Próximos Passos

Após validar a DAG rodando:

1. ✅ Configurar alertas no Grafana baseados nas métricas `fx_*`
2. ✅ Integrar com Slack via webhook (já configurado no script)
3. ✅ Configurar kill-switch threshold via `config.yaml` ou variável de ambiente
4. ✅ Documentar no runbook operacional

---

**Assinatura:**  
Prometheus System v3.0 | CET/Berlin | 2025-11-13

