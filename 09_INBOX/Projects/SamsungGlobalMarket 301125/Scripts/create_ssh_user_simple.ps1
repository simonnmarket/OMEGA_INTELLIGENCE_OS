# Create SSH User for Airflow - Simple Version
# Run as Administrator

Write-Host "=== Creating SSH User for Airflow (Simple) ===" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Botao direito no PowerShell > Executar como Administrador" -ForegroundColor Yellow
    exit 1
}

$sshUsername = "SSHUser"
$sshPassword = Read-Host "Digite uma senha para o usuario SSHUser" -AsSecureString

# Convert to plain text for net user command
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sshPassword)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Check if user exists
$userExists = Get-LocalUser -Name $sshUsername -ErrorAction SilentlyContinue

if ($userExists) {
    Write-Host "Usuario $sshUsername ja existe. Alterando senha..." -ForegroundColor Yellow
    # Use net user command for existing user
    $plainPassword | net user $sshUsername *
    Write-Host "Senha alterada com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Criando usuario $sshUsername usando net user..." -ForegroundColor Yellow
    # Create user using net user command (more reliable)
    net user $sshUsername $plainPassword /add /passwordchg:no /expires:never
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Usuario $sshUsername criado com sucesso!" -ForegroundColor Green
        
        # Now use PowerShell cmdlets for additional configuration
        try {
            Enable-LocalUser -Name $sshUsername -ErrorAction Stop
            Write-Host "  [OK] Usuario habilitado" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Nao foi possivel habilitar usuario: $_" -ForegroundColor Yellow
        }
        
        try {
            Set-LocalUser -Name $sshUsername -PasswordNeverExpires $true -ErrorAction Stop
            Write-Host "  [OK] Senha configurada para nao expirar" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Nao foi possivel configurar expiracao de senha: $_" -ForegroundColor Yellow
        }
        
        # Add to Remote Desktop Users group
        try {
            $rdpGroup = Get-LocalGroup -Name "Remote Desktop Users" -ErrorAction SilentlyContinue
            if ($rdpGroup) {
                Add-LocalGroupMember -Group "Remote Desktop Users" -Member $sshUsername -ErrorAction Stop
                Write-Host "  [OK] Usuario adicionado ao grupo 'Remote Desktop Users'" -ForegroundColor Green
            } else {
                Write-Host "  [AVISO] Grupo 'Remote Desktop Users' nao encontrado" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  [AVISO] Nao foi possivel adicionar ao grupo: $_" -ForegroundColor Yellow
        }
        
        # Grant "Allow log on locally" right using secedit
        try {
            $tmpPath = [System.IO.Path]::GetTempFileName()
            secedit /export /cfg $tmpPath /quiet | Out-Null
            $content = Get-Content $tmpPath
            
            # Find SeInteractiveLogonRight line
            $interactiveLogonLine = $content | Where-Object { $_ -match "SeInteractiveLogonRight" }
            
            if ($interactiveLogonLine -and $interactiveLogonLine -notmatch $sshUsername) {
                Write-Host "  [CORRIGINDO] Configurando permissao 'Allow log on locally'..." -ForegroundColor Yellow
                $newLine = $interactiveLogonLine.TrimEnd() + ",*$sshUsername"
                $content = $content -replace [regex]::Escape($interactiveLogonLine), $newLine
                $content | Set-Content $tmpPath
                
                secedit /configure /db "$env:windir\security\local.sdb" /cfg $tmpPath /areas USER_RIGHTS /quiet | Out-Null
                Write-Host "  [OK] Permissao 'Allow log on locally' concedida" -ForegroundColor Green
            } else {
                Write-Host "  [OK] Permissao 'Allow log on locally' ja configurada" -ForegroundColor Green
            }
            Remove-Item $tmpPath -ErrorAction SilentlyContinue
        } catch {
            Write-Host "  [AVISO] Nao foi possivel configurar 'Allow log on locally' via secedit: $_" -ForegroundColor Yellow
        }
        
        # Restart SSH service
        Write-Host "`nReiniciando servico SSH..." -ForegroundColor Yellow
        try {
            Restart-Service sshd -ErrorAction Stop
            Write-Host "  [OK] Servico SSH reiniciado" -ForegroundColor Green
        } catch {
            Write-Host "  [ERRO] Nao foi possivel reiniciar servico SSH: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "ERRO: Falha ao criar usuario!" -ForegroundColor Red
        exit 1
    }
}

# Verify user
$user = Get-LocalUser -Name $sshUsername -ErrorAction SilentlyContinue
if ($user) {
    Write-Host "`n=== Usuario Verificado ===" -ForegroundColor Cyan
    Write-Host "Nome: $($user.Name)" -ForegroundColor White
    Write-Host "Enabled: $($user.Enabled)" -ForegroundColor $(if ($user.Enabled) { 'Green' } else { 'Red' })
    Write-Host "PasswordNeverExpires: $($user.PasswordNeverExpires)" -ForegroundColor White
} else {
    Write-Host "`n[AVISO] Usuario criado mas nao foi possivel verificar com Get-LocalUser" -ForegroundColor Yellow
    Write-Host "Teste com: net user $sshUsername" -ForegroundColor Cyan
}

Write-Host "`n=== INFORMACOES PARA AIRFLOW ===" -ForegroundColor Cyan
Write-Host "Connection Id: prometheus_executor_host" -ForegroundColor White
Write-Host "Connection Type: SSH" -ForegroundColor White
Write-Host "Host: host.docker.internal" -ForegroundColor White
Write-Host "Login: $sshUsername" -ForegroundColor White
Write-Host "Password: [a senha que voce digitou]" -ForegroundColor White
Write-Host "Port: 22" -ForegroundColor White
Write-Host ""
Write-Host "Teste SSH manualmente:" -ForegroundColor Yellow
Write-Host "  ssh ${sshUsername}@127.0.0.1" -ForegroundColor Cyan

