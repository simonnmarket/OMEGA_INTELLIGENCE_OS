# SCRIPT DE LIMPEZA TOTAL DE CACHE MT5
# Projeto Prometheus v3.0.0 | Samsung Global Market
# Protocolo: Omega TIER-0

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "LIMPEZA TOTAL DE CACHE MT5 - PROTOCOLO CIENTIFICO" -ForegroundColor Yellow
Write-Host "Projeto Prometheus v3.0.0 | Samsung Global Market" -ForegroundColor White
Write-Host "==========================================================================="
Write-Host ""

# Verificar processos MT5
Write-Host "[ETAPA 1/4] Verificando processos MT5 em execucao..." -ForegroundColor Cyan

$processosMT5 = Get-Process | Where-Object {$_.Name -like "*terminal*" -or $_.Name -like "*metaeditor*"} -ErrorAction SilentlyContinue

if ($processosMT5) {
    Write-Host "  [AVISO] Encontrados processos MT5 ativos:" -ForegroundColor Yellow
    $processosMT5 | ForEach-Object {
        Write-Host "    - $($_.Name) (PID: $($_.Id))" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "  [ACAO NECESSARIA] Fechar MT5 completamente antes de continuar" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Pressione qualquer tecla quando tiver fechado o MT5..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
    
    # Verificar novamente
    Start-Sleep -Seconds 2
    $processosMT5 = Get-Process | Where-Object {$_.Name -like "*terminal*" -or $_.Name -like "*metaeditor*"} -ErrorAction SilentlyContinue
    if ($processosMT5) {
        Write-Host "  [FORCANDO] Fechando processos remanescentes..." -ForegroundColor Yellow
        Stop-Process -Name "terminal64" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "metaeditor64" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

Write-Host "  [OK] Nenhum processo MT5 ativo" -ForegroundColor Green
Write-Host ""

# Identificar arquivos .ex5
Write-Host "[ETAPA 2/4] Identificando arquivos .ex5..." -ForegroundColor Cyan

$MT5Path = "$env:APPDATA\MetaQuotes"
$ex5Files = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($ex5Files.Count -eq 0) {
    Write-Host "  [INFO] Nenhum arquivo .ex5 encontrado (ok para prosseguir)" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Encontrados $($ex5Files.Count) arquivo(s) .ex5:" -ForegroundColor Yellow
    $ex5Files | ForEach-Object {
        $age = (Get-Date) - $_.LastWriteTime
        $ageMinutes = [math]::Round($age.TotalMinutes, 1)
        Write-Host "    - $($_.FullName)" -ForegroundColor White
        Write-Host "      Modificado: $($_.LastWriteTime) ($ageMinutes minutos atras)" -ForegroundColor Gray
    }
}

Write-Host ""

# Deletar arquivos .ex5
Write-Host "[ETAPA 3/4] Deletando TODOS os arquivos .ex5..." -ForegroundColor Cyan

if ($ex5Files.Count -gt 0) {
    $ex5Files | Remove-Item -Force -Verbose
    Write-Host "  [OK] $($ex5Files.Count) arquivo(s) deletado(s)" -ForegroundColor Green
} else {
    Write-Host "  [OK] Nenhum arquivo para deletar" -ForegroundColor Green
}

Write-Host ""

# Verificar resultado
Write-Host "[ETAPA 4/4] Validando limpeza..." -ForegroundColor Cyan

$ex5FilesRestantes = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($ex5FilesRestantes.Count -eq 0) {
    Write-Host "  [OK] Cache limpo com sucesso!" -ForegroundColor Green
    Write-Host "  [OK] Nenhum arquivo .ex5 restante" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] Ainda existem $($ex5FilesRestantes.Count) arquivo(s) .ex5" -ForegroundColor Yellow
    Write-Host "  Tentando deletar novamente..." -ForegroundColor Yellow
    $ex5FilesRestantes | Remove-Item -Force
    Start-Sleep -Seconds 1
    
    $verificacaoFinal = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue
    if ($verificacaoFinal.Count -eq 0) {
        Write-Host "  [OK] Cache limpo!" -ForegroundColor Green
    } else {
        Write-Host "  [ERRO] Nao foi possivel deletar alguns arquivos" -ForegroundColor Red
        Write-Host "  Arquivos restantes:" -ForegroundColor Yellow
        $verificacaoFinal | ForEach-Object {
            Write-Host "    - $($_.FullName)" -ForegroundColor White
        }
    }
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "PROXIMOS PASSOS" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""
Write-Host "1. Abrir MetaEditor (SEM abrir MT5 ainda)" -ForegroundColor Cyan
Write-Host "2. Abrir arquivo: SamsungGlobalMarket_EA.mq5" -ForegroundColor White
Write-Host "3. Verificar versao no codigo (deve ser 1.15)" -ForegroundColor White
Write-Host "4. Compilar (F7) - Aguardar: 0 error(s), 0 warning(s)" -ForegroundColor White
Write-Host "5. Fechar MetaEditor" -ForegroundColor White
Write-Host "6. Abrir MT5 Terminal" -ForegroundColor White
Write-Host "7. Anexar EA ao grafico" -ForegroundColor White
Write-Host "8. Validar log mostra versao 1.15 com metricas PCA" -ForegroundColor Green
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host ""

