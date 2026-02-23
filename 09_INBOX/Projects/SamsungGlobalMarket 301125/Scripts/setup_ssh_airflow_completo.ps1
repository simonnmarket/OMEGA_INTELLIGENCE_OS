# Setup SSH completo para Airflow - AUTOMÁTICO
# Run as Administrator

Write-Host "=== Setup SSH Airflow - AUTOMÁTICO ===" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute como Administrador!" -ForegroundColor Red
    exit 1
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$sshKeysDir = Join-Path $projectRoot "Orchestration\Airflow\docker\ssh_keys"
$sshKeyFile = Join-Path $sshKeysDir "airflow_ssh_key"

Write-Host "`n1. Copiando chave SSH para o container..." -ForegroundColor Yellow
try {
    docker cp "${sshKeyFile}" docker-airflow-worker-1:/tmp/airflow_ssh_key 2>&1 | Out-Null
    docker exec docker-airflow-worker-1 chmod 600 /tmp/airflow_ssh_key 2>&1 | Out-Null
    Write-Host "   [OK] Chave copiada e permissões configuradas" -ForegroundColor Green
} catch {
    Write-Host "   [ERRO] Falha ao copiar chave: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Testando conexão SSH..." -ForegroundColor Yellow
$testResult = docker exec docker-airflow-worker-1 ssh -i /tmp/airflow_ssh_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 Lenovo@host.docker.internal "whoami" 2>&1

if ($testResult -match "Lenovo") {
    Write-Host "   [OK] SSH funcionando! Conexão estabelecida." -ForegroundColor Green
} else {
    Write-Host "   [AVISO] Teste SSH falhou, mas configuração básica está pronta" -ForegroundColor Yellow
    Write-Host "   Resposta: $testResult" -ForegroundColor Gray
}

Write-Host "`n=== CONFIGURAÇÃO NO AIRFLOW UI ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vá em: http://localhost:8080 > Admin > Connections" -ForegroundColor White
Write-Host ""
Write-Host "Conexão: prometheus_executor_host" -ForegroundColor Yellow
Write-Host "  Connection Type: SSH" -ForegroundColor White
Write-Host "  Host: host.docker.internal" -ForegroundColor White
Write-Host "  Login: Lenovo" -ForegroundColor White
Write-Host "  Password: (VAZIO)" -ForegroundColor White
Write-Host "  Port: 22" -ForegroundColor White
Write-Host "  Extra:" -ForegroundColor White
Write-Host '    {"key_file": "/tmp/airflow_ssh_key", "no_host_key_check": true}' -ForegroundColor Cyan
Write-Host ""
Write-Host "=== PROXIMO PASSO ===" -ForegroundColor Cyan
Write-Host "1. Configure a conexao no Airflow UI (acima)" -ForegroundColor White
Write-Host "2. Teste a DAG: prometheus_mt5_executor" -ForegroundColor White
Write-Host ""

