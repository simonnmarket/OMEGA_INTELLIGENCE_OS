# Solução: ERR_CONNECTION_REFUSED no Airflow

**Problema:** Ao tentar acessar `http://localhost:8080`, aparece "This site can't be reached" / "ERR_CONNECTION_REFUSED"

**Causa:** O Airflow não está rodando via Docker Compose

---

## 🔍 Diagnóstico Rápido

### Passo 1: Verificar Docker Desktop

1. **Procure na barra de tarefas** (systray, canto inferior direito) por um ícone de baleia 🐳 (Docker)
2. **Se NÃO encontrar o ícone**, o Docker Desktop não está rodando

**Solução:**
- Abra o menu Iniciar do Windows
- Procure por "Docker Desktop"
- Clique para iniciar
- **Aguarde 1-2 minutos** até o Docker Desktop inicializar completamente (o ícone da baleia aparecerá)

---

### Passo 2: Verificar se os Containers do Airflow Estão Rodando

**Opção A - Via Terminal WSL (Ubuntu):**

```bash
# Abra o terminal WSL (Ubuntu)
cd /mnt/c/Users/Lenovo/.cursor/SamsungGlobalMarket/Orchestration/Airflow/docker

# Verifique containers rodando
docker compose -f docker-compose.yaml ps
```

**Opção B - Via PowerShell (Windows):**

```powershell
# Verificar se o Docker Desktop está acessível
docker ps

# Se funcionar, verificar containers do Airflow
docker ps | findstr airflow
```

**Resultado esperado:** Você deve ver containers com nomes como:
- `docker-airflow-apiserver-1`
- `docker-airflow-scheduler-1`
- `docker-airflow-worker-1`

**Se NÃO ver esses containers**, continue para o Passo 3.

---

### Passo 3: Iniciar os Containers do Airflow

**No terminal WSL (Ubuntu):**

```bash
# Navegar até a pasta do Airflow
cd /mnt/c/Users/Lenovo/.cursor/SamsungGlobalMarket/Orchestration/Airflow/docker

# Iniciar os containers
docker compose -f docker-compose.yaml up -d

# Aguardar 30-60 segundos para inicialização completa
sleep 30

# Verificar logs para confirmar que está funcionando
docker compose -f docker-compose.yaml logs --tail=20 airflow-apiserver
```

**✅ Resultado esperado:** 
- Containers iniciando (pode levar 1-2 minutos na primeira vez)
- Logs mostrando "Booting worker" ou "Airflow is ready"

---

### Passo 4: Verificar Porta 8080

**No PowerShell (Windows):**

```powershell
# Verificar se algo está usando a porta 8080
netstat -ano | findstr :8080
```

**Se retornar vazio**, a porta está livre e o Airflow deve ser acessível.

**Se retornar algo como:**
```
TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    12345
```
Isso indica que algo está usando a porta (provavelmente o Airflow).

---

### Passo 5: Testar Acesso ao Airflow

1. **Abra o navegador**
2. **Acesse:** `http://localhost:8080`
3. **Aguarde 10-20 segundos** (primeira carga pode demorar)

**✅ Se funcionar:** Você verá a tela de login do Airflow

**❌ Se ainda não funcionar:** Continue para Troubleshooting abaixo

---

## ⚠️ Troubleshooting Avançado

### Problema 1: Docker Desktop não inicia

**Solução:**
1. Reinicie o computador
2. Abra o Docker Desktop novamente
3. Aguarde até aparecer "Docker Desktop is running" na notificação

### Problema 2: Erro "Cannot connect to Docker daemon"

**Solução:**
1. No Docker Desktop, vá em **Settings → General**
2. Marque **"Use the WSL 2 based engine"**
3. Clique em **"Apply & Restart"**

### Problema 3: Containers do Airflow ficam "Exited"

**Solução:**
```bash
# No terminal WSL
cd /mnt/c/Users/Lenovo/.cursor/SamsungGlobalMarket/Orchestration/Airflow/docker

# Ver logs de erro
docker compose -f docker-compose.yaml logs

# Remover containers antigos e recriar
docker compose -f docker-compose.yaml down
docker compose -f docker-compose.yaml up -d
```

### Problema 4: Porta 8080 já está em uso por outro processo

**Solução:**
```powershell
# Encontrar o processo usando porta 8080
netstat -ano | findstr :8080

# Parar o processo (substitua 12345 pelo PID encontrado)
taskkill /PID 12345 /F
```

**OU** altere a porta do Airflow no `docker-compose.yaml`:
```yaml
ports:
  - "8081:8080"  # Mude 8081 para outra porta livre
```

Depois acesse: `http://localhost:8081`

---

## ✅ Checklist Final

Antes de continuar com o Passo 1 do guia SSH:

- [ ] Docker Desktop está rodando (ícone da baleia visível)
- [ ] Containers do Airflow estão rodando (`docker ps` mostra airflow-*)
- [ ] `http://localhost:8080` abre a tela de login do Airflow
- [ ] Consigo fazer login com `airflow` / `airflow`

**Quando todos os itens estiverem ✅, volte para o PASSO 1 do guia SSH!**

---

**Status:** ⏳ Aguardando Docker/Airflow estar rodando  
**Data:** 2025-11-13 (CET/Berlin)

