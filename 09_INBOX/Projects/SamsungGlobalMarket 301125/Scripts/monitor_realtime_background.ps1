# Monitoramento em tempo real em background (com alertas)
param(
    [int]$IntervalSeconds = 1,
    [switch]$ShowAlerts = $true
)

$ErrorActionPreference = "Continue"
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
$projectPath = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $projectPath "logs\monitor_realtime.log"

# Criar diretório de logs se não existir
if (-not (Test-Path (Split-Path $logFile))) {
    New-Item -ItemType Directory -Path (Split-Path $logFile) -Force | Out-Null
}

function Write-Log { param($Message, $Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry -ErrorAction SilentlyContinue
    
    if ($Level -eq "ERROR" -or $Level -eq "WARN") {
        Write-Host $logEntry -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } else { "Yellow" })
    } elseif ($Level -eq "SUCCESS") {
        Write-Host $logEntry -ForegroundColor Green
    }
}

function Test-ServerRunning {
    $proc = Get-Process python -ErrorAction SilentlyContinue
    if ($proc) {
        $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" | Select-Object -ExpandProperty CommandLine)
        if ($cmd -like "*server_file_based*") {
            return @{ Status = "OK"; PID = $proc.Id }
        } elseif ($cmd -like "*main_server*") {
            return @{ Status = "WRONG"; PID = $proc.Id; Server = "main_server" }
        } else {
            return @{ Status = "UNKNOWN"; PID = $proc.Id }
        }
    }
    return @{ Status = "STOPPED" }
}

function Test-FilesStatus {
    if (-not (Test-Path $mt5Path)) {
        return @{ Status = "ERROR"; Message = "Diretorio nao existe" }
    }
    
    $reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
    $resps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
    
    $oldReqs = if ($reqs) { ($reqs | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -gt 30 }).Count } else { 0 }
    $recentResps = if ($resps) { ($resps | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -lt 10 }).Count } else { 0 }
    
    return @{
        Requests = $reqs.Count
        OldRequests = $oldReqs
        Responses = $resps.Count
        RecentResponses = $recentResps
        Status = if ($oldReqs -gt 0) { "WARN" } else { "OK" }
    }
}

# Loop principal de monitoramento
Write-Log "Monitoramento iniciado (intervalo: $IntervalSeconds segundos)" "INFO"
$iteration = 0

while ($true) {
    $iteration++
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    # 1. Verificar servidor
    $serverStatus = Test-ServerRunning
    if ($serverStatus.Status -eq "STOPPED") {
        Write-Log "ERRO CRITICO: Servidor PARADO!" "ERROR"
        if ($ShowAlerts) {
            [System.Media.SystemSounds]::Exclamation.Play()
        }
    } elseif ($serverStatus.Status -eq "WRONG") {
        Write-Log "ERRO: Servidor incorreto rodando ($($serverStatus.Server))" "ERROR"
    }
    
    # 2. Verificar arquivos
    $filesStatus = Test-FilesStatus
    if ($filesStatus.Status -eq "ERROR") {
        Write-Log "ERRO: $($filesStatus.Message)" "ERROR"
    } elseif ($filesStatus.OldRequests -gt 0) {
        Write-Log "AVISO: $($filesStatus.OldRequests) request(s) antigo(s) (>30s) - Servidor pode nao estar processando" "WARN"
    }
    
    # 3. Verificar ciclos de comunicação (a cada 10 iterações)
    if ($iteration % 10 -eq 0) {
        if ($serverStatus.Status -eq "OK" -and $filesStatus.OldRequests -eq 0 -and $filesStatus.RecentResponses -gt 0) {
            Write-Log "Sistema operacional: Servidor OK, Requests processados, Responses criados" "SUCCESS"
        }
    }
    
    # 4. Verificar acumulação de responses
    if ($filesStatus.Responses -gt 20) {
        Write-Log "AVISO: $($filesStatus.Responses) responses acumulados - EA pode nao estar lendo" "WARN"
    }
    
    Start-Sleep -Seconds $IntervalSeconds
}

