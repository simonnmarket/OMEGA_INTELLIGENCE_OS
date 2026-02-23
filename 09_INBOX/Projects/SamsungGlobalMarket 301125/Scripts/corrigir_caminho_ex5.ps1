# SCRIPT PARA CORRIGIR CAMINHO DO ARQUIVO .EX5
# Projeto Prometheus v3.0.0 | Samsung Global Market

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "CORRECAO DE CAMINHO DO ARQUIVO .EX5" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

$MT5Path = "$env:APPDATA\MetaQuotes"
$caminhoErrado = "$MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket\SamsungGlobalMarket\SamsungGlobalMarket_EA.ex5"
$caminhoCorreto = "$MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.ex5"

Write-Host "[PROBLEMA IDENTIFICADO]" -ForegroundColor Yellow
Write-Host "  Arquivo .ex5 esta no caminho ERRADO (subpasta)" -ForegroundColor Red
Write-Host "  MT5 busca primeiro no caminho CORRETO (Experts\)" -ForegroundColor Yellow
Write-Host "  Se nao encontra, carrega versao antiga ou outro arquivo" -ForegroundColor Yellow
Write-Host ""

# Encontrar todos os arquivos .ex5
Write-Host "[ACAO] Procurando arquivos .ex5..." -ForegroundColor Cyan
$todosEx5 = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($todosEx5.Count -eq 0) {
    Write-Host "  [OK] Nenhum arquivo .ex5 encontrado" -ForegroundColor Green
    Write-Host "  [INFO] Prossiga com a recompilacao" -ForegroundColor Cyan
    exit 0
}

Write-Host "  [INFO] Encontrados $($todosEx5.Count) arquivo(s) .ex5" -ForegroundColor Yellow
Write-Host ""

# Deletar TODOS os arquivos .ex5
Write-Host "[ACAO] Deletando TODOS os arquivos .ex5 encontrados..." -ForegroundColor Cyan
$todosEx5 | ForEach-Object {
    Write-Host "  Deletando: $($_.FullName)" -ForegroundColor Gray
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Todos os arquivos .ex5 foram deletados" -ForegroundColor Green
Write-Host ""

# Verificar se pasta Experts existe
$pastaExperts = "$MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts"
if (-not (Test-Path $pastaExperts)) {
    Write-Host "[ERRO] Pasta Experts nao encontrada: $pastaExperts" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Pasta Experts existe: $pastaExperts" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "PROXIMOS PASSOS" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""
Write-Host "1. FECHAR MT5 COMPLETAMENTE (verificar Task Manager)" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Abrir APENAS MetaEditor (sem MT5)" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Abrir arquivo fonte:" -ForegroundColor Cyan
Write-Host "   $MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5" -ForegroundColor White
Write-Host ""
Write-Host "4. Verificar configuracoes de compilacao:" -ForegroundColor Cyan
Write-Host "   - Menu: Tools -> Options -> Compiler" -ForegroundColor White
Write-Host "   - Verificar que Output Directory esta configurado corretamente" -ForegroundColor White
Write-Host "   - OU simplesmente: Salvar arquivo antes de compilar (Ctrl+S)" -ForegroundColor White
Write-Host ""
Write-Host "5. Compilar (F7) - Aguardar: 0 error(s), 0 warning(s)" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Verificar que arquivo foi gerado em:" -ForegroundColor Cyan
Write-Host "   $caminhoCorreto" -ForegroundColor White
Write-Host ""
Write-Host "7. SE arquivo foi gerado em subpasta:" -ForegroundColor Yellow
Write-Host "   - Copiar arquivo manualmente para pasta Experts\" -ForegroundColor White
Write-Host "   - Deletar subpasta SamsungGlobalMarket\" -ForegroundColor White
Write-Host ""
Write-Host "8. Fechar MetaEditor" -ForegroundColor Cyan
Write-Host ""
Write-Host "9. Abrir MT5 e anexar EA" -ForegroundColor Cyan
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host ""

# Verificar novamente
Start-Sleep -Seconds 1
$verificacao = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue
if ($verificacao.Count -eq 0) {
    Write-Host "[OK] Cache limpo! Nenhum arquivo .ex5 restante" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Ainda existem $($verificacao.Count) arquivo(s) .ex5" -ForegroundColor Yellow
}

Write-Host ""

