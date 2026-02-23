# Fix SSH Configuration - Enable Password Authentication
# Run as Administrator

Write-Host "=== Fixing SSH Configuration ===" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Botao direito no PowerShell > Executar como Administrador" -ForegroundColor Yellow
    exit 1
}

# Backup original config
$configPath = "C:\ProgramData\ssh\sshd_config"
if (Test-Path $configPath) {
    Copy-Item $configPath "$configPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -Force
    Write-Host "Backup criado: $configPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -ForegroundColor Green
} else {
    Write-Host "ERRO: Arquivo sshd_config nao encontrado em $configPath" -ForegroundColor Red
    exit 1
}

# Read config
$content = Get-Content $configPath -Raw

# Ensure PasswordAuthentication is enabled (not commented)
$content = $content -replace '(?m)^#?PasswordAuthentication\s+(yes|no).*$', 'PasswordAuthentication yes'
if ($content -notmatch '(?m)^PasswordAuthentication\s+yes') {
    $content += "`nPasswordAuthentication yes"
}

# Ensure PubkeyAuthentication is enabled (not commented)
$content = $content -replace '(?m)^#?PubkeyAuthentication\s+(yes|no).*$', 'PubkeyAuthentication yes'
if ($content -notmatch '(?m)^PubkeyAuthentication\s+yes') {
    $content += "`nPubkeyAuthentication yes"
}

# Remove any DenyUsers or AllowUsers that might block the current user
$currentUser = $env:USERNAME
$content = $content -replace "(?m)^DenyUsers\s+.*$currentUser.*", '# DenyUsers removed for SSH access'
$content = $content -replace "(?m)^AllowUsers\s+.*(?!.*$currentUser)", "# AllowUsers # User $currentUser should be able to connect"

# Write back
$content | Set-Content $configPath -Encoding UTF8 -NoNewline

Write-Host "`nConfiguracao atualizada!" -ForegroundColor Green

# Verify
Write-Host "`nVerificando configuração:" -ForegroundColor Yellow
Get-Content $configPath | Select-String -Pattern 'PasswordAuthentication|PubkeyAuthentication|DenyUsers|AllowUsers'

# Restart SSH service
Write-Host "`nReiniciando serviço SSH..." -ForegroundColor Yellow
try {
    Restart-Service sshd -ErrorAction Stop
    Write-Host "Serviço SSH reiniciado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao reiniciar serviço SSH: $_" -ForegroundColor Red
    exit 1
}

# Verify service status
Write-Host "`nStatus do serviço SSH:" -ForegroundColor Yellow
$service = Get-Service sshd
Write-Host "  Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq 'Running') { 'Green' } else { 'Red' })

Write-Host "`n=== IMPORTANTE: PIN vs SENHA ===" -ForegroundColor Cyan
Write-Host "O SSH no Windows NAO funciona com PIN!" -ForegroundColor Yellow
Write-Host "Você precisa de uma SENHA da conta local." -ForegroundColor Yellow
Write-Host ""
Write-Host "Para configurar uma senha local:" -ForegroundColor Yellow
Write-Host "1. Vá em Configurações > Contas > Opções de Entrada" -ForegroundColor White
Write-Host "2. Clique em 'Senha' e defina uma senha" -ForegroundColor White
Write-Host "3. Use ESSA SENHA (não o PIN) para o SSH" -ForegroundColor White
Write-Host ""
Write-Host "Agora teste: ssh $currentUser@127.0.0.1" -ForegroundColor Cyan
Write-Host "(Use a SENHA, não o PIN!)" -ForegroundColor Yellow

