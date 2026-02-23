# MEMORY_ID: VALIDATE_SSH_AIRFLOW_SETUP
# TIMESTAMP: 2025-11-13T23:00:00+01:00
# AUTHOR: Cursor_Omega
<#
.SYNOPSIS
    Script de validação da configuração SSH + Airflow + MT5 Executor.

.DESCRIPTION
    Verifica:
    - OpenSSH Server rodando
    - Firewall configurado
    - Script executor existente
    - Porta 63000 disponível
    - SSH acessível localmente
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Validação SSH + Airflow + MT5 Executor ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar serviço SSH
Write-Host "[1/5] Verificando OpenSSH Server..." -ForegroundColor Yellow
$sshService = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($sshService -and $sshService.Status -eq "Running") {
    Write-Host "  ✅ SSH Server está rodando" -ForegroundColor Green
} else {
    Write-Host "  ❌ SSH Server NÃO está rodando" -ForegroundColor Red
    Write-Host "  Execute: Start-Service sshd" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar firewall
Write-Host "[2/5] Verificando Firewall (porta 22)..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "SSH Server inbound" -ErrorAction SilentlyContinue
if ($firewallRule -and $firewallRule.Enabled -eq $true) {
    Write-Host "  ✅ Regra de firewall configurada" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Regra de firewall não encontrada" -ForegroundColor Yellow
    Write-Host "  Execute: New-NetFirewallRule -DisplayName 'SSH Server inbound' -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow" -ForegroundColor Yellow
}

# 3. Verificar script executor
Write-Host "[3/5] Verificando script executor..." -ForegroundColor Yellow
$scriptPath = "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\prometheus_mt5_executor.py"
if (Test-Path $scriptPath) {
    Write-Host "  ✅ Script encontrado: $scriptPath" -ForegroundColor Green
} else {
    Write-Host "  ❌ Script NÃO encontrado: $scriptPath" -ForegroundColor Red
    Write-Host "  Verifique o caminho do script no Airflow DAG" -ForegroundColor Yellow
    exit 1
}

# 4. Verificar porta 63000
Write-Host "[4/5] Verificando porta 63000 (métricas Prometheus)..." -ForegroundColor Yellow
$port63000 = Get-NetTCPConnection -LocalPort 63000 -ErrorAction SilentlyContinue
if ($port63000) {
    Write-Host "  ⚠️  Porta 63000 está em uso (executor pode estar rodando)" -ForegroundColor Yellow
    Write-Host "  Se necessário, pare o executor antes de iniciar novo processo" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Porta 63000 disponível" -ForegroundColor Green
}

# 5. Testar SSH local
Write-Host "[5/5] Testando SSH local..." -ForegroundColor Yellow
$currentUser = $env:USERNAME
try {
    $sshTest = ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no "$currentUser@127.0.0.1" "echo 'SSH_OK'" 2>&1
    if ($sshTest -match "SSH_OK") {
        Write-Host "  ✅ SSH funcionando localmente" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  SSH retornou: $sshTest" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  Erro ao testar SSH: $_" -ForegroundColor Yellow
    Write-Host "  Execute manualmente: ssh $currentUser@127.0.0.1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Validação Concluída ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure a conexão SSH no Airflow UI (Admin → Connections)" -ForegroundColor White
Write-Host "2. Configure PROMETHEUS_MT5_EXECUTOR_COMMAND no .env do Airflow" -ForegroundColor White
Write-Host "3. Ative a DAG 'prometheus_mt5_executor' no Airflow UI" -ForegroundColor White
Write-Host ""
Write-Host "Veja: Documentation/09_Guias_Manuais/GUIA_CONFIGURACAO_AIRFLOW_SSH_MT5.md" -ForegroundColor Cyan

