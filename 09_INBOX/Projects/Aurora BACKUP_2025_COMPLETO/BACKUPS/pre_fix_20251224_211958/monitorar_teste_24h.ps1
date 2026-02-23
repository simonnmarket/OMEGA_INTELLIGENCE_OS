# ============================================================================
# AURORA v5.1 - MONITORAMENTO DO TESTE 24H
# ============================================================================
# Script para monitorar o progresso do teste de estresse de 24 horas
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "AURORA v5.1 - MONITORAMENTO TESTE 24H" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar processo Python do Aurora
$auroraProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*AURORA_FINAL_EXECUCAO_AIC_V5.1.py*" -or
    $_.Path -like "*Aurora*"
}

if ($auroraProcess) {
    Write-Host "[OK] Processo Aurora encontrado:" -ForegroundColor Green
    Write-Host "   PID: $($auroraProcess.Id)" -ForegroundColor Yellow
    Write-Host "   Iniciado: $($auroraProcess.StartTime)" -ForegroundColor Yellow
    Write-Host "   CPU: $([math]::Round($auroraProcess.CPU, 2))s" -ForegroundColor Yellow
    Write-Host "   Memória: $([math]::Round($auroraProcess.WS/1MB, 2)) MB" -ForegroundColor Yellow
} else {
    Write-Host "[AVISO] Processo Aurora não encontrado" -ForegroundColor Yellow
    Write-Host "   Verificando se está rodando em background..." -ForegroundColor Yellow
}

Write-Host ""

# Verificar arquivos de relatório gerados
Write-Host "[INFO] Verificando relatórios gerados..." -ForegroundColor Cyan
$reports = Get-ChildItem -Path . -Filter "aurora_aic_*" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5

if ($reports) {
    Write-Host "[OK] Relatórios encontrados:" -ForegroundColor Green
    foreach ($report in $reports) {
        $age = (Get-Date) - $report.LastWriteTime
        Write-Host "   • $($report.Name)" -ForegroundColor Yellow
        Write-Host "     Modificado: $($report.LastWriteTime) ($([math]::Round($age.TotalMinutes, 1)) minutos atrás)" -ForegroundColor Gray
        Write-Host "     Tamanho: $([math]::Round($report.Length/1KB, 2)) KB" -ForegroundColor Gray
    }
} else {
    Write-Host "[AVISO] Nenhum relatório encontrado ainda" -ForegroundColor Yellow
}

Write-Host ""

# Verificar logs recentes
Write-Host "[INFO] Últimas linhas dos logs (se disponível)..." -ForegroundColor Cyan
$latestReport = Get-ChildItem -Path . -Filter "aurora_aic_report_*.txt" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if ($latestReport) {
    Write-Host "[OK] Lendo: $($latestReport.Name)" -ForegroundColor Green
    Write-Host ""
    Get-Content $latestReport.FullName -Tail 20 -ErrorAction SilentlyContinue | 
        ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "[AVISO] Nenhum log de relatório encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Para monitoramento contínuo, execute este script a cada hora" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

