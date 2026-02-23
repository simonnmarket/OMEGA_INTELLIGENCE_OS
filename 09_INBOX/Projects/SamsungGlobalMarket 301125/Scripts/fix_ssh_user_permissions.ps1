# Fix SSH User Permissions
# Run as Administrator

Write-Host "=== Fixing SSH User Permissions ===" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Botao direito no PowerShell > Executar como Administrador" -ForegroundColor Yellow
    exit 1
}

$sshUsername = "SSHUser"

# Check if user exists
$user = Get-LocalUser -Name $sshUsername -ErrorAction SilentlyContinue
if (-not $user) {
    Write-Host "ERRO: Usuario $sshUsername nao existe!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\Scripts\create_ssh_user.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Usuario $sshUsername encontrado. Configurando permissoes..." -ForegroundColor Yellow

# Enable user account
Enable-LocalUser -Name $sshUsername
Write-Host "  [OK] Usuario habilitado" -ForegroundColor Green

# Set password to never expire
Set-LocalUser -Name $sshUsername -PasswordNeverExpires $true
Write-Host "  [OK] Senha configurada para nao expirar" -ForegroundColor Green

# Grant "Allow log on locally" right (SeInteractiveLogonRight)
try {
    $tmpPath = [System.IO.Path]::GetTempFileName()
    secedit /export /cfg $tmpPath /quiet | Out-Null
    $content = Get-Content $tmpPath
    
    # Find SeInteractiveLogonRight line
    $interactiveLogonLine = $content | Where-Object { $_ -match "SeInteractiveLogonRight" }
    
    if ($interactiveLogonLine) {
        # Add SSHUser to the list if not already present
        if ($interactiveLogonLine -notmatch $sshUsername) {
            $newLine = $interactiveLogonLine.TrimEnd() + ",*$sshUsername"
            $content = $content -replace [regex]::Escape($interactiveLogonLine), $newLine
            $content | Set-Content $tmpPath
            
            secedit /configure /db "$env:windir\security\local.sdb" /cfg $tmpPath /areas USER_RIGHTS /quiet | Out-Null
            Write-Host "  [OK] Permissao 'Allow log on locally' concedida" -ForegroundColor Green
        } else {
            Write-Host "  [OK] Permissao 'Allow log on locally' ja concedida" -ForegroundColor Green
        }
    }
    Remove-Item $tmpPath -ErrorAction SilentlyContinue
} catch {
    Write-Host "  [AVISO] Nao foi possivel configurar 'Allow log on locally' via secedit: $_" -ForegroundColor Yellow
}

# Add to Remote Desktop Users group
try {
    $rdpGroup = Get-LocalGroup -Name "Remote Desktop Users" -ErrorAction SilentlyContinue
    if ($rdpGroup) {
        $members = Get-LocalGroupMember -Group "Remote Desktop Users" -ErrorAction SilentlyContinue
        $isMember = $members | Where-Object { $_.Name -like "*$sshUsername" }
        if (-not $isMember) {
            Add-LocalGroupMember -Group "Remote Desktop Users" -Member $sshUsername -ErrorAction Stop
            Write-Host "  [OK] Usuario adicionado ao grupo 'Remote Desktop Users'" -ForegroundColor Green
        } else {
            Write-Host "  [OK] Usuario ja esta no grupo 'Remote Desktop Users'" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  [AVISO] Nao foi possivel adicionar ao grupo 'Remote Desktop Users': $_" -ForegroundColor Yellow
}

# Check sshd_config for AllowUsers/DenyUsers
$configPath = "C:\ProgramData\ssh\sshd_config"
if (Test-Path $configPath) {
    $content = Get-Content $configPath -Raw
    
    # Remove DenyUsers if it contains SSHUser
    if ($content -match "(?m)^DenyUsers\s+.*$sshUsername") {
        Write-Host "  [CORRIGINDO] Removendo $sshUsername de DenyUsers no sshd_config..." -ForegroundColor Yellow
        $content = $content -replace "(?m)^DenyUsers\s+.*$sshUsername.*", "# DenyUsers # Removed $sshUsername for SSH access"
        $content | Set-Content $configPath -Encoding UTF8 -NoNewline
        Write-Host "  [OK] sshd_config atualizado" -ForegroundColor Green
    }
    
    # Ensure AllowUsers includes SSHUser (or remove it to allow all)
    if ($content -match "(?m)^AllowUsers") {
        $allowUsersLine = [regex]::Match($content, "(?m)^AllowUsers\s+(.+)").Groups[1].Value
        if ($allowUsersLine -notmatch $sshUsername) {
            Write-Host "  [CORRIGINDO] Adicionando $sshUsername a AllowUsers no sshd_config..." -ForegroundColor Yellow
            $content = $content -replace "(?m)^AllowUsers\s+.*", "AllowUsers $allowUsersLine $sshUsername"
            $content | Set-Content $configPath -Encoding UTF8 -NoNewline
            Write-Host "  [OK] sshd_config atualizado" -ForegroundColor Green
        }
    }
    
    # Restart SSH service
    Write-Host "`nReiniciando servico SSH..." -ForegroundColor Yellow
    Restart-Service sshd -ErrorAction Stop
    Write-Host "  [OK] Servico SSH reiniciado" -ForegroundColor Green
}

# Verify user account status
Write-Host "`n=== Status do Usuario ===" -ForegroundColor Cyan
$user = Get-LocalUser -Name $sshUsername
Write-Host "  Nome: $($user.Name)" -ForegroundColor White
Write-Host "  Enabled: $($user.Enabled)" -ForegroundColor $(if ($user.Enabled) { 'Green' } else { 'Red' })
Write-Host "  PasswordNeverExpires: $($user.PasswordNeverExpires)" -ForegroundColor White

# Test if user can be found in system
Write-Host "`n=== Teste Manual Necessario ===" -ForegroundColor Yellow
Write-Host "Agora teste o SSH:" -ForegroundColor White
Write-Host "  ssh ${sshUsername}@127.0.0.1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se ainda nao funcionar, verifique os logs do SSH:" -ForegroundColor Yellow
Write-Host "  Get-EventLog -LogName Application -Source sshd -Newest 10" -ForegroundColor Cyan

