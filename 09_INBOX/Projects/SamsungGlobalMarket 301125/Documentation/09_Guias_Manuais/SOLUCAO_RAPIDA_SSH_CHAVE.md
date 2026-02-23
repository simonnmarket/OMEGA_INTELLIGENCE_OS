# Solução Rápida: SSH com Chave (Sem Senha Local)

**Problema:** SSH com senha não funciona devido a permissões complexas do Windows.

**Solução:** Usar autenticação por chave SSH - funciona imediatamente, sem precisar configurar permissões.

---

## ✅ Passo 1: Gerar Chave SSH no Airflow Container

**No terminal WSL/Git Bash (onde o Airflow está rodando):**

```bash
# Entrar no container do Airflow worker
docker exec -it docker-airflow-worker-1 bash

# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -f /tmp/airflow_ssh_key -N ""

# Exibir chave pública (COPIE TUDO)
cat /tmp/airflow_ssh_key.pub
```

**Copie a chave pública completa** (começa com `ssh-rsa AAAAB3NzaC1yc2E...`)

**Saia do container:**
```bash
exit
```

---

## ✅ Passo 2: Adicionar Chave Pública no Windows

**No PowerShell (Windows normal):**

```powershell
# Criar pasta .ssh se não existir
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"

# Adicionar chave pública ao arquivo authorized_keys
# SUBSTITUA "ssh-rsa AAAAB3NzaC1yc2E..." pela chave que você copiou
$publicKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ..." # Cole sua chave aqui
Add-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value $publicKey

# Corrigir permissões (CRÍTICO para Windows)
icacls "$env:USERPROFILE\.ssh" /reset
icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F" /T
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "$env:USERNAME:F"
```

---

## ✅ Passo 3: Copiar Chave Privada para Volume Persistente

**No terminal WSL/Git Bash:**

```bash
# Criar pasta para chaves SSH no projeto
mkdir -p Orchestration/Airflow/docker/ssh_keys

# Copiar chave privada do container
docker cp docker-airflow-worker-1:/tmp/airflow_ssh_key Orchestration/Airflow/docker/ssh_keys/

# Verificar se copiou
ls -la Orchestration/Airflow/docker/ssh_keys/
```

---

## ✅ Passo 4: Adicionar Volume ao Docker Compose

**Edite o arquivo `Orchestration/Airflow/docker/docker-compose.yml`:**

Adicione ao serviço `airflow-worker`:

```yaml
volumes:
  - ./ssh_keys:/tmp/ssh_keys:ro
```

**Reinicie o Airflow:**
```bash
cd Orchestration/Airflow/docker
docker-compose restart airflow-worker
```

---

## ✅ Passo 5: Configurar Conexão SSH no Airflow com Chave

**No Airflow UI:**

1. Vá em **Admin → Connections**
2. Edite `prometheus_executor_host` (ou crie nova)
3. Preencha:
   - **Connection Id:** `prometheus_executor_host`
   - **Connection Type:** `SSH`
   - **Host:** `host.docker.internal`
   - **Login:** `Lenovo` (sua conta existente)
   - **Password:** (deixe VAZIO)
   - **Port:** `22`
   - **Extra:**
     ```json
     {
       "key_file": "/tmp/ssh_keys/airflow_ssh_key",
       "no_host_key_check": true
     }
     ```
4. Clique em **Save**

---

## ✅ Passo 6: Testar SSH Manualmente (Opcional)

**No terminal WSL/Git Bash:**

```bash
# Testar SSH com chave (do container)
docker exec docker-airflow-worker-1 ssh -i /tmp/ssh_keys/airflow_ssh_key -o StrictHostKeyChecking=no Lenovo@host.docker.internal "whoami"
```

**Se funcionar:** Mostrará `Lenovo` (seu usuário).

---

## ✅ Passo 7: Testar DAG no Airflow

1. Vá em **DAGs → `prometheus_mt5_executor`**
2. Clique em **Trigger DAG**
3. Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

## ✅ Vantagens desta Abordagem

- ✅ **Funciona imediatamente** - não precisa configurar permissões complexas
- ✅ **Mais seguro** - autenticação por chave é melhor que senha
- ✅ **Não depende de usuário local** - funciona com conta Microsoft também
- ✅ **Padrão institucional** - Goldman Sachs usa chaves SSH

---

## ⚠️ Se Ainda Não Funcionar

Se mesmo com chave SSH não funcionar, temos uma alternativa:

**Usar WinRM (Windows Remote Management)** em vez de SSH:

O Airflow tem provider WinRM que funciona nativamente no Windows. Vamos configurar isso se SSH com chave não funcionar.

---

**Tempo estimado:** 10 minutos  
**Complexidade:** Baixa  
**Próxima ação:** Execute os Passos 1-2 e me avise quando terminar.

