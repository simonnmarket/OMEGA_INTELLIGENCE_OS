# Solução: SSH não funciona com PIN do Windows

**Problema:** Ao tentar fazer SSH, mesmo com senha/PIN correto, aparece:
```
Lenovo@127.0.0.1's password:
Connection reset by 127.0.0.1 port 22
```

**Causa:** O SSH no Windows **NÃO funciona com PIN**. Ele requer uma **senha da conta local** configurada.

---

## ✅ Solução: Configurar Senha Local (Não PIN)

### Passo 1: Verificar se você tem senha local configurada

**No PowerShell:**
```powershell
# Verificar método de autenticação atual
net user $env:USERNAME
```

**Se aparecer:** `"Password required: No"` → Você precisa configurar uma senha.

---

### Passo 2: Configurar Senha Local no Windows

**Opção A: Via Configurações (Interface Gráfica)**

1. Abra **Configurações** (Windows + I)
2. Vá em **Contas** → **Opções de Entrada**
3. Procure por **"Senha"**
4. Clique em **"Adicionar"** ou **"Alterar"**
5. Siga as instruções para criar uma senha
6. **IMPORTANTE:** Esta senha será diferente do seu PIN

**Opção B: Via PowerShell (Administrador)**

```powershell
# Alterar senha do usuário atual
net user $env:USERNAME *
```

- Digite a nova senha quando solicitado (não aparecerá na tela)
- Confirme a senha novamente

---

### Passo 3: Corrigir Configuração SSH

**Execute o script de correção:**

```powershell
# No PowerShell como Administrador
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\fix_ssh_config.ps1
```

Este script:
- Habilita `PasswordAuthentication yes`
- Habilita `PubkeyAuthentication yes`
- Remove restrições que possam bloquear seu usuário
- Reinicia o serviço SSH

---

### Passo 4: Testar SSH com a Senha (Não PIN)

**No PowerShell (Windows normal):**
```powershell
ssh Lenovo@127.0.0.1
```

**Quando pedir senha:**
- Digite a **SENHA LOCAL** que você configurou no Passo 2
- **NÃO use o PIN!**
- Pressione Enter

**✅ Se funcionar:** Você verá algo como:
```
Welcome to Windows!
Lenovo@LAPTOP-SJN2KACD C:\Users\Lenovo>
```

**❌ Se ainda der erro:** Continue para Passo 5 (Alternativa: Chave SSH).

---

## 🔑 Alternativa: Usar Chave SSH (Recomendado)

Se você preferir não usar senha ou se a senha local não funcionar, use autenticação por chave SSH:

### Passo 1: Gerar Chave SSH

**No terminal WSL/Linux ou Git Bash:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/airflow_ssh_key -N ""
```

### Passo 2: Copiar Chave Pública para Windows

**No PowerShell (Windows):**
```powershell
# Criar pasta .ssh se não existir
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"

# Ler chave pública (cole o conteúdo que você copiou)
$publicKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ..." # Cole sua chave aqui
Add-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value $publicKey

# Corrigir permissões
icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F"
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "$env:USERNAME:F"
```

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

## ⚠️ Troubleshooting

### Problema: "Password required: No" após configurar senha

**Causa:** Windows pode estar bloqueando senha local para contas Microsoft.

**Solução:** Se você usa conta Microsoft, pode precisar criar um usuário local separado:

```powershell
# No PowerShell como Administrador
net user SSHUser "SuaSenhaAqui" /add
net localgroup Administrators SSHUser /add
```

Depois use `SSHUser` no campo **Login** da conexão SSH no Airflow.

---

### Problema: Update Windows 11 25H2 pendente

**Causa:** Versões antigas do OpenSSH Server podem ter bugs de autenticação.

**Solução:**
1. **Execute o update do Windows 11 25H2** antes de continuar
2. Ou use autenticação por chave SSH (não depende de updates)

---

### Problema: "Connection reset" mesmo com senha correta

**Causa:** Configuração `sshd_config` muito restritiva ou problema no serviço.

**Solução:**
1. Execute novamente o script `fix_ssh_config.ps1`
2. Verifique logs do SSH:
   ```powershell
   Get-EventLog -LogName Application -Source sshd -Newest 10
   ```
3. Verifique se há políticas de grupo bloqueando:
   ```powershell
   gpresult /r | Select-String -Pattern "SSH"
   ```

---

## ✅ Validação Final

Após configurar senha local ou chave SSH:

1. **Teste SSH manualmente:**
   ```powershell
   ssh Lenovo@127.0.0.1
   ```
   (Use a SENHA local, não o PIN)

2. **Teste DAG no Airflow:**
   - Vá em DAGs → `prometheus_mt5_executor`
   - Clique em **Trigger DAG**
   - Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

**Status:** ⏳ Aguardando configuração de senha local  
**Data:** 2025-11-16 (CET/Berlin)  
**Importante:** PIN ≠ SENHA para SSH!

