# ============================================================================
# VERIFICAÇÃO COMPLETA DO ESTADO DO SISTEMA
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "VERIFICAÇÃO COMPLETA DO ECOSISTEMA" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# 1. Processos Python
Write-Host "[1] PROCESSOS PYTHON:" -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  ✅ $($pythonProcs.Count) processo(s) Python encontrado(s)" -ForegroundColor Green
    foreach ($proc in $pythonProcs) {
        $procInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" | Select-Object CommandLine
        Write-Host "    PID: $($proc.Id)" -ForegroundColor Gray
        if ($procInfo.CommandLine) {
            $cmd = $procInfo.CommandLine
            if ($cmd -like "*server_file_based*") {
                Write-Host "      ✅ SERVIDOR FILE-BASED DETECTADO" -ForegroundColor Green
            } elseif ($cmd -like "*main_server*") {
                Write-Host "      ⚠️  Servidor antigo (main_server) - Considere parar" -ForegroundColor Yellow
            } else {
                Write-Host "      ℹ️  $cmd" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "  ❌ NENHUM PROCESSO PYTHON ENCONTRADO!" -ForegroundColor Red
}
Write-Host ""

# 2. Arquivos MT5
Write-Host "[2] ARQUIVOS MT5 (Common/Files):" -ForegroundColor Yellow
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
if (Test-Path $mt5Path) {
    Write-Host "  ✅ Diretório existe: $mt5Path" -ForegroundColor Green
    
    # Requests
    $requests = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
    Write-Host "  📄 Requests: $($requests.Count)" -ForegroundColor Cyan
    if ($requests) {
        foreach ($req in $requests) {
            $age = (Get-Date) - $req.LastWriteTime
            $ageSec = [math]::Round($age.TotalSeconds, 1)
            $status = if ($ageSec -gt 60) { "ANTIGO" } else { "Recente" }
            $color = if ($ageSec -gt 60) { "Yellow" } else { "Green" }
            $msg = "      $status - $($req.Name) - ${ageSec}s atras"
            Write-Host $msg -ForegroundColor $color
        }
    }
    
    # Responses
    $responses = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
    Write-Host "  📄 Responses: $($responses.Count)" -ForegroundColor Cyan
    if ($responses) {
        foreach ($resp in $responses) {
            $age = (Get-Date) - $resp.LastWriteTime
            $ageSec = [math]::Round($age.TotalSeconds, 1)
            $msg = "      OK - $($resp.Name) - ${ageSec}s atras"
            Write-Host $msg -ForegroundColor Green
            try {
                $content = Get-Content $resp.FullName -Raw | ConvertFrom-Json
                Write-Host "        Action: $($content.action) | Confidence: $($content.confidence)" -ForegroundColor Gray
            } catch {
                Write-Host "        ERRO ao ler JSON" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "  ❌ Diretório não existe!" -ForegroundColor Red
}
Write-Host ""

# 3. MT5 Terminal
Write-Host "[3] META TRADER 5:" -ForegroundColor Yellow
$mt5 = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5) {
    Write-Host "  ✅ MT5 em execução" -ForegroundColor Green
} else {
    Write-Host "  ❌ MT5 NÃO está em execução!" -ForegroundColor Red
}
Write-Host ""

# 4. Diagnóstico
Write-Host "[4] DIAGNÓSTICO:" -ForegroundColor Yellow
$problems = @()

if (-not $pythonProcs) {
    $problems += "❌ Servidor Python não está rodando"
}

if ($pythonProcs -and -not ($pythonProcs | Where-Object {
    $procInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" | Select-Object CommandLine
    $procInfo.CommandLine -like "*server_file_based*"
})) {
    $problems += "⚠️  Nenhum servidor file-based detectado (pode estar rodando servidor antigo)"
}

if ($requests -and ($requests | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -gt 60 })) {
    $problems += "⚠️  Requests antigos (>60s) - Servidor pode não estar processando"
}

if ($requests -and -not $responses) {
    $problems += "❌ Requests existem mas nenhum response gerado - Servidor não está processando"
}

if ($problems.Count -eq 0) {
    Write-Host "  ✅ Nenhum problema detectado" -ForegroundColor Green
} else {
    foreach ($prob in $problems) {
        Write-Host "  $prob" -ForegroundColor $(if ($prob -like "❌*") { "Red" } else { "Yellow" })
    }
}
Write-Host ""

# 5. Recomendações
Write-Host "[5] AÇÕES RECOMENDADAS:" -ForegroundColor Yellow
if (-not $pythonProcs -or -not ($pythonProcs | Where-Object {
    $procInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" | Select-Object CommandLine
    $procInfo.CommandLine -like "*server_file_based*"
})) {
    Write-Host "  1. Iniciar servidor: .\Scripts\iniciar_servidor_file_based.ps1" -ForegroundColor Cyan
}

if ($requests -and -not $responses) {
    Write-Host "  2. Verificar logs do servidor para erros" -ForegroundColor Cyan
    Write-Host "  3. Verificar caminho do diretório MT5 no servidor" -ForegroundColor Cyan
}

if ($requests -and ($requests | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -gt 60 })) {
    Write-Host "  4. Requests antigos detectados - Reiniciar servidor pode ajudar" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan

