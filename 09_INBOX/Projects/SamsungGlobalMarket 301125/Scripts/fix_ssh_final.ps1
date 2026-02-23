# Fix SSH Final - Copia chave e testa
Write-Host "=== Fix SSH Final ===" -ForegroundColor Cyan

# Gerar chave no container se não existir
Write-Host "1. Gerando/verificando chave SSH no container..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "if [ ! -f /tmp/airflow_ssh_key ]; then echo '' | ssh-keygen -t rsa -b 4096 -f /tmp/airflow_ssh_key -N ''; fi"
docker exec docker-airflow-worker-1 chmod 600 /tmp/airflow_ssh_key

# Copiar chave pública para Windows
Write-Host "2. Copiando chave publica para Windows..." -ForegroundColor Yellow
$pubKey = docker exec docker-airflow-worker-1 cat /tmp/airflow_ssh_key.pub
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) { New-Item -ItemType Directory -Force -Path $sshDir | Out-Null }
$authKeys = "$sshDir\authorized_keys"
if (Test-Path $authKeys) {
    $content = Get-Content $authKeys -Raw
    if ($content -notmatch [regex]::Escape($pubKey.Split(' ')[1])) {
        Add-Content -Path $authKeys -Value $pubKey
    }
} else {
    Set-Content -Path $authKeys -Value $pubKey
}
icacls "$sshDir" /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
icacls "$authKeys" /grant "${env:USERNAME}:F" | Out-Null

Write-Host "3. Testando conexao SSH..." -ForegroundColor Yellow
$result = docker exec docker-airflow-worker-1 ssh -i /tmp/airflow_ssh_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 Lenovo@host.docker.internal "whoami" 2>&1

if ($result -match "Lenovo") {
    Write-Host "   [OK] SSH funcionando!" -ForegroundColor Green
} else {
    Write-Host "   [AVISO] Teste falhou, mas chave esta configurada" -ForegroundColor Yellow
}

Write-Host "`n=== CONFIGURACAO AIRFLOW ===" -ForegroundColor Cyan
Write-Host "Connection Id: prometheus_executor_host" -ForegroundColor White
Write-Host "Type: SSH | Host: host.docker.internal | Login: Lenovo | Password: (VAZIO)" -ForegroundColor White
Write-Host 'Extra: {"key_file": "/tmp/airflow_ssh_key", "no_host_key_check": true}' -ForegroundColor Cyan

