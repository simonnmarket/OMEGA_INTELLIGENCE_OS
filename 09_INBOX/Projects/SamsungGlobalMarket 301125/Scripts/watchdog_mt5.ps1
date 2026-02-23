# Watchdog para monitorar o MetaTrader 5 e reiniciar se necessário
param(
    [int]$CheckIntervalSeconds = 30,
    [string]$LogFile = "logs\watchdog_mt5.log"
)

$ErrorActionPreference = "Continue"
$projectPath = Split-Path -Parent $PSScriptRoot
$logFileFull = Join-Path $projectPath $LogFile

# Criar diretório de logs
$logDir = Split-Path $logFileFull
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-WatchdogLog { param($Message, $Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFileFull -Value $logEntry
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

Write-WatchdogLog "========================================" "INFO"
Write-WatchdogLog "WATCHDOG MT5 INICIADO" "SUCCESS"
Write-WatchdogLog "Intervalo de verificacao: $CheckIntervalSeconds segundos" "INFO"
Write-WatchdogLog "========================================" "INFO"
Write-Host ""

$consecutiveFailures = 0
$maxConsecutiveFailures = 3

while ($true) {
    Start-Sleep -Seconds $CheckIntervalSeconds
    
    # Verificar se MT5 está rodando
    $mt5Process = Get-Process terminal64 -ErrorAction SilentlyContinue
    
    if (-not $mt5Process) {
        $consecutiveFailures++
        Write-WatchdogLog "MetaTrader 5 NAO ESTA RODANDO! (Falha $consecutiveFailures/$maxConsecutiveFailures)" "ERROR"
        
        if ($consecutiveFailures -ge $maxConsecutiveFailures) {
            Write-WatchdogLog "ALERTA CRITICO: MT5 parado por $($CheckIntervalSeconds * $consecutiveFailures) segundos" "ERROR"
            
            # Tocar som de alerta
            [System.Media.SystemSounds]::Exclamation.Play()
            
            # Tentar reiniciar
            Write-WatchdogLog "Tentando reiniciar MetaTrader 5..." "WARN"
            
            $mt5Paths = @(
                "C:\Program Files\MetaTrader 5\terminal64.exe",
                "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
                "$env:ProgramFiles\MetaTrader 5\terminal64.exe",
                "${env:ProgramFiles(x86)}\MetaTrader 5\terminal64.exe"
            )
            
            $mt5Exe = $null
            foreach ($path in $mt5Paths) {
                if (Test-Path $path) {
                    $mt5Exe = $path
                    break
                }
            }
            
            if ($mt5Exe) {
                Start-Process $mt5Exe
                Write-WatchdogLog "MetaTrader 5 reiniciado. Aguardando inicializacao..." "SUCCESS"
                Start-Sleep -Seconds 10
                
                $mt5Check = Get-Process terminal64 -ErrorAction SilentlyContinue
                if ($mt5Check) {
                    Write-WatchdogLog "MetaTrader 5 reiniciado com sucesso!" "SUCCESS"
                    Write-WatchdogLog "ACAO NECESSARIA: Anexar o EA manualmente ao grafico!" "WARN"
                    $consecutiveFailures = 0
                } else {
                    Write-WatchdogLog "Falha ao reiniciar MetaTrader 5" "ERROR"
                }
            } else {
                Write-WatchdogLog "Executavel do MT5 nao encontrado. Reinicio manual necessario" "ERROR"
            }
        }
    } else {
        if ($consecutiveFailures -gt 0) {
            Write-WatchdogLog "MetaTrader 5 voltou a funcionar" "SUCCESS"
            $consecutiveFailures = 0
        }
        
        # Log silencioso a cada 10 verificações
        if ((Get-Random -Minimum 1 -Maximum 10) -eq 1) {
            Write-WatchdogLog "MetaTrader 5 operando normalmente (PID: $($mt5Process.Id))" "INFO"
        }
    }
    
    # Verificar servidor Python também
    $pythonProcess = Get-Process python -ErrorAction SilentlyContinue
    if (-not $pythonProcess) {
        Write-WatchdogLog "AVISO: Servidor Python nao esta rodando!" "WARN"
    }
}

