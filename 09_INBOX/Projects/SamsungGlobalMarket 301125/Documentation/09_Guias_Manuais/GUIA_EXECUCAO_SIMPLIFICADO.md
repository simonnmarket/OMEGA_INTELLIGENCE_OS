# 🚀 GUIA DE EXECUÇÃO SIMPLIFICADO
## PROTOCOLO DE VALIDAÇÃO - PASSO A PASSO

**Data:** 2025-10-28  
**Projeto:** Prometheus v3.0.0 | Samsung Global Market

---

## ❓ SUAS DÚVIDAS ESCLARECIDAS

### **1. Executar o SERVER primeiro?**

✅ **SIM!** Você executa o servidor primeiro, manualmente.

**Comando:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\start_main_server.ps1
```

**Aguarde aparecer:**
```
[OK] Servico 'SocketService' iniciado na porta 5555
[SUCESSO] TODOS OS SERVICOS INICIADOS COM SUCESSO!
```

---

### **2. Após executar o servidor, você pode executar o restante automaticamente?**

✅ **SIM!** Criei um script que executa **TODOS os testes automaticamente** após você confirmar que o servidor está rodando.

**Comando:**
```powershell
.\Scripts\executar_protocolo_completo.ps1
```

**O que ele faz automaticamente:**
- ✅ Teste quantitativo do servidor (50 testes)
- ✅ Identificação de arquivos .ex5
- ✅ Teste end-to-end (100 segundos)

---

### **3. Após execução dos testes, você anexa a EA?**

✅ **SIM!** Exatamente nessa ordem:

1. ✅ Servidor rodando
2. ✅ Testes automáticos concluídos
3. ✅ **Você anexa a EA ao MT5**

---

## 📋 PROCESSO COMPLETO (3 PASSOS)

### **PASSO 1: Executar Servidor (VOCÊ FAZ)**

Abra uma janela PowerShell e execute:
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\start_main_server.ps1
```

**Deixe esta janela aberta!** O servidor precisa continuar rodando.

---

### **PASSO 2: Executar Testes Automáticos (SCRIPT FAZ)**

Abra **OUTRA janela PowerShell** e execute:
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\executar_protocolo_completo.ps1
```

O script vai:
1. Verificar se servidor está rodando
2. Executar todos os 3 testes automaticamente
3. Mostrar resultados de cada teste
4. Informar quando estiver pronto para anexar EA

---

### **PASSO 3: Anexar EA (VOCÊ FAZ)**

Após os testes passarem:
1. Abra MetaTrader 5
2. Arraste `SamsungGlobalMarket_EA` para um gráfico
3. Configure parâmetros (se necessário)
4. Clique OK

**Validar nos logs do MT5:**
- ✅ `Versao: 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA`
- ✅ `HANDSHAKE CONFIRMADO PELO SERVIDOR`
- ✅ `[DEBUG] Heartbeat recebido` (a cada ~10s)

---

## 🎯 RESUMO VISUAL

```
┌─────────────────────────────────────────┐
│  PASSO 1: Executar Servidor            │
│  VOCÊ: .\Scripts\start_main_server.ps1 │
│  ⏱️ Aguardar: "TODOS OS SERVICOS..."  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  PASSO 2: Testes Automáticos            │
│  VOCÊ: .\Scripts\executar_protocolo...    │
│  🤖 SCRIPT: Executa 3 testes            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  PASSO 3: Anexar EA                     │
│  VOCÊ: MT5 → Arrastar EA → Validar logs│
│  ✅ Versão 1.04 + Heartbeats OK        │
└─────────────────────────────────────────┘
```

---

## ⚠️ IMPORTANTE

### **O que o servidor faz:**
- **1 único servidor** (`main_server.py`) já inicia **TODOS os serviços necessários**:
  - ✅ TradingEngine (geração de sinais)
  - ✅ MT5SocketService (comunicação com EA)
  - ✅ Todos os componentes da arquitetura Big Tech

### **Você NÃO precisa executar múltiplos servidores!**

O `main_server.py` é o **orquestrador central** que inicia tudo automaticamente.

---

## 🔧 COMANDOS RÁPIDOS

### **Iniciar Servidor:**
```powershell
.\Scripts\start_main_server.ps1
```

### **Executar Testes Automáticos:**
```powershell
.\Scripts\executar_protocolo_completo.ps1
```

### **Verificar Arquivos .ex5:**
```powershell
.\Scripts\find_ex5_files.ps1
```

---

## 📊 CRITÉRIOS DE SUCESSO

Após anexar a EA, o sistema está **100% funcional** quando:

- ✅ Servidor rodando sem erros
- ✅ EA mostra versão 1.04 nos logs
- ✅ HANDSHAKE CONFIRMADO aparece
- ✅ Heartbeats recebidos a cada ~10s
- ✅ Zero timeouts ou desconexões em 10 minutos

---

**Pronto! Agora você tem o processo completo passo a passo.**

**Dúvidas?** Consulte `STATUS_PROTOCOLO_VALIDACAO.md` para mais detalhes.

