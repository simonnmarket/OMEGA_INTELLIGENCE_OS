# 🚀 GUIA PÓS-REINICIALIZAÇÃO - VALIDAÇÃO v1.04

**Data:** 2025-10-28  
**Objetivo:** Garantir que EA v1.04 seja carregada corretamente após reiniciar

---

## ✅ PREPARAÇÃO ANTES DE REINICIAR

**Status Atual:**
- ✅ Servidor Python corrigido (sem emojis, heartbeat 10s)
- ✅ Arquivo .mq5 tem versão 1.04 com todas as correções
- ✅ Arquivos .ex5 antigos foram deletados
- ✅ Código tem marcadores de validação únicos

---

## 📋 PROTOCOLO APÓS REINICIAR

### **PASSO 1: Iniciar Servidor Python**

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\start_main_server.ps1
```

**Ou manualmente:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\venv\Scripts\Activate.ps1
python Server\main_server.py
```

**Verificar:**
- Log mostra: `[OK] Servico de Socket iniciado em 127.0.0.1:5555`
- Log mostra: `[OK] Servico 'TradingEngine' iniciado`
- Porta 5555 está aberta

---

### **PASSO 2: Abrir MetaEditor (APENAS MetaEditor, NÃO MT5 ainda)**

1. **Abrir MetaEditor como programa independente**
   - NÃO usar F4 no MT5
   - Abrir MetaEditor diretamente

2. **Abrir arquivo:**
   - `C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5`

3. **Verificar versão no código:**
   - Linha 8: `#property version "1.04"`
   - Linha 95-96: Deve mostrar:
     ```mql5
     Print("Versao: 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA");
     Print("CONFIRMACAO: Se voce ve esta mensagem, a versao 1.04 foi compilada corretamente!");
     ```

4. **COMPILAR (F7):**
   - Aguardar: `0 error(s), 0 warning(s)`
   - Verificar no Navigator: arquivo `.ex5` foi gerado AGORA (data/hora atual)

5. **FECHAR MetaEditor**

---

### **PASSO 3: Abrir MT5 Terminal**

1. Abrir MT5 Terminal (como se fosse primeira vez)
2. Aguardar carregamento completo

---

### **PASSO 4: Anexar EA e VALIDAR VERSÃO**

1. **Arrastar EA para o gráfico**
2. Configurar parâmetros se necessário
3. Clicar em OK

4. **CRÍTICO: Verificar log do MT5 (aba Experts)**

   **DEVE APARECER:**
   ```
   Versao: 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA
   CONFIRMACAO: Se voce ve esta mensagem, a versao 1.04 foi compilada corretamente!
   ```

   **NÃO PODE APARECER:**
   ```
   Versao: 1.02  ← Se aparecer isso, recompilação falhou
   ```

---

### **PASSO 5: Validar Comunicação Completa**

Após anexar EA v1.04, monitorar por 2 minutos:

**Logs do MT5 devem mostrar:**
```
Versao: 1.04 - IMPLEMENTACAO CIENTIFICA VALIDADA
CONFIRMACAO: Se voce ve esta mensagem, a versao 1.04 foi compilada corretamente!
CONEXAO ESTABELECIDA COM SUCESSO!
[DEBUG] Enviando handshake...
[DEBUG] Handshake enviado com sucesso!
HANDSHAKE CONFIRMADO PELO SERVIDOR  ← DEVE APARECER!
[DEBUG] Heartbeat recebido do servidor!  ← DEVE APARECER A CADA 10s!
```

**Logs do Servidor devem mostrar:**
```
[CONEXAO] NOVA CONEXAO ACEITA
[CLIENTE] EA conectado (Total de clientes: 1)
[DADOS] Dados recebidos: handshake
[HANDSHAKE] EA: SamsungGlobalMarket_EA v1.04
[HANDSHAKE] ACK enviado
[HEARTBEAT] Enviado para 1 cliente(s)  ← A cada 10s
```

---

## ✅ CRITÉRIOS DE SUCESSO

**Sistema totalmente funcional SE:**
- ✅ Log MT5 mostra versão 1.04 (com mensagem de confirmação)
- ✅ Log MT5 mostra "HANDSHAKE CONFIRMADO"
- ✅ Log MT5 mostra heartbeats recebidos
- ✅ Log servidor mostra heartbeats sendo enviados
- ✅ Zero timeouts de heartbeat

**Se algum critério falhar:**
- Documentar qual critério
- Verificar logs de ambos os lados
- Reportar problema específico

---

## 🔍 COMANDOS ÚTEIS PARA VALIDAÇÃO

### **Verificar status do servidor:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
Get-Content logs\main_server.log -Tail 30
```

### **Verificar eventos de conexão:**
```powershell
.\check_connection_events.ps1
```

### **Verificar se porta está aberta:**
```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 5555
```

---

## 🚨 SE AINDA MOSTRAR v1.02

Se mesmo após reiniciar, o log ainda mostrar versão 1.02:

1. **Verificar se há múltiplos arquivos .mq5:**
   ```powershell
   Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.mq5"
   ```
   Editar TODOS para versão 1.04

2. **Deletar TODOS os .ex5 novamente:**
   ```powershell
   Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" | Remove-Item -Force
   ```

3. **Recompilar novamente**

---

## 📊 CHECKLIST PÓS-REINICIALIZAÇÃO

- [ ] Computador reiniciado
- [ ] Servidor Python iniciado e rodando
- [ ] MetaEditor aberto (sem MT5)
- [ ] Arquivo .mq5 verificado (versão 1.04)
- [ ] Compilação bem-sucedida (0 errors, 0 warnings)
- [ ] Arquivo .ex5 gerado (data/hora atual)
- [ ] MetaEditor fechado
- [ ] MT5 Terminal aberto
- [ ] EA anexado ao gráfico
- [ ] Log MT5 mostra versão 1.04 (com confirmação)
- [ ] Log MT5 mostra "HANDSHAKE CONFIRMADO"
- [ ] Log MT5 mostra heartbeats recebidos
- [ ] Log servidor mostra heartbeats enviados
- [ ] Zero timeouts após 2 minutos

---

## 🎯 OBJETIVO FINAL

Após validar todos os critérios de sucesso:

✅ **INICIAR FASE 5: PAPER TRADING**

O sistema estará 100% funcional com:
- Comunicação bidirecional completa
- Heartbeats funcionando
- Sinais sendo enviados e recebidos
- Sistema pronto para operar 24/7

---

**Status:** ⏳ AGUARDANDO REINICIALIZAÇÃO E VALIDAÇÃO

**Boas práticas após reiniciar:**
1. Seguir protocolo passo a passo
2. Não pular etapas
3. Verificar cada critério de sucesso
4. Documentar qualquer anomalia

**Boa sorte! A reinicialização deve resolver o problema de cache definitivamente.**

