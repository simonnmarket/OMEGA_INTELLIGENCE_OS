# SCRIPT DE RECUPERACAO COMPLETA DO EA
# Projeto Prometheus v3.0.0 | Samsung Global Market
# Restaura arquivo .mq5 e corrige caminho do .ex5

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "RECUPERACAO COMPLETA DO EA" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$mq5Origem = Join-Path $projectRoot "SamsungGlobalMarket_EA.mq5"
$mq5Destino = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5"
$ex5CaminhoErrado = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket\SamsungGlobalMarket\SamsungGlobalMarket_EA.ex5"
$ex5CaminhoCorreto = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.ex5"
$pastaExperts = "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts"

# ETAPA 1: Recuperar arquivo .mq5
Write-Host "[ETAPA 1/4] Recuperando arquivo .mq5..." -ForegroundColor Cyan

if (Test-Path $mq5Origem) {
    if (-not (Test-Path $pastaExperts)) {
        New-Item -ItemType Directory -Path $pastaExperts -Force | Out-Null
        Write-Host "  [OK] Pasta Experts criada" -ForegroundColor Green
    }
    
    Copy-Item $mq5Origem $mq5Destino -Force
    Write-Host "  [OK] Arquivo .mq5 copiado para: $mq5Destino" -ForegroundColor Green
    
    # Verificar versão no arquivo
    $conteudo = Get-Content $mq5Destino -TotalCount 100
    $versao = $conteudo | Select-String -Pattern 'version\s+"1\.04"'
    if ($versao) {
        Write-Host "  [OK] Arquivo contem versao 1.04" -ForegroundColor Green
    } else {
        Write-Host "  [AVISO] Versao no arquivo pode nao estar correta" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERRO] Arquivo .mq5 nao encontrado em: $mq5Origem" -ForegroundColor Red
    Write-Host "  [ACAO] Voce precisa restaurar o arquivo .mq5 manualmente" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ETAPA 2: Deletar todos os arquivos .ex5
Write-Host "[ETAPA 2/4] Deletando TODOS os arquivos .ex5..." -ForegroundColor Cyan

$todosEx5 = Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($todosEx5.Count -gt 0) {
    Write-Host "  [INFO] Encontrados $($todosEx5.Count) arquivo(s) .ex5 para deletar" -ForegroundColor Yellow
    $todosEx5 | ForEach-Object {
        Write-Host "    Deletando: $($_.FullName)" -ForegroundColor Gray
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  [OK] Todos os arquivos .ex5 deletados" -ForegroundColor Green
} else {
    Write-Host "  [OK] Nenhum arquivo .ex5 encontrado (limpo)" -ForegroundColor Green
}

Write-Host ""

# ETAPA 3: Fechar processos MT5
Write-Host "[ETAPA 3/4] Verificando processos MT5..." -ForegroundColor Cyan

$processos = Get-Process | Where-Object {$_.Name -like "*terminal*" -or $_.Name -like "*metaeditor*"} -ErrorAction SilentlyContinue

if ($processos) {
    Write-Host "  [AVISO] Encontrados processos MT5 ativos:" -ForegroundColor Yellow
    $processos | ForEach-Object {
        Write-Host "    - $($_.Name) (PID: $($_.Id))" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "  [ACAO] Fechando processos..." -ForegroundColor Cyan
    Stop-Process -Name "terminal64" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "metaeditor64" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  [OK] Processos fechados" -ForegroundColor Green
} else {
    Write-Host "  [OK] Nenhum processo MT5 ativo" -ForegroundColor Green
}

Write-Host ""

# ETAPA 4: Instruções finais
Write-Host "[ETAPA 4/4] Instrucoes para compilacao..." -ForegroundColor Cyan

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "PROXIMOS PASSOS OBRIGATORIOS" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""
Write-Host "1. Abrir MetaEditor (SEM abrir MT5 ainda)" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Abrir arquivo:" -ForegroundColor Cyan
Write-Host "   $mq5Destino" -ForegroundColor White
Write-Host ""
Write-Host "3. Verificar versao (linha 8):" -ForegroundColor Cyan
Write-Host "   #property version "1.04"" -ForegroundColor White
Write-Host ""
Write-Host "4. IMPORTANTE: Salvar arquivo (Ctrl+S) antes de compilar" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Compilar (F7) - Aguardar: 0 error(s), 0 warning(s)" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Verificar que arquivo .ex5 foi gerado em:" -ForegroundColor Cyan
Write-Host "   $ex5CaminhoCorreto" -ForegroundColor White
Write-Host ""
Write-Host "   (NAO deve estar em subpasta SamsungGlobalMarket\)" -ForegroundColor Yellow
Write-Host ""
Write-Host "7. SE arquivo foi gerado na subpasta:" -ForegroundColor Yellow
Write-Host "   - Mover manualmente para pasta Experts\" -ForegroundColor White
Write-Host "   - OU ajustar Output Directory no MetaEditor" -ForegroundColor White
Write-Host ""
Write-Host "8. Fechar MetaEditor" -ForegroundColor Cyan
Write-Host ""
Write-Host "9. Abrir MT5 e anexar EA" -ForegroundColor Cyan
Write-Host ""
Write-Host "10. Validar log mostra versao 1.04" -ForegroundColor Green
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host ""

# Verificação final
Write-Host "[VERIFICACAO FINAL]" -ForegroundColor Cyan
if (Test-Path $mq5Destino) {
    Write-Host "  [OK] Arquivo .mq5 restaurado" -ForegroundColor Green
} else {
    Write-Host "  [ERRO] Falha ao restaurar arquivo .mq5" -ForegroundColor Red
}

$ex5Restantes = Get-ChildItem -Path "$env:APPDATA\MetaQuotes" -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue
if ($ex5Restantes.Count -eq 0) {
    Write-Host "  [OK] Cache limpo (nenhum arquivo .ex5 restante)" -ForegroundColor Green
} else {
    Write-Host "  [AVISO] Ainda existem $($ex5Restantes.Count) arquivo(s) .ex5" -ForegroundColor Yellow
}

Write-Host ""

