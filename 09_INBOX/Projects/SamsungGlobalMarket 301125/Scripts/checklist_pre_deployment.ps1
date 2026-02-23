# CHECKLIST PRÉ-DEPLOYMENT - Evitar erros como cache Python

param(
    [switch]$AutoFix = $false
)

$ErrorActionPreference = "Continue"
$projectPath = Split-Path -Parent $PSScriptRoot
$allOK = $true

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "CHECKLIST PRE-DEPLOYMENT" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# 1. Verificar cache Python
Write-Host "[1] Verificando cache Python..." -ForegroundColor Yellow
$cacheDir = Join-Path $projectPath "Server\__pycache__"
if (Test-Path $cacheDir) {
    Write-Host "  AVISO: Cache Python encontrado!" -ForegroundColor Yellow
    $cacheFiles = Get-ChildItem $cacheDir -Recurse
    Write-Host "  Arquivos em cache: $($cacheFiles.Count)" -ForegroundColor Gray
    
    if ($AutoFix) {
        Write-Host "  Removendo cache..." -ForegroundColor Yellow
        Remove-Item $cacheDir -Recurse -Force
        Write-Host "  Cache removido" -ForegroundColor Green
    } else {
        Write-Host "  ACAO NECESSARIA: Remover cache antes de deployment" -ForegroundColor Red
        Write-Host "    Remove-Item '$cacheDir' -Recurse -Force" -ForegroundColor Cyan
        $allOK = $false
    }
} else {
    Write-Host "  OK: Nenhum cache encontrado" -ForegroundColor Green
}
Write-Host ""

# 2. Verificar processos Python rodando
Write-Host "[2] Verificando processos Python..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  AVISO: $($pythonProcs.Count) processo(s) Python rodando" -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        Write-Host "    PID: $($proc.Id)" -ForegroundColor Gray
    }
    
    if ($AutoFix) {
        Write-Host "  Encerrando processos..." -ForegroundColor Yellow
        $pythonProcs | Stop-Process -Force
        Write-Host "  Processos encerrados" -ForegroundColor Green
    } else {
        Write-Host "  ACAO NECESSARIA: Encerrar processos antes de reiniciar" -ForegroundColor Red
        Write-Host "    Get-Process python | Stop-Process -Force" -ForegroundColor Cyan
        $allOK = $false
    }
} else {
    Write-Host "  OK: Nenhum processo Python rodando" -ForegroundColor Green
}
Write-Host ""

# 3. Verificar arquivo do servidor
Write-Host "[3] Verificando arquivo do servidor..." -ForegroundColor Yellow
$serverFile = Join-Path $projectPath "Server\server_file_based_v2.0.0.py"
if (Test-Path $serverFile) {
    $lastModified = (Get-Item $serverFile).LastWriteTime
    Write-Host "  OK: Arquivo encontrado" -ForegroundColor Green
    Write-Host "  Ultima modificacao: $lastModified" -ForegroundColor Gray
    
    # Verificar se código contém nova lógica
    $content = Get-Content $serverFile -Raw
    if ($content -match "spread < 3\.0.*# Spread razoável") {
        Write-Host "  OK: Nova logica detectada no codigo" -ForegroundColor Green
    } else {
        Write-Host "  ERRO: Nova logica NAO detectada no codigo!" -ForegroundColor Red
        $allOK = $false
    }
} else {
    Write-Host "  ERRO: Arquivo do servidor nao encontrado!" -ForegroundColor Red
    $allOK = $false
}
Write-Host ""

# 4. Verificar variáveis de ambiente
Write-Host "[4] Verificando variaveis de ambiente..." -ForegroundColor Yellow
if ($env:PYTHONDONTWRITEBYTECODE) {
    Write-Host "  OK: PYTHONDONTWRITEBYTECODE = $env:PYTHONDONTWRITEBYTECODE" -ForegroundColor Green
} else {
    Write-Host "  AVISO: PYTHONDONTWRITEBYTECODE nao definida" -ForegroundColor Yellow
    Write-Host "  Cache pode ser criado novamente" -ForegroundColor Yellow
    
    if ($AutoFix) {
        $env:PYTHONDONTWRITEBYTECODE = "1"
        Write-Host "  Variavel definida para esta sessao" -ForegroundColor Green
    } else {
        Write-Host "  RECOMENDACAO: Definir antes de iniciar servidor" -ForegroundColor Yellow
        Write-Host "    `$env:PYTHONDONTWRITEBYTECODE = '1'" -ForegroundColor Cyan
    }
}
Write-Host ""

# 5. Verificar diretório MT5
Write-Host "[5] Verificando diretorio MT5..." -ForegroundColor Yellow
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
if (Test-Path $mt5Path) {
    Write-Host "  OK: Diretorio MT5 encontrado" -ForegroundColor Green
    
    $oldRequests = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
    $oldResponses = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
    
    if ($oldRequests.Count -gt 0 -or $oldResponses.Count -gt 0) {
        Write-Host "  AVISO: Arquivos antigos encontrados" -ForegroundColor Yellow
        Write-Host "    Requests: $($oldRequests.Count)" -ForegroundColor Gray
        Write-Host "    Responses: $($oldResponses.Count)" -ForegroundColor Gray
        
        if ($AutoFix) {
            Write-Host "  Removendo arquivos antigos..." -ForegroundColor Yellow
            $oldRequests | Remove-Item -Force
            $oldResponses | Remove-Item -Force
            Write-Host "  Arquivos removidos" -ForegroundColor Green
        } else {
            Write-Host "  RECOMENDACAO: Limpar antes de deployment" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  OK: Nenhum arquivo antigo" -ForegroundColor Green
    }
} else {
    Write-Host "  AVISO: Diretorio MT5 nao encontrado (sera criado)" -ForegroundColor Yellow
}
Write-Host ""

# 6. Verificar MetaTrader
Write-Host "[6] Verificando MetaTrader 5..." -ForegroundColor Yellow
$mt5Process = Get-Process terminal64 -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-Host "  OK: MetaTrader 5 rodando (PID: $($mt5Process.Id))" -ForegroundColor Green
} else {
    Write-Host "  AVISO: MetaTrader 5 nao esta rodando" -ForegroundColor Yellow
    Write-Host "  Sera necessario iniciar e anexar EA" -ForegroundColor Yellow
}
Write-Host ""

# Resultado final
Write-Host "===========================================================================" -ForegroundColor Cyan
if ($allOK) {
    Write-Host "CHECKLIST: APROVADO" -ForegroundColor Green
    Write-Host "Sistema pronto para deployment" -ForegroundColor Green
} else {
    Write-Host "CHECKLIST: FALHOU" -ForegroundColor Red
    Write-Host "Corrigir problemas antes de deployment" -ForegroundColor Red
}
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $allOK -and -not $AutoFix) {
    Write-Host "Execute com -AutoFix para corrigir automaticamente:" -ForegroundColor Yellow
    Write-Host "  .\Scripts\checklist_pre_deployment.ps1 -AutoFix" -ForegroundColor Cyan
    Write-Host ""
}

return $allOK

