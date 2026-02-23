@echo off
echo ========================================
echo Iniciando Numeia v2.0
echo ========================================
echo.

cd /d "%~dp0Server\Numeia"
echo Diretorio: %CD%
echo.

python numeia_executor_v2.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao executar o sistema!
    pause
)

