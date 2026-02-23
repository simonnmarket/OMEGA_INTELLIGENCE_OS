# Forçar chave RSA limpa e garantir que Paramiko use apenas RSA
Write-Host "=== Forçar Chave RSA Limpa ===" -ForegroundColor Cyan

Write-Host "1. Removendo TODAS as chaves antigas..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "rm -f /tmp/airflow_ssh_key* /tmp/ssh_keys/* /root/.ssh/* 2>&1" | Out-Null

Write-Host "2. Gerando chave RSA 2048 NOVA..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "mkdir -p /tmp/ssh_keys && ssh-keygen -t rsa -b 2048 -f /tmp/ssh_keys/airflow_ssh_key -N '' -C 'airflow@prometheus' 2>&1"
docker exec docker-airflow-worker-1 chmod 600 /tmp/ssh_keys/airflow_ssh_key
docker exec docker-airflow-worker-1 chmod 644 /tmp/ssh_keys/airflow_ssh_key.pub

Write-Host "3. Verificando formato da chave..." -ForegroundColor Yellow
$keyType = docker exec docker-airflow-worker-1 bash -c "head -n 1 /tmp/ssh_keys/airflow_ssh_key"
Write-Host "   Tipo de chave: $keyType" -ForegroundColor White

if ($keyType -match "BEGIN RSA PRIVATE KEY" -or $keyType -match "BEGIN OPENSSH PRIVATE KEY") {
    Write-Host "   [OK] Chave RSA valida!" -ForegroundColor Green
} else {
    Write-Host "   [ERRO] Chave nao e RSA!" -ForegroundColor Red
    exit 1
}

Write-Host "4. Copiando chave publica para Windows..." -ForegroundColor Yellow
$pubKey = docker exec docker-airflow-worker-1 cat /tmp/ssh_keys/airflow_ssh_key.pub

# Limpar authorized_keys completamente e adicionar apenas a nova chave
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
}

$authKeys = "$sshDir\authorized_keys"
Set-Content -Path $authKeys -Value $pubKey -Encoding UTF8
icacls "$sshDir" /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
icacls "$authKeys" /grant "${env:USERNAME}:F" | Out-Null

Write-Host "5. Testando conexao SSH..." -ForegroundColor Yellow
$result = docker exec docker-airflow-worker-1 ssh -i /tmp/ssh_keys/airflow_ssh_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 Lenovo@host.docker.internal "whoami" 2>&1

if ($result -match "Lenovo") {
    Write-Host "   [OK] SSH funcionando!" -ForegroundColor Green
} else {
    Write-Host "   [AVISO] Teste falhou: $result" -ForegroundColor Yellow
}

Write-Host "`n6. Limpando cache do Airflow..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "rm -rf /tmp/airflow* /root/.ssh/known_hosts 2>&1" | Out-Null

Write-Host "`n=== CONFIGURACAO AIRFLOW ===" -ForegroundColor Cyan
Write-Host "Chave RSA limpa gerada e configurada." -ForegroundColor White
Write-Host "Extra no Airflow UI (json):" -ForegroundColor Yellow
Write-Host '{"key_file": "/tmp/ssh_keys/airflow_ssh_key", "no_host_key_check": true}' -ForegroundColor Cyan
Write-Host "`nReinicie o Airflow worker e teste novamente:" -ForegroundColor Yellow
Write-Host "  docker-compose -f Orchestration/Airflow/docker/docker-compose.yaml restart airflow-worker" -ForegroundColor Cyan

