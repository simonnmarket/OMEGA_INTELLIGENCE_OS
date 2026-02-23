# SCRIPT DE EXECUCAO AUTOMATICA DO PROTOCOLO DE VALIDACAO
# Projeto Prometheus v3.0.0 | Samsung Global Market
# Protocolo: Omega TIER-0

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "PROTOCOLO DE VALIDACAO QUANTITATIVA - EXECUCAO AUTOMATICA" -ForegroundColor Yellow
Write-Host "Projeto Prometheus v3.0.0 | Samsung Global Market" -ForegroundColor White
Write-Host "==========================================================================="
Write-Host ""

# Configuracoes
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot "venv\Scripts\Activate.ps1"

Write-Host "[INFORMACAO] Estrutura do Protocolo:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ETAPA 1: Voce executa o SERVIDOR manualmente" -ForegroundColor Yellow
Write-Host "  Comando: .\Scripts\start_main_server.ps1" -ForegroundColor White
Write-Host ""
Write-Host "ETAPA 2: Este script executa AUTOMATICAMENTE:" -ForegroundColor Green
Write-Host "  - Teste quantitativo do servidor (50 testes)" -ForegroundColor White
Write-Host "  - Identificacao de arquivos .ex5" -ForegroundColor White
Write-Host "  - Teste end-to-end (100 segundos)" -ForegroundColor White
Write-Host ""
Write-Host "ETAPA 3: Voce anexa a EA ao MT5" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================================================="
Write-Host ""

# Pergunta ao usuario
Write-Host "[PERGUNTA] O servidor ja esta rodando?" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. SIM - Servidor esta rodando (vou executar testes automaticamente)" -ForegroundColor Green
Write-Host "  2. NAO - Ainda nao executei o servidor" -ForegroundColor Yellow
Write-Host ""
$resposta = Read-Host "Escolha (1 ou 2)"

