# MEMORY_ID: TASK_VALIDACAO_FINAL
# TIMESTAMP: 09-11-2025 21:51 CET
# AUTHOR: Cursor_Omega

param(
    [string]$ProjectRoot = "$PSScriptRoot\..",
    [int]$MaxRetries = 3,
    [int]$RetryDelaySeconds = 30
)

Set-Location $ProjectRoot

$logFile = Join-Path $ProjectRoot "logs/core_main_fallback.log"
$fallbackLog = Join-Path $ProjectRoot "logs/core_main_fallback_errors.log"

if (-not (Test-Path (Split-Path $logFile))) {
    New-Item -ItemType Directory -Force -Path (Split-Path $logFile) | Out-Null
}

$attempt = 0
$success = $false

while ($attempt -lt $MaxRetries -and -not $success) {
    $attempt++
    Write-Host "[Prometheus] Tentativa $attempt de execução do Core.Main..." -ForegroundColor Cyan
    try {
        python -m Core.Main *>> $logFile
        $success = $true
        Write-Host "[Prometheus] Execução concluída com sucesso." -ForegroundColor Green
    } catch {
        $errorMsg = "[{0}] Falha na tentativa {1}: {2}" -f (Get-Date -Format o), $attempt, $_.Exception.Message
        $errorMsg | Out-File -FilePath $fallbackLog -Append
        Write-Host $errorMsg -ForegroundColor Red
        if ($attempt -lt $MaxRetries) {
            Write-Host "[Prometheus] Aguardando $RetryDelaySeconds segundos antes de nova tentativa..." -ForegroundColor Yellow
            Start-Sleep -Seconds $RetryDelaySeconds
        }
    }
}

if (-not $success) {
    Write-Host "[Prometheus] Falha após $MaxRetries tentativas. Verifique $fallbackLog." -ForegroundColor Red
    exit 1
}

