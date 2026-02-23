# 🔧 SOLUÇÃO DEFINITIVA - PROBLEMA DE VERSÃO EA

**Problema:** MT5 continua carregando versão 1.02 mesmo após edição do código para 1.04

---

## 🔍 CAUSA RAIZ

O MetaTrader 5 pode estar carregando o arquivo `.ex5` compilado de um dos seguintes locais:
1. Cache do terminal
2. Diretório diferente de Experts
3. Arquivo `.ex5` antigo não foi sobrescrito

---

## ✅ SOLUÇÃO PASSO A PASSO

### **Método 1: Forçar Recompilação Limpa (RECOMENDADO)**

1. **Fechar MT5 completamente**
   - Fechar todos os gráficos
   - Fechar MT5 Terminal

2. **Abrir MetaEditor separadamente**
   - Não usar F4 no MT5
   - Abrir MetaEditor como programa independente

3. **Localizar arquivo .mq5**
   - Navegar até: `C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\`
   - Abrir: `SamsungGlobalMarket_EA.mq5`

4. **Verificar versão no código**
   - Linha 95 deve mostrar: `Print("Versao: 1.04");`
   - Linha 8 deve mostrar: `#property version "1.04"`

5. **COMPILAR (F7)**
   - Aguardar: `0 error(s), 0 warning(s)`

6. **DELETAR arquivo .ex5 antigo manualmente**
   - No Windows Explorer, navegar até o diretório acima
   - Deletar arquivo: `SamsungGlobalMarket_EA.ex5` (se existir)
   - Isso força recompilação do zero

7. **COMPILAR NOVAMENTE (F7)**
   - Isso criará um novo arquivo .ex5

8. **Fechar MetaEditor**

9. **Abrir MT5 Terminal**

10. **Anexar EA ao gráfico**
    - Arrastar EA para o gráfico
    - Verificar logs: `Versao: 1.04`

---

### **Método 2: Verificar Múltiplos Diretórios**

O MT5 pode ter múltiplos diretórios de Experts. Verificar todos:

```powershell
# Procurar todos os arquivos .ex5 do EA
Get-ChildItem -Path "$env:APPDATA\MetaQuotes\Terminal" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" | Select-Object FullName, LastWriteTime
```

**Ação:** Deletar TODOS os arquivos `.ex5` encontrados e recompilar.

---

### **Método 3: Verificar Código Fonte**

Confirmar que o arquivo `.mq5` realmente tem versão 1.04:

```powershell
# Verificar versão no código
Select-String -Path "SamsungGlobalMarket_EA.mq5" -Pattern "Versao: 1.04"
Select-String -Path "SamsungGlobalMarket_EA.mq5" -Pattern '#property version.*"1.04"'
```

Se não encontrar, o arquivo precisa ser atualizado.

---

## 🔬 DIAGNÓSTICO AUTOMATIZADO

Execute este script PowerShell para diagnóstico:

```powershell
$eaPath = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts"
$mq5File = Join-Path $eaPath "SamsungGlobalMarket_EA.mq5"
$ex5File = Join-Path $eaPath "SamsungGlobalMarket_EA.ex5"

Write-Host "Verificando arquivo .mq5:" -ForegroundColor Cyan
if (Test-Path $mq5File) {
    $mq5Content = Get-Content $mq5File -Raw
    if ($mq5Content -match 'Versao: 1\.04') {
        Write-Host "[OK] Arquivo .mq5 tem versao 1.04" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Arquivo .mq5 NAO tem versao 1.04" -ForegroundColor Red
    }
} else {
    Write-Host "[ERRO] Arquivo .mq5 nao encontrado" -ForegroundColor Red
}

Write-Host "`nVerificando arquivo .ex5:" -ForegroundColor Cyan
if (Test-Path $ex5File) {
    $ex5Info = Get-Item $ex5File
    Write-Host "Arquivo .ex5 encontrado:" -ForegroundColor Yellow
    Write-Host "  Local: $($ex5Info.FullName)"
    Write-Host "  Modificado: $($ex5Info.LastWriteTime)"
    Write-Host "  Tamanho: $($ex5Info.Length) bytes"
} else {
    Write-Host "[INFO] Arquivo .ex5 nao encontrado (precisa compilar)" -ForegroundColor Yellow
}
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

Após recompilação:

- [ ] MetaEditor mostra `0 error(s), 0 warning(s)`
- [ ] Arquivo `.ex5` foi gerado/atualizado
- [ ] Data/hora do `.ex5` é recente
- [ ] MT5 foi fechado e reaberto
- [ ] EA foi removido e anexado novamente
- [ ] Log mostra `Versao: 1.04` (não 1.02)

---

## ⚠️ SE AINDA MOSTRAR 1.02

1. **Verificar se há múltiplos arquivos .mq5:**
   ```powershell
   Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.mq5" | Select-Object FullName
   ```

2. **Editar TODOS os arquivos encontrados** para versão 1.04

3. **Compilar TODOS**

4. **Deletar TODOS os .ex5 antigos**

5. **Reiniciar MT5 completamente**

---

## 🎯 OBJETIVO FINAL

Garantir que quando o EA for anexado, o log mostre:
```
Versao: 1.04  ← CRÍTICO
```

Apenas então poderemos iniciar Paper Trading com segurança.

