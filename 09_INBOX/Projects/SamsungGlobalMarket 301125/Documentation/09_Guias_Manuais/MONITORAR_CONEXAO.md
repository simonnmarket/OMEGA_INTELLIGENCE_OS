# 📊 MONITORAMENTO DE CONEXÃO - INSTRUÇÕES

**Status:** Servidor iniciado com logs detalhados

---

## 🔍 O QUE MONITORAR

Após iniciar o servidor, os logs vão mostrar **EXATAMENTE** o que acontece quando o EA se conecta.

---

## 📋 CHECKLIST DE VALIDAÇÃO

### **1. Servidor Iniciado**
- [ ] Verificar: `✅ Serviço de Socket iniciado em 127.0.0.1:5555`
- [ ] Verificar: `📡 Aguardando conexões de EAs...`

### **2. EA Conecta**
Quando o EA anexar ao gráfico, você DEVE ver nos logs:

- [ ] `🔌 NOVA CONEXÃO ACEITA de ('127.0.0.1', XXXXX)`
- [ ] `🤝 EA conectado de ('127.0.0.1', XXXXX) (Total de clientes: 1)`
- [ ] `📡 Thread de handler iniciada para ('127.0.0.1', XXXXX)`
- [ ] `📨 Handler iniciado para ('127.0.0.1', XXXXX) - aguardando mensagens...`

### **3. EA Envia Handshake**
- [ ] `📥 Dados recebidos de ('127.0.0.1', XXXXX): X bytes - {"message_type":"HANDSHAKE"...}`
- [ ] `[HANDSHAKE] EA: SamsungGlobalMarket_EA v1.02 | Conta: XXXXX`
- [ ] `[HANDSHAKE] ACK enviado para SamsungGlobalMarket_EA`

### **4. Heartbeats Enviados**
- [ ] `[HEARTBEAT] Enviado para 1 cliente(s)` (a cada 30 segundos)

---

## 🚨 CENÁRIOS PROBLEMÁTICOS

### **Se NÃO aparecer "NOVA CONEXÃO ACEITA":**
- **Problema:** Servidor não está registrando conexão do EA
- **Possível causa:** Porta bloqueada, firewall, ou problema no socket.accept()

### **Se aparecer conexão mas NÃO aparecer "Dados recebidos":**
- **Problema:** EA conecta mas não envia handshake
- **Possível causa:** EA não está enviando mensagem após conectar

### **Se aparecer dados mas NÃO aparecer "HANDSHAKE":**
- **Problema:** Servidor recebe dados mas não processa como handshake
- **Possível causa:** Formato JSON incorreto ou parsing falhando

### **Se aparecer handshake mas NÃO aparecer "HEARTBEAT Enviado":**
- **Problema:** Cliente não está na lista de clientes para heartbeat
- **Possível causa:** Cliente foi removido da lista antes do heartbeat

---

## 📊 COMANDO PARA MONITORAR

```powershell
# Monitorar logs em tempo real
Get-Content logs\main_server.log -Wait -Tail 20

# OU ver últimas 30 linhas
Get-Content logs\main_server.log -Tail 30
```

---

## ⏱️ TEMPO DE TESTE

**Aguardar 2 minutos após anexar EA:**
- Verificar se handshake aparece
- Verificar se pelo menos 1-2 heartbeats são enviados
- Verificar se há erros nos logs

---

**PRÓXIMA AÇÃO:** Monitorar logs enquanto EA está anexado e verificar quais eventos aparecem.

