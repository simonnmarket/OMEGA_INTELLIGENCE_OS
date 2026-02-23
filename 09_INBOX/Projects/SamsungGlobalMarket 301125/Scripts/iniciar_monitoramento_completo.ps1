# Iniciar monitoramento completo (servidor + monitor)

$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO SISTEMA COMPLETO COM MONITORAMENTO EM TEMPO REAL" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# 1. Parar processos anteriores
Write-Host "[1] Parando processos anteriores..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" | Select-Object -ExpandProperty CommandLine)
    $cmd -like "*server*" -or $cmd -like "*monitor*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  OK" -ForegroundColor Green
Write-Host ""

# 2. Iniciar servidor
Write-Host "[2] Iniciando servidor..." -ForegroundColor Yellow
$serverScript = Join-Path $projectPath "Scripts\iniciar_servidor_com_validacao.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $serverScript -WindowStyle Minimized
Start-Sleep -Seconds 5
Write-Host "  Servidor iniciado em janela separada" -ForegroundColor Green
Write-Host ""

# 3. Verificar servidor
Write-Host "[3] Verificando servidor..." -ForegroundColor Yellow
$proc = Get-Process python -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "  OK - Servidor rodando (PID: $($proc.Id))" -ForegroundColor Green
} else {
    Write-Host "  AVISO - Servidor pode nao ter iniciado ainda" -ForegroundColor Yellow
}
Write-Host ""

# 4. Iniciar monitoramento em tempo real
Write-Host "[4] Iniciando monitoramento em tempo real..." -ForegroundColor Yellow
$monitorScript = Join-Path $projectPath "Scripts\monitor_realtime_background.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $monitorScript -WindowStyle Normal
Write-Host "  Monitoramento iniciado em janela separada" -ForegroundColor Green
Write-Host ""

# 5. Iniciar alerta de 10 minutos sem trades
Write-Host "[5] Iniciando alerta de 10 minutos sem trades..." -ForegroundColor Yellow
$alertaScript = Join-Path $projectPath "Scripts\alerta_10_minutos_sem_trades.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $alertaScript -WindowStyle Normal
Write-Host "  Alerta de 10 minutos ativado em janela separada" -ForegroundColor Green
Write-Host ""

# 5. Instruções
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "SISTEMA INICIADO" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "Janelas abertas:" -ForegroundColor Yellow
Write-Host "  1. Servidor (minimizada)" -ForegroundColor Cyan
Write-Host "  2. Monitoramento em tempo real (visivel)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitoramento:" -ForegroundColor Yellow
Write-Host "  - Verifica servidor a cada 1 segundo" -ForegroundColor White
Write-Host "  - Alerta se servidor parar" -ForegroundColor White
Write-Host "  - Detecta requests antigos (>30s)" -ForegroundColor White
Write-Host "  - Monitora responses acumulados" -ForegroundColor White
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
Write-Host "  logs\monitor_realtime.log - Log completo do monitoramento" -ForegroundColor Cyan
Write-Host "  logs\server_output.txt - Output do servidor" -ForegroundColor Cyan
Write-Host ""
Write-Host "AGORA VOCE PODE REANEXAR A EA - SISTEMA MONITORANDO EM TEMPO REAL" -ForegroundColor Green
Write-Host ""

