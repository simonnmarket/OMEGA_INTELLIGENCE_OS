# PASSO 1: Criar Conexão SSH no Airflow UI

**Objetivo:** Configurar conexão SSH para o Airflow executar scripts no Windows host  
**Tempo estimado:** 2-3 minutos  
**Dificuldade:** Fácil

---

## 📋 Pré-requisitos

- ✅ Airflow rodando via Docker Compose (porta 8080)
- ✅ OpenSSH Server rodando no Windows (porta 22)
- ✅ Usuário e senha do Windows para autenticação SSH

---

## 🎯 Passo a Passo Detalhado

### 1.1 Abrir o Airflow UI

1. **Abra seu navegador** (Chrome, Edge, Firefox)
2. **Acesse:** `http://localhost:8080`
3. **Login padrão:**
   - **Usuário:** `airflow`
   - **Senha:** `airflow`
4. **Clique em "Sign In"** ou pressione Enter

**✅ Resultado esperado:** Você verá a página inicial do Airflow (Dashboard com lista de DAGs)

---

### 1.2 Navegar até Connections

1. **No menu superior** (topo da página), procure por **"Admin"**
2. **Clique em "Admin"** (menu dropdown abrirá)
3. **No dropdown, clique em "Connections"**

**✅ Resultado esperado:** Você verá a página "Connections" com uma lista de conexões existentes (pode estar vazia)

---

### 1.3 Criar Nova Conexão

1. **No canto superior direito** da página "Connections", procure por um botão **"+ Add a new record"** ou **"+"** ou **"Create"**
2. **Clique neste botão**

**✅ Resultado esperado:** Um formulário de "Add Connection" aparecerá na tela

---

### 1.4 Preencher Formulário SSH

Agora você precisa preencher os campos do formulário:

#### Campo 1: Connection Id
- **Digite:** `prometheus_executor_host`
- **Descrição:** Nome identificador da conexão (obrigatório ser exatamente assim)

#### Campo 2: Connection Type
- **Clique no dropdown** (pode estar como "HTTP" por padrão)
- **Procure e selecione:** `SSH`

#### Campo 3: Host
- **Digite:** `host.docker.internal`
- **Descrição:** Este é o hostname especial do Docker Desktop para acessar o host Windows

**⚠️ Alternativa:** Se `host.docker.internal` não funcionar, use o IP do Windows:
- No PowerShell, execute: `ipconfig` e procure por "IPv4 Address" (ex: `192.168.1.100`)
- Use este IP no lugar de `host.docker.internal`

#### Campo 4: Schema (opcional)
- **Deixe vazio** ou digite: `22`
- **Descrição:** Porta SSH (22 é o padrão)

#### Campo 5: Login
- **Digite seu usuário Windows** (ex: `Lenovo` ou `simonnmarket`)
- **Descrição:** Mesmo usuário que você usa para fazer login no Windows

#### Campo 6: Password
- **Digite sua senha do Windows**
- **Descrição:** Senha da conta de usuário Windows acima

#### Campo 7: Port (se disponível)
- **Digite:** `22`
- **Descrição:** Porta padrão do SSH

#### Campo 8: Extra (opcional)
- **Deixe vazio** por enquanto
- **Descrição:** Configurações adicionais (não necessário agora)

---

### 1.5 Salvar Conexão

1. **Após preencher todos os campos obrigatórios**, procure por um botão **"Save"** ou **"Create"** no final do formulário
2. **Clique em "Save"**

**✅ Resultado esperado:** 
- A página retornará para a lista de "Connections"
- Você verá a nova conexão `prometheus_executor_host` listada na tabela
- Status deve mostrar como "Active" ou similar

---

## ✅ Validação do Passo 1

Para confirmar que o Passo 1 foi concluído com sucesso:

1. **Na lista de Connections**, procure por `prometheus_executor_host`
2. **Verifique que está listada** com Connection Type = `SSH`
3. **Clique na conexão** para editar (se quiser verificar os detalhes)

**✅ Se você conseguir ver a conexão `prometheus_executor_host` na lista, o Passo 1 está COMPLETO!**

---

## ⚠️ Problemas Comuns (Troubleshooting)

### Problema 1: "Connection refused" ou "Cannot connect to host"

**Solução:**
- Verifique se o OpenSSH Server está rodando:
  ```powershell
  Get-Service sshd
  ```
  Deve mostrar "Running"

- Verifique se o firewall permite porta 22:
  ```powershell
  Get-NetFirewallRule -DisplayName "SSH Server inbound"
  ```
  Deve mostrar "Enabled = True"

### Problema 2: "Authentication failed" ao testar conexão

**Solução:**
- Verifique usuário e senha Windows (precisam ser exatos)
- Teste SSH manualmente no PowerShell:
  ```powershell
  ssh SEU_USUARIO@127.0.0.1
  ```
  Se funcionar manualmente, o problema pode ser no hostname (`host.docker.internal`)

### Problema 3: Campo "Connection Type" não mostra "SSH"

**Solução:**
- Verifique se o Airflow está usando a versão correta
- O provider SSH deve estar instalado (já vem no Airflow Docker Compose padrão)

---

## 📝 Próximo Passo

**Após concluir o Passo 1 com sucesso, avise-me e vamos para o Passo 2:**
- **Passo 2:** Criar conexão HTTP (`prometheus_localhost`)

---

**Status do Passo 1:** ⏳ Aguardando execução  
**Data:** 2025-11-13 (CET/Berlin)

