@echo off
REM ========================================
REM AURORA PROJECT - EXECUTOR DO SISTEMA
REM Execucao independente do Cursor
REM ========================================

echo.
echo ========================================
echo   AURORA PROJECT - EXECUTOR DO SISTEMA
echo ========================================
echo.

cd /d "%~dp0"

echo Escolha uma opcao:
echo.
echo 1. Executar Sistema Principal (main.py)
echo 2. Executar Sistema NCNT (main_ncnt.py)
echo 3. Executar Auditoria Completa
echo 4. Testar Modulo v2.0
echo 5. Verificar Instalacao
echo 6. Sair
echo.

set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" (
    echo.
    echo Executando Sistema Principal...
    echo.
    python main.py
    goto end
)

if "%opcao%"=="2" (
    echo.
    echo Executando Sistema NCNT...
    echo.
    python main_ncnt.py
    goto end
)

if "%opcao%"=="3" (
    echo.
    echo Executando Auditoria Completa...
    echo.
    python 00-Governanca\run_complete_audit.py
    goto end
)

if "%opcao%"=="4" (
    echo.
    echo Testando Modulo v2.0...
    echo.
    python 00-Governanca\test_module_v2.py
    goto end
)

if "%opcao%"=="5" (
    echo.
    echo Verificando Instalacao...
    echo.
    python scripts\verify_installation_v2.ps1
    goto end
)

if "%opcao%"=="6" (
    exit /b
)

echo Opcao invalida!

:end
echo.
pause

