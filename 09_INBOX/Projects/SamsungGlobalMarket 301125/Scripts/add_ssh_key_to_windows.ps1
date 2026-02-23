# Add SSH Public Key to Windows authorized_keys
# Run as Administrator

Write-Host "=== Adicionando Chave SSH ao Windows ===" -ForegroundColor Cyan

$publicKey = @"
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC93lGK+7RaZLeEp7lJ63FIYE/smgm2nmSjjwpeigS7TBEndz0QwogtNO2WnBFXEhXiyAi4bRu+HtJLOt9GC98gYpGBYxSX/KEPAI3ol+WS5F3oMFWq8bDZ1M6wDGFrXqMjrprawzwBYVWnkcf0HNaViNVDMs0DOlzKPtBbdpSCe20ALf0/2V3rp+oOypUJWNL04IEY+TlGtTvlX/lYesXw7a/rm2pQlRkqLBaf0ldIcUb7bsXH6nezpJp/QGdX0jCbza2mlQCPt3+em89pel4/ey0r/NpK9u9OIcKaoTcH3stDeD6fDzDF29sle+TdzWM2qhA8axNYKzXARSgkil449VAbc9xr3Djt1UkYLEB2Pyjv+DqlEtm7/UF4b80DkiPGzudLlKh1wNdw6UbX3DqZadc8qkTM9HAF591PS6U4FprkbsXpKeuFK+QuKtasump/Gq2rcLOGalA+rXmgpBrw2qTXSwXZD3GzJZA4MvpaC5qYcTlOdbzthEjRJPa/f/w7fiwUorJtRFZN01ZAZ5DANLDoBbqyN0loJDtY/MHdJbx4Y0d+BikKr1ov7WIzQUEtquoqo8WD5XOt33kVIxrwOSesfcb6spLRla5ghc2YpmE+4mETTSLWTImFj1xRgUGVCwtUVN0T844pHi+mViAnZ1blhPXJOX/V5sSm6YKWXw== default@e3a52eebf398
"@

# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
    Write-Host "Pasta .ssh criada: $sshDir" -ForegroundColor Green
}

# Add public key to authorized_keys
$authorizedKeysFile = "$sshDir\authorized_keys"

# Check if key already exists
if (Test-Path $authorizedKeysFile) {
    $existingKeys = Get-Content $authorizedKeysFile -Raw
    if ($existingKeys -match [regex]::Escape($publicKey.Split(' ')[1])) {
        Write-Host "Chave SSH ja existe em authorized_keys" -ForegroundColor Yellow
    } else {
        Add-Content -Path $authorizedKeysFile -Value $publicKey
        Write-Host "Chave SSH adicionada a authorized_keys" -ForegroundColor Green
    }
} else {
    Set-Content -Path $authorizedKeysFile -Value $publicKey
    Write-Host "Arquivo authorized_keys criado com chave SSH" -ForegroundColor Green
}

# Fix permissions (CRITICAL for Windows)
Write-Host "`nCorrigindo permissoes..." -ForegroundColor Yellow

try {
    # Reset permissions
    icacls "$sshDir" /reset | Out-Null
    
    # Grant full control to current user
    icacls "$sshDir" /grant "${env:USERNAME}:(OI)(CI)F" /T | Out-Null
    
    # Grant full control to authorized_keys
    icacls "$authorizedKeysFile" /grant "${env:USERNAME}:F" | Out-Null
    
    Write-Host "Permissoes corrigidas com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao corrigir permissoes: $_" -ForegroundColor Red
    exit 1
}

# Verify
Write-Host "`n=== Verificacao ===" -ForegroundColor Cyan
Write-Host "Pasta .ssh: $sshDir" -ForegroundColor White
Write-Host "Arquivo authorized_keys existe: $(Test-Path $authorizedKeysFile)" -ForegroundColor White

if (Test-Path $authorizedKeysFile) {
    Write-Host "`nConteudo do authorized_keys:" -ForegroundColor Yellow
    Get-Content $authorizedKeysFile | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}

Write-Host "`n=== PROXIMO PASSO ===" -ForegroundColor Cyan
Write-Host "1. Copie a chave privada do container para persistir:" -ForegroundColor White
Write-Host "   docker cp docker-airflow-worker-1:/tmp/airflow_ssh_key Orchestration/Airflow/docker/ssh_keys/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Configure a conexao SSH no Airflow:" -ForegroundColor White
Write-Host "   - Connection Id: prometheus_executor_host" -ForegroundColor Gray
Write-Host "   - Connection Type: SSH" -ForegroundColor Gray
Write-Host "   - Host: host.docker.internal" -ForegroundColor Gray
Write-Host "   - Login: Lenovo" -ForegroundColor Gray
Write-Host "   - Password: (deixe VAZIO)" -ForegroundColor Gray
Write-Host "   - Port: 22" -ForegroundColor Gray
Write-Host "   - Extra: {'key_file': '/tmp/ssh_keys/airflow_ssh_key', 'no_host_key_check': true}" -ForegroundColor Gray

