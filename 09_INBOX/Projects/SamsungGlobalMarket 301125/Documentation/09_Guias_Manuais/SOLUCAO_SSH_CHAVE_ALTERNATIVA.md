# Solução Alternativa: SSH com Chave (Sem Senha, Sem Dependência de Update)

**Vantagem:** Não precisa configurar senha local nem esperar update do Windows. Funciona imediatamente.

---

## ✅ Configuração Rápida: SSH com Chave

### Passo 1: Gerar Chave SSH no Container Airflow

**No terminal WSL/Git Bash (onde o Airflow está rodando):**

```bash
# Entrar no container do Airflow worker
docker exec -it docker-airflow-worker-1 bash

# Gerar chave SSH (dentro do container)
ssh-keygen -t rsa -b 4096 -f /tmp/airflow_ssh_key -N ""

# Exibir chave pública (copie toda a saída)
cat /tmp/airflow_ssh_key.pub
```

**Copie a chave pública completa** (começa com `ssh-rsa AAAAB3NzaC1yc2E...`)

**Saia do container:**
```bash
exit
```

---

### Passo 2: Adicionar Chave Pública no Windows

**No PowerShell (Windows normal):**

```powershell
# Criar pasta .ssh se não existir
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"

# Adicionar chave pública ao arquivo authorized_keys
# SUBSTITUA "ssh-rsa AAAAB3NzaC1yc2E..." pela chave que você copiou
$publicKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ..." # Cole sua chave aqui
Add-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value $publicKey

# Corrigir permissões (IMPORTANTE para Windows)
icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F" /T
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "$env:USERNAME:F"
```

---

### Passo 3: Copiar Chave Privada para o Container (Persistente)

**No terminal WSL/Git Bash:**

```bash
# Copiar chave privada do container para fora (para persistir após reiniciar)
docker cp docker-airflow-worker-1:/tmp/airflow_ssh_key ./airflow_ssh_key
docker cp docker-airflow-worker-1:/tmp/airflow_ssh_key.pub ./airflow_ssh_key.pub

# Copiar de volta quando o container reiniciar (ou adicionar ao docker-compose)
# Por enquanto, vamos usar volume mount
```

**Ou adicionar ao docker-compose.yml:**

```yaml
volumes:
  - ./airflow_ssh_key:/tmp/airflow_ssh_key:ro
  - ./airflow_ssh_key.pub:/tmp/airflow_ssh_key.pub:ro
```

---

### Passo 4: Configurar Conexão SSH no Airflow com Chave

**No Airflow UI:**

1. Vá em **Admin → Connections**
2. Edite `prometheus_executor_host` (ou crie nova)
3. Preencha:
   - **Connection Id:** `prometheus_executor_host`
   - **Connection Type:** `SSH`
   - **Host:** `host.docker.internal` (ou IP do Windows)
   - **Login:** `Lenovo`
   - **Password:** (deixe vazio)
   - **Port:** `22`
   - **Extra:**
     ```json
     {
       "key_file": "/tmp/airflow_ssh_key",
       "no_host_key_check": true
     }
     ```
4. Clique em **Save**

---

### Passo 5: Testar SSH Manualmente (Opcional)

**No terminal WSL/Git Bash:**

```bash
# Testar SSH com chave (do host Linux, não do container)
ssh -i ./airflow_ssh_key Lenovo@127.0.0.1
```

**Se funcionar:** Você verá o prompt do Windows sem pedir senha.

---

### Passo 6: Testar DAG no Airflow

1. Vá em **DAGs → `prometheus_mt5_executor`**
2. Clique em **Trigger DAG**
3. Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

## ⚠️ Troubleshooting

### Problema: "Permission denied (publickey)"

**Causa:** Permissões incorretas no Windows ou chave pública não adicionada corretamente.

**Solução:**
```powershell
# Verificar se authorized_keys existe e tem conteúdo
Get-Content "$env:USERPROFILE\.ssh\authorized_keys"

# Recorrigir permissões
icacls "$env:USERPROFILE\.ssh" /reset
icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F"
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "$env:USERNAME:F"
```

---

### Problema: Chave não encontrada no container

**Causa:** Chave foi gerada dentro do container e foi perdida após reiniciar.

**Solução:** Use volume mount no `docker-compose.yml` para persistir a chave.

---

## ✅ Vantagens desta Abordagem

- ✅ **Não precisa de senha local** (funciona mesmo com PIN)
- ✅ **Não depende de update do Windows**
- ✅ **Mais seguro** (autenticação por chave é melhor prática)
- ✅ **Funciona imediatamente** após configuração
- ✅ **Padrão institucional** (Goldman Sachs usa chaves SSH)

---

**Status:** ✅ Pronto para usar  
**Data:** 2025-11-16 (CET/Berlin)  
**Recomendação:** Use esta abordagem se não quiser configurar senha local ou esperar update.

