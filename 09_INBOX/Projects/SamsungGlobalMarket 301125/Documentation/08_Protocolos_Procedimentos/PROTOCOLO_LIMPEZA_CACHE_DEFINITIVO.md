# PROTOCOLO DEFINITIVO: LIMPEZA DE CACHE E COMPILAÇÃO v1.15

**PROJETO:** Prometheus v3.0.0 | Samsung Global Market  
**DATA:** 2025-10-29  
**VERSÃO ALVO:** v1.15  
**STATUS:** ✅ **CRÍTICO - EXECUTAR ANTES DE TESTAR**

---

## 🚨 PROBLEMA IDENTIFICADO

Os logs mostram que o MT5 está carregando a **versão 1.13** mesmo após atualização do código para **v1.15**. Isso indica que:

1. ❌ Cache do MT5 está usando arquivo `.ex5` antigo
2. ❌ A nova versão não foi compilada ou não está no diretório correto
3. ❌ O timeout otimizado (50ms durante PCA) não está ativo

**Evidência:**
```
Log do EA: "Versao: 1.13 - ANALISE FINAL COMPLETA"
Log do Servidor: "[HANDSHAKE] EA: SamsungGlobalMarket_EA v1.13"
```

---

## ✅ SOLUÇÃO: PROTOCOLO DE LIMPEZA DEFINITIVO

### PASSO 1: Fechar MT5 Completamente (OBRIGATÓRIO)

**Ações:**
1. Fechar todas as janelas do MetaTrader 5
2. Fechar MetaEditor (se aberto)
3. Verificar Processos no Gerenciador de Tarefas:
   - `terminal64.exe` - **DEVE SER FECHADO**
   - `metaeditor64.exe` - **DEVE SER FECHADO**
4. Se processos ainda estiverem rodando:
   - Clicar com botão direito → Finalizar tarefa
   - Ou usar: `Stop-Process -Name terminal64 -Force`

### PASSO 2: Executar Script de Limpeza

**Comando:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\limpar_cache_mt5.ps1
```

**O que o script faz:**
- ✅ Detecta e fecha processos MT5 automaticamente
- ✅ Identifica TODOS os arquivos `.ex5` do sistema
- ✅ Deleta cache antigo completamente
- ✅ Valida limpeza

**Saída Esperada:**
```
[OK] Cache limpo com sucesso!
[OK] Nenhum arquivo .ex5 restante
```

### PASSO 3: Compilar EA v1.15

**Ações:**
1. Abrir MetaEditor (NÃO abrir MT5 ainda)
2. Abrir arquivo: `SamsungGlobalMarket_EA.mq5`
3. Verificar no código (linha 8):
   ```mql5
   #property version   "1.15"
   ```
4. Verificar mensagem de confirmação (linhas 144-154):
   ```mql5
   Print("Versao: 1.15 - APERFEICOAMENTOS ALTO NIVEL - EA TIER-0");
   Print("CONFIRMACAO CRITICA v1.15:");
   Print("  - Timeout PCA otimizado: 50ms (forceRead)");
   ```
5. Compilar: Pressionar `F7` ou Menu `Compile`
6. **AGUARDAR:** Mensagem "0 error(s), 0 warning(s)"
7. Fechar MetaEditor

### PASSO 4: Validar Compilação

**Localizar arquivo `.ex5` compilado:**
```
C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\<ID_TERMINAL>\MQL5\Experts\SamsungGlobalMarket_EA.ex5
```

**Verificar:**
- ✅ Data de modificação deve ser **AGORA** (últimos minutos)
- ✅ Tamanho deve ser similar a versões anteriores (~100-200 KB)
- ✅ Deve existir apenas **UM** arquivo `.ex5`

### PASSO 5: Abrir MT5 e Anexar EA

**Ações:**
1. Abrir MetaTrader 5 Terminal
2. Ir para aba "Expert Advisors"
3. Arrastar `SamsungGlobalMarket_EA` para um gráfico
4. Configurar parâmetros (se necessário)
5. Marcar "Allow automated trading"
6. Clicar "OK"

### PASSO 6: Validar Versão Carregada

**Logs Esperados (Versão 1.15 CORRETA):**
```
=========================================================
SAMSUNG GLOBAL MARKET EA - INICIALIZANDO
=========================================================
Versao: 1.15 - APERFEICOAMENTOS ALTO NIVEL - EA TIER-0
=========================================================
CONFIRMACAO CRITICA v1.15:
  - Timeout PCA otimizado: 50ms (forceRead)
  - Metricas de Performance: ATIVADAS
  - Backoff Adaptativo: ATIVADO
  - Logging forceRead: ATIVADO
