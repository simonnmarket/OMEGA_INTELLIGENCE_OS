@echo off
REM ============================================================================
REM AURORA v5.1 - SCRIPT DE EXECUÇÃO EXTERNA (FORA DO CURSOR)
REM ============================================================================
REM Este script executa o sistema Aurora de forma independente
REM Compatível com execução em background e monitoramento via MT5
REM ============================================================================

echo ============================================================================
echo AURORA v5.1 - EXECUCAO EXTERNA
echo ============================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Mudar para diretório do projeto
cd /d "%~dp0"

REM Verificar se requirements estão instalados
echo [INFO] Verificando dependencias...
python -c "import yfinance, pandas, numpy, aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Algumas dependencias podem estar faltando.
    echo [INFO] Instalando dependencias necessarias...
    pip install yfinance pandas numpy aiohttp --quiet
)

REM Verificar argumentos
set PHASE=alpha
if not "%1"=="" set PHASE=%1

echo [INFO] Iniciando execucao na FASE: %PHASE%
echo [INFO] Sistema rodando externamente - ordens aparecerao no MT5
echo.

REM Executar script principal
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py %PHASE%

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo [ERRO] Execucao falhou. Verifique os logs acima.
    pause
    exit /b 1
) else (
    echo.
    echo [SUCESSO] Execucao concluida com sucesso.
    echo [INFO] Verifique os relatorios gerados no diretorio atual.
)

pause

