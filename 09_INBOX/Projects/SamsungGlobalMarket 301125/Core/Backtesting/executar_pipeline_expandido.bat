@echo off
REM Script Batch para Executar Pipeline Expandido OpenMyMind Project 007
REM Versão: 1.0
REM Data: 20 de Novembro de 2025

echo ================================================================================
echo PIPELINE EXPANDIDO OPENMYMIND PROJECT 007 - CONTA DEMO
echo ================================================================================
echo.
echo Iniciando pipeline expandido OpenMyMind na conta demo...
echo Data/Hora: %DATE% %TIME%
echo.

cd /d "%~dp0\..\.."

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERRO: Python nao encontrado. Por favor, instale Python antes de continuar.
    pause
    exit /b 1
)

echo Executando pipeline expandido...
echo.

python Core\Backtesting\openmymind_pipeline_007_expandido.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================================================================
    echo Pipeline executado com sucesso!
    echo ================================================================================
    echo.
    echo Relatorios gerados em: Core\Backtesting\data\
    echo.
) else (
    echo.
    echo ================================================================================
    echo Falha na execucao do pipeline. Verifique logs acima.
    echo ================================================================================
    echo.
)

pause

