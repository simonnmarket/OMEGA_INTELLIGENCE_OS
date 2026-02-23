# Gerar chave SSH limpa (RSA 2048) para Airflow
Write-Host "=== Gerar Chave SSH Limpa ===" -ForegroundColor Cyan

Write-Host "1. Removendo chave antiga do container..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 rm -f /tmp/airflow_ssh_key /tmp/airflow_ssh_key.pub /tmp/ssh_keys/airflow_ssh_key 2>&1 | Out-Null

Write-Host "2. Gerando nova chave RSA 2048..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "ssh-keygen -t rsa -b 2048 -f /tmp/airflow_ssh_key -N '' -C 'airflow@prometheus'"
docker exec docker-airflow-worker-1 chmod 600 /tmp/airflow_ssh_key
docker exec docker-airflow-worker-1 chmod 644 /tmp/airflow_ssh_key.pub

Write-Host "3. Copiando chave publica para Windows..." -ForegroundColor Yellow
$pubKey = docker exec docker-airflow-worker-1 cat /tmp/airflow_ssh_key.pub

# Remover chave antiga do Windows
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
}

$authKeys = "$sshDir\authorized_keys"
if (Test-Path $authKeys) {
    # Remover todas as chaves do airflow
    $content = Get-Content $authKeys -Raw
    $lines = $content -split "`n" | Where-Object { $_ -notmatch "default@e3a52eebf398" -and $_ -notmatch "airflow@prometheus" -and $_ -notmatch "^$" }
    $lines | Set-Content $authKeys -Encoding UTF8
}

# Adicionar nova chave
Add-Content -Path $authKeys -Value $pubKey
icacls "$sshDir" /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
icacls "$authKeys" /grant "${env:USERNAME}:F" | Out-Null

Write-Host "4. Copiando chave para /tmp/ssh_keys no container..." -ForegroundColor Yellow
docker exec docker-airflow-worker-1 bash -c "mkdir -p /tmp/ssh_keys && cp /tmp/airflow_ssh_key /tmp/ssh_keys/ && chmod 600 /tmp/ssh_keys/airflow_ssh_key"

Write-Host "5. Testando conexao SSH..." -ForegroundColor Yellow
$result = docker exec docker-airflow-worker-1 ssh -i /tmp/ssh_keys/airflow_ssh_key -o StrictHostKeyChecking=no -o ConnectTimeout=5 Lenovo@host.docker.internal "whoami" 2>&1

if ($result -match "Lenovo") {
    Write-Host "   [OK] SSH funcionando com chave RSA limpa!" -ForegroundColor Green
} else {
    Write-Host "   [AVISO] Teste falhou: $result" -ForegroundColor Yellow
}

Write-Host "`n=== CONFIGURACAO AIRFLOW ===" -ForegroundColor Cyan
Write-Host "A chave foi gerada e configurada corretamente." -ForegroundColor White
Write-Host "Nao precisa alterar nada no Airflow UI - a conexao deve funcionar agora." -ForegroundColor White
Write-Host "`nTeste a DAG novamente no Airflow UI." -ForegroundColor Yellow

