@echo off
chcp 65001 >nul
cls
echo ============================================================
echo PROMETHEUS V2.3 - VOLTAR AO MODO NORMAL
echo ============================================================
echo.
echo Este script altera TEST_MODE = False em prometheus_config_test.py
echo.
cd /d "%~dp0"

if not exist "prometheus_config_test.py" (
    echo ❌ Arquivo prometheus_config_test.py não encontrado!
    pause
    exit /b 1
)

echo Alterando TEST_MODE para False...
powershell -Command "(Get-Content prometheus_config_test.py) -replace 'TEST_MODE = True', 'TEST_MODE = False' | Set-Content prometheus_config_test.py"

echo.
echo ✅ Configuração alterada!
echo.
echo Verificando...
python -c "from prometheus_config_test import TEST_MODE; print(f'TEST_MODE: {TEST_MODE}')" 2>nul

echo.
echo ============================================================
echo Sistema configurado para MODO NORMAL
echo (Todos os ativos do Market Watch)
echo ============================================================
echo.
pause