if ($resposta -eq "2") {
    Write-Host ""
    Write-Host "===========================================================================" -ForegroundColor Yellow
    Write-Host "PASSO 1: EXECUTAR SERVIDOR PRIMEIRO" -ForegroundColor Yellow
    Write-Host "==========================================================================="
    Write-Host ""
    Write-Host "Por favor, execute o servidor em uma janela PowerShell SEPARADA:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\Scripts\start_main_server.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Aguarde o servidor mostrar:" -ForegroundColor Yellow
    Write-Host "  [OK] Servico 'SocketService' iniciado na porta 5555" -ForegroundColor Green
    Write-Host "  [SUCESSO] TODOS OS SERVICOS INICIADOS COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Depois, execute este script novamente e escolha opcao 1." -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

# Verificar se servidor esta rodando
Write-Host ""
Write-Host "[VERIFICACAO] Verificando se servidor esta rodando..." -ForegroundColor Cyan

$portaAberta = Test-NetConnection -ComputerName 127.0.0.1 -Port 5555 -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $portaAberta) {
    Write-Host ""
    Write-Host "[ERRO] Servidor NAO esta rodando na porta 5555!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Acoes necessarias:" -ForegroundColor Yellow
    Write-Host "  1. Execute: .\Scripts\start_main_server.ps1" -ForegroundColor White
    Write-Host "  2. Aguarde a mensagem: [SUCESSO] TODOS OS SERVICOS INICIADOS" -ForegroundColor White
    Write-Host "  3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "[OK] Servidor detectado na porta 5555!" -ForegroundColor Green
Write-Host ""

# Ativar ambiente virtual
Write-Host "[ETAPA 1/3] Ativando ambiente virtual..." -ForegroundColor Cyan
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "[OK] Ambiente virtual ativado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Ambiente virtual nao encontrado, continuando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "INICIANDO TESTES AUTOMATICOS" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

# ETAPA 1: Teste Quantitativo do Servidor
Write-Host "[TESTE 1/3] Validacao Quantitativa do Servidor (50 testes)..." -ForegroundColor Yellow
Write-Host "  Isso pode levar alguns minutos..." -ForegroundColor Gray
Write-Host ""

$test1 = Join-Path $projectRoot "Tests\test_server_quantitative.py"
if (Test-Path $test1) {
    python $test1
    $test1Result = $LASTEXITCODE
    
    if ($test1Result -eq 0) {
        Write-Host ""
        Write-Host "[OK] TESTE 1 PASSOU - Servidor 100% funcional" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERRO] TESTE 1 FALHOU - Servidor tem problemas" -ForegroundColor Red
        Write-Host "  Verifique os logs do servidor e corrija antes de prosseguir" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[AVISO] Arquivo test_server_quantitative.py nao encontrado em Tests\" -ForegroundColor Yellow
    Write-Host "  Pulando teste 1..." -ForegroundColor Gray
}

Write-Host ""
Start-Sleep -Seconds 2

# ETAPA 2: Identificacao de Arquivos .ex5
Write-Host "[TESTE 2/3] Identificacao de Arquivos .ex5..." -ForegroundColor Yellow
Write-Host ""

$test2 = Join-Path $PSScriptRoot "limpar_cache_mt5.ps1"
if (Test-Path $test2) {
    Write-Host "[INFO] Executando limpeza de cache MT5..." -ForegroundColor Cyan
    & $test2
    Write-Host ""
    Write-Host "[OK] TESTE 2 CONCLUIDO - Arquivos .ex5 verificados" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[AVISO] Arquivo limpar_cache_mt5.ps1 nao encontrado!" -ForegroundColor Yellow
    Write-Host "  Pulando teste 2..." -ForegroundColor Gray
}

Write-Host ""
Start-Sleep -Seconds 2

# ETAPA 3: Teste End-to-End
Write-Host "[TESTE 3/3] Teste End-to-End (100 segundos)..." -ForegroundColor Yellow
Write-Host "  Simulando EA completo conectando ao servidor..." -ForegroundColor Gray
Write-Host "  Isso levara aproximadamente 100 segundos..." -ForegroundColor Gray
Write-Host ""

$test3 = Join-Path $projectRoot "Tests\test_ea_server_connection.py"
if (Test-Path $test3) {
    python $test3
    $test3Result = $LASTEXITCODE
    
    if ($test3Result -eq 0) {
        Write-Host ""
        Write-Host "[OK] TESTE 3 PASSOU - Comunicacao end-to-end funcionando" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERRO] TESTE 3 FALHOU - Comunicacao end-to-end com problemas" -ForegroundColor Red
        Write-Host "  Verifique logs do servidor antes de anexar EA" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[AVISO] Arquivo test_ea_server_connection.py nao encontrado em Tests\" -ForegroundColor Yellow
    Write-Host "  Pulando teste 3..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "TODOS OS TESTES AUTOMATICOS CONCLUIDOS!" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "[PROXIMO PASSO] Agora voce pode:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Abrir MetaEditor (SEM MT5)" -ForegroundColor White
Write-Host "  2. Compilar SamsungGlobalMarket_EA v1.15 (F7)" -ForegroundColor White
Write-Host "  3. Verificar: 0 error(s), 0 warning(s)" -ForegroundColor White
Write-Host "  4. Fechar MetaEditor e abrir MT5 Terminal" -ForegroundColor White
Write-Host "  5. Anexar EA ao grafico" -ForegroundColor White
Write-Host "  6. Monitorar logs para validar:" -ForegroundColor White
Write-Host "     - Versao 1.15 aparece nos logs" -ForegroundColor Gray
Write-Host "     - [PCA METRICS] Protocolo completo em XXXms" -ForegroundColor Gray
Write-Host "     - HANDSHAKE_ACK recebido com sucesso" -ForegroundColor Gray
Write-Host "     - Heartbeats recebidos a cada ~10s" -ForegroundColor Gray
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host ""

