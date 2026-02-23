# Solução: SSH Authentication Failed - Connection Reset

**Problema:** Ao tentar fazer SSH, aparece:
```
Lenovo@127.0.0.1's password:
Connection reset by 127.0.0.1 port 22
```

**Causa:** O OpenSSH Server no Windows está bloqueando autenticação por senha ou tem configurações restritivas.

---

## ✅ Solução: Habilitar Autenticação por Senha no SSH Server

### Passo 1: Verificar Configuração Atual

**No PowerShell (como Administrador):**

```powershell
Get-Content C:\ProgramData\ssh\sshd_config | Select-String -Pattern "PasswordAuthentication|PubkeyAuthentication"
```

**Se aparecer:**
- `PasswordAuthentication no` → Precisamos habilitar (mudar para `yes`)
- `#PasswordAuthentication yes` → Está comentado, precisamos descomentar

---

### Passo 2: Editar Configuração SSH

**No PowerShell (como Administrador):**

1. **Faça backup da configuração:**
   ```powershell
   Copy-Item C:\ProgramData\ssh\sshd_config C:\ProgramData\ssh\sshd_config.backup
   ```

2. **Abra o arquivo para editar:**
   ```powershell
   notepad C:\ProgramData\ssh\sshd_config
   ```

3. **Procure por `PasswordAuthentication`** e altere para:
   ```
   PasswordAuthentication yes
   ```

   **Se não encontrar, adicione no final do arquivo:**
   ```
   PasswordAuthentication yes
   PubkeyAuthentication yes
   ```

4. **Salve o arquivo** (Ctrl+S) e **feche o Notepad**.

---

### Passo 3: Reiniciar Serviço SSH

**No PowerShell (como Administrador):**

```powershell
Restart-Service sshd
```

**Verifique se o serviço está rodando:**
```powershell
Get-Service sshd
```

**Deve mostrar:** `Running`

---

### Passo 4: Testar SSH Manualmente

**No PowerShell (Windows normal):**

```powershell
ssh Lenovo@127.0.0.1
```

**Quando pedir senha:**
- Digite sua **senha do Windows**
- **Pressione Enter**

**✅ Se funcionar:** Você verá algo como:
```
Welcome to Windows!
Lenovo@LAPTOP-SJN2KACD C:\Users\Lenovo>
```

**❌ Se ainda der erro:** Continue para Passo 5 (Alternativa: Chave SSH).

---

## 🔑 Alternativa: Usar Chave SSH (Recomendado para Produção)

Se autenticação por senha não funcionar ou você preferir usar chave SSH:

### Passo 1: Gerar Chave SSH no Airflow Container

**No terminal WSL/Linux onde o Airflow está rodando:**

```bash
cd /mnt/c/Users/Lenovo/.cursor/SamsungGlobalMarket/Orchestration/Airflow/docker

# Gerar chave SSH no container
docker exec docker-airflow-worker-1 ssh-keygen -t rsa -b 4096 -f /tmp/airflow_ssh_key -N ""

# Copiar chave pública
docker exec docker-airflow-worker-1 cat /tmp/airflow_ssh_key.pub
```

**Copie a chave pública** (começa com `ssh-rsa ...`)

---

### Passo 2: Adicionar Chave Pública no Windows

**No PowerShell (Windows):**

1. **Criar pasta `.ssh` no perfil do usuário (se não existir):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"
   ```

2. **Adicionar chave pública ao arquivo `authorized_keys`:**
   ```powershell
   # Cole a chave pública que você copiou acima
   Add-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ..."
   ```

3. **Corrigir permissões:**
   ```powershell
   icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F"
   icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "$env:USERNAME:F"
   ```

---

### Passo 3: Configurar Conexão SSH no Airflow com Chave

**No Airflow UI:**

1. Vá em **Admin → Connections**
2. Edite `prometheus_executor_host`
3. Em **Extra**, adicione JSON:
   ```json
   {
     "key_file": "/tmp/airflow_ssh_key",
     "no_host_key_check": true
   }
   ```
4. **Deixe Password vazio** (não é necessário com chave SSH)
5. Clique em **Save**

---

## ✅ Validação

Após habilitar autenticação por senha ou configurar chave SSH:

1. **Teste SSH manualmente:**
   ```powershell
   ssh Lenovo@127.0.0.1
   ```

2. **Teste DAG no Airflow:**
   - Vá em DAGs → `prometheus_mt5_executor`
   - Clique em **Trigger DAG**
   - Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

## ⚠️ Troubleshooting

### Problema: "Permission denied" mesmo com senha correta

**Causa:** Usuário Windows não tem permissão de login via SSH.

**Solução:**
1. Adicione o usuário ao grupo **Remote Desktop Users** (se estiver usando login Microsoft)
2. Ou crie um usuário local específico para SSH

### Problema: "Connection reset" após digitar senha

**Causa:** Configuração `sshd_config` muito restritiva.

**Solução:** Verifique se não há `DenyUsers` ou `AllowUsers` bloqueando seu usuário.

---

**Status:** ⏳ Aguardando correção da configuração SSH  
**Data:** 2025-11-16 (CET/Berlin)