=========================================================
```

**⚠️ SE VOCÊ VER "Versao: 1.13":**
- ❌ CACHE NÃO FOI LIMPO CORRETAMENTE
- ❌ Executar PASSO 1 e 2 novamente
- ❌ Verificar se há múltiplos arquivos `.ex5` no sistema

---

## 🔍 VALIDAÇÃO ADICIONAL

### Verificar Múltiplos Arquivos .ex5

**Comando PowerShell:**
```powershell
Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" | Select-Object FullName, LastWriteTime, Length
```

**Resultado Esperado:**
- Apenas **1** arquivo `.ex5`
- Data de modificação: **AGORA**

**Se houver múltiplos arquivos:**
- Deletar TODOS manualmente
- Recompilar EA
- Validar novamente

---

## 📊 CHECKLIST DE VALIDAÇÃO

Marque cada item após completar:

### Pré-Compilação
- [ ] MT5 Terminal fechado completamente
- [ ] MetaEditor fechado
- [ ] Processos `terminal64.exe` e `metaeditor64.exe` finalizados
- [ ] Script `limpar_cache_mt5.ps1` executado
- [ ] Nenhum arquivo `.ex5` restante no sistema

### Compilação
- [ ] MetaEditor aberto (sem MT5)
- [ ] Arquivo `SamsungGlobalMarket_EA.mq5` aberto
- [ ] Versão no código: `#property version "1.15"`
- [ ] Compilação: 0 erros, 0 warnings
- [ ] MetaEditor fechado

### Validação
- [ ] Apenas 1 arquivo `.ex5` com data atual
- [ ] MT5 Terminal aberto
- [ ] EA anexado ao gráfico
- [ ] Log mostra "Versao: 1.15"
- [ ] Log mostra "Timeout PCA otimizado: 50ms"
- [ ] Log mostra métricas PCA após handshake

---

## 🚨 TROUBLESHOOTING

### Problema: Logs ainda mostram versão 1.13

**Causas Possíveis:**
1. Cache não foi limpo completamente
2. Múltiplos arquivos `.ex5` em diferentes diretórios
3. MT5 carregou versão antiga antes da compilação

**Solução:**
```powershell
# 1. Fechar MT5 e MetaEditor
Stop-Process -Name terminal64 -Force -ErrorAction SilentlyContinue
Stop-Process -Name metaeditor64 -Force -ErrorAction SilentlyContinue

# 2. Deletar TODOS os arquivos .ex5 manualmente
Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" | Remove-Item -Force

# 3. Aguardar 5 segundos
Start-Sleep -Seconds 5

# 4. Reabrir MetaEditor e compilar
# 5. Verificar data do arquivo .ex5 gerado
# 6. Reabrir MT5
```

### Problema: Múltiplos arquivos .ex5 encontrados

**Solução:**
```powershell
# Listar todos os arquivos
Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" | 
    ForEach-Object {
        Write-Host "Deletando: $($_.FullName)"
        Remove-Item -Path $_.FullName -Force
    Write-Host "  [OK] Deletado"
    }
```

---

## ✅ CRITÉRIO DE SUCESSO

O protocolo será considerado **BEM-SUCEDIDO** quando:

1. ✅ Logs do EA mostram **"Versao: 1.15"**
2. ✅ Logs mostram **"Timeout PCA otimizado: 50ms"**
3. ✅ Logs mostram **"[PCA METRICS]"** após handshake
4. ✅ HANDSHAKE_ACK é recebido em <500ms
5. ✅ PCA completo em <2 segundos
6. ✅ Heartbeats recebidos a cada ~10 segundos

---

**PROTOCOLO APROVADO PELO CONSELHO CONSULTIVO**  
**Data:** 2025-10-29  
**Versão do Documento:** 1.0

