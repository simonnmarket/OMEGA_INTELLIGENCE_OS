# Próximos Passos: SSH Configurado - Configurar Senha Local

**Status Atual:** ✅ SSH configurado com sucesso  
**Data:** 2025-11-16 (CET/Berlin)

---

## ✅ O Que Foi Feito

1. ✅ `PasswordAuthentication yes` habilitado
2. ✅ `PubkeyAuthentication yes` habilitado
3. ✅ Serviço SSH reiniciado e rodando
4. ✅ Backup do `sshd_config` criado

---

## 🔑 Próximo Passo: Configurar Senha Local

### ⚠️ Problema: Conta Microsoft (Online Provider)

Se você receber o erro:
```
System error 8646 has occurred.
The system is not authoritative for the specified account...
```

**Isso significa:** Sua conta `Lenovo` é uma **conta Microsoft** (online), não uma conta local. O Windows não pode alterar a senha localmente porque ela é gerenciada pela Microsoft.

---

### ✅ Solução 1: Testar SSH com a Senha que Você Configurou

Se você já alterou a senha via **Configurações do Windows**, teste diretamente:

```powershell
ssh Lenovo@127.0.0.1
```

- Use a senha que você configurou no sistema
- Se funcionar, pode usar essa senha no Airflow

---

### ✅ Solução 2: Criar Usuário Local Dedicado para SSH (Recomendado)

Se a senha da conta Microsoft não funcionar para SSH, crie um usuário local separado:

**No PowerShell como Administrador:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\create_ssh_user.ps1
```

O script vai:
1. Criar usuário `SSHUser` (local, não Microsoft)
2. Pedir para você definir uma senha
3. Configurar permissões necessárias
4. Mostrar as informações para configurar no Airflow

**Depois use:**
- **Login no Airflow:** `SSHUser`
- **Password no Airflow:** A senha que você definiu

---

## 🧪 Testar SSH com a Senha Local

**No PowerShell (Windows normal):**

```powershell
ssh Lenovo@127.0.0.1
```

**Quando pedir senha:**
- Digite a **SENHA LOCAL** que você configurou (NÃO o PIN!)
- Pressione Enter

**✅ Se funcionar:** Você verá algo como:
```
Welcome to Windows!
Lenovo@LAPTOP-SJN2KACD C:\Users\Lenovo>
```

**Saia do SSH:** Digite `exit`

---

## 🔧 Atualizar Conexão SSH no Airflow

Após confirmar que o SSH funciona manualmente:

1. No **Airflow UI**, vá em **Admin → Connections**
2. Edite `prometheus_executor_host`
3. Preencha:
   - **Connection Id:** `prometheus_executor_host`
   - **Connection Type:** `SSH`
   - **Host:** `host.docker.internal` (ou IP do Windows)
   - **Login:** `Lenovo`
   - **Password:** A **SENHA LOCAL** que você configurou (NÃO o PIN!)
   - **Port:** `22`
   - **Extra:** (deixe vazio)
4. Clique em **Save**

---

## 🧪 Testar DAG no Airflow

1. Vá em **DAGs → `prometheus_mt5_executor`**
2. Clique em **Trigger DAG**
3. Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

## ⚠️ Lembrete Importante

- **PIN ≠ SENHA para SSH!**
- Use a **SENHA LOCAL** que você configurou, não o PIN
- Se não tiver senha local configurada, o SSH não funcionará mesmo com o PIN correto

---

## 📝 Status

- ✅ SSH configurado corretamente
- ⏳ Aguardando configuração de senha local
- ⏳ Aguardando teste SSH manual
- ⏳ Aguardando atualização da conexão no Airflow
- ⏳ Aguardando teste da DAG

---

**Próxima Ação:** Configure a senha local e teste o SSH manualmente.

