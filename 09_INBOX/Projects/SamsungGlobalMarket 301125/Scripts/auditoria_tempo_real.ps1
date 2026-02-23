# ============================================================================
# AUDITORIA EM TEMPO REAL - ECOSISTEMA SAMSUNG GLOBAL MARKET
# PROTOCOLO: Omega TIER-0
# ============================================================================

param(
    [int]$IntervalSeconds = 5,  # Intervalo entre verificações (segundos)
    [switch]$Continuous = $true  # Modo contínuo (loop)
)

$ErrorActionPreference = "Continue"

# Cores para output
function Write-Status { param($Message, $Status)
    $color = switch($Status) {
        "OK" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    Write-Host "[$Status] $Message" -ForegroundColor $color
}

function Write-Separator {
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

# Função principal de auditoria
function Invoke-SystemAudit {
    Write-Separator
    Write-Host "AUDITORIA DO ECOSISTEMA - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    Write-Separator
    Write-Host ""
    
    # ========================================================================
    # 1. VERIFICAR SERVIDOR PYTHON
    # ========================================================================
    Write-Host "[1] VERIFICANDO SERVIDOR PYTHON..." -ForegroundColor Yellow
    Write-Host ""
    
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Status "Servidor Python encontrado: $($pythonProcesses.Count) processo(s)" "OK"
        foreach ($proc in $pythonProcesses) {
            $procInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" | Select-Object CommandLine
            Write-Host "  PID: $($proc.Id) | Memória: $([math]::Round($proc.WS / 1MB, 2)) MB" -ForegroundColor Gray
            if ($procInfo.CommandLine -like "*server_file_based*") {
                Write-Status "  ✅ Servidor file-based detectado!" "OK"
            }
        }
    } else {
        Write-Status "❌ SERVIDOR PYTHON NÃO ENCONTRADO!" "ERROR"
        Write-Status "  Ação: Iniciar server_file_based_v2.0.0.py" "WARN"
    }
    Write-Host ""
    
    # ========================================================================
    # 2. VERIFICAR DIRETÓRIO DE ARQUIVOS MT5
    # ========================================================================
    Write-Host "[2] VERIFICANDO DIRETÓRIO DE ARQUIVOS MT5..." -ForegroundColor Yellow
    Write-Host ""
    
    $mt5CommonPath = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
    Write-Status "Caminho esperado: $mt5CommonPath" "INFO"
    
    if (Test-Path $mt5CommonPath) {
        Write-Status "✅ Diretório existe" "OK"
        
        # Verificar arquivos de request
        $requestFiles = Get-ChildItem -Path $mt5CommonPath -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
        if ($requestFiles) {
            Write-Status "✅ Requests encontrados: $($requestFiles.Count)" "OK"
            foreach ($req in $requestFiles) {
                $content = Get-Content $req.FullName -Raw -ErrorAction SilentlyContinue
                $age = (Get-Date) - $req.LastWriteTime
                Write-Host "  📄 $($req.Name) | Idade: $([math]::Round($age.TotalSeconds, 1))s" -ForegroundColor Gray
                if ($age.TotalSeconds -gt 60) {
                    Write-Status "  ⚠️  Request antigo (>60s) - Servidor pode não estar processando!" "WARN"
                }
            }
        } else {
            Write-Status "⚠️  Nenhum request encontrado" "WARN"
            Write-Status "  Possível causa: EA não está enviando ou arquivos foram processados" "INFO"
        }
        
        # Verificar arquivos de response
        $responseFiles = Get-ChildItem -Path $mt5CommonPath -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
        if ($responseFiles) {
            Write-Status "✅ Responses encontrados: $($responseFiles.Count)" "OK"
            foreach ($resp in $responseFiles) {
                $content = Get-Content $resp.FullName -Raw -ErrorAction SilentlyContinue
                $age = (Get-Date) - $resp.LastWriteTime
                Write-Host "  📄 $($resp.Name) | Idade: $([math]::Round($age.TotalSeconds, 1))s" -ForegroundColor Gray
                
                # Tentar parsear JSON
                try {
                    $json = $content | ConvertFrom-Json
                    Write-Host "    Action: $($json.action) | Confidence: $($json.confidence)" -ForegroundColor Gray
                } catch {
                    Write-Status "  ⚠️  JSON inválido ou corrompido" "WARN"
                }
            }
        } else {
            Write-Status "⚠️  Nenhum response encontrado" "WARN"
            Write-Status "  Possível causa: Servidor não está processando requests" "WARN"
        }
        
        # Listar todos os arquivos JSON (debug)
        $allJson = Get-ChildItem -Path $mt5CommonPath -Filter "*.json" -ErrorAction SilentlyContinue
        Write-Host "  Total de arquivos JSON no diretório: $($allJson.Count)" -ForegroundColor Gray
    } else {
        Write-Status "❌ DIRETÓRIO NÃO EXISTE!" "ERROR"
        Write-Status "  Caminho: $mt5CommonPath" "ERROR"
        Write-Status "  Ação: Criar diretório ou verificar caminho" "WARN"
    }
    Write-Host ""
    
    # ========================================================================
    # 3. VERIFICAR PROCESSOS MT5
    # ========================================================================
    Write-Host "[3] VERIFICANDO META TRADER 5..." -ForegroundColor Yellow
    Write-Host ""
    
    $mt5Processes = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
    if ($mt5Processes) {
        Write-Status "✅ MT5 em execução: $($mt5Processes.Count) instância(s)" "OK"
    } else {
        Write-Status "❌ MT5 NÃO ESTÁ EM EXECUÇÃO!" "ERROR"
    }
    Write-Host ""
    
    # ========================================================================
    # 4. VERIFICAR CONECTIVIDADE E PERMISSÕES
    # ========================================================================
    Write-Host "[4] VERIFICANDO PERMISSÕES E CONECTIVIDADE..." -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path $mt5CommonPath) {
        # Testar escrita
        $testFile = Join-Path $mt5CommonPath "_test_write_$(Get-Date -Format 'yyyyMMddHHmmss').txt"
        try {
            "test" | Out-File -FilePath $testFile -ErrorAction Stop
            Remove-Item $testFile -ErrorAction SilentlyContinue
            Write-Status "✅ Permissões de escrita: OK" "OK"
        } catch {
            Write-Status "❌ Sem permissão de escrita no diretório!" "ERROR"
        }
        
        # Verificar permissões de leitura
        try {
            Get-ChildItem $mt5CommonPath -ErrorAction Stop | Out-Null
            Write-Status "✅ Permissões de leitura: OK" "OK"
        } catch {
            Write-Status "❌ Sem permissão de leitura no diretório!" "ERROR"
        }
    }
    Write-Host ""
    
    # ========================================================================
    # 5. RESUMO E DIAGNÓSTICO
    # ========================================================================
    Write-Host "[5] RESUMO E DIAGNÓSTICO..." -ForegroundColor Yellow
    Write-Host ""
    
    $issues = @()
    
    if (-not $pythonProcesses) {
        $issues += "Servidor Python não está rodando"
    }
    
    if (-not (Test-Path $mt5CommonPath)) {
        $issues += "Diretório MT5 não existe"
    }
    
    if ($requestFiles -and ($requestFiles | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -gt 60 })) {
        $issues += "Requests antigos detectados (>60s) - Servidor não processando"
    }
    
    if (-not $responseFiles) {
        $issues += "Nenhum response gerado - Servidor não processando requests"
    }
    
    if ($issues.Count -eq 0) {
        Write-Status "✅ Sistema aparentemente operacional" "OK"
    } else {
        Write-Status "❌ PROBLEMAS DETECTADOS: $($issues.Count)" "ERROR"
        foreach ($issue in $issues) {
            Write-Host "  • $issue" -ForegroundColor Red
        }
    }
    
    Write-Separator
    Write-Host ""
}

# Loop principal
if ($Continuous) {
    Write-Host "AUDITORIA CONTÍNUA ATIVADA (Intervalo: $IntervalSeconds segundos)" -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    
    while ($true) {
        Clear-Host
        Invoke-SystemAudit
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    Invoke-SystemAudit
}

