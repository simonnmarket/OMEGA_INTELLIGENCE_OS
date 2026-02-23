@echo off
REM Script Batch Principal para Executar Pipeline Demo OpenMyMind Project 007
REM Versão: 1.0
REM Data: 20 de Novembro de 2025

echo ================================================================================
echo OPENMYMIND PROJECT 007 - PIPELINE EXPANDIDO DEMO
echo ================================================================================
echo.
echo Iniciando pipeline expandido OpenMyMind na conta demo...
echo Data/Hora: %DATE% %TIME%
echo.

REM Mudar para diretório raiz do projeto
cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERRO] Python nao encontrado no PATH.
    echo Por favor, instale Python 3.7+ antes de continuar.
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado.
python --version
echo.

REM Verificar se diretório de dados existe
if not exist "Core\Backtesting\data" (
    echo [INFO] Criando diretório de dados...
    mkdir "Core\Backtesting\data"
)

echo Executando pipeline expandido...
echo.
echo --------------------------------------------------------------------------------
echo.

REM Executar pipeline expandido demo
python Core\Backtesting\pipeline_expandido_demo.py

REM Capturar código de saída
set EXIT_CODE=%ERRORLEVEL%

echo.
echo --------------------------------------------------------------------------------
echo.

if %EXIT_CODE% equ 0 (
    echo.
    echo ================================================================================
    echo [SUCESSO] Pipeline executado com sucesso!
    echo ================================================================================
    echo.
    echo Relatorios gerados em: Core\Backtesting\data\
    echo.
    echo Próximos passos:
    echo   1. Revise os relatórios em data\relatorio_expandido_*.json
    echo   2. Verifique os dados coletados em data\*.parquet
    echo   3. Configure API keys se necessário para coleta on-chain/whale alerts
    echo.
    echo ================================================================================
) else if %EXIT_CODE% equ 130 (
    echo.
    echo ================================================================================
    echo [AVISO] Execução interrompida pelo usuário (Ctrl+C)
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo [ERRO] Falha na execução do pipeline (código: %EXIT_CODE%)
    echo ================================================================================
    echo.
    echo Verifique os logs acima para detalhes do erro.
    echo.
    echo Possíveis causas:
    echo   - Dependências não instaladas (pip install -r requirements.txt)
    echo   - Erro de conexão com APIs externas
    echo   - Erro de permissão de arquivo
    echo.
    echo ================================================================================
)

echo.
pause

