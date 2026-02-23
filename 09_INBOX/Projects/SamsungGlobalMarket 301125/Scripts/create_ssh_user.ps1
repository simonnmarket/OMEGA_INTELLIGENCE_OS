# Create SSH User for Airflow Connection
# Run as Administrator

Write-Host "=== Creating SSH User for Airflow ===" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Botao direito no PowerShell > Executar como Administrador" -ForegroundColor Yellow
    exit 1
}

# User details
$sshUsername = "SSHUser"
$sshPassword = Read-Host "Digite uma senha para o usuario SSHUser" -AsSecureString
$passwordConfirm = Read-Host "Confirme a senha" -AsSecureString

# Convert to plain text for comparison
$BSTR1 = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sshPassword)
$plainPassword1 = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR1)
$BSTR2 = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($passwordConfirm)
$plainPassword2 = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR2)

if ($plainPassword1 -ne $plainPassword2) {
    Write-Host "ERRO: As senhas nao coincidem!" -ForegroundColor Red
    exit 1
}

# Check if user already exists
$userExists = Get-LocalUser -Name $sshUsername -ErrorAction SilentlyContinue

if ($userExists) {
    Write-Host "Usuario $sshUsername ja existe. Alterando senha..." -ForegroundColor Yellow
    Set-LocalUser -Name $sshUsername -Password $sshPassword
} else {
    Write-Host "Criando usuario $sshUsername..." -ForegroundColor Yellow
    
    New-LocalUser -Name $sshUsername -Password $sshPassword -Description "SSH user for Airflow MT5 executor" -PasswordNeverExpires -UserMayNotChangePassword:$false
    
    # Enable user account
    Enable-LocalUser -Name $sshUsername
    
    # Add to Remote Desktop Users group (may be needed for SSH access)
    $rdpGroup = Get-LocalGroup -Name "Remote Desktop Users" -ErrorAction SilentlyContinue
    if ($rdpGroup) {
        Add-LocalGroupMember -Group "Remote Desktop Users" -Member $sshUsername -ErrorAction SilentlyContinue
    }
    
    # Grant "Allow log on locally" right using secedit
    try {
        $tmpPath = [System.IO.Path]::GetTempFileName()
        secedit /export /cfg $tmpPath /quiet | Out-Null
        $content = Get-Content $tmpPath
        
        # Find SeInteractiveLogonRight line
        $interactiveLogonLine = $content | Where-Object { $_ -match "SeInteractiveLogonRight" }
        
        if ($interactiveLogonLine -and $interactiveLogonLine -notmatch $sshUsername) {
            $newLine = $interactiveLogonLine.TrimEnd() + ",*$sshUsername"
            $content = $content -replace [regex]::Escape($interactiveLogonLine), $newLine
            $content | Set-Content $tmpPath
            
            secedit /configure /db "$env:windir\security\local.sdb" /cfg $tmpPath /areas USER_RIGHTS /quiet | Out-Null
        }
        Remove-Item $tmpPath -ErrorAction SilentlyContinue
    } catch {
        Write-Host "  [AVISO] Nao foi possivel configurar 'Allow log on locally' via secedit: $_" -ForegroundColor Yellow
    }
}

Write-Host "`nUsuario $sshUsername criado/atualizado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "=== INFORMACOES PARA AIRFLOW ===" -ForegroundColor Cyan
Write-Host "Connection Id: prometheus_executor_host" -ForegroundColor White
Write-Host "Connection Type: SSH" -ForegroundColor White
Write-Host "Host: host.docker.internal" -ForegroundColor White
Write-Host "Login: $sshUsername" -ForegroundColor White
Write-Host "Password: [a senha que voce digitou]" -ForegroundColor White
Write-Host "Port: 22" -ForegroundColor White
Write-Host ""
Write-Host "Teste SSH manualmente:" -ForegroundColor Yellow
Write-Host "  ssh ${sshUsername}@127.0.0.1" -ForegroundColor Cyan

