# ============================================================================
# SOLUÇÃO AGRESSIVA - FORÇAR COMPILAÇÃO v1.04
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "SOLUCAO AGRESSIVA - FORCAR COMPILACAO EA v1.04" -ForegroundColor Cyan
Write-Host "==========================================================================="
Write-Host ""

# 1. Deletar TODOS os arquivos .ex5 do EA
Write-Host "[1/5] Deletando TODOS os arquivos .ex5 antigos..." -ForegroundColor Yellow
$ex5Files = Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue
if ($ex5Files) {
    foreach ($file in $ex5Files) {
        Write-Host "  Deletando: $($file.FullName)" -ForegroundColor Gray
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] $($ex5Files.Count) arquivo(s) .ex5 deletado(s)" -ForegroundColor Green
} else {
    Write-Host "[OK] Nenhum arquivo .ex5 encontrado" -ForegroundColor Green
}
Write-Host ""

# 2. Verificar arquivo .mq5
Write-Host "[2/5] Verificando arquivo .mq5..." -ForegroundColor Yellow
$mq5Path = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5"
if (Test-Path $mq5Path) {
    $mq5Content = Get-Content $mq5Path -Raw
    if ($mq5Content -match 'Versao: 1\.04') {
        Write-Host "[OK] Arquivo .mq5 tem versao 1.04" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Arquivo .mq5 NAO tem versao 1.04!" -ForegroundColor Red
        Write-Host "  O arquivo precisa ser atualizado manualmente" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[ERRO] Arquivo .mq5 nao encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Verificar processos MT5
Write-Host "[3/5] Verificando processos MT5..." -ForegroundColor Yellow
$mt5Processes = Get-Process | Where-Object {$_.ProcessName -like "*terminal*" -or $_.ProcessName -like "*meta*" -or $_.ProcessName -like "*mt5*"} -ErrorAction SilentlyContinue
if ($mt5Processes) {
    Write-Host "[AVISO] Encontrados $($mt5Processes.Count) processo(s) MT5 rodando:" -ForegroundColor Yellow
    foreach ($proc in $mt5Processes) {
        Write-Host "  - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
    }
    Write-Host "[IMPORTANTE] Fechar TODOS os processos MT5 antes de compilar!" -ForegroundColor Red
} else {
    Write-Host "[OK] Nenhum processo MT5 rodando" -ForegroundColor Green
}
Write-Host ""

# 4. Instruções finais
Write-Host "[4/5] INSTRUCOES FINAIS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. FECHAR TODOS os processos MT5 listados acima" -ForegroundColor Cyan
Write-Host "  2. Abrir MetaEditor SEPARADAMENTE (nao usar F4)" -ForegroundColor Cyan
Write-Host "  3. Abrir arquivo: $mq5Path" -ForegroundColor Cyan
Write-Host "  4. Verificar linha 95 mostra: Versao: 1.04" -ForegroundColor Cyan
Write-Host "  5. COMPILAR (F7) - aguardar: 0 error(s), 0 warning(s)" -ForegroundColor Green
Write-Host "  6. Verificar Navigator: arquivo .ex5 foi criado AGORA" -ForegroundColor Cyan
Write-Host "  7. FECHAR MetaEditor" -ForegroundColor Cyan
Write-Host "  8. Abrir MT5 Terminal" -ForegroundColor Cyan
Write-Host "  9. Anexar EA e VERIFICAR log mostra: Versao: 1.04" -ForegroundColor Green
Write-Host ""

# 5. Verificar se precisa reiniciar
Write-Host "[5/5] SE AINDA NAO FUNCIONAR:" -ForegroundColor Yellow
Write-Host "  - Reiniciar computador (limpa cache completamente)" -ForegroundColor White
Write-Host "  - Após reiniciar, seguir protocolo novamente" -ForegroundColor White
Write-Host ""

Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "SCRIPT CONCLUIDO - SEGUIR INSTRUCOES ACIMA" -ForegroundColor Cyan
Write-Host "==========================================================================="

